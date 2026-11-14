# Quarantine receipt — tests/UPGPProvingGround.test.ts (2026-11-14)

- Diagnosis: printed hard-coded "diagnostics" (mean 6012.45us, Welch t=0.4012, F=1.152, KS=0.0700, Wasserstein 25ns) as measurements it never took; printed [PASS] for 15 escape vectors without executing them; claimed a generated Seccomp-BPF profile; exited 0 regardless.
- Reality check (run 2026-11-14 on the development host): the actual harness in tests/test_side_channel_verification.cjs FAILS Axis 2 (F-ratio ~38–53) and Axis 4 (Wasserstein ~14–29µs vs 5µs target) on this host, with Axes 1 and 3 passing. The quarantined file asserted PASS on all four because it asserted nothing.
- Action: moved intact, not deleted. package.json "test" now runs the real harness, which exits non-zero on failure and names the failing axes.

Addendum: `.github/workflows/mars-gatekeeper-maven.yml` (sic) moved into the same quarantine. It was the mirror of the main repo's mock: ran `mvn validate enforcer:enforce` on a repository with no Java and no POM, and "Layer 4 - SMT" was an echo printing 'SMT Verification Passed. Zero hallucinations detected.' without invoking any solver. Replaced by `falsification_gate.yml`, which runs only real, executable checks in this repository.

Addendum 2 (same date): Pages deploy artifact is `docs/`, so the live site is `docs/index.html`. The repo-root `index.html` (older copy) moved to this quarantine to prevent two divergent copies of the public page. Also moved: `docs/assets/xoras_studio_v2_antigravity_edition_1791504152706.jpg` (foreign tool branding in a live asset path; referenced nowhere in the HTML surface as shipped).
