---
name: Flutter逆向
description: Flutter 应用逆向专项。当分析 Flutter 引擎打包的安卓 App（识别标志：libflutter.so、libapp.so、assets/flutter_assets/、kernel_blob.bin）需要分析 Dart 逻辑、抓包（Flutter 不走系统代理）时使用。
---

# Flutter 应用逆向

## 一、识别 Flutter App
- `lib/*/libflutter.so`（引擎本体）
- `lib/*/libapp.so`（**你的 Dart 业务代码编译产物，AOT 快照**）
- `assets/flutter_assets/`

## 二、Flutter 逆向的难点
- Dart AOT 编译成 native，**没有现成反编译器**能还原成 Dart 源码
- Flutter **不使用系统 HTTP 代理**，普通抓包（设 WiFi 代理）抓不到

## 三、抓包（最常见需求）
Flutter 走自己的 BoringSSL，忽略系统证书和代理。三种方法：

1. **reFlutter（推荐）**：重打包，patch libflutter.so 让它走代理 + 忽略证书
   - 用 reFlutter 处理 APK → 生成新 APK → 装上后配合 Burp 抓包
2. **Frida hook ssl_verify**：hook libflutter.so 里的 `ssl_client_socket` / `SSL_CTX_set_custom_verify`（配合 frida-scripts 技能）
3. **iptables/透明代理**：把设备流量强制转发到抓包机（不依赖 App 的代理设置）

### reFlutter 抓包流程
```
reFlutter your_app.apk        # 选 Frida 模式 or 抓包模式
# 输出 release.RE.apk
# 重签名后安装，设代理指向 Burp（默认 8083）
```

## 四、分析 Dart 逻辑
1. 把 `libapp.so` 拖进 IDA/Ghidra
2. Dart 快照有自己的结构，用 **Doldrums** 或 **flutter-header** 工具解析 snapshot，恢复部分类名/函数名
3. 新版 Flutter 快照格式变化快，工具可能滞后 → 退回到纯汇编分析关键函数

## 五、改逻辑
- 定位到 libapp.so 里的关键函数后，patch 汇编（配合 `reverse-patch-techniques` 技能）
- 或 Frida 动态 hook libapp.so 的函数偏移

## 六、抓到包后
- Flutter App 的接口通常是标准 REST/JSON 或 gRPC
- 若接口有签名/加密 → 配合 `protocol-crypto-analysis` 技能分析签名算法

## 边界
用于自有 App、已授权渗透测试、接口联调、学习 Flutter 原理。不协助未授权攻击、侵权或牟利。
