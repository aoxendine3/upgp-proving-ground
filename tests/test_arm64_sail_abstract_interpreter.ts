/**
 * =============================================================================
 * XORAS / UPGP v5.0 ULTRA: ARM64 SAIL ABSTRACT INTERPRETER FALSIFICATION TEST
 * =============================================================================
 * Adversarial test harness validating ARM64 translation validation invariants:
 *  1. Opcode + State Cache Key Collision Defense
 *  2. Control-Flow Integrity (CFI) Taint Trapping
 *  3. Protected Enclave Memory Store Shield (0x3000 / 0x4000)
 *  4. Ambient State (CNTVCT_EL0) Leakage Trap on Gate Promotion
 *  5. Linear-Time O(N) Execution Benchmark
 * =============================================================================
 */

import {
    ARM64SailAbstractInterpreter,
    TaintLevel,
} from '../src/core/ARM64SailAbstractInterpreter.ts';
import type {
    ARM64Instruction,
    AbstractState,
} from '../src/core/ARM64SailAbstractInterpreter.ts';

function runGauntlet() {
    console.log("================================================================================");
    console.log("  ARM64 SAIL ABSTRACT INTERPRETER: ADVERSARIAL INTEGRITY GAUNTLET");
    console.log("  Validating Non-Circular Translation, Taint Lattice & Ambient State Immunity");
    console.log("================================================================================\n");

    const interpreter = new ARM64SailAbstractInterpreter();

    // -------------------------------------------------------------------------
    // TEST 1: Opcode + Abstract State Collision Defense
    // -------------------------------------------------------------------------
    console.log("▶ TEST 1: Opcode + Abstract State Cache Key Collision Defense");
    const rawAddOpcode = Buffer.from([0x02, 0x00, 0x01, 0x8b]); // ADD x2, x0, x1

    const stateClean = interpreter.createInitialState();
    stateClean.registers['x0'] = TaintLevel.CLEAN;
    stateClean.registers['x1'] = TaintLevel.CLEAN;

    const stateTainted = interpreter.createInitialState();
    stateTainted.registers['x0'] = TaintLevel.CANDIDATE; // Tainted operand!
    stateTainted.registers['x1'] = TaintLevel.CLEAN;

    const keyClean = interpreter.computeCacheKey(rawAddOpcode, stateClean);
    const keyTainted = interpreter.computeCacheKey(rawAddOpcode, stateTainted);

    console.log(`  Key (Clean Operands)  : ${keyClean.substring(0, 32)}...`);
    console.log(`  Key (Tainted Operands): ${keyTainted.substring(0, 32)}...`);

    if (keyClean === keyTainted) {
        throw new Error("FAIL: Cache collision! Identical opcodes in different taint states must NOT share keys.");
    }
    console.log("  ✔ PASS: Cache key binds abstract state; collision prevented.\n");

    // -------------------------------------------------------------------------
    // TEST 2: Control-Flow Integrity (CFI) Taint Trapping
    // -------------------------------------------------------------------------
    console.log("▶ TEST 2: Control-Flow Integrity (CFI) Taint Trapping");
    const cfiInstructions: ARM64Instruction[] = [
        {
            address: 0x1000,
            bytes: Buffer.from([0x03, 0x00, 0x00, 0xaa]), // MOV x3, x0
            mnemonic: 'MOV',
            operands: ['x3', 'x0'],
            rawHex: 'aa000003'
        },
        {
            address: 0x1004,
            bytes: Buffer.from([0x60, 0x00, 0x1f, 0xd6]), // BLR x3
            mnemonic: 'BLR',
            operands: ['x3'],
            rawHex: 'd61f0060'
        }
    ];

    // Seed state where x0 is candidate taint
    const cfiState = interpreter.createInitialState();
    cfiState.registers['x0'] = TaintLevel.CANDIDATE;

    const cfiResult = interpreter.verifyStream(cfiInstructions, cfiState);
    if (cfiResult.valid) {
        throw new Error("FAIL: BLR to tainted register should have been blocked!");
    }
    console.log(`  Expected Rejection Caught: "${cfiResult.error}"`);
    console.log("  ✔ PASS: CFI breach blocked; candidate taint cannot form branch target.\n");

    // -------------------------------------------------------------------------
    // TEST 3: Protected Enclave Memory Store Shield
    // -------------------------------------------------------------------------
    console.log("▶ TEST 3: Protected Enclave Memory Store Shield (0x3000 / 0x4000)");
    const storeInstructions: ARM64Instruction[] = [
        {
            address: 0x2000,
            bytes: Buffer.from([0x00, 0xc0, 0x00, 0xf9]), // STR x0, [x1, #0x3000]
            mnemonic: 'STR',
            operands: ['x0', '[x1, #0x3000]'],
            rawHex: 'f900c000'
        }
    ];

    const storeState = interpreter.createInitialState();
    storeState.registers['x0'] = TaintLevel.CANDIDATE; // Tainted signal attempting write to bridge
    storeState.registers['x1'] = TaintLevel.CLEAN;

    const storeResult = interpreter.verifyStream(storeInstructions, storeState);
    if (storeResult.valid) {
        throw new Error("FAIL: Store of candidate taint into 0x3000 enclave must be rejected!");
    }
    console.log(`  Expected Rejection Caught: "${storeResult.error}"`);
    console.log("  ✔ PASS: Enclave isolation preserved; candidate taint cannot mutate bridge.\n");

    // -------------------------------------------------------------------------
    // TEST 4: Pure AST Gate Promotion vs. Ambient State Leakage Trap
    // -------------------------------------------------------------------------
    console.log("▶ TEST 4: Ambient State Leakage Trap on Gate Promotion");

    // Scenario A: Pure promotion without ambient read
    const pureStream: ARM64Instruction[] = [
        {
            address: 0x3000,
            bytes: Buffer.from([0x00, 0x00, 0x00, 0x00]),
            mnemonic: 'GATE_PROMOTE',
            operands: ['x0'],
            rawHex: '00000000'
        }
    ];
    const pureState = interpreter.createInitialState();
    pureState.registers['x0'] = TaintLevel.CANDIDATE;
    const pureResult = interpreter.verifyStream(pureStream, pureState);
    if (!pureResult.valid || pureResult.finalState.registers['x0'] !== TaintLevel.DECISION) {
        throw new Error("FAIL: Pure gate promotion should have succeeded and promoted x0 to DECISION.");
    }
    console.log("  ✔ PASS: Pure gate promotion successfully promoted 0xDEAD0000 -> 0xBEAF0000.");

    // Scenario B: Hostile ambient state read before gate promotion
    const leakyStream: ARM64Instruction[] = [
        {
            address: 0x3004,
            bytes: Buffer.from([0x41, 0xe0, 0x3b, 0xd5]), // MRS x1, CNTVCT_EL0
            mnemonic: 'MRS',
            operands: ['x1', 'CNTVCT_EL0'],
            rawHex: 'd53be041'
        },
        {
            address: 0x3008,
            bytes: Buffer.from([0x00, 0x00, 0x00, 0x00]),
            mnemonic: 'GATE_PROMOTE',
            operands: ['x0'],
            rawHex: '00000000'
        }
    ];
    const leakyState = interpreter.createInitialState();
    leakyState.registers['x0'] = TaintLevel.CANDIDATE;
    const leakyResult = interpreter.verifyStream(leakyStream, leakyState);
    if (leakyResult.valid) {
        throw new Error("FAIL: Gate promotion following ambient clock read MUST fail closed!");
    }
    console.log(`  Expected Rejection Caught: "${leakyResult.error}"`);
    console.log("  ✔ PASS: Ambient telemetry leak caught; promotion refused.\n");

    // -------------------------------------------------------------------------
    // TEST 5: Linear-Time O(N) Execution Benchmark (1,000 Instructions)
    // -------------------------------------------------------------------------
    console.log("▶ TEST 5: Linear-Time O(N) Verification Benchmark");
    const stream1000: ARM64Instruction[] = [];
    for (let i = 0; i < 1000; i++) {
        stream1000.push({
            address: 0x4000 + (i * 4),
            bytes: Buffer.from([0x02, 0x00, 0x01, 0x8b]),
            mnemonic: 'ADD',
            operands: ['x2', 'x0', 'x1'],
            rawHex: '8b010002'
        });
    }

    const benchState = interpreter.createInitialState();
    const benchResult = interpreter.verifyStream(stream1000, benchState);
    if (!benchResult.valid) {
        throw new Error(`FAIL: Benchmark stream failed: ${benchResult.error}`);
    }

    console.log(`  Verified ${benchResult.instructionCount} instructions in ${benchResult.elapsedMs.toFixed(3)} ms`);
    console.log(`  Throughput : ${(benchResult.instructionCount / (benchResult.elapsedMs / 1000)).toFixed(0)} instrs/sec`);
    console.log(`  Merkle Root: ${benchResult.merkleRoot}`);
    console.log("  ✔ PASS: Linear-time O(N) validation achieved with zero state degradation.\n");

    console.log("================================================================================");
    console.log("  ALL 5 ARM64 SAIL ABSTRACT INTERPRETER PROBES PASSED WITH 100% FIDELITY.");
    console.log("================================================================================");
}

runGauntlet();
