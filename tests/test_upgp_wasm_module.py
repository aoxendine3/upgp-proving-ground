#!/usr/bin/env python3
import subprocess
import os
import sys

def test_wasm_binary():
    wasm_path = "docs/assets/wasm/upgp_simulator.wasm"
    if not os.path.exists(wasm_path):
        wasm_path = "assets/wasm/upgp_simulator.wasm"
    if not os.path.exists(wasm_path):
        print(f"❌ WASM Binary not found at docs/assets/wasm/upgp_simulator.wasm or assets/wasm/upgp_simulator.wasm")
        sys.exit(1)
        
    print(f"[STEP 1] Validating Compiled Stateful WASM File Exists ({os.path.getsize(wasm_path)} bytes)...")
    
    node_test_script = f"""
    const fs = require('fs');
    const wasmBuffer = fs.readFileSync('{wasm_path}');
    
    WebAssembly.instantiate(wasmBuffer).then(wasmModule => {{
        const exports = wasmModule.instance.exports;
        console.log('  * WASM Exports:', Object.keys(exports));
        
        const hexSize = exports.init_hexcell_topology(25);
        console.log('  * init_hexcell_topology(25) =', hexSize, '(Expected 3200)');
        if (hexSize !== 3200) process.exit(1);
        
        const ops = exports.simulate_mtpo_concurrency(100, 1000);
        console.log('  * simulate_mtpo_concurrency(100, 1000) =', ops);
        if (ops <= 0) process.exit(1);
        
        const rollback = exports.trigger_saga_rollback(42);
        console.log('  * trigger_saga_rollback(42) =', rollback, '(Expected 1)');
        if (rollback !== 1) process.exit(1);
        
        const nonce = 1791648000000n;
        
        // 1. Fresh Nonce Pass -> Expected 1 (SECURE)
        const res1 = exports.verify_state_signature(nonce, 0xABCDEF, 0x76);
        console.log('  * verify_state_signature(Fresh Nonce) =', res1, '(Expected 1 SECURE)');
        if (res1 !== 1) process.exit(1);
        
        // 2. Duplicate Nonce Replay Pass -> Expected 2 (REPLAY ATTACK)
        const res2 = exports.verify_state_signature(nonce, 0xABCDEF, 0x76);
        console.log('  * verify_state_signature(Duplicate Nonce) =', res2, '(Expected 2 REPLAY ATTACK)');
        if (res2 !== 2) process.exit(1);
        
        // 3. Bit-flipped signature pass -> Expected 0 (CORRUPTED)
        const res3 = exports.verify_state_signature(1791649000000n, 0xABCDEF, 0x06);
        console.log('  * verify_state_signature(Bit Flipped) =', res3, '(Expected 0 CORRUPTED)');
        if (res3 !== 0) process.exit(1);
        
        console.log('✅ ALL STATEFUL WASM EXPORTED FUNCTIONS PASSED UN-MOCKED INTEGRITY CHECKS!');
    }}).catch(err => {{
        console.error('❌ WASM Instantiation Error:', err);
        process.exit(1);
    }});
    """
    
    result = subprocess.run(["node", "-e", node_test_script], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ WASM Test Failed:\n{result.stderr}")
        sys.exit(1)
        
    print("==========================================================================")
    print("  ✅ UN-MOCKED STATEFUL WEBASSEMBLY KERNEL VERIFICATION 100% PASSED")
    print("==========================================================================")

if __name__ == "__main__":
    test_wasm_binary()
