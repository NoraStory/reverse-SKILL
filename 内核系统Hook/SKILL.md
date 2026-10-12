---
name: 内核系统Hook
description: 内核级 / 系统服务级 Hook 方法论（供安全研究/自有设备）。当标准 Java/Native Hook 被 App 检测或绕不过时，需要在更底层（system_server 系统服务、syscall/内核）拦截环境探测（root 检测、调试检测、frida 检测）。涵盖 KernelSU/APatch 内核模块、系统服务 Hook、syscall 拦截思路。
---

# 内核级 / 系统服务级 Hook

当 App 的环境探测（root/调试/frida/模拟器检测）在应用层拦不住时，往下沉到系统服务层或内核层拦截。

## 一、先判断需要多底层
| 层级 | 手段 | 适合 |
|---|---|---|
| 应用层 | Xposed/LSPosed hook Java API | 普通 root 检测（Build 属性、su 路径） |
| Native 层 | Frida/inline hook libc（`fopen`/`access`/`stat`） | 检测走 native 直接读文件 |
| **系统服务层** | hook system_server 里的 PackageManager/ActivityManager | App 查其他包、查进程列表来反检测 |
| **内核层** | KernelSU/APatch 内核模块、syscall hook | App 直接走 syscall 绕过 libc，或检测非常严 |

## 二、系统服务层 Hook（system_server）
- LSPosed 可 hook system_server 进程（作用域勾选"系统框架"）。
- 常 hook 点：
  - `PackageManagerService.getInstalledPackages/getPackageInfo` —— 隐藏 Magisk/Xposed 管理器等敏感包
  - `ActivityManagerService.getRunningAppProcesses` —— 隐藏 frida-server/可疑进程
  - `Settings.Global/Secure.getInt` —— 伪造 adb_enabled、development_settings_enabled
- 注意：改系统服务影响全局，务必精确匹配调用方（只对目标 App 生效），否则可能引起系统不稳定。

## 三、syscall / 内核层拦截
- **场景**：App 用内联汇编直接发 `svc` 系统调用（绕过 libc，Frida hook libc 就失效，见 svc-instruction-trace 技能）。
- **KernelSU / APatch**：提供内核态能力，可用 kprobe/kretprobe 挂钩 syscall 入口，或用其提供的 `susfs` 之类方案隐藏 root 痕迹。
- **思路**：
  1. 确定 App 检测走哪个 syscall（openat 读 `/proc/self/maps`、`/proc/net/tcp` 查 frida 端口等）
  2. 内核模块里 hook 对应 syscall，对目标进程返回伪造结果
  3. 或用现成的隐藏框架（Shamiko/susfs/Zygisk 模块）先试，能解决就不用自己写内核模块

## 四、实操建议
- 优先用**现成隐藏方案**（Shamiko + LSPosed 排除列表、Zygisk-based hide），能过大多数检测，成本最低。
- 现成的过不了再考虑自写内核模块（需要 KernelSU/APatch 环境 + 内核开发能力）。
- 每加一层 hook 都要验证：目标 App 是否还检测得到、系统是否稳定。

## 边界
用于自有设备的安全研究、反检测机制学习、隐私保护、恶意软件的环境对抗分析。不协助攻击他人设备、绕过他人系统的安全控制去实施侵害。
