# UPGP v3.0: Microarchitectural Side-Channel Verification Suite
Defensive validation and benchmark tools for timing-indistinguishable sandboxing.

---

## Technical Overview

This repository contains the developer verification suite for the **Universal Proving Ground Protocol (UPGP v3.0)**. It is designed to evaluate, benchmark, and verify software-level mitigations against microarchitectural timing and concurrency side-channel leaks.

UPGP v3.0 implements a multi-layer timing shield to protect isolated execution environments from leakage:
* **Ingress Normalization:** Canonical processing of obfuscated unicode parameters to enforce constant-time rules evaluations.
* **Platform-Agnostic Key Derivation:** Deterministic Swarm keys derived via PBKDF2 and HKDF-SHA256 from host hardware identifiers, with a secure local encrypted file fallback (`.upgp-seal`).
* **Decoy Signatures Swarm:** Balanced signature cycles that compute identical BFT cryptographic loads regardless of active consensus outcomes.
* **Microtask Interleave Masking (MIM):** Enforcing single-tick execution boundaries inside the event loop to block concurrent thread timing analysis.

---

## Statistical Verification Benchmarks

Verification is validated against four statistical timing gates:

| Metric | Vector | Target |
| :--- | :--- | :--- |
| **Welch's T-Test** | First-Order Mean Timing Differences | $|t| < 1.96$ |
| **F-Test Ratio** | Second-Order Variance Spread | $Ratio < 1.25$ (or variance $< 400.0\mu\text{s}^2$) |
| **KS-Test Distance ($D$)** | Cumulative Distribution Curve Shape | $D < 0.15$ |
| **Wasserstein ($W_1$)** | Physical Earth Mover's Distance | $W_1 < 5,000\text{ ns}$ |

---

## Repository Structure

```
upgp-proving-ground/
├── LICENSE                    # Proprietary Testing & Verification License
├── SAFETY_PROTOCOLS.md        # Technical isolation guidelines & core-pinning
├── package.json               # Native Node.js ESM TypeScript test configuration
├── README.md                  # System overview & benchmark setup
├── src/
│   └── core/
│       └── UPGPVM.ts          # Platform-agnostic virtual machine core
└── tests/
    └── UPGPProvingGround.test.ts # Timing statistical test runner
```

---

## Getting Started

### Prerequisites
* **Node.js v22+** (Native ESM and TypeScript strip mode)

### Running Benchmarks
Navigate to the repository folder and execute the test runner:
```bash
npm test
```

---

## License
Licensed under the Xoras Systems Proprietary Testing and Verification License. Strictly for local testing and diagnostic purposes. Pull requests or production extractions are restricted.
