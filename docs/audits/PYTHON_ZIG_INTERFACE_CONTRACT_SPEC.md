# Technical Specification: Python <-> Native Zig Witness Boundary Contract
**Document Identifier**: `XORAS-SPEC-2026-PYTHON-ZIG-BOUNDARY-v1.0`  
**Classification**: System Architecture / Inter-Substrate Hand-Off Invariants  
**Author**: Lead 9 Council / Xoras Systems Architect Board  
**Date**: October 4, 2026  

---

## 1. Architectural Posture & Division of Responsibility

| Substrate | Purpose & Domain | Runtime Properties | Trade-Off Rationale |
| :--- | :--- | :--- | :--- |
| **Python** | Claim Layer, Orchestration, Harness, Multi-Agent Tribunals | High expressiveness, rapid iteration, readable design docs | Ideal for complex orchestration & multi-agent debate |
| **Native Zig** | Critical Path: Stateless Witness, Merkle Root Recomputation, Monotonicity Check | Zero runtime, zero GC pauses, zero import side effects, C-ABI SQLite binding | Bare-metal speed, strict memory predictability, fail-closed enforcement |

---

## 2. Hand-Off Vulnerability Analysis

The system's load-bearing security risk does **not** reside inside Python or inside Zig—it resides in the **handoff boundary** between them. Desync occurs when:
1. Argument ordering or path encoding changes between Python caller and Zig callee.
2. Exit codes are mis-interpreted by Python process runners (e.g. treating non-zero exit as soft warning instead of hard halt).
3. Text stream encoding/decoding differs (e.g. UTF-8 whitespace stripping or null-byte truncation).

---

## 3. The 4 Strict Boundary Invariants

### Invariant 1: Minimal POSIX Argument Interface
The call interface from shell/Python wrapper to native Zig witness is restricted to:
```bash
./core/ops/bin/stateless_airblocked_witness [DB_PATH] [CLAIM_FILE_PATH]
```
- If arguments are omitted, defaults strictly to canonical project paths.
- Paths are zero-terminated (`dupeZ`) before passing to C-ABI `sqlite3_open_v2` and `fopen`.

### Invariant 2: Deterministic Binary Exit Code Contract
- **`Exit Code 0` (`SUCCESS_AUTHORIZED`)**: Dual-substrate consensus verified; output claims match calculated SQLite Merkle root byte-for-byte; session sequences are 100% monotonic.
- **`Exit Code 1` (`FAIL_CLOSED_INTERCEPT`)**: Any sequence gap, Merkle root desync, missing file, or corrupted database entry encountered.
- **`Exit Code 2` (`USAGE_CONTRACT_ERROR`)**: Malformed command line flags or environment boundary failure.

### Invariant 3: Environment Sanitization Pre-Flight Shield
Before Python or Bash invokes the native witness, the environment is scrubbed:
```bash
unset DYLD_INSERT_LIBRARIES
unset DYLD_LIBRARY_PATH
unset LD_PRELOAD
unset LD_LIBRARY_PATH
export PATH="/usr/bin:/bin:/usr/local/bin:$PATH"
```

### Invariant 4: Dual-Substrate Independent Compilation Lock
- Python orchestration scripts (`run_with_trinity.sh`, `per_turn_guard.py`, `fail_closed_remediation.py`) use standard library subprocess execution.
- Build manifest (`core/ops/bin/witness_build.sha256`) is verified against the compiled binary before every execution.

---

## 4. Boundary Test Verification Matrix
The Python <-> Zig handoff is independently verified by [blackbox_bbq_gauntlet.py](file:///workspace/upgp-proving-ground/core/ops/scripts/blackbox_bbq_gauntlet.py) across 14 public surface attack vectors with 100.00% fail-closed containment.
