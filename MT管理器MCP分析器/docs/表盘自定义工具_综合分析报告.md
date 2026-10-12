# 表盘自定义工具 - APK分析报告

## 基本信息

| 项目 | 值 |
|------|------|
| APK名称 | 表盘自定义工具_6.4.0.apk |
| 包名 | tech.pingx.watchface |
| 版本 | 6.4.0 (versionCode: 163) |
| 最低SDK | 24 (Android 7.0) |
| 目标SDK | 33 (Android 13) |
| 文件大小 | 45.6 MB |
| DEX文件数 | 3 |
| 类总数 | 25,534 |
| 签名方式 | V1 + V2 |
| 签名证书 | CN=pingx.tech (有效期: 2019-06-23 至 2119-06-23) |

## 权限分析

### 核心功能权限

| 权限 | 用途 | 风险等级 |
|------|------|----------|
| BLUETOOTH_ADVERTISE | 蓝牙广播 | 低 |
| BLUETOOTH_CONNECT | 蓝牙连接 | 低 |
| BLUETOOTH_SCAN | 蓝牙扫描 | 低 |
| BLUETOOTH_ADMIN | 蓝牙管理 | 低 |
| BLUETOOTH | 蓝牙基础 | 低 |

**说明：** 蓝牙权限用于与智能手表/手环设备通信，传输表盘数据。

### 存储权限

| 权限 | 用途 | 风险等级 |
|------|------|----------|
| WRITE_EXTERNAL_STORAGE | 写入外部存储 | 中 |
| READ_EXTERNAL_STORAGE | 读取外部存储 | 中 |
| MANAGE_EXTERNAL_STORAGE | 管理所有文件 | 高 |
| READ_MEDIA_IMAGES | 读取图片 | 中 |
| READ_MEDIA_VIDEO | 读取视频 | 中 |

**说明：** 存储权限用于保存和读取表盘文件、图片资源。MANAGE_EXTERNAL_STORAGE权限范围较广，需关注使用场景。

### 网络与位置权限

| 权限 | 用途 | 风险等级 |
|------|------|----------|
| INTERNET | 网络访问 | 中 |
| ACCESS_NETWORK_STATE | 网络状态 | 低 |
| ACCESS_WIFI_STATE | WiFi状态 | 低 |
| CHANGE_WIFI_STATE | 修改WiFi状态 | 中 |
| ACCESS_FINE_LOCATION | 精确位置 | 高 |
| ACCESS_COARSE_LOCATION | 粗略位置 | 中 |
| ACCESS_BACKGROUND_LOCATION | 后台位置 | 高 |

**说明：** 位置权限可能用于蓝牙设备配对时的定位需求，或广告SDK定位投放。

### 其他敏感权限

| 权限 | 用途 | 风险等级 |
|------|------|----------|
| CAMERA | 相机 | 高 |
| READ_PHONE_STATE | 读取手机状态 | 高 |
| REQUEST_INSTALL_PACKAGES | 安装应用 | 高 |
| QUERY_ALL_PACKAGES | 查询所有包 | 高 |
| SCHEDULE_EXACT_ALARM | 精确闹钟 | 中 |
| VIBRATE | 振动 | 低 |

**说明：**
- CAMERA权限用于表盘设计时的图片拍摄
- READ_PHONE_STATE用于设备识别
- REQUEST_INSTALL_PACKAGES可能用于应用内更新
- QUERY_ALL_PACKAGES可查询设备上所有应用，隐私风险较高

## 功能模块分析

### 1. 表盘设计功能

**主要类：**
- `com.givemefive.ble.design.DesignActivity` - 设计主界面
- `com.givemefive.ble.design.CropActivity` - 图片裁剪
- `com.givemefive.ble.PictureActivity` - 图片处理
- `com.givemefive.ble.PictureCropActivity` - 图片裁剪

**功能说明：** 支持自定义表盘设计，包括图片导入、裁剪、编辑等功能。

### 2. 蓝牙传输功能

**主要类：**
- `com.givemefive.ble.BLEActivity` - 蓝牙主界面
- `com.givemefive.ble.BLEActivityMi7` - 小米手环7适配
- `com.givemefive.ble.BLEActivityMi8` - 小米手环8适配
- `com.givemefive.ble.BLEActivityMi8Pro` - 小米手环8 Pro适配
- `com.givemefive.ble.service.ForegroundService` - 前台服务

**支持的设备：**
- 小米手环7/8/8 Pro
- 小米健康应用（com.mi.health）
- 小米穿戴应用（com.xiaomi.wearable）

**功能说明：** 通过蓝牙将自定义表盘传输到智能手表/手环设备。

### 3. 电子书功能

**主要类：**
- `com.givemefive.ble.EBookActivity` - 电子书界面
- `com.givemefive.ble.EBookActivityMi8Pro` - 小米手环8 Pro适配
- `com.givemefive.ble.EBookActivityMi8Pro2` - 小米手环8 Pro二代适配

**功能说明：** 支持将电子书内容传输到手表设备显示。

### 4. VIP/会员功能

**发现的关键字符串：**
- `vip` - VIP标识
- `libxgVipSecurity.so` - VIP安全库
- `/userSvipTaskLog/gzmShareReport?` - SVIP任务日志上报

**定位器信息：**
- 类：`Ld/h;` 包含 `libxgVipSecurity.so` 字符串
- 类：`Lcom/dcloudym/utils/r;` 包含SVIP相关API路径

**功能说明：** 应用包含VIP会员功能，可能有高级表盘资源或功能解锁机制。

### 5. 支付功能

**发现的关键字符串：**
- `Payment` - 支付标识
- `Payment-getUserInfo` - 支付获取用户信息
- `Payment Required` - HTTP状态码

**定位器信息：**
- 类：`Lio/dcloud/feature/payment/PaymentFeatureImpl;` - 支付功能实现
- 类：`Lio/dcloud/common/DHInterface/IFeature;` - 功能接口

**功能说明：** 应用集成支付功能，可能用于VIP会员购买或表盘资源付费下载。

### 6. 登录认证功能

**发现的关键字符串：**
- `login` - 登录标识
- `_needloginbeforemonthpay=1` - 月付前需登录
- `ym_dcloudym_common_login` - 登录事件

**定位器信息：**
- 类：`Lcom/dcloudym/activityComm/CommonLogin;` - 登录界面

**功能说明：** 应用需要用户登录才能使用部分功能，登录状态影响支付和VIP功能。

## 安全分析

### 1. 敏感字符串

**发现的敏感关键词：**

| 关键词 | 出现次数 | 主要位置 | 风险评估 |
|--------|----------|----------|----------|
| password | 多处 | 通用加密类、数据库类 | 中 - 用于加密配置 |
| secret | 多处 | SDK初始化、密钥配置 | 中 - SDK密钥配置 |
| secretKey | 1次 | 广告SDK配置 | 中 - 广告SDK密钥 |
| api_key | 1次 | 百度地图API | 中 - 地图SDK密钥 |
| token | 多处 | 会话管理、推送服务 | 中 - 用户会话令牌 |

**具体发现：**
- `com.baidu.lbsapi.API_KEY` - 百度地图SDK密钥
- `secretKey` - 广告SDK密钥配置
- `EfsReporter init, secret is empty` - SDK初始化日志

**风险评估：** 这些字符串多为第三方SDK配置参数，非硬编码密码，风险可控。

### 2. 加密机制

**发现的加密相关字符串：**
- `use_encryption` - 使用加密标志
- `use_v3_encryption` - 使用V3加密
- `encryption` - 加密字段

**定位器信息：**
- 类：`Lb/e;` 包含加密配置
- 类：`Lc/b;` 包含V3加密配置
- 类：`Lcom/czhj/sdk/common/Database/SQLiteMTAHelper;` 包含加密数据库字段

**功能说明：** 应用使用加密机制保护数据传输和存储，具体加密算法需进一步分析。

### 3. 网络安全配置

**发现的网络配置：**
- `usesCleartextTraffic="true"` - 允许明文传输
- 多个HTTPS域名

**风险评估：** 允许明文传输可能存在中间人攻击风险，建议检查网络安全配置文件。

### 4. WebView使用

**发现的WebView相关：**
- 多个WebView Activity
- JavaScript接口

**风险评估：** WebView使用需注意JavaScript接口安全性，防止XSS攻击。

### 5. 组件暴露

**发现的暴露组件：**
- `FileOpenActivity` - exported=true，处理.bin/.rpk/.face文件
- `PandoraEntry` - exported=true，主入口
- `PandoraEntryActivity` - exported=true，需要特殊权限

**风险评估：** FileOpenActivity暴露可能被恶意应用利用，需验证文件处理逻辑。

## 第三方SDK分析

### 1. 广告SDK

| SDK名称 | 包名 | 功能 | 风险等级 |
|---------|------|------|----------|
| 快手广告SDK | com.kwad.sdk | 视频广告、激励广告 | 中 |
| 贝子广告SDK | com.beizi.ad | 插屏广告、下载广告 | 中 |
| 章鱼广告SDK | com.octopus.ad | 多种广告形式 | 中 |
| Sigmob广告SDK | com.sigmob.sdk | 广告聚合 | 中 |
| 穿山甲广告SDK | com.fl.saas | 激励视频、全屏视频 | 中 |

**发现的关键字符串：**
- `KUAISHOU` - 快手广告标识
- 多个广告Activity配置

**功能说明：** 应用集成多个广告SDK，通过广告变现。激励视频广告可能用于解锁VIP功能或表盘资源。

### 2. 推送SDK

| SDK名称 | 包名 | 功能 |
|---------|------|------|
| UniPush | io.dcloud.feature.unipush | 消息推送 |
| 个推SDK | com.igexen.sdk | 推送服务 |

**配置信息：**
- `GETUI_APPID` - 个推应用ID
- `PUSH_APPID` - 推送应用ID
- `PUSH_APPKEY` - 推送应用密钥
- `PUSH_APPSECRET` - 推送应用密钥

**功能说明：** 用于消息推送、表盘更新通知等。

### 3. 地图SDK

| SDK名称 | 功能 |
|---------|------|
| 百度地图API | 定位服务 |

**配置信息：**
- `com.baidu.lbsapi.API_KEY` - 百度地图API密钥

**功能说明：** 可能用于蓝牙设备定位或广告定位投放。

### 4. 图片加载SDK

| SDK名称 | 包名 | 功能 |
|---------|------|------|
| Glide | com.bumptech.glide | 图片加载缓存 |

**功能说明：** 用于表盘图片资源的加载和缓存。

### 5. 网络请求SDK

| SDK名称 | 包名 | 功能 |
|---------|------|------|
| OkHttp3 | com.czhj.volley.toolbox.OkHttp3Stack | HTTP请求 |
| Volley | com.czhj.volley | 网络请求框架 |

**功能说明：** 用于网络请求，包括表盘资源下载、API调用等。

### 6. DCloud框架

| 模块 | 功能 |
|------|------|
| uni-app | 跨平台开发框架 |
| Weex | 前端渲染框架 |
| HTML5+ | 原生能力扩展 |

**功能说明：** 应用基于DCloud uni-app框架开发，部分功能使用原生代码实现。

### 7. 其他SDK

| SDK名称 | 功能 |
|---------|------|
| Shizuku | 系统权限管理 |
| 微博SDK | 社交分享 |
| FastJSON | JSON解析 |
| Apache Commons | 工具库 |

## 网络通信分析

### 1. API域名

**发现的域名：**
- `ask.dcloud.net.cn` - DCloud问答社区
- `pingx.tech` - 应用主域名
- 多个广告SDK域名

**定位器信息：**
- 类：`Lb/a$d;` 包含 `https://ask.dcloud.net.cn/article/35627`
- 类：`Lb/a$e;` 包含 `https://ask.dcloud.net.cn/article/35877`

### 2. 文件传输协议

**支持的文件格式：**
- `.bin` - 二进制表盘文件
- `.rpk` - 快应用包
- `.face` - 表盘文件

**Intent过滤器：**
```xml
<data android:mimeType="*/*" />
<data android:pathPattern=".*\\.bin" />
<data android:pathPattern=".*\\.rpk" />
<data android:pathPattern=".*\\.face" />
```

### 3. 自定义Scheme

**发现的Scheme：**
- `watchface://` - 表盘自定义协议

**功能说明：** 用于应用内跳转和表盘文件打开。

## 应用架构分析

### 1. 包结构

**主要包名：**
- `com.givemefive.ble` - 蓝牙功能模块
- `com.givemefive.ble.design` - 表盘设计模块
- `com.givemefive.ble.activity` - Activity集合
- `com.givemefive.ble.service` - 服务模块
- `com.givemefive.viewhelper` - 视图辅助工具

### 2. Activity分析

**主要Activity：**
- `io.dcloud.PandoraEntry` - 主入口（uni-app）
- `com.givemefive.ble.BLEActivity` - 蓝牙主界面
- `com.givemefive.ble.design.DesignActivity` - 设计界面
- `com.givemefive.ble.EBookActivity` - 电子书界面

### 3. Service分析

**主要Service：**
- `com.givemefive.ble.service.ForegroundService` - 前台服务
- `io.dcloud.feature.unipush.CustomGTService` - 推送服务
- `com.kwad.sdk.api.proxy.app.DownloadService` - 广告下载服务

### 4. Provider分析

**主要Provider：**
- `rikka.shizuku.ShizukuProvider` - Shizuku权限服务
- 多个FileProvider - 文件共享

## 潜在风险与建议

### 1. 高风险项

| 风险项 | 描述 | 建议 |
|--------|------|------|
| MANAGE_EXTERNAL_STORAGE | 全文件访问权限 | 评估是否必要，考虑使用Scoped Storage |
| ACCESS_BACKGROUND_LOCATION | 后台定位权限 | 明确使用场景，最小化权限范围 |
| QUERY_ALL_PACKAGES | 查询所有应用 | 评估必要性，考虑使用特定包名查询 |
| usesCleartextTraffic | 允许明文传输 | 配置网络安全策略，限制明文传输范围 |
| FileOpenActivity暴露 | 文件处理组件暴露 | 验证文件处理逻辑，防止恶意文件攻击 |

### 2. 中风险项

| 风险项 | 描述 | 建议 |
|--------|------|------|
| 多个广告SDK | 广告SDK可能收集用户数据 | 检查SDK隐私政策，限制数据收集范围 |
| WebView使用 | JavaScript接口安全 | 禁用不必要的JavaScript接口，验证输入 |
| API密钥硬编码 | 第三方SDK密钥暴露 | 使用服务器下发或动态配置 |

### 3. 低风险项

| 风险项 | 描述 | 建议 |
|--------|------|------|
| 签名证书有效期过长 | 证书有效期100年 | 符合规范，无需处理 |
| 多DEX文件 | 应用较大，分包加载 | 正常优化手段，无需处理 |

### 4. 安全加固建议

1. **权限最小化**
   - 评估MANAGE_EXTERNAL_STORAGE必要性，考虑使用Scoped Storage API
   - 限制后台定位权限使用场景
   - 使用特定包名查询替代QUERY_ALL_PACKAGES

2. **网络安全**
   - 配置network_security_config.xml，限制明文传输域名
   - 启用HTTPS证书固定（Certificate Pinning）
   - 验证服务器证书有效性

3. **组件安全**
   - FileOpenActivity添加权限保护或验证调用来源
   - WebView禁用不必要的JavaScript接口
   - 验证Intent过滤器处理逻辑

4. **数据保护**
   - 检查敏感数据存储加密
   - 验证SharedPreferences安全性
   - 检查日志输出是否包含敏感信息

5. **第三方SDK**
   - 审查广告SDK隐私政策合规性
   - 限制SDK数据收集范围
   - 定期更新SDK版本，修复安全漏洞

## 功能修改建议

### 1. VIP功能解锁

**定位信息：**
- VIP标识类：`Ld/h;`
- VIP安全库：`libxgVipSecurity.so`
- SVIP任务上报：`/userSvipTaskLog/gzmShareReport?`

**修改思路：**
- 搜索VIP状态检查方法，修改返回值
- 定位VIP功能限制逻辑，移除限制
- 注意VIP安全库可能包含签名校验

**风险提示：**
- VIP功能可能包含服务器验证，本地修改可能无效
- VIP安全库可能包含防篡改机制
- 修改后可能触发服务器风控

### 2. 广告移除

**定位信息：**
- 快手广告SDK：`com.kwad.sdk`
- 贝子广告SDK：`com.beizi.ad`
- 章鱼广告SDK：`com.octopus.ad`

**修改思路：**
- 定位广告加载方法，提前返回
- 移除广告Activity配置
- 禁用广告SDK初始化

**风险提示：**
- 广告SDK可能与应用功能耦合
- 移除广告可能影响激励视频解锁功能
- 需验证广告SDK初始化逻辑

### 3. 登录绕过

**定位信息：**
- 登录界面：`Lcom/dcloudym/activityComm/CommonLogin;`
- 登录状态检查：`_needloginbeforemonthpay=1`

**修改思路：**
- 定位登录状态检查方法，修改返回值
- 移除登录前置检查逻辑

**风险提示：**
- 登录状态可能影响服务器交互
- 绕过登录可能导致功能异常
- 需验证登录状态存储位置

## 总结

**应用类型：** 智能手表/手环表盘自定义工具

**核心功能：**
- 表盘设计编辑
- 蓝牙传输到设备
- 电子书传输
- VIP会员功能
- 广告变现

**技术架构：**
- DCloud uni-app框架
- 原生蓝牙通信模块
- 多广告SDK集成
- OkHttp3网络请求

**安全评估：**
- 权限使用较多，部分高风险权限需评估必要性
- 集成多个广告SDK，需关注隐私合规
- 网络安全配置需加固
- 组件暴露需验证安全性

**修改建议：**
- VIP功能修改需处理服务器验证和安全库
- 广告移除需验证功能耦合
- 登录绕过需验证服务器交互

---

*报告生成时间: 2025-06-23*
*分析工具: MT管理器 MCP APK Analyzer*
*分析类型: 综合分析*