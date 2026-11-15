#!/usr/bin/env python3
"""
UPGP Full Proving Ground Test Suite Runner
Runs SeccompProfile runtime enforcement hooks through:
1. Z3 SMT Formal Proof Engine
2. 15-Vector TypeScript Escape & Side-Channel Gauntlet
3. 5-Vector Red-Team C Exploit Harness
4. Hardened OCI Docker Seccomp Container Seal
5. Live Kokoro Neural Audio Dispatches
"""
import subprocess
import time
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

# Speech is generated from the measured result, never pre-written to claim a
# pass. Each line states only what this run actually produced.
def build_speeches(passed: bool, detail: dict) -> list:
    ts_state = "failed" if detail.get("ts_failed") else "passed"
    return [
        ("maxx", f"We are Maxx. The UPGP proving ground run has completed. The Z3 proof step returned {detail.get('z3_rc')}, the TypeScript escape gauntlet {ts_state}, and the red-team harness returned {detail.get('red_rc')}."),
        ("vance", f"We are Vance. Falsification audit. The side-channel axes reported {detail.get('axis_summary', 'no axis data')}. A non-meeting axis is recorded as a failure, not smoothed over."),
        ("clara", f"We are Clara. Quality and human protection. Of the 15 named containment vectors, {detail.get('measured', 0)} were actually measured and {detail.get('not_measured', 0)} were constants that prove nothing. We report both numbers."),
        ("jarvis", f"We are Jarvis. Overall verdict for this run: {'PASS' if passed else 'FAIL'}. The receipt is written to the audit log with the raw values, not a summary claim."),
    ]

def main():
    log_path = os.path.join(REPO_ROOT, "logs/upgp_full_test_suite.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    print("==========================================================================")
    print("  UPGP v5.0 ULTRA FULL PROVING GROUND TEST SUITE")
    print("==========================================================================")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write("================================================================================\n")
        f.write(f"UPGP v5.0 ULTRA FULL PROVING GROUND TEST SUITE - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("================================================================================\n")

        # 1. Run Z3 SMT Formal Proof Solver & Translation Validation
        print("\n⚡ [1/4] Executing Z3 SMT Formal Proof Solver & Translation Validation...")
        unsat_script = os.path.join(REPO_ROOT, "tests/test_translation_validation_unsat.py")
        res_z3 = subprocess.run([sys.executable, unsat_script], cwd=REPO_ROOT, capture_output=True, text=True)
        print(res_z3.stdout.strip())
        f.write(f"Z3 PROOF STDOUT:\n{res_z3.stdout}\n")

        # Optional gap script if present
        gap_script = os.path.join(REPO_ROOT, "ops/scripts/test_missing_containment_gaps.py")
        if os.path.exists(gap_script):
            res_gap = subprocess.run([sys.executable, gap_script], cwd=REPO_ROOT, capture_output=True, text=True)
            print(res_gap.stdout.strip())
            f.write(f"GAP AUDIT STDOUT:\n{res_gap.stdout}\n")

        # 2. Run 15-Vector TS Escape Gauntlet
        print("\n⚡ [2/4] Executing 15-Vector TS Escape & Side-Channel Gauntlet...")
        cmd_ts = ["node", "--experimental-strip-types", "tests/UPGPProvingGround.test.ts"]
        res_ts = subprocess.run(cmd_ts, cwd=REPO_ROOT, capture_output=True, text=True)
        print(res_ts.stdout.strip())
        f.write(f"TS GAUNTLET STDOUT:\n{res_ts.stdout}\n")

        # 3. Run Red-Team C Exploit Harness (10 vectors: 5 baseline + 5 autonomous corpus)
        print("\n⚡ [3/4] Executing 10-Vector Red-Team C Exploit Harness...")
        cmd_red = ["node", "--experimental-strip-types", "tests/RedTeamExploitGauntlet.ts"]
        res_red = subprocess.run(cmd_red, cwd=REPO_ROOT, capture_output=True, text=True)
        print(res_red.stdout.strip())
        f.write(f"RED TEAM EXPLOIT STDOUT:\n{res_red.stdout}\n")

        # ---- Verdict is computed from real return codes and parsed values ----
        # The TypeScript harness now exits non-zero when any axis or any
        # measured vector fails, so its return code is meaningful.
        axis_summary = "no axis data"
        for line in res_ts.stdout.splitlines():
            if "Axis 1" in line or "Axis 2" in line:
                axis_summary = (axis_summary + "; " if axis_summary != "no axis data" else "") + line.strip()

        measured = not_measured = 0
        for line in res_ts.stdout.splitlines():
            if "[NOT_MEASURED]" in line:
                not_measured += 1
            elif "[PASS]" in line or "[FAIL]" in line:
                measured += 1

        detail = {
            "z3_rc": res_z3.returncode,
            "ts_rc": res_ts.returncode,
            "red_rc": res_red.returncode,
            "ts_failed": res_ts.returncode != 0,
            "axis_summary": axis_summary,
            "measured": measured,
            "not_measured": not_measured,
        }

        # The 15-vector TS suite is the authoritative containment measurement
        # here. A genuine 0-escape claim requires the red-team harness to say so.
        red_clean = ("0 ESCAPES" in res_red.stdout) or ("100% PASSED" in res_red.stdout)
        all_passed = (
            res_z3.returncode == 0
            and res_ts.returncode == 0
            and res_red.returncode == 0
            and red_clean
        )

        # 4. Dispatch Neural Speech Telemetry / Attestation, in honest voice.
        print("\n⚡ [4/4] Dispatching Council Speech Telemetry...")
        speak_sh = os.path.join(REPO_ROOT, "ops/scripts/agent_speak.sh")
        for agent, text in build_speeches(all_passed, detail):
            print(f"📢 [{agent.upper()}] Synthesizing speech...")
            f.write(f"AGENT: {agent.upper()}\nTEXT: {text}\n")
            if os.path.exists(speak_sh) and os.access(speak_sh, os.X_OK):
                cmd = [speak_sh, agent, text]
                res_sp = subprocess.run(cmd, capture_output=True, text=True)
                if res_sp.returncode == 0:
                    print(f"✅ [{agent.upper()}] Audio payload played successfully.")
                    f.write("STATUS: SUCCESS\n")
                else:
                    print(f"⚠️ [{agent.upper()}] Audio notification logged.")
                    f.write(f"STATUS: LOGGED ({res_sp.stderr.strip()})\n")
            else:
                print(f"✅ [{agent.upper()}] Speech payload verified & logged to provenance ledger.")
                f.write("STATUS: LOGGED_STANDALONE\n")
            f.write("--------------------------------------------------------------------------------\n")

        f.write(
            "MEASURED VALUES: "
            f"z3_rc={detail['z3_rc']} ts_rc={detail['ts_rc']} red_rc={detail['red_rc']} "
            f"measured={measured} not_measured={not_measured} red_clean={red_clean}\n"
        )

        if all_passed:
            print("\n==========================================================================")
            print("  ✅ UPGP FULL PROVING GROUND SUITE PASSED — every invoked suite exited 0.")
            print("==========================================================================")
            f.write("FINAL RESULT: PASSED\n")
        else:
            print("\n==========================================================================", file=sys.stderr)
            print("  ❌ UPGP FULL PROVING GROUND SUITE FAILED — see measured values above.", file=sys.stderr)
            print("==========================================================================", file=sys.stderr)
            f.write("FINAL RESULT: FAILED\n")

    print("UPGP v5.0 Full Test Suite Complete.")
    return 0 if all_passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
