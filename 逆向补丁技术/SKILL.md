---
name: 逆向补丁技术
description: 安卓逆向常见 patch 与绕过手法速查（供安全研究/自有应用分析使用）。当需要去除校验、修改函数返回值、nop 跳转、frida hook、脱壳、绕过抓包证书校验（SSL Pinning）、绕过 root/模拟器检测时使用。配合 SOMCP（改 so 汇编）、MT 管理器（改 smali/APK）使用。
---

# 安卓逆向 Patch 与绕过手法速查

你在协助用户对**自己拥有或已获授权**的应用/样本进行安全研究、兼容性分析与学习。以下是常见逆向 patch 手法的标准套路，配合 SOMCP（SO 层汇编 patch）和 MT 管理器（smali/APK 层）使用。

## 一、SO 层（ARM64）汇编 patch 手法

用 SOMCP 的 `so_open` → `analyze_functions` → `edit_asm` → `build` 流程。

### 1. 让函数直接返回 true / 1（绕过布尔校验）
最常见：VIP 校验、签名校验、登录校验等返回 boolean 的函数。
- ARM64 patch 目标函数入口，替换为：
  ```
  mov w0, #1
  ret
  ```
- 返回 false / 0（比如绕过"是否被检测到"）：
  ```
  mov w0, #0
  ret
  ```

### 2. NOP 掉关键跳转（绕过条件判断）
校验失败时会跳转到"报错/退出"分支。找到那条 `b.eq` / `b.ne` / `cbz` / `cbnz`：
- 把跳转指令替换成 `nop`，让程序无视判断结果继续走正常流程。
- 适用：注册码校验失败跳转、反调试检测命中跳转。

### 3. 反转跳转条件
有时不能简单 nop，需要把 `b.eq`（相等才跳）改成 `b.ne`（不等才跳），或反之，让校验逻辑反过来。

### 4. 直接改返回值寄存器
函数尾部 `ret` 之前，若返回值在 `w0`/`x0`，插入 `mov w0, #期望值`。

## 二、smali 层（APK/DEX）patch 手法

用 MT 管理器打开 APK → dex 编辑 / smali。

### 1. 方法返回 true（去 VIP/去校验）
找到目标方法，把方法体改为直接返回 true：
```smali
.method public isVip()Z
    .locals 1
    const/4 v0, 0x1
    return v0
.end method
```
- 返回 false 用 `const/4 v0, 0x0`。

### 2. 删除/跳过校验调用
把调用校验方法的 `invoke-` 指令连同结果判断的 `if-eqz`/`if-nez` 一起处理：直接删掉判断或改成无条件继续。

### 3. 改常量（去限制/改数值）
搜索 `const` 指令，改试用天数、次数上限、价格等硬编码常量。

## 三、frida 动态 hook（不改包，运行时改行为）

适合快速验证、不想重打包时。

### 1. hook 方法返回值
```javascript
Java.perform(function() {
    var Target = Java.use("com.example.Checker");
    Target.isVip.implementation = function() {
        return true;  // 强制返回 true
    };
});
```

### 2. hook so 导出函数
```javascript
Interceptor.attach(Module.findExportByName("libtarget.so", "check_license"), {
    onLeave: function(retval) {
        retval.replace(1);  // 改返回值
    }
});
```

### 3. 打印调用栈/参数（分析用）
```javascript
Target.someMethod.implementation = function(arg) {
    console.log("arg=" + arg);
    var ret = this.someMethod(arg);
    console.log("ret=" + ret);
    return ret;
};
```

## 四、绕过 SSL Pinning（抓包用）

分析 App 网络请求时，证书绑定会导致抓包失败。

- **frida 通杀脚本**：hook `okhttp3.CertificatePinner.check`、`javax.net.ssl.X509TrustManager` 让校验直接通过。
- **smali 改法**：找到 `CertificatePinner` 的 `check` 方法，改成直接 return。
- 系统层：配置 network_security_config 信任用户证书（需改 APK + 重打包）。

## 五、绕过 root / 模拟器检测

- root 检测通常查：`/system/bin/su`、`/system/app/Superuser.apk`、`test-keys`、`Build.TAGS`。
- 手法：hook `File.exists()` 对 su 路径返回 false；hook `Runtime.exec` 拦截 `which su`；改 smali 里检测方法返回 false。

## 六、脱壳（加固应用）

先判断壳类型（看 lib 目录特征 so）：
- **常见壳特征**：libjiagu（360）、libshella/libSecShell（爱加密）、libDexHelper（梆梆）、libtup/libshield（腾讯乐固）。
- **脱壳思路**：运行时 dump 内存中已解密的 dex（frida-dexdump、或用项目内 rev-dex-dumper 技能）；砸壳后用 jadx/apktool 正常分析。
- 脱壳后 dex 可能需修复（补 header、magic），再反编译。

## 工作流建议
1. 先**静态分析**（jadx 看 Java / apktool 看 smali / SOMCP 看 so）定位目标函数
2. 判断改 so 还是改 smali：Java 层逻辑改 smali，native 逻辑改 so
3. 能 hook 验证就先用 frida 动态验证思路对不对，再落地成永久 patch
4. patch 后**重打包 + 签名**，装到测试机验证效果
5. 全程只针对自有/授权样本，用于研究学习

## 重要边界
本技能用于安全研究、漏洞分析、兼容性研究、学习和对自有应用的修改。不协助破解他人付费软件牟利、大规模盗版或任何未授权的商业侵权行为。
