# 🛡️ UPGP v3.0: MICROARCHITECTURAL SAFETY PROTOCOLS
## Diagnostic Containment, Sandbox Rules, and Anti-Leak Guidelines
**Author:** Xoras Systems Security Sentinel  
**Classification:** Xoras Proprietary // Testing and Verification Only  

---

## Ⅰ. The Sandbox Isolation Protocol

The **Universal Proving Ground Protocol (UPGP v3.0)** operates on a strict, double-isolated paradigm. To ensure testing does not compromise host security or leak timing signatures:

1. **Virtual Network Air-Gap:**
   The UPGP execution core must never be run on an instance with active outbound internet sockets. All dynamic web-scouring loops must be simulated via mock loopback adapters or pre-cached visual dictionaries inside `/static`.
2. **Process Group Pinning:**
   To neutralize Axis 5 (Concurrency-Based Interleaving) noisy-neighbor attacks, developers must run the testing suite using CPU-pinning utilities (such as `taskset` on Linux or `taskpolicy` on macOS) to isolate the VM's V8 event loop onto a single core:
   ```bash
   # Pin process to CPU Core 2 to isolate timing evaluations
   taskset -c 2 node UPGPProvingGround.test.js
   ```
3. **No Code Grabs / Read-Only Policy:**
   This testing harness is designed exclusively to verify side-channel mitigations. Copying algorithms, extracting key derivation libraries, or merging enclaves into production codebases outside Xoras-authorized deployment plans is strictly prohibited.

---

## Ⅱ. Side-Channel Evaluation Standards

When running verification tests, the testing environment must enforce **Statistical Isolation**:

* **Quiet-State Host Verification:**
  Before running Welch's t-test or Wasserstein distance evaluations, the testing framework checks active CPU usage. If background CPU usage exceeds $5\%$, the tests will halt with `WARNING_ENVIRONMENT_NOISY`, preventing external background spikes from corrupting the empirical CDF timing curve.
* **Warm-up Cycles Enforced:**
  Never measure the latency of cold execution loops. Always execute exactly $200$ pre-warming prefrontal runs to ensure the V8 JIT compiler has optimized the bytecode path.

---

## Ⅲ. Unified Cross-Platform Keys Safety

If a developer runs the proving ground on a host with restricted system privileges:
* Do not attempt to execute `sudo` or modify permissions to query system UUIDs.
* The framework automatically initiates the **Cryptographic Local Fallback (CLF)**, creating an encrypted local entropy registry file (`.upgp-seal`) locked via a PBKDF2 expanded passphrase.
* This ensures that absolute timing security is maintained even on serverless, standard user, or stateless container infrastructures.
