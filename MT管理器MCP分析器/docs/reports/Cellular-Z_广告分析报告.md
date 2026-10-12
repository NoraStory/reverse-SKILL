# Cellular-Z 7.2.1 - 广告分析报告

## 基本信息

| 项目 | 值 |
|------|------|
| APK名称 | Cellular-Z_7.2.1.apk |
| 包名 | make.more.r2d2.cellular_z |
| 版本 | 7.2.1 (221) |
| 最低SDK | 24 |
| 目标SDK | 30 |
| 加壳方式 | 360加固 (libjiagu.so) |

## 广告SDK检测结果

### ⚠️ 检测到 4 个广告SDK

| 序号 | 广告SDK | 提供商 | 广告类型 | 风险等级 |
|------|---------|--------|----------|----------|
| 1 | 快手广告SDK (KsAd) | 快手 | 开屏、激励视频、插屏、Banner | 高 |
| 2 | 腾讯广点通 (GDT) | 腾讯 | 激励视频、插屏、Banner | 高 |
| 3 | 穿山甲SDK (Pangle) | 字节跳动 | 开屏、激励视频、插屏 | 高 |
| 4 | Google广告ID | Google | 广告追踪 | 中 |

---

## 详细分析

### 1. 快手广告SDK (KsAd/KwAd)

**包名**: `com.kwad.*`

**检测到的组件**:

#### Activity组件
- `com.kwad.sdk.api.proxy.app.AdWebViewActivity` - 广告WebView页面
- `com.kwad.sdk.api.proxy.app.KsFullScreenVideoActivity` - 全屏视频广告

#### 广告类型支持
- 开屏广告 (Splash Ad) - `com.kwad.components.ad.splashscreen.*`
- 激励视频 (Reward Video) - `com.kwad.components.ad.reward.*`
- 插屏广告 (Interstitial) - `com.kwad.components.ad.interstitial.*`
- Banner广告 - `com.kwad.components.ad.widget.*`
- Feed流广告 - `com.kwad.sdk.widget.*`

#### 资源文件
- `assets/ksad_common_encrypt_image.png` - 快手广告加密图片
- `assets/ksad_idc.json` - 快手广告IDC配置

#### 配置文件 (ksad_idc.json)
```json
{
  "api": ["open.e.kuaishou.com", "open.e.kuaishou.cn"],
  "ulog": ["ulog-sdk.gifshow.com", "ulog-sdk.ksapisrv.com"],
  "cdn": ["w1.kskwai.com", "w2.kskwai.com", "w1.gskwai.com", "w2.gskwai.com"],
  "zt": ["zt.gifshow.com", "api.kuaishouzt.com", "api.kwaizt.com"],
  "eapi": ["api.e.kuaishou.com", "api.e.kuaishou.cn"]
}
```

---

### 2. 腾讯广点通 (GDT)

**包名**: `com.qq.e.*`

**检测到的组件**:

#### Activity组件
- `com.qq.e.ads.RewardvideoPortraitADActivity` - 激励视频广告(竖屏)

#### Provider组件
- `com.qq.e.comm.GDTFileProvider` - GDT文件提供者
  - authorities: `make.more.r2d2.cellular_z.gdt.fileprovider`

#### 资源文件
- `assets/gdt_plugin/gdtadv2.jar` - GDT广告插件JAR包 (约2MB)

---

### 3. 穿山甲广告SDK (Pangle/头条SDK)

**包名**: `com.bytedance.sdk.openadsdk.*`

**检测到的权限**:
```xml
<permission android:name="make.more.r2d2.cellular_z.openadsdk.permission.TT_PANGOLIN" 
            android:protectionLevel="signature"/>
<uses-permission android:name="make.more.r2d2.cellular_z.openadsdk.permission.TT_PANGOLIN"/>
```

**Native库文件**:
- `lib/arm64-v8a/libpanglearmor.so` (264KB)
- `lib/arm64-v8a/libpangleflipped.so` (10KB)
- `lib/arm64-v8a/libPglbizssdk_ml.so` (1.1MB)
- `lib/armeabi-v7a/libpangleflipped.so` (9KB)

---

### 4. Google广告ID

**权限声明**:
```xml
<uses-permission android:name="com.google.android.gms.permission.AD_ID"/>
```

**用途**: 用于获取Google广告ID，进行广告追踪和个性化推荐。

---

## AndroidManifest中的广告相关配置

### 权限汇总
```xml
<!-- 穿山甲权限 -->
<permission android:name="make.more.r2d2.cellular_z.openadsdk.permission.TT_PANGOLIN" 
            android:protectionLevel="signature"/>
<uses-permission android:name="make.more.r2d2.cellular_z.openadsdk.permission.TT_PANGOLIN"/>

<!-- Google广告ID权限 -->
<uses-permission android:name="com.google.android.gms.permission.AD_ID"/>
```

### 广告Activity配置
```xml
<!-- 快手广告WebView -->
<activity android:name="com.kwad.sdk.api.proxy.app.AdWebViewActivity"
          android:screenOrientation="portrait"/>

<!-- 快手全屏视频广告 -->
<activity android:name="com.kwad.sdk.api.proxy.app.KsFullScreenVideoActivity"
          android:screenOrientation="portrait"/>

<!-- GDT激励视频广告 -->
<activity android:name="com.qq.e.ads.RewardvideoPortraitADActivity"
          android:exported="false" android:multiprocess="true"/>
```

---

## 移除广告的方法

### 方法一：使用MT管理器（推荐）

#### 步骤1：移除广告Activity
在 `AndroidManifest.xml` 中删除以下组件：

```xml
<!-- 删除快手广告Activity -->
<activity android:name="com.kwad.sdk.api.proxy.app.AdWebViewActivity" .../>
<activity android:name="com.kwad.sdk.api.proxy.app.KsFullScreenVideoActivity" .../>

<!-- 删除GDT广告Activity -->
<activity android:name="com.qq.e.ads.RewardvideoPortraitADActivity" .../>

<!-- 删除GDT FileProvider -->
<provider android:name="com.qq.e.comm.GDTFileProvider" .../>
```

#### 步骤2：移除广告权限
删除以下权限声明：

```xml
<uses-permission android:name="make.more.r2d2.cellular_z.openadsdk.permission.TT_PANGOLIN"/>
<uses-permission android:name="com.google.android.gms.permission.AD_ID"/>
<permission android:name="make.more.r2d2.cellular_z.openadsdk.permission.TT_PANGOLIN" .../>
```

#### 步骤3：删除广告资源文件
删除 `assets/` 目录下的广告相关文件：

```
assets/gdt_plugin/           # GDT广告插件目录
assets/ksad_common_encrypt_image.png  # 快手广告图片
assets/ksad_idc.json         # 快手广告配置
```

#### 步骤4：删除广告Native库
删除 `lib/` 目录下的广告相关SO文件：

```
lib/arm64-v8a/libpanglearmor.so
lib/arm64-v8a/libpangleflipped.so
lib/arm64-v8a/libPglbizssdk_ml.so
lib/armeabi-v7a/libpangleflipped.so
```

#### 步骤5：删除广告布局文件
删除 `res/` 目录下以 `ksad_` 开头的所有资源和布局文件。

---

### 方法二：使用LSPosed/Xposed框架Hook（免修改APK）

可使用以下模块：
- **Fuck AD** - 通用广告屏蔽模块
- **AdBlocker** - 广告拦截模块

Hook点示例：
```java
// Hook快手广告
XposedHelpers.findAndHookMethod("com.kwad.sdk.api.KsAdSDK", 
    lpparam.classLoader, "init", Context.class, 
    new XC_MethodReplacement() {
        @Override
        protected Object replaceHookedMethod(MethodHookParam param) {
            return null; // 阻止初始化
        }
    });
```

---

### 方法三：使用MT管理器活动记录器

1. 打开MT管理器
2. 进入活动记录器
3. 打开Cellular-Z
4. 触发广告展示
5. 记录广告Activity类名
6. 在AndroidManifest中禁用对应Activity（添加 `android:enabled="false"`）

---

## 注意事项

### ⚠️ 加壳提醒
本APK使用 **360加固** 保护，直接修改DEX可能无效。建议：

1. **优先修改AndroidManifest** - 删除广告组件声明
2. **删除资源文件** - 删除assets和res中的广告资源
3. **删除Native库** - 删除广告SDK的SO文件
4. **脱壳后修改** - 如需深度修改，先使用脱壳工具

### 脱壳工具推荐
- **BlackDex** - 一键脱壳
- **FART** - 基于ART的脱壳工具
- **DumpDex** - 通用脱壳工具

### 修改后处理
修改完成后需要：
1. 重新签名APK
2. 卸载原版应用
3. 安装修改后的APK

---

## 总结

Cellular-Z 7.2.1 集成了 **4个广告SDK**：

| SDK | 用途 | 移除难度 |
|-----|------|----------|
| 快手广告SDK | 开屏、激励视频、插屏广告 | 中等 |
| 腾讯广点通 | 激励视频、Banner广告 | 简单 |
| 穿山甲SDK | 开屏、激励视频广告 | 中等 |
| Google广告ID | 广告追踪 | 简单 |

**推荐移除方案**：
1. 使用MT管理器删除AndroidManifest中的广告组件
2. 删除assets和lib中的广告相关文件
3. 删除res中的广告布局资源
4. 重新签名安装

---

*报告生成时间: 2026-05-24*
*分析工具: mt_mcp APK Analyzer*
