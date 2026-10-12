# APKPure APK 安全分析报告

## 基本信息

| 属性 | 值 |
|------|-----|
| 应用名称 | APKPure |
| 包名 | com.apkpure.aegon |
| 版本名称 | 3.20.66 |
| 版本代码 | 3206657 |
| 最低SDK | 19 |
| 目标SDK | 34 |
| ZIP条目数 | 4,462 |
| DEX文件数 | 3 |
| XML文件数 | 3,133 |
| 类数量 | 31,521 |

---

## 收费功能分析

### 1. VIP 会员系统 [高风险]

应用内置了完整的 VIP 会员体系，包含以下组件：

#### 核心类

| 类名 | 源文件 | 功能描述 |
|------|--------|----------|
| `com.apkpure.aegon.main.mainfragment.b0` | MyselfFragment.kt | VIP 布局和图标显示 |
| `com.apkpure.aegon.main.mainfragment.my.d` | ReqUserinfo.kt | VIP 用户信息请求 |
| `com.apkpure.aegon.utils.y` | - | VIP 状态判断工具 |

#### 协议类

| 类名 | 功能 |
|------|------|
| `GetVipUserReq` | VIP 用户请求协议 |
| `GetVipUserRsp` | VIP 用户响应协议 |
| `VipEnter` | VIP 入口控制 |
| `VipUser` | VIP 用户数据模型 |

#### 关键代码

```smali
// isVip 状态判断
const-string v0, "isVip"
const-string v1, "0"

// VIP 用户请求
const-string v0, "get_vip_user"
```

#### 资源文件

| 资源ID | 资源名称 | 类型 |
|--------|----------|------|
| 0x7f0801f8 | $me_vip_icon__0 | drawable |
| 0x7f080537 | me_vip_arrow | drawable |
| 0x7f080539 | me_vip_icon | drawable |
| 0x7f080538 | me_vip_bg | drawable |

---

### 2. 支付功能 [中风险]

应用集成了多个支付 SDK：

#### 支付相关字符串

| 字符串 | 来源 | 用途 |
|--------|------|------|
| `qc_payment_mode_show` | 字节跳动 SDK | 支付模式展示 |
| `ST_PAYMENTS_RISK_DATA` | Google GTM | 支付风险数据 |
| `ST_PAYMENTS_INFO` | Google GTM | 支付信息 |
| `add_payment_info` | Google Measurement | 添加支付信息 |
| `payment_type` | Google Measurement | 支付类型 |
| `application/set-payment-initiation` | 支付处理 | 支付初始化 |

#### 支付相关类

| 类名 | 功能 |
|------|------|
| `com.bytedance.sdk.component.ycc.emc.xq.emc` | 字节跳动支付组件 |
| `com.google.android.gms.internal.gtm.zzaby` | Google 支付数据处理 |
| `com.google.android.gms.measurement.internal.zzii` | 支付事件追踪 |

---

### 3. 应用内购买 [中风险]

存在电商和应用内购买功能：

#### 购买相关字符串

| 字符串 | 用途 |
|--------|------|
| `purchase` | 购买事件 |
| `ecommerce_purchase` | 电商购买事件 |
| `in_app_purchase` | 应用内购买 |
| `is_user_a_purchaser` | 用户购买状态判断 |
| `setInGamePurchasesUSD` | 游戏内购买金额设置 |

#### 购买相关类

| 类名 | 功能 |
|------|------|
| `com.google.android.gms.analytics.ecommerce.ProductAction` | 商品操作 |
| `com.tiktok.appevents.TTPurchaseInfo` | TikTok 购买信息 |
| `com.vungle.ads.fpd.Revenue` | 广告收入/购买状态 |

---

### 4. 订阅功能 [低风险]

发现订阅相关功能，主要是推送订阅：

| 字符串 | 用途 |
|--------|------|
| `app_store_subscription_cancel` | 订阅取消 |
| `app_store_subscription_convert` | 订阅转换 |
| `SubscribeTopicRequest` | 主题订阅请求 |
| `UnSubscribeTopicReq` | 取消主题订阅 |

---

## 风险评估汇总

| 功能模块 | 风险等级 | 说明 |
|----------|----------|------|
| VIP 会员系统 | 高 | 完整的 VIP 体系，可能存在付费会员功能 |
| 支付功能 | 中 | 集成了多个支付 SDK，具备支付能力 |
| 应用内购买 | 中 | 支持电商购买和应用内购买 |
| 订阅功能 | 低 | 主要是推送订阅，非付费订阅 |

---

## 隐藏收费风险点

### 高风险区域

1. **VIP 入口判断**
   - 位置: `MyselfFragment.kt`
   - 方法: `j2()` - 处理 VIP 入口显示逻辑
   - 可能存在: VIP 专属功能入口

2. **VIP 状态检查**
   - 位置: `com.apkpure.aegon.utils.y`
   - 方法: 包含 `isVip` 字符串数组
   - 可能存在: 基于 VIP 状态的功能限制

3. **VIP 用户信息请求**
   - 接口: `get_vip_user`
   - 协议: `GetVipUserReq` / `GetVipUserRsp`
   - 可能存在: 服务端 VIP 权益验证

---

## 建议

1. **运行时分析**: 建议使用抓包工具分析 `get_vip_user` 接口返回数据
2. **界面审查**: 检查 VIP 相关界面的具体权益描述
3. **功能测试**: 测试非 VIP 用户的功能限制情况
4. **代码审计**: 深入分析 `MyselfFragment.kt` 的完整实现

---

## 分析时间

- 分析日期: 2026-05-24
- 工具: mt_mcp APK 分析服务
