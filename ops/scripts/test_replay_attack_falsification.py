#!/usr/bin/env python3
"""
UPGP v5.0 Ultra — Adversarial Replay Attack Falsification Test
Tests:
1. Duplicate Payload Replay Attack Detection
2. Stale Timestamp Replay Attack Detection (Max 30s drift)
3. Fresh Payload Recovery
"""

import json
import os
import urllib.request
import hmac
import hashlib
import time
import sys
import ssl

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
LOCAL_LOGS = os.path.join(REPO_ROOT, "logs")
os.makedirs(LOCAL_LOGS, exist_ok=True)

MANIFEST_PATH = os.environ.get("UPGP_MANIFEST_PATH", os.path.join(LOCAL_LOGS, "state_manifest.json"))
SEEN_NONCES_PATH = os.environ.get("UPGP_NONCES_PATH", os.path.join(LOCAL_LOGS, "seen_nonces.json"))
API_URL = os.environ.get("UPGP_API_URL", "http://localhost:8443/api/telemetry")
SECRET_KEY = b"XORAS_SOVEREIGN_TRINITY_GATE_SECRET_KEY_2026"

def write_signed_manifest(nonce: int, ts: int):
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    payload = {
        "version": "UPGP-5.0-ULTRA",
        "vectors": 15,
        "enclave": "APPLE_SILICON_M4_POSIX_SHM",
        "timestamp": ts,
        "nonce": nonce
    }
    payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
    sig = hmac.new(SECRET_KEY, payload_bytes, hashlib.sha256).hexdigest()
    manifest = {
        "payload": payload,
        "signature": sig
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return manifest

def get_telemetry():
    req = urllib.request.Request(API_URL)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def test_replay_falsification():
    print("==========================================================================")
    print("  UPGP v5.0 ULTRA ADVERSARIAL REPLAY ATTACK FALSIFICATION TEST")
    print("==========================================================================")

    # Clear seen nonces ledger for deterministic test
    if os.path.exists(SEEN_NONCES_PATH):
        os.remove(SEEN_NONCES_PATH)

    now = int(time.time())
    nonce_1 = int(time.time() * 1000)

    # 1. Fresh Payload Test
    print("\n[STEP 1] Generating Fresh State Payload (Nonce N1, T_now)...")
    write_signed_manifest(nonce_1, now)
    t1 = get_telemetry()
    print(f"  * signatureValid: {t1.get('signatureValid')}")
    print(f"  * enclaveState  : {t1.get('enclaveState')}")
    print(f"  * enclaveMsg    : {t1.get('enclaveIntegrity')}")

    assert t1.get('signatureValid') is True, "Fresh payload must pass!"
    assert t1.get('enclaveState') == "SECURE", "Fresh state must be SECURE!"
    print("  ✓ STEP 1 PASSED: Fresh state payload accepted.")

    # 2. Duplicate Payload Replay Attack Test
    print("\n[STEP 2] Executing Duplicate Payload Replay Attack (Replaying N1)...")
    # Query dashboard again without changing manifest (simulates capturing and replaying same payload)
    t2 = get_telemetry()
    print(f"  * signatureValid: {t2.get('signatureValid')}")
    print(f"  * enclaveState  : {t2.get('enclaveState')}")
    print(f"  * enclaveMsg    : {t2.get('enclaveIntegrity')}")

    assert t2.get('signatureValid') is False, "Dashboard MUST reject duplicate replayed payload!"
    assert t2.get('enclaveState') == "CORRUPTED", "Dashboard state MUST drop to CORRUPTED / ALERT!"
    assert "DUPLICATE PAYLOAD REPLAY" in t2.get('enclaveIntegrity'), "Must explicitly report duplicate replay!"
    print("  ✓ STEP 2 PASSED: Replay attack intercepted & rejected!")

    # 3. Stale Timestamp Replay Attack Test
    print("\n[STEP 3] Executing Stale Timestamp Replay Attack (T_now - 600s)...")
    stale_ts = now - 600
    nonce_stale = nonce_1 + 100
    write_signed_manifest(nonce_stale, stale_ts)
    t3 = get_telemetry()
    print(f"  * signatureValid: {t3.get('signatureValid')}")
    print(f"  * enclaveState  : {t3.get('enclaveState')}")
    print(f"  * enclaveMsg    : {t3.get('enclaveIntegrity')}")

    assert t3.get('signatureValid') is False, "Dashboard MUST reject stale timestamp payload!"
    assert t3.get('enclaveState') == "CORRUPTED", "Dashboard state MUST stay CORRUPTED!"
    assert "STALE TIMESTAMP" in t3.get('enclaveIntegrity'), "Must explicitly report stale timestamp replay!"
    print("  ✓ STEP 3 PASSED: Stale timestamp replay intercepted & rejected!")

    # 4. Fresh Valid State Commit Recovery
    print("\n[STEP 4] Submitting Fresh State Payload (Nonce N2, T_now)...")
    time.sleep(1)
    fresh_now = int(time.time())
    nonce_2 = nonce_1 + 200
    write_signed_manifest(nonce_2, fresh_now)
    t4 = get_telemetry()
    print(f"  * signatureValid: {t4.get('signatureValid')}")
    print(f"  * enclaveState  : {t4.get('enclaveState')}")
    print(f"  * enclaveMsg    : {t4.get('enclaveIntegrity')}")

    assert t4.get('signatureValid') is True, "New fresh payload must be accepted!"
    assert t4.get('enclaveState') == "SECURE", "Dashboard MUST recover to SECURE!"
    print("  ✓ STEP 4 PASSED: Dashboard recovered to SECURE for fresh state commit.")

    print("\n==========================================================================")
    print("  ✅ UN-MOCKED ANTI-REPLAY FALSIFICATION AUDIT 100% PASSED")
    print("==========================================================================")

if __name__ == '__main__':
    test_replay_falsification()
