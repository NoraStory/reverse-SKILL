---
name: 协议加密分析
description: 安卓 App 网络协议分析与加密算法识别速查（供安全研究/自有应用分析）。当需要抓包分析请求、识别加密算法(AES/DES/RSA/MD5/SHA/魔改)、定位加解密/签名函数、分析请求签名(sign)参数、还原协议、处理加密的请求体/响应时使用。
---

# 协议分析与加密算法识别速查

面向对**自有或已授权**应用的协议与加密分析。目标：看懂 App 和服务器怎么通信、请求怎么加密/签名，从而分析、调试或做兼容。

## 一、抓包（先看到流量）
- **HTTP/HTTPS**：Charles / Fiddler / mitmproxy / Reqable。需装系统证书；遇 SSL Pinning 用 `frida-scripts` 技能的 bypass。
- **底层/非 HTTP**：tcpdump + Wireshark；或 frida hook socket。
- **抓不到**：多半是 SSL Pinning 或用了非标准端口/协议 → 先绕 pinning，或直接 hook 加密函数看明文。

## 二、识别加密算法（看特征）

### 静态特征（jadx/apktool 里搜关键词）
搜这些字符串/类名快速定位：
- `AES` / `Cipher.getInstance` → 看模式 "AES/CBC/PKCS5Padding" "AES/ECB"
- `RSA` / `KeyFactory` / `PublicKey`
- `MessageDigest` `MD5` `SHA-256` → 摘要/签名
- `Mac` `HmacSHA256` → HMAC 签名
- `Base64` → 编码（常和加密配合）
- `DES` `DESede`（3DES）`Blowfish`
- `sign` `signature` `token` `sercet`/`secret` `appkey` `nonce` `timestamp` → 请求签名参数

### 算法指纹（识别魔改）
- **MD5**：输出 16 字节/32 hex；魔改常改初始向量或加盐
- **AES**：16 字节块；看 IV、key、模式；魔改常改 S 盒或轮数
- **RSA**：看 modulus 长度(1024/2048)、指数(常 65537)
- **CRC/自定义**：短输出、查表 → 可能是校验

## 三、定位加解密函数（动静结合）
1. **静态**：jadx 搜 `Cipher` / `doFinal` / `getInstance`，回溯调用者
2. **动态**：用 `frida-scripts` hook `javax.crypto.Cipher.doFinal`，打印
   输入输出 + 算法 + key + IV：
   ```javascript
   Java.perform(function () {
     var Cipher = Java.use('javax.crypto.Cipher');
     Cipher.doFinal.overload('[B').implementation = function (input) {
       var ret = this.doFinal(input);
       console.log('[Cipher] algo=' + this.getAlgorithm());
       console.log('  in =' + bytesToHex(input));
       console.log('  out=' + bytesToHex(ret));
       return ret;
     };
   });
   ```
3. hook `MessageDigest.digest` / `Mac.doFinal` 抓签名计算

## 四、还原请求签名(sign)
App 常见套路：`sign = MD5(参数排序拼接 + secret + timestamp)`。还原步骤：
1. 抓包看请求带哪些参数、哪个是 sign
2. hook 摘要/HMAC 函数，看 sign 计算时喂进去的**原始字符串**（关键！）
3. 分析拼接规则（参数排序、分隔符、salt/secret 位置）
4. 用脚本复现 sign 计算，验证和抓包一致

## 五、native 层加密（.so 里）
逻辑在 so 里时：
- 用 `frida-scripts` hook so 导出的加解密函数
- 或用 SOMCP 反汇编分析算法实现
- 关注 JNI 函数 `Java_xxx_encrypt` 之类

## 工作流
1. 抓包 → 看哪些字段是加密/签名的
2. jadx 静态搜关键词定位候选函数
3. frida hook Cipher/MessageDigest/Mac 抓明文和 key
4. 分析拼接/算法规则 → 脚本复现验证
5. native 加密则配合 SOMCP/frida 分析 so

## 边界
用于自有/授权应用的协议分析、兼容开发、安全研究、学习。不协助攻击他人服务、盗刷、未授权数据获取。
