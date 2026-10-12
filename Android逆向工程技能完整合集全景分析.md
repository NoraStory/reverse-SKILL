# Android 逆向工程技能完整合集 — 全景分析

## 概述

本合集整合三套独立技能包，共 **47 个专业技能**、**231 个文件**，覆盖 Android/iOS 逆向工程的完整技术栈：从 APK 反编译、Java/Smali 静态分析、Frida/Xposed 动态 Hook、Native SO 深度逆向（IDA Pro/OLLVM/VMP）、流量抓包渗透测试、加壳识别与脱壳、Unity/Flutter 逆向、iOS 脱壳，到构建签名发布和 Xposed 模块开发。

---

## 技能全景图

### 一、核心逆向分析链（主线）

| 技能 | 功能 |
|------|------|
| Jadx反编译 | APK → Java 源码（首选） |
| APK解包工具 | APK → Smali 代码 + 资源 |
| Android逆向工程 | 7 阶段编排：依赖→反编译→结构分析→调用链→API提取→动态分析→Native分析 |
| APK线索提取 | SDK 识别、公司关联、版本追踪、批量分析 |

### 二、Java/DEX 层工具

| 技能 | 功能 |
|------|------|
| Smali重打包 | Smali 修改后重新打包签名 |
| DEX内存脱壳 | 从内存 dump 解密后的 DEX（含 panda-dex-dumper） |
| Android脱壳 | 通用 Android 脱壳流程 |
| 加壳识别 | 识别 APK 使用的加壳方案 |

### 三、动态分析链

| 技能 | 功能 |
|------|------|
| Android动态分析 | Frida + Objection + ADB 完整流程 |
| Android模拟器操控 | uiautomator 语义导航、手势自动化 |
| Frida脚本集 | 常用 Frida Hook 脚本库 |
| Frida逆向 | Frida 深度逆向方法论 |
| 安卓渗透测试 | scrcpy + Burp + Frida + jadx 渗透测试 |
| 免RootHook | 无需 Root 的 Hook 方案 |
| 内核系统Hook | Linux 内核层 Hook 技术 |
| SVC指令追踪 | ARM SVC 系统调用追踪 |

### 四、Native 层逆向链

| 技能 | 功能 |
|------|------|
| IDAPro逆向分析 | IDAPython 完整 API + 11 个分析场景 + 5 个内置工具（reai/findcrypt/export_check等） |
| IDA反编译 | IDA MCP 工具集 |
| IDA智能补丁 | 自动化补丁生成 |
| IDAPython逆向 | IDAPython 深度脚本编写 |
| OLLVM反混淆 | 控制流平坦化、字符串加密等反混淆 |
| VMP虚拟化还原 | 虚拟机保护还原 |
| 静态符号执行 | 符号执行分析 |
| Unicorn调试 | Unicorn 模拟执行调试 |
| 结构体逆向 | 逆向还原 C/C++ 结构体 |
| 符号恢复 | 从二进制恢复函数符号 |

### 五、游戏/引擎逆向

| 技能 | 功能 |
|------|------|
| Unity IL2CPP逆向 | IL2CPP 编译的 Unity 游戏逆向 |
| Unity3D脱壳 | Unity3D 资源/代码提取 |
| Flutter逆向 | Flutter/Dart 应用逆向 |

### 六、iOS 逆向

| 技能 | 功能 |
|------|------|
| iOS脱壳 | iOS IPA 脱壳与逆向 |

### 七、破解与绕过

| 技能 | 功能 |
|------|------|
| 签名绕过 | APK 签名校验绕过 |
| 内存完整性绕过 | 内存保护机制绕过 |
| 广告移除 | APK 广告 SDK 移除 |
| 逆向补丁技术 | 二进制补丁生成技术 |
| 协议加密分析 | 通信协议加密逆向 |
| 混合H5逆向 | WebView/H5 混合应用逆向 |

### 八、开发与发布

| 技能 | 功能 |
|------|------|
| Android构建逻辑 | Gradle 构建系统配置 |
| Android发布签名 | APK/AAB 签名与发布 |
| Xposed模块构建 | Xposed 模块开发框架 |
| OpenClawSDK开发 | OpenClaw SDK 开发框架 |
| MT管理器MCP分析器 | MT 管理器 MCP 集成分析 |
| AndroidStudio开发辅助 | IDE 全功能手册（调试/性能分析/重构） |

### 九、AI 与自动化

| 技能 | 功能 |
|------|------|
| AI逆向工作流 | AI 辅助逆向分析编排 |
| 参考 | 逆向参考知识库 |
| 破 | gpt-5.6-sol 破甲安全性评估与回归测试框架（360 条测试集、6 场景 × 3 级别 × 2 语言、pass/fail 判定、门禁策略） |
| 破限 | 大模型破甲提示词完整方法论（v5/v35/v41 三代策略、部署工具、测试框架、跨模型性能矩阵）—— 基于 gpt-5.6-instruct (3.5k+ Stars) |

### 十、附加资源

| 资源 | 说明 |
|------|------|
| `SimpleHook配置生成与修复技能.md` | 自然语言需求转 Hook 配置，覆盖全部 11 种模式 |
| `SimpleHook全功能示例配置.json` | 全模式示例配置，可直接导入使用 |

---

## 技能统计

| 维度 | 数值 |
|------|------|
| 技能总数 | 47 |
| 文件总数 | 231+ |
| 脚本文件 | 60+ |
| 参考文档 | 80+ |
| IDA API 模块 | 14 个分类 |
| 分析场景指南 | 11 个 |
| 破限版本 | v5 / v35 / v41 三代策略 |

---

## 技能来源

| 来源 | 技能数 | 核心贡献 |
|------|--------|---------|
| 第一套（skill工作流.zip） | 16 | 完整 Android 逆向链路、动态分析、渗透测试 |
| 第二套（skills.zip） | 47 | 全量技能集（含第一套全部 + 31 个增量技能） |
| 第三套（skills补充.zip） | 47 | 与第二套内容相同 |
| 本项目新增 | 2 | SimpleHook 配置生成与修复技能、全功能示例配置 |

三套已去重合并，以第二套为基准（最全），保留所有 47 个技能。

---

## 总结

47 个技能覆盖了从 APK 入口到 Native 底层、从静态反编译到动态 Hook、从 Java 层到 Unity/Flutter 引擎、从 Android 到 iOS、从渗透测试到签名发布的完整技术栈，配合 SimpleHook 配置生成能力，可实现分析结果到实战配置的即时转化。