#!/usr/bin/env python3
"""
UPGP v5.0 Ultra — Automated Product Packaging & Sovereign Bundle Generator
Builds a verified, self-contained distribution tarball with SHA-256 checksum.
"""

import subprocess
import tarfile
import hashlib
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DIST_DIR = os.path.join(REPO_ROOT, "dist")
BUNDLE_NAME = "upgp-v5.0-ultra-sovereign-bundle.tar.gz"
BUNDLE_PATH = os.path.join(DIST_DIR, BUNDLE_NAME)

FILES_TO_PACKAGE = [
    "README.md",
    "LICENSE",
    "LICENSE_COMMERCIAL.md",
    "package.json",
    "index.html",
    "seccomp_upgp.json",
    "Dockerfile.upgp",
    "docker-compose.yml",
    "core/products/upgp/SeccompProfile.ts",
    "core/products/upgp/TelemetryDashboardServer.ts",
    "src/native/upgp_seccomp_native.c",
    "ops/scripts/launch_upgp_dashboard.py",
    "ops/scripts/enforce_doc_sync_gate.py",
    "ops/scripts/test_bit_flip_falsification.py",
    "ops/scripts/test_replay_attack_falsification.py",
    "ops/scripts/run_upgp_full_test_gauntlet.py",
    "docs/assets/images/upgp_v5_ultra_telemetry_dashboard.jpg",
    "docs/assets/images/upgp_v5_ultra_kernel_isolation_flow.jpg",
    "docs/audits/XORAS_029_SECCOMP_RUNTIME_ENFORCEMENT_HOOKS_V_AND_V.md",
    "docs/audits/UPGP_BREAKING_POINT_AND_REMEDIATION_AUDIT.md",
    "docs/research/GLOBAL_SANDBOX_LANDSCAPE_AND_UPGP_FUTURE_SPECIFICATION.md",
    "tests/UPGPProvingGround.test.ts"
]

def run_preflight_tests():
    print("==========================================================================")
    print("  UPGP v5.0 ULTRA PRODUCT PACKAGING — PRE-FLIGHT VERIFICATION")
    print("==========================================================================")

    # 1. Run Doc Sync Gate
    print("\n[1/3] Verifying Documentation Integrity Gate...")
    res = subprocess.run([sys.executable, "ops/scripts/enforce_doc_sync_gate.py"], cwd=REPO_ROOT)
    if res.returncode != 0:
        print("❌ PRE-FLIGHT FAILED: Documentation gate failed.", file=sys.stderr)
        sys.exit(1)

    # Spin up dashboard server if not running
    import urllib.request
    import time
    dashboard_proc = None
    try:
        urllib.request.urlopen("http://localhost:8443/api/telemetry", timeout=1)
        print("  ✓ Telemetry dashboard already running on port 8443.")
    except Exception:
        print("  Starting background telemetry dashboard on port 8443 for pre-flight verification...")
        dashboard_proc = subprocess.Popen([sys.executable, "ops/scripts/launch_upgp_dashboard.py"], cwd=REPO_ROOT)
        time.sleep(1.5)

    try:
        # 2. Run Bit-Flip Falsification Test
        print("\n[2/3] Verifying Cryptographic Bit-Flip Falsification Engine...")
        res = subprocess.run([sys.executable, "ops/scripts/test_bit_flip_falsification.py"], cwd=REPO_ROOT)
        if res.returncode != 0:
            print("❌ PRE-FLIGHT FAILED: Bit-flip test failed.", file=sys.stderr)
            sys.exit(1)

        # 3. Run Anti-Replay Test
        print("\n[3/3] Verifying Anti-Replay Attack Engine...")
        res = subprocess.run([sys.executable, "ops/scripts/test_replay_attack_falsification.py"], cwd=REPO_ROOT)
        if res.returncode != 0:
            print("❌ PRE-FLIGHT FAILED: Anti-replay test failed.", file=sys.stderr)
            sys.exit(1)
    finally:
        if dashboard_proc:
            dashboard_proc.terminate()
            dashboard_proc.wait()

    print("\n✅ PRE-FLIGHT VERIFICATION 100% PASSED")

def package_product():
    os.makedirs(DIST_DIR, exist_ok=True)
    print(f"\n[PACKAGING] Building distribution bundle at {BUNDLE_PATH}...")

    with tarfile.open(BUNDLE_PATH, "w:gz") as tar:
        for rel_path in FILES_TO_PACKAGE:
            abs_path = os.path.join(REPO_ROOT, rel_path)
            if os.path.exists(abs_path):
                tar.add(abs_path, arcname=rel_path)
                print(f"  + Added: {rel_path}")
            else:
                print(f"  ⚠️ Warning: File missing: {rel_path}")

    # Compute SHA-256 Checksum
    with open(BUNDLE_PATH, "rb") as f:
        bundle_bytes = f.read()
    sha256_hash = hashlib.sha256(bundle_bytes).hexdigest()

    checksum_path = f"{BUNDLE_PATH}.sha256"
    with open(checksum_path, "w", encoding="utf-8") as f:
        f.write(f"{sha256_hash}  {BUNDLE_NAME}\n")

    size_mb = len(bundle_bytes) / (1024 * 1024)
    print("--------------------------------------------------------------------------")
    print(f"✅ PRODUCT BUNDLE CREATED SUCCESSFULLY")
    print(f"  * Bundle File : {BUNDLE_PATH}")
    print(f"  * Size        : {size_mb:.2f} MB")
    print(f"  * SHA-256     : {sha256_hash}")
    print(f"  * Checksum    : {checksum_path}")
    print("==========================================================================")

if __name__ == '__main__':
    run_preflight_tests()
    package_product()
