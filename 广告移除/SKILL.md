---
name: 广告移除
description: 安卓 App 去广告 / 去开屏弹窗净化专项（供自有设备净化使用）。当需要去除应用内的开屏广告、插屏广告、Banner、信息流广告、更新弹窗、强制弹窗时使用。配合 jadx 定位、MT 管理器/apktool 改 smali、frida 动态验证。
---

# 安卓去广告 / 去弹窗

净化自用 App 的广告与打扰性弹窗。核心是"定位广告触发点 → 让它不执行"。

## 一、先分清广告类型（打法不同）
| 类型 | 特征 | 打法 |
|---|---|---|
| 开屏广告 | 启动时全屏图/视频，倒计时跳过 | 定位 SplashActivity/开屏加载，跳过或直接进主页 |
| 插屏广告 | 操作中途弹全屏 | 定位 show() 调用，让它 return |
| Banner | 页面顶/底部条 | 隐藏 AdView，或让加载方法空转 |
| 信息流 | 混在列表里 | 过滤广告 item / 改数据源 |
| 更新弹窗/公告弹窗 | 启动弹 Dialog | 定位弹窗触发，改条件为 false |

## 二、定位广告 SDK（jadx 搜关键词）
先看用了哪家广告 SDK，对症下药：
- 搜包名：`com.google.android.gms.ads`(AdMob)、`com.qq.e`(优量汇/广点通)、`com.bytedance...` / `com.bykv`(穿山甲)、`com.kwad`(快手)、`com.mbridge`、`com.applovin`、`com.unity3d.ads`
- 搜方法名：`loadAd`、`showAd`、`ShowInterstitial`、`SplashAd`、`onAdLoaded`、`showSplash`
- 搜字符串："跳过"、"广告"、"skip"、倒计时相关

## 三、去广告手法（配合 reverse-patch-techniques）

### 手法 1：让广告加载/展示方法空转
定位 `loadAd()`/`showXxxAd()`，smali 里把方法体改成直接 `return-void`（不加载=不显示）。

### 手法 2：改判断条件跳过
开屏广告常有 `if(shouldShowAd)` → 改成恒 false（`if-eqz` ↔ `if-nez` 翻转，见 smali-repack 技能）。

### 手法 3：直接跳过开屏进主页
定位开屏 Activity 的倒计时结束/跳过按钮回调，让它立即执行"进主页"逻辑（调 startMainActivity），跳过等待。

### 手法 4：广告位控件隐藏
`AdView`/容器 `setVisibility(GONE)`，或 hook `addView` 拦截广告容器。

### 手法 5：Frida 动态定位（配合 frida-scripts）
不确定改哪时，先 Frida hook 广告 SDK 的 show 方法，打印调用栈，找到真正的触发点再固化成 smali patch：
```javascript
Java.perform(function(){
  var Ad = Java.use("com.xxx.AdManager");
  Ad.showInterstitial.implementation = function(){
    console.log("拦截插屏广告 show, 调用栈:\n" + threadStackTrace());
    // 不调用 this.showInterstitial() 即不展示
  };
});
```

## 四、去更新/公告弹窗
- jadx 搜 `AlertDialog`、`Dialog`、`checkUpdate`、`showUpdate`、`公告`、`versionCode` 比对
- 定位弹窗 `show()` 调用，改条件或让方法空转
- 强制更新弹窗（不更新就退出）：找退出逻辑 `finish()`/`System.exit`，去掉

## 五、验证
改完回编重签装机（配合 smali-repack），逐个功能点走一遍确认广告没了、App 不崩、核心功能正常。

## 边界
用于净化**自有设备上自用**的 App 广告、去打扰弹窗，属于个人使用范畴。不协助破坏他人应用的商业模式、去除付费功能或侵权分发。开发者靠广告养活应用，尊重正版、有能力请支持原作者。
