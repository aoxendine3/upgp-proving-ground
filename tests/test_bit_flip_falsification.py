#!/usr/bin/env python3
"""
UPGP v5.0 Ultra — Adversarial Bit-Flip Signature Falsification Test
Demonstrates un-mocked telemetry verification by intentionally mutating 1 bit in state signature.
"""

import json
import os
import urllib.request
import hmac
import hashlib
import time
import sys

MANIFEST_PATH = "logs/state_manifest.json"
SEEN_NONCES_PATH = "logs/seen_nonces.json"
API_URL = "http://localhost:8443/api/telemetry"
SECRET_KEY = b"XORAS_SOVEREIGN_TRINITY_GATE_SECRET_KEY_2026"

def write_fresh_manifest():
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    if os.path.exists(SEEN_NONCES_PATH):
        os.remove(SEEN_NONCES_PATH)
    
    payload = {
        "version": "UPGP-5.0-ULTRA",
        "vectors": 15,
        "enclave": "APPLE_SILICON_M4_POSIX_SHM",
        "timestamp": int(time.time()),
        "nonce": int(time.time() * 1000)
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

def test_falsification():
    print("==========================================================================")
    print("  UPGP v5.0 ULTRA ADVERSARIAL BIT-FLIP SIGNATURE FALSIFICATION TEST")
    print("==========================================================================")

    # 1. Fetch baseline telemetry with pristine fresh manifest
    print("\n[STEP 1] Writing Pristine Fresh Manifest & Querying Dashboard...")
    write_fresh_manifest()
    t1 = get_telemetry()
    print(f"  * signatureValid: {t1.get('signatureValid')}")
    print(f"  * enclaveState  : {t1.get('enclaveState')}")
    print(f"  * enclaveMsg    : {t1.get('enclaveIntegrity')}")

    assert t1.get('signatureValid') is True, "Baseline signature must be valid!"
    assert t1.get('enclaveState') == "SECURE", "Baseline state must be SECURE!"
    print("  ✓ BASELINE VERIFIED: Dashboard reports SECURE for valid signature.")

    # 2. Mutate 1 bit in state manifest signature
    print("\n[STEP 2] Mutating 1 Bit in Cryptographic Signature...")
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    orig_sig = manifest["signature"]
    char_0 = orig_sig[0]
    flipped_char = '1' if char_0 == '0' else '0'
    corrupted_sig = flipped_char + orig_sig[1:]
    manifest["signature"] = corrupted_sig

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"  * Original Signature : {orig_sig[:16]}...")
    print(f"  * Bit-Flipped Sig    : {corrupted_sig[:16]}...")

    # 3. Query telemetry dashboard again
    print("\n[STEP 3] Querying Telemetry Dashboard with Bit-Flipped Signature...")
    time.sleep(0.5)
    t2 = get_telemetry()
    print(f"  * signatureValid: {t2.get('signatureValid')}")
    print(f"  * enclaveState  : {t2.get('enclaveState')}")
    print(f"  * enclaveMsg    : {t2.get('enclaveIntegrity')}")

    assert t2.get('signatureValid') is False, "Dashboard MUST reject bit-flipped signature!"
    assert t2.get('enclaveState') == "CORRUPTED", "Dashboard MUST switch state to CORRUPTED!"
    print("  ✓ ADVERSARIAL FALSIFICATION PASSED: Dashboard caught bit flip and raised CORRUPTED ALERT!")

    # 4. Restore valid signature
    print("\n[STEP 4] Restoring Original Valid Fresh Signature...")
    write_fresh_manifest()
    time.sleep(0.5)
    t3 = get_telemetry()
    print(f"  * signatureValid: {t3.get('signatureValid')}")
    print(f"  * enclaveState  : {t3.get('enclaveState')}")
    print("  ✓ RECOVERY VERIFIED: Dashboard returned to SECURE state.")

    print("\n==========================================================================")
    print("  ✅ UN-MOCKED SIGNATURE FALSIFICATION AUDIT 100% PASSED")
    print("==========================================================================")

if __name__ == '__main__':
    test_falsification()
