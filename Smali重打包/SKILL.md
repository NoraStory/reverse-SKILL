---
name: Smali重打包
description: Smali 精修与重打包实战（供安全研究/自有应用分析）。当需要看懂/修改 smali 代码、改方法返回值、改常量、注入代码、然后用 apktool/MT 回编译并重签名安装时使用。配合 MT 管理器（直接改 smali）或 apktool（命令行回编）。
---

# Smali 精修与重打包实战

Smali 是 dex 的汇编。改 App 逻辑最通用的方式：jadx 看懂 Java → 定位 smali → 改 → 回编 → 重签名。

## 一、Smali 速查（最常改的几种）

### 改方法直接返回 true / false
```smali
# 返回 true
const/4 v0, 0x1
return v0
# 返回 false
const/4 v0, 0x0
return v0
```

### 改 boolean/int 常量
```smali
const/4 v0, 0x1        # 小数值 (-8~7)
const/16 v0, 0x64      # 中等 (100)
const v0, 0x3e8        # 大数值 (1000)
```

### 让判断失效（nop 掉跳转）
```smali
# 原： if-eqz v0, :cond_0   (v0==0 就跳)
# 改成永不跳 / 永远跳，或直接删掉 if
```

### 常见 if 指令对照
| 指令 | 含义 | 反转 |
|---|---|---|
| if-eqz | ==0 跳 | if-nez |
| if-nez | !=0 跳 | if-eqz |
| if-eq | 相等跳 | if-ne |
| if-ne | 不等跳 | if-eq |

反转判断逻辑：把 `if-eqz` 改 `if-nez` 就能翻转校验结果。

## 二、常见改机目标定位（jadx 搜关键词）
- **VIP/会员**：`isVip`、`isMember`、`getUserType`、`checkPro` → 改返回 true
- **广告**：`showAd`、`AdView`、`loadAd`、`Interstitial` → 让其不执行/直接 return
- **登录/试用**：`isLogin`、`checkLogin`、`trialDays`、`isExpired` → 改返回值
- **签名校验**：见 `signature-bypass` 技能

## 三、回编流程（apktool）
```
apktool d app.apk -o app_src        # 反编译
# 改 app_src/smali*/.../Xxx.smali
apktool b app_src -o app_new.apk    # 回编译
# 必须重签名（否则装不上）
apksigner sign --ks my.keystore app_new.apk
# 或用 uber-apk-signer 自动签
```

## 四、MT 管理器改法（手机上，最方便）
1. MT 打开 APK → dex 编辑器（自带 jadx 反编译看 Java）
2. 直接改对应 smali → 保存 → MT 自动回编 + 签名
3. 适合小改动，不用来回传电脑

## 五、常见回编报错
- **资源报错**：加 `apktool b --use-aapt2` 或用 `-r` 跳过资源重编
- **smali 语法错**：寄存器数不够 → 改 `.locals`/`.registers` 数量
- **方法太大**：单方法超 64K 指令 → 拆分或换 hook 方案
- **multidex**：改的类在 classes2.dex/classes3.dex 里，别改错 dex

## 六、寄存器注意
改 smali 加代码要注意寄存器够不够用，`.locals N` 声明了 N 个局部寄存器。多用寄存器就把 N 调大。参数寄存器是 p0(this)、p1、p2...

## 七、验证
回编签名后装真机跑，看目标功能是否改成功；闪退就看 logcat 定位（可能签名校验没过 → 用 signature-bypass 技能）。

## 边界
用于自有 App 调试改造、已授权测试、去广告净化自用、学习 dalvik。不协助盗版、破解付费、侵权分发。
