---
name: Unity IL2CPP逆向
description: Unity 游戏逆向专项（IL2CPP / Mono）。当分析 Unity 引擎打包的安卓游戏 App（识别标志：assets/bin/Data/、libil2cpp.so、libunity.so、global-metadata.dat）需要还原 C# 逻辑、导出符号、改数值时使用。
---

# Unity 游戏逆向（IL2CPP / Mono）

## 一、先判断是 Mono 还是 IL2CPP
- **Mono**：`assets/bin/Data/Managed/*.dll`（标准 .NET 程序集）→ 用 dnSpy / ILSpy 直接反编译 C#，可改可回编，最简单
- **IL2CPP**：`lib/*/libil2cpp.so` + `assets/bin/Data/Managed/Metadata/global-metadata.dat` → C# 已编译成 native，需还原符号

## 二、IL2CPP 还原符号（核心工具 Il2CppDumper）
1. 从 APK 提取两个文件：
   - `lib/arm64-v8a/libil2cpp.so`
   - `assets/bin/Data/Managed/Metadata/global-metadata.dat`
2. 用 **Il2CppDumper** 处理这两个文件，产出：
   - `dump.cs`：所有 C# 类/方法/字段的定义（含偏移地址）
   - `script.json` / `il2cpp.h`：给 IDA/Ghidra 用的符号脚本
3. 把 libil2cpp.so 拖进 IDA，运行 Il2CppDumper 生成的 `ida_with_struct_py3.py` 脚本 → 自动命名所有函数

## 三、定位关键逻辑
- 在 `dump.cs` 里搜关键词：`Gold`、`Coin`、`Hp`、`Damage`、`IsVip`、`CheckPurchase`、`Verify`
- 找到方法的 `RVA`（相对虚拟地址）→ 到 IDA 对应偏移看反汇编
- 数值类：找 get_/set_ 属性方法
- 校验类：找返回 bool 的 Check/Verify/Validate 方法

## 四、修改手段
1. **改 so 汇编**：定位方法，patch 汇编（如把校验函数改成直接 `mov w0,#1; ret`）→ 用 `reverse-patch-techniques` 技能的方法
2. **Frida 动态 hook**（推荐，配合 frida-scripts 技能）：
   ```javascript
   // hook IL2CPP 方法：先拿到 libil2cpp.so 基址 + RVA
   var base = Module.findBaseAddress("libil2cpp.so");
   var target = base.add(0x1234560); // dump.cs 里的 RVA
   Interceptor.attach(target, {
     onLeave: function(ret) { ret.replace(ptr(1)); } // 校验恒为真
   });
   ```
3. **改 global-metadata.dat**：改字符串常量（部分版本有 XOR 加密头，需先解密）

## 五、常见反制
- **metadata 加密**：global-metadata.dat 头部被改/加密 → 需从 libil2cpp.so 的初始化函数里找解密逻辑，或用 Zygisk-Il2CppDumper 运行时 dump
- **字符串加密**：dump.cs 里字符串是密文 → 运行时 Frida hook 解密函数

## 边界
用于自有游戏、已授权测试、学习引擎原理、单机存档研究。不协助破坏在线游戏公平性、外挂牟利、侵犯他人版权。
