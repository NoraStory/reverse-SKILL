# 签名校验问题分析

## 问题原因

AppApplication类中有4个安全检查：

### 1. 类名包名检查 (a方法)
```smali
.method private a()Z
    # 检查类名是否为"AppApplication"
    # 检查包名是否为"com.givemefive.ble.application"
    # 如果不匹配，返回false
.end method
```

### 2. PackageManager检查 (b方法)
```smali
.method private b()Z
    # 检查PackageManager是否是系统服务
    # 检查mPM字段是否为"android.content.pm.IPackageManager$Stub$Proxy"
    # 如果不匹配，返回false
.end method
```

### 3. 签名检查 - 旧版API (c方法)
```smali
.method private c(Landroid/content/Context;)Z
    # 获取应用签名
    # 计算签名hash值
    # 检查hash是否等于 -0x7aca758a (即 0x85358a76)
    # 这是原始签名的hash值
    # 如果不匹配，返回false
.end method
```

### 4. 签名检查 - 新版API (d方法)
```smali
.method private d()Z
    # Android 9+使用SigningInfo获取签名
    # 计算签名hash值
    # 检查hash是否等于 -0x7aca758a
    # 如果不匹配，返回false
.end method
```

### onCreate方法中的检查流程
```smali
.method public onCreate()V
    # 检查1：类名包名
    invoke-direct {p0}, Lcom/givemefive/ble/application/AppApplication;->a()Z
    move-result v0
    if-nez v0, :cond_0
    return-void  ← 检查失败，不初始化
    
    # 检查2：签名（旧版）
    :cond_0
    invoke-direct {p0, v0}, Lcom/givemefive/ble/application/AppApplication;->c(Landroid/content/Context;)Z
    move-result v0
    if-nez v0, :cond_1
    return-void  ← 签名检查失败
    
    # 检查3：PackageManager
    :cond_1
    invoke-direct {p0}, Lcom/givemefive/ble/application/AppApplication;->b()Z
    move-result v0
    if-nez v0, :cond_2
    return-void  ← 检查失败
    
    # 检查4：签名（新版）
    :cond_2
    invoke-direct {p0}, Lcom/givemefive/ble/application/AppApplication;->d()Z
    move-result v0
    if-nez v0, :cond_3
    return-void  ← 签名检查失败
    
    # 所有检查通过，才初始化应用
    :cond_3
    invoke-super {p0}, Lio/dcloud/application/DCloudApplication;->onCreate()V
    ...
.end method
```

## 问题分析

**签名hash值对比：**
- 原始签名hash：`-0x7aca758a` (即 `0x85358a76`)
- 测试签名hash：不匹配（因为使用了Android测试签名）

**签名信息对比：**
- 原始签名：CN=pingx.tech
- 测试签名：CN=Android (Android测试签名)

**结果：**
签名检查失败，应用不初始化，显示"application配置有误"提示。

## 解决方案

### 方案1：修改签名检查方法（推荐）

修改 `c()` 和 `d()` 方法，让它们始终返回true。

**修改c方法：**
```smali
.method private c(Landroid/content/Context;)Z
    .registers 5
    
    const/4 v0, 0x1  ← 直接返回true
    return v0
    
    # 保留原始代码（可选）
    # const/4 v0, 0x0
    # :try_start_0
    # ... 签名检查逻辑 ...
    # const v1, -0x7aca758a
    # if-ne v1, p1, :cond_0
    # const/4 v0, 0x1
    # :cond_0
    # return v0
.end method
```

**修改d方法：**
```smali
.method private d()Z
    .registers 5
    
    const/4 v0, 0x1  ← 直接返回true
    return v0
    
    # 保留原始代码（可选）
    # const/4 v0, 0x0
    # :try_start_0
    # ... 签名检查逻辑 ...
    # const v2, -0x7aca758a
    # if-ne v2, v1, :cond_1
    # const/4 v0, 0x1
    # :cond_1
    # return v0
.end method
```

### 方案2：修改onCreate方法

跳过所有检查，直接初始化。

```smali
.method public onCreate()V
    .registers 2
    
    # 跳过所有检查，直接初始化
    invoke-super {p0}, Lio/dcloud/application/DCloudApplication;->onCreate()V
    invoke-static {}, Lx4/c;->d()Lx4/c;
    move-result-object v0
    invoke-virtual {v0, p0}, Lx4/c;->f(Landroid/content/Context;)V
    return-void
    
    # 保留原始检查代码（可选）
    # invoke-direct {p0}, Lcom/givemefive/ble/application/AppApplication;->a()Z
    # move-result v0
    # if-nez v0, :cond_0
    # return-void
    # ...
.end method
```

### 方案3：使用原始签名

使用原始签名重新打包，但这需要原始签名的私钥，我们无法获取。

## 推荐方案

**推荐使用方案1：修改签名检查方法**

**优点：**
- 只修改签名检查，不影响其他安全机制
- 稳定性高，不会影响应用其他功能
- 修改简单，只需修改2个方法

**修改步骤：**
1. 打开APK → 启动编辑会话
2. 搜索类：`com.givemefive.ble.application.AppApplication`
3. 修改 `c()` 方法：直接返回true
4. 修改 `d()` 方法：直接返回true
5. 检查修改 → 构建APK → 保存

**预期效果：**
- 签名检查通过
- 应用正常初始化
- 无"application配置有误"提示
- 所有功能正常使用