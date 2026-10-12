---
name: 安卓脱壳
description: 安卓加固(壳)识别与脱壳手法速查（供安全研究/自有应用分析）。当遇到 APK 被加固(360加固/爱加密/梆梆/腾讯乐固/娜迦/顶像/几维等)、jadx 打开看不到真实代码、dex 是壳的 stub、需要脱壳(dump 真实 dex)时使用。
---

# 安卓加固识别与脱壳速查

面向对**自有或已授权**应用的分析。加固(壳)会把真实 dex 加密/隐藏，jadx 打开只看到壳的加载器 stub。脱壳 = 在运行时把内存中解密后的真实 dex dump 出来。

## 一、先识别是什么壳

看 APK 的 `lib/` 目录和入口 Application 特征：

| 壳厂商 | 特征 so / 包名 |
|---|---|
| 360加固 | `libjiagu.so` / `libjiagu_art.so`，com.stub.StubApp |
| 爱加密 | `libexec.so` / `libexecmain.so`，s.h.e.l.l |
| 梆梆 | `libDexHelper.so` / `libSecShell.so` |
| 腾讯乐固 | `libshellx.so` / `libtxx.so`，com.tencent.StubShell |
| 娜迦(Nagain) | `libddog.so` / `libchaosvmp.so`（VMP，难） |
| 顶像 | `libx3g.so` |
| 几维 | `libkwscmm.so` / `libkwsgmain.so` |
| 百度 | `libbaiduprotect.so` |

识别后，不同壳脱法不同，但**通用脱壳方案能覆盖大部分一代壳**。

## 二、脱壳方案（按难度）

### 方案 A：通用脱壳机（最省事，一代壳首选）
用现成的脱壳工具/框架，root 或免 root：
- **FRIDA-DEXDump**：frida 脚本，扫描内存里的 dex magic，自动 dump。通杀大部分一代壳。
  `frida -U -f 包名 -l frida-dexdump.js`，或用配套 python 工具。
- **反射大师 / MT 的脱壳插件**：手机端一键脱壳（论坛常见），对常见壳有效。
- **BlackDex / FullDump**：免 root 脱壳 App，直接跑目标 App 后 dump。
- **Youpk / FART / Zhenghun**：定制 ROM/Xposed 级主动调用脱壳，对抗强壳，但门槛高。

### 方案 B：内存 dump dex（配合本项目的 rev-dex-dumper 技能）
运行时在 dex 被解密加载后，从内存 dump：
1. hook `DexFile` / `openDexFile` / `defineClass` 等加载点
2. 或直接扫内存 `dex\n035` magic
3. dump 出来的 dex 用 `rev-dex-dumper` 技能的方法修复(补 header/magic/校验)

### 方案 C：主动调用脱壳（对抗 dex 抽取型/函数抽取壳）
二代壳(如新版乐固/梆梆)会把方法体抽走、运行时才回填。需**主动调用每个方法**触发回填，再 dump。用 FART/Youpk 这类主动调用框架。

## 三、脱壳后处理
1. dump 出的可能是多个 dex（classesN.dex）
2. 部分 dex 头/校验被破坏 → 用 `rev-dex-dumper` 技能修复，或用工具重建 header
3. 修复后用 jadx / apktool 正常反编译分析
4. 若只是要改逻辑：脱壳分析定位 → 在原 APK 的对应 smali/so 上 patch（很多壳允许改 smali 后重打包仍能跑）

## 四、工作流
1. 看 `lib/` 的 so → 识别壳厂商
2. 一代壳 → FRIDA-DEXDump / BlackDex 通用脱
3. 二代壳(方法抽取) → FART/Youpk 主动调用脱
4. dump → 修复 dex → jadx 分析
5. VMP 壳(娜迦 chaosvmp 等) → 极难，通常只能动态调试分析关键逻辑，不强求完整脱

## 边界
用于自有/授权样本的安全研究、恶意软件分析、学习。不协助盗版牟利或未授权侵权。
