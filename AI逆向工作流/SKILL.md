---
name: AI逆向工作流
description: AI 辅助安卓逆向的标准工作流（供安全研究/自有应用分析，尤其适合零基础）。当用户丢来一个 APK 说"帮我分析/看看/改一下"但没说清怎么做时，用这套流程系统地推进：先侦察→再定位→后动手→最后验证，并说明每步该调哪个 MCP 工具/技能。
---

# AI 辅助逆向工作流（零基础也能跟）

当用户给一个模糊任务（"分析这个 App""帮我改改""看看怎么回事"），别乱试，按这套标准流程推进。**每一步先想调哪个工具/技能**。

## 阶段 0 · 明确目标（先问清或先推断）
- 用户到底要什么？分析 / 去广告 / 去校验 / 抓包 / 改数值 / 学习原理？
- 目标是自有 App 还是授权样本？（默认按授权/学习处理）
- 目标不清时，先做"侦察"给出发现，再让用户确认方向。

## 阶段 1 · 侦察（搞清这是个什么 App）
1. **加固识别**：看 lib/ 下的 so、assets、入口 Application 类名 → 用 `packer-identification` 技能判断有没有壳。
   - 有壳 → 先脱壳（`android-unpacking` / `rev-dex-dumper`），否则 jadx 看到的是壳代码。
2. **技术栈识别**：
   - `libil2cpp.so` + global-metadata → Unity（用 `unity-il2cpp-reverse`）
   - `libapp.so` + `libflutter.so` → Flutter（用 `flutter-reverse`）
   - `assets/www` / `app-service.js` / `index.android.bundle` → H5/uni-app/RN（用 `hybrid-h5-reverse`）
   - 否则就是原生 Java/Kotlin → jadx 直接看
3. **用 MT 管理器 MCP**（`mt_apk_open` + `mt_apk_list`）开包、看结构、看权限、看 lib/。

## 阶段 2 · 定位（找到要改/要分析的那段）
- 用 **jadx** 反编译看 Java，搜关键词定位：
  - 会员/VIP：`isVip`/`isMember`/`checkPro`（自有应用调试用）
  - 广告：`loadAd`/`showAd`/`Splash`（用 `ad-removal`）
  - 校验：`verify`/`check`/`sign`/`getPackageInfo`（自有应用/授权测试）
  - 网络：`OkHttp`/`Retrofit`/接口 URL
- native 逻辑（.so）→ 用 **SOMCP**（`so_open` + `analyze_functions` + `analyze_crypto`）或 IDA（`ida-decompile`/`rev-idapython`）。
- 静态看不明白 → **动态**：Frida hook 打印参数/返回/堆栈（`frida-scripts`/`rev-frida`），或 `rev-unicorn-debug` 模拟跑一段。
- 要看网络请求 → **ProxyPin 抓包** + `protocol-crypto-analysis` 分析签名/加密。

## 阶段 3 · 动手（改 / 提取 / 生成）
- 改 Java 层逻辑 → 改 smali（`smali-repack`）+ MT 管理器回编。
- 改 native → SOMCP patch 汇编/字节 + `build_so`。
- 动态改（不改文件）→ Frida hook / 免 root（`noroot-hook`）。
- 生成 Xposed 模块 → `xposed-module-builder`。
- 手法不确定 → 查 `reverse-patch-techniques`（去校验/改返回值/绕过总表）。

## 阶段 4 · 验证 & 复盘
- 改完回编、重签（`signature-bypass` 过签名校验）、装真机走一遍。
- 崩了看 logcat / 安全模式崩溃报告，定位是签名校验没过还是改错了。
- 完成后按 systemPrompt 里的"任务复盘"模板输出结构化总结。

## 通用原则
- **一次一步，每步交代用了什么工具、看到了什么、下一步干嘛**，别跳步。
- 优先"改动小、可回滚"的方案（Frida 动态 > smali patch > so patch）。
- 遇到具体场景先 `use_skill` 调对口技能，按标准套路做，别凭记忆瞎试。
- 卡住就换track：静态卡了上动态、Java 层没有就去 native、单点难就抓包看全局。

## 边界
用于自有 App / 已授权样本的分析、学习、研究。不协助盗版牟利、破解他人付费服务、侵权。
