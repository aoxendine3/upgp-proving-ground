# UPGP v3.0: Microarchitectural Safety & Isolation Guidelines
Technical standards for isolated side-channel benchmarking.

---

## 1. Environment Isolation

To ensure baseline statistical timing metrics are not distorted by host scheduler noise:

* **Network Air-Gap:** Testing must be performed strictly offline. Network packet round-trip times and DNS resolution latency introduce high-variance noise that invalidates empirical cumulative distribution curves.
* **CPU Core Affinity (Core-Pinning):** To prevent V8 event loop context switching from leaking path lengths, pin the testing process to a single dedicated core.
  ```bash
  # Example: Pin process to Core 2 on Linux
  taskset -c 2 npm test
  ```
* **System Load Validation:** The test suite verifies that background CPU utilization remains under $5\%$ before running benchmarks to avoid scheduling preemptions.

---

## 2. Key Material Integrity

* **Stateless Containment:** Switches between local hardware identifier lookups and local file fallback (`.upgp-seal`) occur automatically based on platform privileges.
* **Zero Outbound Exposure:** Generated deterministic Swarm keys are retained strictly within private memory enclaves and never exported or printed.
