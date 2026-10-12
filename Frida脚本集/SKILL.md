---
name: Frida脚本集
description: Frida 动态插桩常用脚本速查（供安全研究/自有应用分析）。当需要用 frida hook 安卓应用、绕过 SSL Pinning（证书校验）、绕过 root/模拟器/调试检测、hook Java/native 函数改返回值、dump 内存/参数、跟踪加密函数调用时使用。
---

# Frida 动态插桩脚本速查

面向对**自有或已授权**应用的动态分析、调试与安全研究。frida 通过运行时插桩，在不改包的情况下 hook 函数、改行为、dump 数据，非常适合先用 frida 验证思路，再落地成永久 patch。

## 前置
- 设备需能跑 frida-server（root 设备直接跑；或用 frida-gadget 注入到重打包后的 APK）。
- 电脑端：`frida -U -f 包名 -l 脚本.js`（spawn 模式）或 `frida -U 包名 -l 脚本.js`（attach）。
- 无 root 时可用 objection / frida-gadget 方案。

## 一、Hook Java 方法

### 改方法返回值（最常用：VIP/登录/校验返回 true）
```javascript
Java.perform(function () {
  var Target = Java.use('com.example.VipManager');
  // 无重载
  Target.isVip.implementation = function () {
    console.log('[+] isVip called -> forced true');
    return true;
  };
  // 有重载时用 overload 指定参数类型
  Target.check.overload('java.lang.String').implementation = function (s) {
    console.log('[+] check(' + s + ') -> true');
    return true;
  };
});
```

### 打印方法参数和调用栈
```javascript
Java.perform(function () {
  var C = Java.use('com.example.Crypto');
  C.encrypt.implementation = function (data) {
    console.log('[encrypt] input=' + data);
    var ret = this.encrypt(data);
    console.log('[encrypt] output=' + ret);
    // 调用栈
    console.log(Java.use('android.util.Log').getStackTraceString(
      Java.use('java.lang.Exception').$new()));
    return ret;
  };
});
```

## 二、绕过 SSL Pinning（抓包必备）
```javascript
// 通杀思路：hook 常见校验点。实战优先用社区维护的通杀脚本（如 frida 官方 codeshare 的
// "universal android ssl pinning bypass"），这里给核心思路：
Java.perform(function () {
  // 1) 干掉 TrustManager 校验
  var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
  var SSLContext = Java.use('javax.net.ssl.SSLContext');
  var TrustManager = Java.registerClass({
    name: 'com.bypass.TrustAll',
    implements: [X509TrustManager],
    methods: {
      checkClientTrusted: function () {},
      checkServerTrusted: function () {},
      getAcceptedIssuers: function () { return []; }
    }
  });
  var init = SSLContext.init.overload(
    '[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;',
    'java.security.SecureRandom');
  init.implementation = function (km, tm, sr) {
    init.call(this, km, [TrustManager.$new()], sr);
  };
  // 2) OkHttp CertificatePinner.check 直接放行
  try {
    var CP = Java.use('okhttp3.CertificatePinner');
    CP.check.overload('java.lang.String', 'java.util.List').implementation = function () {};
  } catch (e) {}
});
```
> 实战建议：直接用社区通杀脚本（覆盖 OkHttp/Conscrypt/TrustKit/Flutter 等），比手写全。

## 三、绕过 Root / 模拟器 / 调试检测
```javascript
Java.perform(function () {
  // 常见：hook 检测方法返回 false
  var names = ['isRooted', 'checkRoot', 'isEmulator', 'isDebuggerConnected'];
  // 具体类名要先逆向定位，这里示意
  var Detector = Java.use('com.example.security.Detector');
  names.forEach(function (m) {
    if (Detector[m]) {
      Detector[m].implementation = function () { return false; };
    }
  });
  // 干掉 Debug.isDebuggerConnected
  var Debug = Java.use('android.os.Debug');
  Debug.isDebuggerConnected.implementation = function () { return false; };
});
```

## 四、Hook native 函数（.so 里的逻辑）
```javascript
// hook 导出函数
var addr = Module.findExportByName('libnative.so', 'check_license');
Interceptor.attach(addr, {
  onEnter: function (args) { this.a0 = args[0]; },
  onLeave: function (retval) {
    console.log('[check_license] ret=' + retval);
    retval.replace(ptr(1)); // 强制返回 1
  }
});
// 未导出函数用 模块基址 + 偏移
var base = Module.findBaseAddress('libnative.so');
Interceptor.attach(base.add(0x1234), { /* ... */ });
```

## 五、常见工作流
1. `frida-trace -U -j 'com.example.*!*check*'` 快速定位可疑方法
2. hook 打印参数/返回值/调用栈，看清逻辑
3. 改返回值验证效果（够用就 frida 常驻；要永久就落地成 so/smali patch）
4. 抓包场景：SSL Pinning bypass 脚本 + 系统代理/证书

## 与永久 patch 的关系
frida 是**运行时**改，重启失效、需 frida 环境。验证思路正确后，用 `reverse-patch-techniques` 的手法把改动落地到 so（SOMCP）或 smali（MT），做成永久 patch。

## 边界
用于自有/授权应用的安全研究、调试、学习。不协助破解他人付费软件牟利或未授权侵权。
