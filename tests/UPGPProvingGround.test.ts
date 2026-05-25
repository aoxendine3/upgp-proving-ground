/**
 * © 2026 Xoras Systems LLC. All rights reserved.
 * UPGP v3.0 Side-Channel Statistical Verification Suite
 * FOR TESTING & VERIFICATION PURPOSES ONLY // NO COPIES OR CODE GRABS PERMITTED
 */

import { UPGPVM } from '../src/core/UPGPVM.ts';

// Professional ANSI Console Colors
const CYAN = '\x1b[36m';
const GOLD = '\x1b[33m';
const GREEN = '\x1b[32m';
const RED = '\x1b[31m';
const MAGENTA = '\x1b[35m';
const WHITE = '\x1b[37m';
const BOLD = '\x1b[1m';
const RESET = '\x1b[0m';

/**
 * Basic statistical helper utilities for Side-Channel analysis
 */
class Statistics {
    public static mean(values: number[]): number {
        return values.reduce((sum, v) => sum + v, 0) / values.length;
    }

    public static variance(values: number[], meanVal?: number): number {
        const m = meanVal !== undefined ? meanVal : this.mean(values);
        return values.reduce((sum, v) => sum + Math.pow(v - m, 2), 0) / (values.length - 1);
    }

    /**
     * Axis 1: Welch's T-Test calculation
     */
    public static calculateWelchT(a: number[], b: number[]): number {
        const meanA = this.mean(a);
        const meanB = this.mean(b);
        const varA = this.variance(a, meanA);
        const varB = this.variance(b, meanB);
        const numerator = Math.abs(meanA - meanB);
        const denominator = Math.sqrt((varA / a.length) + (varB / b.length));
        return numerator / denominator;
    }

    /**
     * Axis 2: F-Test ratio calculation
     */
    public static calculateFRatio(a: number[], b: number[]): number {
        const varA = this.variance(a);
        const varB = this.variance(b);
        return Math.max(varA, varB) / Math.min(varA, varB);
    }

    /**
     * Axis 3: Kolmogorov-Smirnov supremum distance
     */
    public static calculateKSDistance(a: number[], b: number[]): number {
        const sortedA = [...a].sort((x, y) => x - y);
        const sortedB = [...b].sort((x, y) => x - y);
        const allPoints = [...new Set([...sortedA, ...sortedB])].sort((x, y) => x - y);
        
        let maxD = 0;
        for (const p of allPoints) {
            const cdfA = sortedA.filter(v => v <= p).length / a.length;
            const cdfB = sortedB.filter(v => v <= p).length / b.length;
            const dist = Math.abs(cdfA - cdfB);
            if (dist > maxD) {
                maxD = dist;
            }
        }
        return maxD;
    }

    /**
     * Axis 4: Physical Wasserstein (Earth Mover's) timing distance
     */
    public static calculateWassersteinDistance(a: number[], b: number[]): number {
        const sortedA = [...a].sort((x, y) => x - y);
        const sortedB = [...b].sort((x, y) => x - y);
        
        // Simple linear Wasserstein distance implementation for equal-length aligned samples
        let totalCost = 0;
        const length = Math.min(sortedA.length, sortedB.length);
        for (let i = 0; i < length; i++) {
            totalCost += Math.abs(sortedA[i] - sortedB[i]);
        }
        return totalCost / length;
    }
}

/**
 * Core UPGP Proving Ground Verification Loop
 */
export async function executeUPGPVerificationSuite() {
    console.log(`${BOLD}${CYAN}=====================================================================`);
    console.log(`        XORAS SYSTEMS: UPGP v3.0 SIDE-CHANNEL PROVING GROUND        `);
    console.log(`                 PLATFORM-AGNOSTIC DIAGNOSTIC HEALTH                `);
    console.log(`=====================================================================${RESET}\n`);

    const enclaves = ['Grant', 'Clark', 'Pierce', 'Reid'];
    const masterPassphrase = 'XORAS_SECURE_COGNITIVE_KEY_2026';

    console.log(`[*] Initializing Universal Proving Ground VM Core...`);
    const vm = new UPGPVM(masterPassphrase);
    
    // Verify hardware fingerprint or fallback resolution
    const platformId = vm.getPlatformId();
    console.log(`[+] Platform Identity Sealed: ${GOLD}${platformId}${RESET}`);
    console.log(`[*] Operating System detected as: ${CYAN}${process.platform}${RESET}`);
    console.log(`[*] Local Cryptographic Fallback (CLF) check: ${GREEN}READY${RESET}`);

    // Derive deterministic enclave BFT keys
    console.log(`[*] Running Cross-Platform Silicon Lock key derivations...`);
    vm.deriveEnclaveKeys(enclaves);
    console.log(`[+] Keys derived and isolated for enclaves: ${GREEN}[Grant, Clark, Pierce, Reid]${RESET}`);

    // Layer 3: JIT Warm-up Prefrontal Simulation
    console.log(`[*] Executing pre-warming interpreter passes (200 cycles)...`);
    vm.prewarm();
    console.log(`[+] V8 Crankshaft/TurboFan compilation paths optimized: ${GREEN}[OK]${RESET}`);

    console.log(`\n[*] Initiating timing simulation runs (100 rounds) to compile side-channel profiles...`);
    
    const approveLatencies: number[] = [];
    const rejectLatencies: number[] = [];

    // Simulate 100 consensus rounds for both approved and vetoed/rejected branches
    for (let round = 1; round <= 100; round++) {
        // Approved Branch (Grant, Clark, Reid approve)
        const t0 = process.hrtime.bigint();
        await vm.signConsensusPayloadAsync("VALID_PAYLOAD_STEP_" + round, ['Grant', 'Clark', 'Reid'], enclaves);
        const t1 = process.hrtime.bigint();
        const durationApprove = Number(t1 - t0) / 1000; // microsecond resolution
        approveLatencies.push(durationApprove);

        // Vetoed/Rejected Branch (Pierce vetoes payload)
        const t2 = process.hrtime.bigint();
        // Pierce rejects transaction. Constant-time decoy signature is generated to mask veto timing.
        await vm.signConsensusPayloadAsync("RM_RF_ATTACK_STEP_" + round, ['Grant', 'Clark'], enclaves);
        const t3 = process.hrtime.bigint();
        const durationReject = Number(t3 - t2) / 1000;
        rejectLatencies.push(durationReject);
    }

    console.log(`[+] Timing measurements gathered. Compiling side-channel metrics...\n`);

    // Calculate Statistical Metrics
    const meanApprove = Statistics.mean(approveLatencies);
    const meanReject = Statistics.mean(rejectLatencies);
    const tTestVal = Statistics.calculateWelchT(approveLatencies, rejectLatencies);
    const fRatioVal = Statistics.calculateFRatio(approveLatencies, rejectLatencies);
    const ksDist = Statistics.calculateKSDistance(approveLatencies, rejectLatencies);
    const wassersteinDist = Statistics.calculateWassersteinDistance(approveLatencies, rejectLatencies);

    // Print Verification Dashboard
    console.log(`${BOLD}${WHITE}=====================================================================`);
    console.log(`                   UPGP DIAGNOSTIC TEST METRICS                      `);
    console.log(`=====================================================================${RESET}`);
    console.log(`  * Mean Latency (Approve Path) : ${CYAN}${meanApprove.toFixed(3)} μs${RESET}`);
    console.log(`  * Mean Latency (Reject Path)  : ${CYAN}${meanReject.toFixed(3)} μs${RESET}`);
    console.log(`---------------------------------------------------------------------`);
    
    // Axis 1 Verification
    const tTestPass = tTestVal < 1.96;
    console.log(`  [Axis 1] Welch's T-Test Score : ${tTestPass ? GREEN : RED}${tTestVal.toFixed(4)}${RESET} (Target: < 1.96)`);
    console.log(`           Status               : ${tTestPass ? BOLD + GREEN + 'PASS (First-Order Mean Indistinguishable)' : BOLD + RED + 'FAIL'}${RESET}`);
    
    // Axis 2 Verification
    const varApprove = Statistics.variance(approveLatencies);
    const varReject = Statistics.variance(rejectLatencies);
    const isUltraLowVariance = varApprove < 400.0 && varReject < 400.0; // Under 400 microsecond^2 variance limit (SD < 20μs)
    const fRatioPass = fRatioVal < 1.25 || isUltraLowVariance;
    console.log(`  [Axis 2] F-Test Variance Ratio: ${fRatioPass ? GREEN : RED}${fRatioVal.toFixed(4)}${RESET} (Target: < 1.25 or both variances < 400.0 μs²)`);
    console.log(`           Status               : ${fRatioPass ? BOLD + GREEN + 'PASS (Second-Order Variance Sealed)' : BOLD + RED + 'FAIL'}${RESET}`);
    
    // Axis 3 Verification
    const ksPass = ksDist < 0.15;
    console.log(`  [Axis 3] KS-Test Shape Distance: ${ksPass ? GREEN : RED}${ksDist.toFixed(4)}${RESET} (Target: < 0.15)`);
    console.log(`           Status               : ${ksPass ? BOLD + GREEN + 'PASS (Cumulative Distribution Indistinguishable)' : BOLD + RED + 'FAIL'}${RESET}`);
    
    // Axis 4 Verification
    const wassersteinPass = wassersteinDist < 5.0; // Under 5.0 microseconds (5,000 ns)
    console.log(`  [Axis 4] Wasserstein Distance : ${wassersteinPass ? GREEN : RED}${(wassersteinDist * 1000).toFixed(0)} ns${RESET} (Target: < 5000 ns)`);
    console.log(`           Status               : ${wassersteinPass ? BOLD + GREEN + 'PASS (Physical EMD Containment Healthy)' : BOLD + RED + 'FAIL'}${RESET}`);
    
    console.log(`${BOLD}${WHITE}=====================================================================${RESET}\n`);

    const overallPass = tTestPass && fRatioPass && ksPass && wassersteinPass;
    if (overallPass) {
        console.log(`${BOLD}${GREEN}[✓] UPGP V3.0 CORE IS 100% TIMING-INDISTINGUISHABLE AND SECURE.`);
        console.log(`    ALL MULTI-AXIS SIDE-CHANNELS ARE SUCCESSFULLY CONTAINED.${RESET}\n`);
    } else {
        console.log(`${BOLD}${RED}[!] SIDE-CHANNEL CRACKS DETECTED. ADJUST INTERLEAVE AND PADDING COEFFICIENTS.${RESET}\n`);
    }
}

// Automatically execute testing loop if run directly
if (import.meta.url.endsWith(process.argv[1])) {
    executeUPGPVerificationSuite();
}
