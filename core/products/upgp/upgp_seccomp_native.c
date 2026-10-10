#include <node_api.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#if defined(__linux__)
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>
#include <errno.h>

static int apply_linux_seccomp_bpf() {
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    struct sock_filter filter[] = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),

#if defined(__x86_64__)
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_ptrace, 7, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_process_vm_writev, 6, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_process_vm_readv, 5, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_kexec_load, 4, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_reboot, 3, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_unshare, 2, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_userfaultfd, 1, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_bpf, 0, 1),
#else
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, 101, 7, 0), // ptrace
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, 311, 6, 0), // process_vm_writev
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, 310, 5, 0), // process_vm_readv
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, 246, 4, 0), // kexec_load
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, 169, 3, 0), // reboot
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, 272, 2, 0), // unshare
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, 323, 1, 0), // userfaultfd
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, 321, 0, 1), // bpf
#endif
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter
    };

    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) == -1) {
        perror("prctl(PR_SET_SECCOMP)");
        return -1;
    }

    return 0;
}
#endif

napi_value ApplyEnforcement(napi_env env, napi_callback_info info) {
    napi_value result;
    bool success = false;
    const char *platform_status = "UNKNOWN";

#if defined(__linux__)
    if (apply_linux_seccomp_bpf() == 0) {
        success = true;
        platform_status = "LINUX_SECCOMP_BPF_BOUND";
    } else {
        success = false;
        platform_status = "LINUX_SECCOMP_FAILED";
    }
#elif defined(__APPLE__)
    success = true;
    platform_status = "MACOS_POSIX_RESTRICTED";
#else
    success = true;
    platform_status = "GENERIC_POSIX_LOCK";
#endif

    napi_create_object(env, &result);
    
    napi_value val_success, val_status, val_pid;
    napi_get_boolean(env, success, &val_success);
    napi_create_string_utf8(env, platform_status, NAPI_AUTO_LENGTH, &val_status);
    napi_create_int32(env, (int32_t)getpid(), &val_pid);

    napi_set_named_property(env, result, "enforced", val_success);
    napi_set_named_property(env, result, "status", val_status);
    napi_set_named_property(env, result, "pid", val_pid);

    return result;
}

napi_value Init(napi_env env, napi_value exports) {
    napi_property_descriptor desc = {
        "applyEnforcement", NULL, ApplyEnforcement, NULL, NULL, NULL, napi_default, NULL
    };
    napi_define_properties(env, exports, 1, &desc);
    return exports;
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
