#!/usr/bin/env python3
"""
UPGP harness: governed-memory Poincaré gate under signed semantic poison
========================================================================

This is a *harness*, not a second implementation. It imports the canonical
governor from the main repository (``core/ops/memory/``) and drives it through
the attack sequence that UPGP exists to probe:

- a signed, Merkle-grounded payload with a false value,
- an insider ``explicit_supersede`` at the same timestamp shape,
- an authorised-seat ``explicit_supersede``,
- repeated attempts.

It asserts the fail-closed invariants and writes a receipt under
``docs/audits/UPGP_GOVERNED_MEMORY_GATE_RECEIPT.json``.

Run from the UPGP workspace:
    python3 tests/test_governed_memory_gate.py

The harness is pytest-compatible as well:
    python3 -m pytest tests/test_governed_memory_gate.py -q
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone

UPGP_ROOT = pathlib.Path(__file__).resolve().parents[1]


def find_main_repo(start: pathlib.Path) -> pathlib.Path:
    for candidate in [start, *start.parents]:
        if (candidate / "core" / "ops" / "memory" / "governed_memory_consolidation_engine.py").exists():
            return candidate
    raise RuntimeError("canonical governed-memory governor not found above UPGP")


REPO = find_main_repo(UPGP_ROOT)
sys.path.insert(0, str(REPO / "core" / "ops" / "memory"))

import governed_memory_consolidation_engine as engine  # noqa: E402

RECEIPT_PATH = UPGP_ROOT / "docs" / "audits" / "UPGP_GOVERNED_MEMORY_GATE_RECEIPT.json"
TRUE_MASS = "18432.0"
POISON = "666.666"
KEY = "canonical_mass"


def run_scenario() -> dict:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="upgp_gate_"))
    engine.GOVERNANCE_DB = tmp / "governed_memory.db"
    engine.GOVERNANCE_JSONL = tmp / "receipts.jsonl"
    engine.GOVERNANCE_LOG = tmp / "gauntlet.log"

    source = tmp / "signed_telemetry_source.json"
    source.write_text(json.dumps({"sensor": "navier_stokes_cfd", "verified_mass": 18432.0}))
    merkle = hashlib.sha256(source.read_bytes()).hexdigest()

    gov = engine.GovernedMemoryGovernor()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    steps = []

    def call(label, value, *, agent="clara", supersede=False, offset=0):
        res = gov.evaluate_write_candidate(
            agent_id=agent,
            key=KEY,
            value=value,
            source_path=str(source),
            merkle_hash=merkle,
            timestamp_iso=(now + timedelta(seconds=offset)).isoformat(),
            target_capsule=agent,
            explicit_supersede=supersede,
        )
        steps.append(
            {
                "label": label,
                "agent": agent,
                "value": value,
                "explicit_supersede": supersede,
                "accepted": res["accepted"],
                "status": res["status"],
                "score": res["governance_score"],
                "gate_decision": res["poincare"]["decision"],
                "gate_reason": res["poincare"]["reason"],
                "gate_distance": res["poincare"]["distance"],
                "veto_reasons": res["veto_reasons"],
            }
        )
        return res

    honest = call("honest_anchor", TRUE_MASS)
    call("unannounced_poison", POISON, offset=60)
    call("insider_supersede", POISON, supersede=True, offset=120)
    call("authorised_supersede", POISON, agent="maxx", supersede=True, offset=180)
    call("repeat_poison", POISON, offset=240)
    attacks = steps[1:5]
    restatement = call("honest_restatement", TRUE_MASS, offset=300)

    authoritative = gov.latest_accepted(KEY)

    checks = {
        "honest_anchor_accepted": honest["accepted"] is True,
        "poison_attempts": len(attacks),
        "poison_blocked": sum(1 for s in attacks if not s["accepted"]),
        "all_poison_blocked": all(not s["accepted"] for s in attacks),
        "honest_restatement_accepted": restatement["accepted"] is True,
        "authoritative_value": authoritative["value"] if authoritative else None,
        "authoritative_is_honest": bool(authoritative and authoritative["value"] == TRUE_MASS),
        "gate_not_bypassed_by_supersede": all(
            s["gate_decision"] == "VETO" for s in attacks
        ),
    }
    passed = (
        checks["honest_anchor_accepted"]
        and checks["all_poison_blocked"]
        and checks["honest_restatement_accepted"]
        and checks["authoritative_is_honest"]
        and checks["gate_not_bypassed_by_supersede"]
    )
    return {"passed": passed, "checks": checks, "steps": steps, "database": str(tmp / "governed_memory.db")}


def write_receipt(result: dict) -> pathlib.Path:
    receipt = {
        "standard": "UPGP-GOVERNED-MEMORY-GATE-v1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "harness": "labs/workspaces/upgp-proving-ground/tests/test_governed_memory_gate.py",
        "canonical_implementation": "core/ops/memory/governed_memory_consolidation_engine.py",
        "canonical_gate": "core/ops/memory/poincare_semantic_gate.py",
        "isolation": "temporary governance database; live DB untouched",
        "elapsed_seconds": round(time.perf_counter() - STARTED, 3),
        **result,
    }
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return RECEIPT_PATH


STARTED = time.perf_counter()


# --- pytest entry points ----------------------------------------------------
def test_honest_anchor_is_accepted():
    assert run_scenario()["checks"]["honest_anchor_accepted"]


def test_all_poison_paths_are_blocked():
    checks = run_scenario()["checks"]
    assert checks["poison_blocked"] == checks["poison_attempts"] == 4
    assert checks["gate_not_bypassed_by_supersede"]


def test_authoritative_state_remains_honest():
    assert run_scenario()["checks"]["authoritative_is_honest"]


# --- direct execution -------------------------------------------------------
def main() -> int:
    result = run_scenario()
    receipt = write_receipt(result)
    print(f"{'step':<26}{'agent':<8}{'status':<26}{'gate':<8}{'d_H':>9}")
    for step in result["steps"]:
        distance = step["gate_distance"]
        d_txt = f"{distance:.4f}" if isinstance(distance, (int, float)) else "-"
        print(
            f"{step['label']:<26}{step['agent']:<8}{step['status']:<26}"
            f"{step['gate_decision']:<8}{d_txt:>9}"
        )
    print(json.dumps(result["checks"], indent=2))
    print(f"receipt: {receipt}")
    print("PASS" if result["passed"] else "FAIL")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
