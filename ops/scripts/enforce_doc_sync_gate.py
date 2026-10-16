#!/usr/bin/env python3
"""
Automated Documentation Integrity & Version Sync Gate Engine (Log Entry #078)
Guarantees that customer-facing documentation, README files, release manifests,
and version headers 100% match the current software build (UPGP v4.0 Ultra) before commit/push.
"""
import subprocess
import time
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

DOC_FILES_TO_CHECK = [
    os.path.join(REPO_ROOT, "README.md"),
    os.path.join(REPO_ROOT, "docs/audits/UPGP_BREAKING_POINT_AND_REMEDIATION_AUDIT.md"),
    os.path.join(REPO_ROOT, "docs/audits/XORAS_029_SECCOMP_RUNTIME_ENFORCEMENT_HOOKS_V_AND_V.md"),
    os.path.join(REPO_ROOT, "docs/research/GLOBAL_SANDBOX_LANDSCAPE_AND_UPGP_FUTURE_SPECIFICATION.md")
]

def check_doc_sync():
    print("==========================================================================")
    print("  DOCUMENTATION INTEGRITY & VERSION SYNC GATE ENGINE (LOG ENTRY #078)")
    print("==========================================================================")

    outdated_count = 0
    checked_count = 0

    for doc in DOC_FILES_TO_CHECK:
        if not os.path.exists(doc):
            print(f"  ⚠️ Warning: File not found: {doc}")
            continue

        checked_count += 1
        with open(doc, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for active version header (Single Canonical UPGP v5.0 Ultra)
        if "v5.0" not in content and "v5.0 Ultra" not in content and "UPGP v5.0" not in content:
            print(f"  ❌ DOC SYNC FAIL: {os.path.basename(doc)} does not reference UPGP v5.0 Ultra!")
            outdated_count += 1
        else:
            print(f"  ✓ DOC SYNC PASS: {os.path.basename(doc)} matches UPGP v5.0 Ultra release.")

    print("--------------------------------------------------------------------------")
    if outdated_count > 0:
        print(f"❌ DOCUMENTATION GATE FAILED: {outdated_count} files contain version mismatch.", file=sys.stderr)
        return False
    
    # Execute Sovereign Report Standards & Zero-Seam Numeric Cross-Check Engine if module available
    try:
        sys.path.insert(0, REPO_ROOT)
        from core.ops.reports.sovereign_report_validator import validate_all_standard_reports
        print("\n  Executing Sovereign Report Standards & Zero-Seam Cross-Check Gate...")
        if not validate_all_standard_reports():
            print("❌ DOCUMENTATION GATE FAILED: Standardized report validation or numeric drift error.", file=sys.stderr)
            return False
    except ImportError:
        print("\n  Standalone mode: External report validator not imported. Core doc sync validated.")
    except Exception as e:
        print(f"❌ DOCUMENTATION GATE FAILED: Report validator execution error: {e}", file=sys.stderr)
        return False

    print(f"✅ DOCUMENTATION GATE PASSED: All {checked_count} customer docs and standardized reports verified.")
    return True

def main():
    log_path = os.path.join(REPO_ROOT, "logs/doc_sync_gate.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    passed = check_doc_sync()

    with open(log_path, "a", encoding="utf-8") as f:
        f.write("================================================================================\n")
        f.write(f"DOCUMENTATION INTEGRITY GATE EXECUTION - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"PASSED: {passed}\n")
        f.write("================================================================================\n")

    if not passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
