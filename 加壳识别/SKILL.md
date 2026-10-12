---
name: 加壳识别
description: 安卓加固壳精准识别特征库（基于 APKiD 规则整理，供安全研究/自有应用分析）。当需要判断一个 APK 用了哪家加固/壳/保护/混淆（看 lib 里的 so 名、assets 特征、类名特征）时使用，识别后再配合 android-unpacking 技能选对应脱壳方法。
---

# 安卓加固壳识别特征库

通过 APK 里的 **so 文件名、assets 路径、类名** 精准识别加固厂商。识别对了才能选对脱壳方法（配合 `android-unpacking` 技能）。

## 一、看 lib/ 里的 so 名（最快）

| 特征 so | 加固厂商 |
|---|---|
| libjiagu.so / libjiagu_art.so / libjiagu_x86.so | **360 加固** |
| libDexHelper.so / libDexHelper-x86.so | **梆梆（SecNeo/Bangcle 新版）** |
| libsecexe.so / libsecmain.so | **梆梆（Bangcle 旧版）** |
| libSecShell.so / libSecShell-x86.so | **梆梆 SecShell** |
| libshellx-super.2019.so / libtup.so / libexec.so / libtprt.so | **腾讯乐固/御安全** |
| libnesec.so | **网易易盾** |
| libnativehelper 变体 + assets/ijiami.dat | **爱加密（旧）** |
| ijiami.ajm / ijiami3.ajm | **爱加密（新）** |
| libexecmain.so / assets/ijm_lib/ | **爱加密** |
| libapp-xxx.so + libtosprotection | **通付盾** |
| libnqshield.so | **网秦** |
| libbaiduprotect.so / baiduprotect1.jar | **百度加固** |
| libzuma.so / libapktool... | **阿里聚安全** |
| libmobisec.so | **阿里（旧）** |
| libtongfudun.so / libegis.so | **通付盾/tongfudun** |
| libkiroro.so | **Kiro** |
| libnagain... / libDexProtector | **DexProtector（商业）** |
| libapssec.so / assets/appsealing | **AppSealing** |

## 二、看 assets/ 特征

| assets 路径 | 厂商 |
|---|---|
| assets/ijiami.dat / ijiami.ajm | 爱加密 |
| assets/bangcleplugin/ / bangcleclasses.jar | 梆梆 |
| assets/libjiagu* | 360 |
| assets/baiduprotect* | 百度 |
| assets/appsealing* | AppSealing |
| assets/qihoo/ | 360 |

## 三、看入口 Application 类名

| 类名 | 厂商 |
|---|---|
| com.stub.StubApp | 360 加固 |
| com.tencent.StubShell.* / com.tencent.bugly | 腾讯 |
| s.h.e.l.l.S / com.shell.SuperApplication | 爱加密系 |
| com.secneo.apkwrapper.ApplicationWrapper | 梆梆 |
| com.baidu.protect.* | 百度 |
| com.netease.nis.wrapper.* | 网易易盾 |

## 四、识别流程
1. 解包 APK，看 `lib/arm64-v8a/` 下的 so 名 → 对照上表
2. 看 assets/ 特殊文件
3. 看 AndroidManifest 的 `android:name`（入口 Application）
4. 确定厂商后 → 用 `android-unpacking` 技能选对应脱壳法（一代壳通用脱，二代抽取壳用 FART/Youpk）

## 五、加固级别判断
- **一代壳（整体 dex 加密）**：脱壳相对容易，FRIDA-DEXDump / BlackDex 通用脱
- **二代壳（方法抽取/抽取 dex）**：需主动调用脱壳（FART/Youpk）
- **VMP 壳（指令虚拟化，如娜迦/腾讯 legu VMP）**：极难，通常只能动态调试关键逻辑

## 边界
用于对自有或已授权样本的安全研究、恶意软件分析、兼容性研究、学习。不协助盗版牟利或未授权侵权。
