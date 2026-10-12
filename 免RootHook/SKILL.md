---
name: 免Root Hook
description: 免 Root Hook 注入专项（供安全研究/自有应用分析）。当设备没 Root 又想动态 hook、修改应用行为时使用——LSPatch 把 Xposed 模块寄生进目标 APK、SimpleHook/太极免root、Frida Gadget 内嵌。适合无 root 环境的动态分析。
---

# 免 Root Hook 注入

没 Root 也能动态 hook 的几套方案，按场景选。

## 一、方案总览（按易用度）
| 方案 | 原理 | 适合 |
|---|---|---|
| **LSPatch** | 把 Xposed 模块 + LSPosed 框架寄生进目标 APK，重打包 | 已有 Xposed 模块、想免 root 用 |
| **SimpleHook** | 一个 App 里配置 hook 规则（改返回值/参数），底层用免 root 注入 | 简单改返回值/常量，不会写代码 |
| **Frida Gadget** | 把 frida-gadget.so 内嵌进 APK，随 App 启动 | 想用 Frida 脚本但设备没 root |
| **VirtualApp/太极** | 在宿主 App 内加载目标，实现 hook | 部分场景 |

## 二、LSPatch（Xposed 模块免 root 化）
最实用——把你写的 Xposed 模块（配合 xposed-module-builder 技能生成）用 LSPatch 打进目标 APK：
1. 准备：目标 APK + 你的 Xposed 模块 APK
2. 用 LSPatch（manager 模式或 jar 命令行）：`java -jar lspatch.jar 目标.apk -m 模块.apk -l 2`
3. 产出寄生版 APK，装上即生效（模块随目标启动被加载）
4. 注意：本地模式(-l 2 集成模块) vs manager 模式(需装 LSPatch manager App 管理)

## 三、Frida Gadget 内嵌（免 root 用 Frida）
设备没 root 时让 Frida 脚本也能跑：
1. 解包目标 APK，把 `frida-gadget.so`（对应 abi）放进 `lib/arm64-v8a/`
2. 在入口 Activity 的 smali 或 native 库里加载它（`System.loadLibrary("gadget")`），或改 Application 让它最早加载
3. 配置 `libgadget.config.so`（指定脚本路径/监听模式）
4. 重签打包（配合 signature-bypass 过签名校验）
5. 装上后 gadget 会加载你的 JS 脚本（写法同 frida-scripts 技能）

## 四、SimpleHook（零代码改返回值）
适合不写代码只想改个返回值/开关：
1. 装 SimpleHook（免 root 版），选目标 App
2. 搜方法（如 `isVip`），配置 hook 返回固定值
3. 部分场景需把配置转成模块（见下）

### SimpleHook 配置转 Xposed 模块（无 root 用户）
SimpleHook 导出的 hook 配置可以转成独立 hook 模块，配合 LSPatch 免 root 应用——适合把调试好的 hook 固化下来分发/长期用。

## 五、选择建议
- 只改个返回值/常量 → **SimpleHook** 最快
- 有现成 Xposed 模块 → **LSPatch** 寄生
- 要跑复杂 Frida 脚本 → **Frida Gadget** 内嵌
- 复杂动态分析且能 root → 直接 root + LSPosed/Frida server 最强（见 frida-scripts）

## 边界
用于自有 App / 已授权样本的动态分析、调试、学习 hook 原理、无 root 环境研究。不协助未授权攻击、破解付费、侵权。
