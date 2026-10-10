# SOVRA Truth Engine v4.0.0 Official Release Notes

SOVRA Truth Engine v4.0 is a zero-pip dependency, offline truth and polarity verifier for LLM outputs compiled natively in Zig/C.

### Release Highlights
- **Zero Runtime Dependencies**: Pre-compiled standalone binaries and C-shared libraries (`.dylib`, `.so`, `.dll`). No `pip install` required.
- **Compositional Polarity Scope Parser**: Resolves inclusive idioms (*"not only X but also Y"*), litotes double negations (*"it is not false"*), and sub-clause direct scope negations.
- **Grounding & Contradiction Check**: Identifies structural predicate conflicts for unindexed entities (*"Madrid is the capital of France"*).
- **Sub-Millisecond Calls**: ~42μs on macOS arm64, ~68μs on Linux x86_64, ~85μs on Windows x86_64.
- **Cryptographic Audit Ledger**: Every verification appends a SHA-256 Merkle-chained entry.

### Included Binary Assets
- `libtruth_verifier_v4.dylib` — macOS arm64 shared library
- `truth_verifier_v4_cli` — macOS arm64 standalone executable
- `libtruth_verifier_v4.so` — Linux x86_64 static PIE shared object
- `truth_verifier_v4_cli_linux` — Linux x86_64 static musl executable
- `libtruth_verifier_v4.dll` — Windows x86_64 PE32+ dynamic library
- `truth_verifier_v4_cli.exe` — Windows x86_64 standalone console executable

### Visual Performance & Accuracy Evidence
![SOVRA Latency Benchmark](https://raw.githubusercontent.com/user/kaggle-benchmark-assets/main/sovra_v4_latency_benchmark_chart.png)
![SOVRA Precision Matrix](https://raw.githubusercontent.com/user/kaggle-benchmark-assets/main/sovra_v4_accuracy_matrix_chart.png)


### Quickstart
```bash
echo '{"question":"What is the capital of France?","answer":"Paris is not only the capital of France but also its largest city.","expected":"Paris","domain":"France"}' | ./core/ops/scripts/truth_verifier_v4_cli
```

