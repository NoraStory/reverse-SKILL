# 表盘自定义工具 - 捐赠者功能破解方案

## 一、验证机制分析

### 1.1 捐赠者验证流程

**核心验证方法：** `ActivityUtil.checkTk()`

```smali
.method public static checkTk()Z
    .registers 5
    
    # 检查tk字段是否为空
    sget-object v0, Lcom/givemefive/ble/activity/ActivityUtil;->tk:Ljava/lang/String;
    invoke-static {v0}, Lorg/apache/commons/lang3/q;->A0(Ljava/lang/CharSequence;)Z
    move-result v0
    const/4 v1, 0x0
    if-eqz v0, :cond_0
    return v1  ← tk为空，返回false
    
    :cond_0
    # 构建API URL
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V
    sget-object v4, Lcom/givemefive/ble/activity/ActivityUtil;->baseUrl:Ljava/lang/String;
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v4, "member/is/donationApp/"
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    sget-object v4, Lcom/givemefive/ble/activity/ActivityUtil;->tk:Ljava/lang/String;
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    
    # 发起HTTP请求
    invoke-virtual {v2, v3, v0}, Lcom/givemefive/ble/util/g;->a(Ljava/lang/String;Lcom/givemefive/ble/util/g$g;)Z
    
    # 解析返回的JSON
    invoke-static {v0}, Lcom/alibaba/fastjson/a;->parseObject(Ljava/lang/String;)Lcom/alibaba/fastjson/JSONObject;
    move-result-object v0
    const-string v2, "code"
    invoke-virtual {v0, v2}, Lcom/alibaba/fastjson/JSONObject;->getIntValue(Ljava/lang/String;)I
    move-result v0
    
    # 判断code是否为0
    if-nez v0, :cond_1  ← code==0，是捐赠者
    const/4 v0, 0x1
    return v0  ← 返回true
    
    :cond_1
    return v1  ← code!=0，不是捐赠者，返回false
.end method
```

**验证逻辑总结：**
1. 检查`tk`字段是否为空，为空返回false
2. 构建API URL：`baseUrl + "member/is/donationApp/" + tk`
3. 发起HTTP GET请求
4. 解析返回的JSON，获取`code`字段
5. `code==0`表示是捐赠者，返回true
6. `code!=0`表示不是捐赠者，返回false

### 1.2 限制逻辑分析

**限制位置1：** `BLEActivityMi8BleNew$i.run()`

```smali
.method public run()V
    .registers 2
    
    invoke-static {}, Lcom/givemefive/ble/activity/ActivityUtil;->checkTk()Z
    move-result v0
    
    if-nez v0, :cond_0  ← 如果checkTk返回false（不是捐赠者）
    
    iget-object v0, p0, Lcom/givemefive/ble/BLEActivityMi8BleNew$i;->a:Lcom/givemefive/ble/BLEActivityMi8BleNew;
    invoke-virtual {v0}, Landroid/app/Activity;->finish()V  ← 关闭Activity
    
    :cond_0
    return-void
.end method
```

**限制位置2：** `BLEActivityMi8Pro$p.run()`

```smali
.method public run()V
    .registers 2
    
    invoke-static {}, Lcom/givemefive/ble/activity/ActivityUtil;->checkTk()Z
    move-result v0
    
    if-nez v0, :cond_0  ← 如果checkTk返回false（不是捐赠者）
    
    iget-object v0, p0, Lcom/givemefive/ble/BLEActivityMi8Pro$p;->a:Lcom/givemefive/ble/BLEActivityMi8Pro;
    invoke-virtual {v0}, Landroid/app/Activity;->finish()V  ← 关闭Activity
    
    :cond_0
    return-void
.end method
```

**限制逻辑总结：**
- 在Activity的onCreate中启动Runnable检查
- 如果`checkTk()`返回false，调用`finish()`关闭Activity
- 如果`checkTk()`返回true，Activity继续运行

### 1.3 其他限制位置

**限制提示信息：**
- `该功能仅限捐赠者` - PreviewActivity$c类
- `未捐赠无法使用蓝牙安装` - DesignActivity$10类
- `未捐赠无法使用智能安装` - DesignActivityMi8$9类
- `未捐赠无法使用图片替换功能` - WebViewInterface和WebViewInterfaceMi8类

这些限制可能使用类似的验证逻辑，需要进一步分析。

### 1.4 关键字段

**静态字段：**
```smali
.field public static isD:Z  ← 捐赠者标志（布尔值）
.field public static tk:Ljava/lang/String;  ← 捐赠者token
.field public static baseUrl:Ljava/lang/String;  ← API基础URL
```

**初始化：**
```smali
.method static constructor <clinit>()V
    const/4 v0, 0x0
    sput-boolean v0, Lcom/givemefive/ble/activity/ActivityUtil;->isD:Z  ← 初始化为false
    const-string v0, ""
    sput-object v0, Lcom/givemefive/ble/activity/ActivityUtil;->tk:Ljava/lang/String;  ← 初始化为空字符串
    sput-object v0, Lcom/givemefive/ble/activity/ActivityUtil;->baseUrl:Ljava/lang/String;  ← 初始化为空字符串
    return-void
.end method
```

## 二、破解方案分析

### 2.1 方案对比

| 方案 | 修改位置 | 修改难度 | 稳定性 | 推荐度 |
|------|----------|----------|--------|--------|
| 方案1 | checkTk()方法 | 简单 | 高 | ★★★★★ |
| 方案2 | 调用checkTk()的地方 | 中等 | 中 | ★★★☆☆ |
| 方案3 | isD字段初始化 | 简单 | 低 | ★★☆☆☆ |
| 方案4 | tk字段伪造 | 复杂 | 低 | ★☆☆☆☆ |

### 2.2 方案1：修改checkTk()方法（推荐）

**优点：**
- 修改简单，只需修改一个方法
- 稳定性高，不影响其他逻辑
- 绕过服务器验证，无需网络请求

**缺点：**
- 可能存在其他验证逻辑
- 服务器可能检测到异常行为

**修改方案：**

**原始代码：**
```smali
.method public static checkTk()Z
    .registers 5
    
    sget-object v0, Lcom/givemefive/ble/activity/ActivityUtil;->tk:Ljava/lang/String;
    invoke-static {v0}, Lorg/apache/commons/lang3/q;->A0(Ljava/lang/CharSequence;)Z
    move-result v0
    const/4 v1, 0x0
    if-eqz v0, :cond_0
    return v1
    
    :cond_0
    # ... 网络请求逻辑 ...
    
    if-nez v0, :cond_1
    const/4 v0, 0x1
    return v0
    
    :cond_1
    return v1
.end method
```

**修改后代码：**
```smali
.method public static checkTk()Z
    .registers 5
    
    # 直接返回true，跳过所有验证逻辑
    const/4 v0, 0x1
    return v0
    
    # 保留原始代码（可选，用于调试）
    # sget-object v0, Lcom/givemefive/ble/activity/ActivityUtil;->tk:Ljava/lang/String;
    # invoke-static {v0}, Lorg/apache/commons/lang3/q;->A0(Ljava/lang/CharSequence;)Z
    # move-result v0
    # const/4 v1, 0x0
    # if-eqz v0, :cond_0
    # return v1
    # 
    # :cond_0
    # ... 网络请求逻辑 ...
    # 
    # if-nez v0, :cond_1
    # const/4 v0, 0x1
    # return v0
    # 
    # :cond_1
    # return v1
.end method
```

**修改步骤：**
1. 打开APK → Dex编辑器++
2. 搜索类名：`com.givemefive.ble.activity.ActivityUtil`
3. 找到`checkTk()`方法
4. 在方法开头添加：
   ```smali
   const/4 v0, 0x1
   return v0
   ```
5. 保存并退出 → 自动签名

### 2.3 方案2：修改调用checkTk()的地方

**优点：**
- 不修改核心验证方法
- 可以精确控制哪些功能被解锁

**缺点：**
- 需要修改多个位置
- 可能遗漏某些验证点
- 稳定性较低

**修改方案：**

**原始代码：**
```smali
.method public run()V
    .registers 2
    
    invoke-static {}, Lcom/givemefive/ble/activity/ActivityUtil;->checkTk()Z
    move-result v0
    
    if-nez v0, :cond_0  ← 如果checkTk返回false
    
    iget-object v0, p0, Lcom/givemefive/ble/BLEActivityMi8BleNew$i;->a:Lcom/givemefive/ble/BLEActivityMi8BleNew;
    invoke-virtual {v0}, Landroid/app/Activity;->finish()V
    
    :cond_0
    return-void
.end method
```

**修改后代码：**
```smali
.method public run()V
    .registers 2
    
    # 跳过checkTk()调用，直接继续执行
    # invoke-static {}, Lcom/givemefive/ble/activity/ActivityUtil;->checkTk()Z
    # move-result v0
    # if-nez v0, :cond_0
    
    # 直接跳转到:cond_0，不执行finish()
    goto :cond_0
    
    # iget-object v0, p0, Lcom/givemefive/ble/BLEActivityMi8BleNew$i;->a:Lcom/givemefive/ble/BLEActivityMi8BleNew;
    # invoke-virtual {v0}, Landroid/app/Activity;->finish()V
    
    :cond_0
    return-void
.end method
```

**需要修改的位置：**
- `BLEActivityMi8BleNew$i.run()`
- `BLEActivityMi8Pro$p.run()`
- 其他包含"未捐赠"提示的类

### 2.4 方案3：修改isD字段初始化

**优点：**
- 修改简单，只需修改一个字段初始化

**缺点：**
- isD字段可能不被使用
- 可能存在其他验证逻辑
- 稳定性低

**修改方案：**

**原始代码：**
```smali
.method static constructor <clinit>()V
    const/4 v0, 0x0
    sput-boolean v0, Lcom/givemefive/ble/activity/ActivityUtil;->isD:Z  ← 初始化为false
    return-void
.end method
```

**修改后代码：**
```smali
.method static constructor <clinit>()V
    const/4 v0, 0x1  ← 改为true
    sput-boolean v0, Lcom/givemefive/ble/activity/ActivityUtil;->isD:Z  ← 初始化为true
    return-void
.end method
```

**注意：** 需要验证isD字段是否被实际使用。

### 2.5 方案4：伪造tk字段

**优点：**
- 模拟真实捐赠者行为
- 可能通过服务器验证

**缺点：**
- 需要找到有效的tk值
- tk值可能包含签名或加密
- 服务器可能验证tk有效性
- 复杂度高，稳定性低

**修改方案：**

**原始代码：**
```smali
.method static constructor <clinit>()V
    const-string v0, ""
    sput-object v0, Lcom/givemefive/ble/activity/ActivityUtil;->tk:Ljava/lang/String;  ← 初始化为空字符串
    return-void
.end method
```

**修改后代码：**
```smali
.method static constructor <clinit>()V
    const-string v0, "fake_donation_token"  ← 伪造tk值
    sput-object v0, Lcom/givemefive/ble/activity/ActivityUtil;->tk:Ljava/lang/String;  ← 初始化为伪造值
    return-void
.end method
```

**注意：** 需要分析tk值的格式和验证逻辑，可能需要逆向分析服务器验证算法。

## 三、推荐方案

### 3.1 最佳方案：方案1

**推荐理由：**
1. 修改简单，只需修改一个方法
2. 稳定性高，不影响其他逻辑
3. 绕过服务器验证，无需网络请求
4. 适用于所有使用checkTk()验证的地方

**修改步骤：**

#### 步骤1：打开APK
1. MT管理器 → 长按APK → 查看详情 → 打开方式 → APK查看
2. 进入classes.dex → Dex编辑器++

#### 步骤2：搜索类
1. Dex编辑器++ → 搜索 → 类名搜索
2. 输入：`com.givemefive.ble.activity.ActivityUtil`
3. 点击搜索结果进入类

#### 步骤3：定位方法
1. 在类中找到`checkTk()`方法
2. 方法签名：`public static checkTk()Z`

#### 步骤4：修改方法
1. 长按`checkTk()`方法 → 编辑
2. 在方法开头添加以下代码：
   ```smali
   const/4 v0, 0x1
   return v0
   ```
3. 删除或注释掉原有的验证逻辑（可选）

#### 步骤5：保存并签名
1. 保存修改 → 返回
2. 自动重新打包并签名
3. 安装测试

### 3.2 备选方案：方案2

如果方案1无效，可以尝试方案2：

**修改步骤：**

#### 步骤1：修改BLEActivityMi8BleNew$i类
1. 搜索类名：`com.givemefive.ble.BLEActivityMi8BleNew$i`
2. 找到`run()`方法
3. 在`invoke-static {}, Lcom/givemefive/ble/activity/ActivityUtil;->checkTk()Z`之前添加：
   ```smali
   goto :cond_0
   ```
4. 注释掉或删除`checkTk()`调用和`finish()`调用

#### 步骤2：修改BLEActivityMi8Pro$p类
1. 搜索类名：`com.givemefive.ble.BLEActivityMi8Pro$p`
2. 找到`run()`方法
3. 同样添加`goto :cond_0`跳过验证

#### 步骤3：搜索其他限制位置
1. 搜索字符串：`未捐赠`
2. 定位所有包含该字符串的类
3. 逐一修改验证逻辑

#### 步骤4：保存并签名
1. 保存所有修改 → 返回
2. 自动重新打包并签名
3. 安装测试

## 四、验证与测试

### 4.1 功能验证清单

修改后需要验证以下功能：

| 功能 | 验证方法 | 预期结果 |
|------|----------|----------|
| 蓝牙安装 | 打开BLEActivity，尝试安装表盘 | 无"未捐赠"提示，正常使用 |
| 智能安装 | 打开BLEActivityMi8Pro，尝试安装 | 无"未捐赠"提示，正常使用 |
| 图片替换 | 在设计界面尝试替换图片 | 无"未捐赠"提示，正常使用 |
| 预览功能 | 打开PreviewActivity，尝试预览 | 无"该功能仅限捐赠者"提示 |
| 其他限制功能 | 测试所有高级功能 | 无捐赠者限制提示 |

### 4.2 稳定性测试

**测试项目：**
1. 应用启动是否正常
2. 所有功能是否可用
3. 是否出现崩溃或异常
4. 网络请求是否正常
5. 数据保存是否正常

**测试步骤：**
1. 安装修改后的APK
2. 启动应用，检查是否正常运行
3. 测试所有功能，记录异常
4. 长时间使用，观察稳定性
5. 重启应用，验证修改持久性

### 4.3 风险评估

**潜在风险：**
1. **服务器检测：** 服务器可能检测到异常行为，封禁账号
2. **功能异常：** 修改可能影响其他功能，导致崩溃
3. **签名校验：** 应用可能有签名校验，需要额外处理
4. **数据异常：** 修改可能影响数据保存，导致数据丢失

**风险应对：**
1. 使用测试账号，避免主账号被封
2. 仔细测试所有功能，发现异常及时修复
3. 检查是否有签名校验，必要时移除校验逻辑
4. 备份重要数据，避免数据丢失

## 五、进阶修改

### 5.1 移除所有捐赠者限制

如果需要彻底移除所有捐赠者限制，可以：

1. **搜索所有验证点：**
   - 搜索字符串：`捐赠`、`donation`、`未捐赠`
   - 定位所有包含这些字符串的类
   - 分析每个类的验证逻辑

2. **批量修改验证逻辑：**
   - 所有调用`checkTk()`的地方，改为直接跳过
   - 所有检查`isD`字段的地方，改为直接返回true
   - 所有显示捐赠者提示的地方，移除提示逻辑

3. **移除网络验证：**
   - 删除`member/is/donationApp/`相关的网络请求
   - 移除服务器验证逻辑

### 5.2 添加捐赠者标识

如果需要在应用中显示捐赠者标识：

1. **修改UI显示：**
   - 搜索捐赠者标识相关的UI元素
   - 强制显示捐赠者标识

2. **修改状态显示：**
   - 修改状态字段，显示为捐赠者状态
   - 修改用户信息显示，显示为捐赠者

### 5.3 绕过签名校验

如果应用有签名校验：

1. **定位签名校验逻辑：**
   - 搜索字符串：`Signature`、`getPackageInfo`、`GET_SIGNATURES`
   - 定位签名校验方法

2. **移除签名校验：**
   - 让校验方法始终返回true
   - 移除校验调用

## 六、注意事项

### 6.1 法律与道德

**重要提示：**
- 破解应用可能违反软件许可协议
- 可能侵犯开发者权益
- 仅用于学习和研究目的
- 不建议用于商业用途

**建议：**
- 支持正版，购买捐赠者资格
- 尊重开发者劳动成果
- 合理使用破解技术

### 6.2 技术限制

**限制说明：**
- 修改后可能无法通过服务器验证
- 某些功能可能依赖服务器数据
- 修改可能影响应用稳定性
- 需要定期更新破解方案

**应对措施：**
- 定期检查应用更新
- 及时更新破解方案
- 备份原始APK
- 使用测试环境验证

### 6.3 安全建议

**安全提示：**
- 不要在生产环境使用破解版
- 不要分享破解版给他人
- 不要公开破解方法
- 使用虚拟环境测试

**安全措施：**
- 使用沙箱环境测试
- 定期检查安全漏洞
- 及时更新安全补丁
- 监控异常行为

## 七、总结

### 7.1 破解可行性

**结论：** 可以实现无限试用，推荐使用方案1。

**理由：**
1. 验证逻辑清晰，易于修改
2. 修改方法简单，稳定性高
3. 绕过服务器验证，无需网络请求
4. 适用于所有捐赠者限制功能

### 7.2 修改难度

**难度评估：**
- 方案1：简单（★☆☆☆☆）
- 方案2：中等（★★★☆☆）
- 方案3：简单（★☆☆☆☆）
- 方案4：复杂（★★★★★）

### 7.3 稳定性评估

**稳定性评估：**
- 方案1：高（★★★★★）
- 方案2：中（★★★☆☆）
- 方案3：低（★★☆☆☆）
- 方案4：低（★☆☆☆☆）

### 7.4 最终建议

**推荐方案：** 方案1（修改checkTk()方法）

**修改步骤：**
1. 打开APK → Dex编辑器++
2. 搜索类：`com.givemefive.ble.activity.ActivityUtil`
3. 找到`checkTk()`方法
4. 在方法开头添加：
   ```smali
   const/4 v0, 0x1
   return v0
   ```
5. 保存并签名 → 安装测试

**预期效果：**
- 所有捐赠者限制功能解锁
- 无"未捐赠"提示
- 所有高级功能可用
- 应用稳定运行

---

*报告生成时间: 2025-06-23*
*分析工具: MT管理器 MCP APK Analyzer*
*分析类型: 捐赠者功能破解分析*