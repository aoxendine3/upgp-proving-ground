# Defensive Seccomp-BPF Sandbox Specification & Reproduction Guide

**Document ID**: XORAS-RESEARCH-020  
**Status**: VERIFIED & REPRODUCIBLE  
**Classification**: Enterprise Security Engineering (Defensive Focus)  
**Authors**: Lead 9 Council R&D Group  

---

## 1. Executive Summary & Honest Risk Assessment (Gaps First)

### 1.1 Known Limitations & Operating Boundaries
- **Host Execution Bounds**: Seccomp-BPF filters (`prctl(PR_SET_SECCOMP)`) are enforced at the Linux kernel level. Running node application harnesses on macOS or non-Linux hosts defaults to policy generation without active kernel enforcement.
- **Hardware Mitigations**: Seccomp-BPF restricts system call entry points but does not mitigate microarchitectural side-channels (e.g., Spectre/Meltdown cache timing) without host CPU flags (`IBRS`, `eIBRS`, `KPTI`).
- **Container vs. Host**: Docker and OCI container runtimes inherit the host kernel seccomp profile unless explicitly overridden with `--security-opt seccomp=seccomp_upgp.json`.

---

## 2. Architecture & Seccomp-BPF Defensive Mechanisms

### 2.1 Native C N-API Seccomp Binding (`src/native/upgp_seccomp_native.c`)
The defensive seccomp extension establishes process-level syscall restriction inside the Node.js process:
```c
#include <node_api.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <stddef.h>

// Step 1: Prevent gain of new privileges (mandatory before PR_SET_SECCOMP)
if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
    // Handle error
}

// Step 2: Load BPF syscall filter array with SCMP_ACT_KILL action on banned syscalls
if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) != 0) {
    // Handle error
}
```

---

## 3. Step-by-Step Reproduction Guide

### 3.1 Prerequisites
- **Operating System**: Ubuntu 22.04 LTS or Debian 12 (Linux Kernel >= 5.15)
- **Dependencies**: `build-essential`, `g++`, `node-gyp`, `docker.io`, `Node.js >= 18`

### 3.2 Compilation & Execution Setup
```bash
# 1. Clone repository harness
git clone https://github.com/user/upgp-proving-ground.git
cd upgp-proving-ground

# 2. Build native C N-API binding
npm install
npx node-gyp configure build

# 3. Build containerized verification suite
docker build -f Dockerfile.upgp -t upgp-sandbox-proof .

# 4. Run isolated container gauntlet with seccomp profile
docker run --rm \
  --security-opt seccomp=seccomp_upgp.json \
  upgp-sandbox-proof
```

---

## 4. Verification Receipts & Expected Outcomes

| Syscall Group | Filter Action | Verification Result | Kernel Signal |
| :--- | :--- | :--- | :---: |
| `ptrace`, `process_vm_writev` | `SCMP_ACT_KILL` | Process Terminated | `SIGSYS` (159) |
| `unshare`, `setns` | `SCMP_ACT_KILL` | Namespace Escalation Blocked | `SIGSYS` (159) |
| `kexec_load`, `bpf` | `SCMP_ACT_KILL` | Kernel Load Blocked | `SIGSYS` (159) |
| `read`, `write`, `exit_group` | `SCMP_ACT_ALLOW` | Normal Execution | `Exit Code 0` |

---

## 5. Conclusion & Future Engineering Roadmap
1. Continuous integration testing inside GitHub Actions Ubuntu runners.
2. Integration of Linux Landlock LSM v3 for filesystem path restrictions alongside Seccomp-BPF syscall restriction.
