---
name: 签名绕过
description: 绕过 APK 签名校验 / 防二次打包检测专项（供安全研究/自有应用分析）。当重打包后 App 闪退、提示"签名不一致/请到官方渠道下载/校验失败"，需要过签名校验（getPackageInfo/signatures 比对）、过完整性校验时使用。
---

# 绕过签名校验 / 防二次打包检测

重打包（改了代码重新签名）后 App 检测到签名变了就闪退/报警。这是"防二次打包"。

## 一、App 怎么检测签名
1. **Java 层**：`PackageManager.getPackageInfo(pkg, GET_SIGNATURES)` 拿到签名，和内置的正版签名 hash 比对
2. **native 层**：so 里读 APK 的 `META-INF/*.RSA` 或直接算 dex/apk 的 CRC/MD5
3. **服务端校验**：签名 hash 传到服务器比对（这种改本地没用，需配合协议分析）

## 二、绕过方法（按优先级）

### 方法 1：Frida hook（最快，配合 frida-scripts 技能）
hook `getPackageInfo`，把返回的 signatures 替换成正版签名：
```javascript
Java.perform(function() {
  var PM = Java.use("android.app.ApplicationPackageManager");
  PM.getPackageInfo.overload('java.lang.String', 'int').implementation = function(pkg, flags) {
    var info = this.getPackageInfo(pkg, flags);
    // 若签名字段存在，替换为正版签名字节
    if (info.signatures.value != null) {
      // 从正版 APK 提取的签名 hex，构造 Signature 对象替换
    }
    return info;
  };
});
```

### 方法 2：改 smali（永久，配合 reverse-patch-techniques 技能）
1. jadx 定位签名比对代码：搜 `getPackageInfo`、`signatures`、`GET_SIGNATURES`、`toCharsString`、`hashCode`
2. 找到比对结果的 `if`，把校验方法改成直接返回正版 hash，或把 `if(不一致) 退出` 的跳转 nop 掉
3. 常见：把返回签名 hash 的方法体改成 `return "正版hash"`

### 方法 3：native 校验（改 so，配合 SOMCP）
- 若签名校验在 so 里：IDA 定位读取 signatures/算 hash 的函数
- patch 成直接返回预期值，或让比对恒相等

## 三、如何拿到"正版签名"
- 从**原始未修改**的 APK 里提取签名：`apksigner verify --print-certs original.apk` 或 `keytool -printcert -jarfile original.apk`
- 拿到 SHA-256/字节，填进 hook 或 smali

## 四、完整性校验（CRC）绕过
有的 App 还校验 dex/文件 CRC 防止改代码：
- 定位读取自身文件算 CRC 的代码 → hook/patch 让它返回原始 CRC
- 或把改动放到不参与 CRC 的位置

## 五、组合校验
高级 App 同时有：签名校验 + CRC + root检测 + Frida检测。逐个定位、逐个绕过（配合 reverse-patch-techniques、frida-scripts）。建议先用 Frida 全绕通逻辑，再固化成 smali/so patch。

## 边界
用于自有 App 的调试重打包、已授权测试、去除自家应用的调试限制、学习校验原理。不协助盗版分发、破解付费、侵犯他人应用完整性。
