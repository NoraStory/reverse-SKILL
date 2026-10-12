---
name: 混合H5逆向
description: 混合应用(H5/WebView/Cordova/uni-app/React Native)逆向专项（供安全研究/自有应用分析）。当 App 主要逻辑是网页(WebView 加载 H5)、需要分析 JS 代码、调试 WebView、hook JSBridge、还原 uni-app/RN 的 JS bundle 时使用。
---

# 混合应用（H5 / WebView / RN / uni-app）逆向

## 一、识别混合应用类型
| 特征文件 | 类型 |
|---|---|
| assets/www/ + cordova.js | **Cordova / PhoneGap** |
| assets/apps/__UNI__xxx/ + app-service.js | **uni-app** |
| assets/index.android.bundle | **React Native** |
| assets/*.js + WebView 大量使用 | 普通 H5 壳 |
| lib/*/libweexcore.so | Weex |

## 二、找到 H5/JS 代码
1. 解包 APK，看 `assets/` 下的 www/、dist/、*.js
2. **JS 通常被压缩/混淆**（webpack 打包、uglify）→ 用 js-beautify 格式化
3. uni-app：核心在 `app-service.js`（整个应用逻辑），格式化后搜关键词

## 三、调试 WebView（动态，最有效）
1. 前提：App 的 WebView 开了调试（`setWebContentsDebuggingEnabled(true)`）。没开可以 hook 强制打开：
   ```javascript
   // Frida 强制打开 WebView 调试
   Java.perform(function() {
     var WV = Java.use("android.webkit.WebView");
     WV.setWebContentsDebuggingEnabled(true);
   });
   ```
2. 电脑 Chrome 打开 `chrome://inspect` → 连上设备 → 直接看 DOM、断点调 JS、看网络请求
3. 这是分析 H5 逻辑最爽的方式，等于给你一个完整 DevTools

## 四、hook JSBridge（JS 和原生的桥）
- 混合应用靠 JSBridge 通信（`addJavascriptInterface` 或 `shouldOverrideUrlLoading` 拦 scheme）
- hook `addJavascriptInterface` 看暴露了哪些原生方法给 JS
- hook `evaluateJavascript` / `loadUrl` 看原生往 JS 注入什么

## 五、React Native 专项
- `index.android.bundle` 是打包的 JS（可能是 Hermes 字节码）
- 纯 JS bundle：格式化后直接读
- **Hermes 字节码**（文件头 `\x89HBC`）：用 `hermes-dec` / `hbctool` 反编译

## 六、抓包
- WebView 走系统代理 → 普通设代理 + 证书就能抓（比 Flutter 简单）
- 若有 SSL Pinning → 配合 frida-scripts 技能过掉

## 七、改逻辑
- 改 assets 里的 JS 文件 → 重打包（配合 apktool/MT）→ 重签名（配合 signature-bypass 技能过校验）
- 或运行时 hook 注入 JS

## 边界
用于自有 App、已授权测试、H5 接口联调、学习混合开发。不协助侵权、破解、未授权攻击。
