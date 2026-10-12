---
name: SVC指令追踪
description: SVC 系统调用指令追踪与分析（供安全研究/自有应用）。当 App 用内联汇编直接发 svc 指令绕过 libc 标准库函数（导致 Frida hook libc 失效）时，用于识别 svc 指令、解析 syscall 编号、还原它在做什么系统调用。涵盖 arm64 svc 机制、syscall 号对照、追踪手段。
---

# SVC 指令追踪与分析

有些加固/反调试 App 不调用 libc 的 `open/read/ioctl`，而是**内联汇编直接发 `svc #0`** 触发系统调用，绕过你在 libc 层下的 hook。这个技能教你识别和追踪它们。

## 一、原理：arm64 的 syscall 怎么发
- arm64 上系统调用通过 `svc #0` 指令触发。
- **syscall 编号放在 `x8` 寄存器**，参数依次放 `x0`~`x5`，返回值在 `x0`。
- 例：`openat` 的号是 56，App 会先 `mov x8, #56` 再 `svc #0`。

## 二、为什么普通 hook 失效
- Frida `Interceptor.attach` 挂的是**函数地址**（如 libc 的 `openat`）。
- App 直接 `svc` 就没经过 libc 函数，hook 点根本不触发 → 你以为没调用，其实偷偷调了。

## 三、怎么找到 svc 指令
1. **静态**：在 IDA/反汇编里搜 `SVC` 指令（`analyze_functions` + 反汇编后 grep "svc"）。
   - 看它前面给 `x8` 赋的值 = syscall 号，对照下表知道在干嘛。
2. **动态**：
   - Frida `Stalker` 追踪指令流，过滤 `svc` 类型指令，打印当时的 x8/x0-x5。
   - 或用 `ptrace`（PTRACE_SYSCALL）单步到每个 syscall，读寄存器。
   - 内核层：kprobe 挂 syscall 入口（见 kernel-system-hook）。

## 四、常用 arm64 syscall 号对照（检测常用的）
| 号(x8) | syscall | App 拿来干嘛 |
|---|---|---|
| 56 | openat | 读 `/proc/self/maps`、`/system/bin/su`、`/proc/net/tcp` |
| 63 | read | 读上面打开的文件内容做检测 |
| 62 | lseek | — |
| 57 | close | — |
| 79 | newfstatat | stat 检测文件是否存在（su/frida） |
| 260 | wait4 | 反调试（检测被 trace） |
| 117 | ptrace | 自己 ptrace 自己防调试 |
| 129 | kill(0) | 检测进程是否存在 |

## 五、拿到 svc 调用后怎么应对
- 知道它在读 `/proc/self/maps` 查 frida → 在**内核层或 svc 返回处**改返回内容（隐藏 frida 段）。
- 知道它 `ptrace(PTRACE_TRACEME)` 防调试 → hook 让它返回成功但不实际生效，或抢先占坑。
- 配合 kernel-system-hook 在 syscall 层动手。

## 边界
用于自有 App / 授权样本的反调试机制分析、加固研究、学习 syscall 层原理。不协助攻击他人系统。
