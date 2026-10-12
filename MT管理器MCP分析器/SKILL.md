---
name: MT管理器APK分析
description: "MT管理器MCP服务专用APK分析技能。基于MT管理器的mt_mcp服务对APK文件进行深度分析（支付功能、敏感字符串、类结构、资源等），生成结构化分析报告。当用户需要分析APK时触发此技能。"
---

# MT管理器MCP APK分析技能

基于 mt_mcp 服务分析 APK,支持只读分析和编辑重打包。**根据用户需求动态分析,不预设固定流程。**

## 核心流程

**必须先 `mt_apk_open`** → 获取 `workspaceId` → 后续所有工具都需要此 ID。

### 只读分析工具

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `mt_apk_open` | 打开 APK,获取 workspaceId | path, temporary |
| `mt_apk_list_available_apks` | 列出可用 APK 文件 | prefix, limit |
| `mt_apk_list` | 浏览 ZIP/DEX类/资源表 | workspaceId, editSessionId, view, prefix, limit |
| `mt_apk_outline_class` | 查看类结构(字段+方法) | workspaceId, editSessionId, locator, limit |
| `mt_apk_search` | 搜索关键词/代码/字符串 | workspaceId, editSessionId, target, query, queryType |
| `mt_apk_read_text` | 读取 Smali/XML/文本 | workspaceId, editSessionId, locator, limit, maxChars |
| `mt_apk_read_resource` | 批量读取资源值 | workspaceId, editSessionId, reads[], maxValueXmlChars |
| `mt_apk_read_zip_bytes` | 读取 ZIP 原始字节(十六进制) | workspaceId, editSessionId, locator, byteOffset, maxBytes |
| `mt_apk_xref_dex` | DEX 交叉引用(方法/字段/类调用者) | workspaceId, editSessionId, locator, methodResolution, limit |
| `mt_apk_xref_resource` | 资源引用查询 | workspaceId, editSessionId, locator, scopes, limit |
| `mt_apk_continue` | 翻页 | workspaceId, editSessionId, nextCursor, limit |

### 编辑流程工具

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `mt_apk_edit_open` | 创建编辑会话 → editSessionId | workspaceId |
| `mt_apk_edit_text` | 编辑 Smali/AXML/ZIP文本 | workspaceId, editSessionId, locator, targetVersion, edits[] |
| `mt_apk_edit_resource` | 编辑资源值 | workspaceId, editSessionId, edits[] |
| `mt_apk_edit_check` | 检查编辑/构建可行性 | workspaceId, editSessionId, runBuildChecks |
| `mt_apk_build` | 构建并签名 APK | workspaceId, editSessionId, outputName, overwrite |
| `mt_apk_close` | 关闭临时工作区(temporary=true) | workspaceId |

---

## 关键规则

### Locator 格式(字符串,非 JSON)

```
dex_class:Lcom/example/Foo;
dex_method:Lcom/example/Foo;->bar()V
dex_field:Lcom/example/Foo;->flag:Z
zip_entry:assets/config.json
axml:AndroidManifest.xml
resource:0x7f010000
```

Dalvik 类名格式:`L` 前缀 + `/` 替换 `.` + `;` 后缀(如 `Lcom/example/MyClass;`)。

### editSessionId 规则

- 读取基础工作区:传 `""`(空字符串)
- 读取/编辑编辑会话:传 `mt_apk_edit_open` 返回的 ID
- 所有 list/search/read/xref/continue 工具都需要此参数

### 通用必填参数

所有工具的参数均为必填(无可选参数)。常用默认值:
- `limit=50`(搜索/xref) / `200`(list/outline) / `500`(read_text)
- `maxChars=49152` / `maxBytes=256`
- `prefix=""` 表示无过滤

---

## 搜索 target 选择器

`mt_apk_search` 用 `target`(单值枚举)选择搜索范围:

| target | 搜索内容 | 最佳用途 |
|--------|----------|----------|
| `overview` | ZIP路径+AXML+资源ID/名称/值+DEX名称+DEX字符串 | 未知目标的广搜(不含smali) |
| `files` | ZIP路径+解码AXML文本 | 搜索清单/布局/文件路径 |
| `resource_table_names` | 资源ID/名称 | 按名称查找资源 |
| `resource_table_values` | 解码资源值 | 查找字符串资源值 |
| `resource_table_file_paths` | 指向ZIP路径的资源值 | 查找引用文件路径的资源 |
| `dex_names` | 类/字段/方法名称 | 按名称查DEX实体 |
| `dex_strings` | DEX字符串字面量(按类分组) | 硬编码文本、URL、密钥 |
| `dex_string_members` | DEX字符串字面量(按成员分组) | 字符串使用详情 |
| `smali` | 完整Smali反汇编文本 | 指令模式、字段访问、调用 |

**prefix 参数(因 target 而异):** `overview` 必须为 `""`;`files` 用 ZIP路径前缀;`resource_table_*` 用 `0x7f..`/`type/name`/`name`;`dex_*`/`smali` 用类所有者前缀(Java包名/斜杠/L前缀)。

---

## 工具参数详解

### mt_apk_open

| 参数 | 说明 |
|------|------|
| path | `"mt://current-apk"` / `"mt://workspace/<id>"`(重开) / `list_available_apks` 返回的相对路径 |
| temporary | `true`=一次性(可close删除);`false`=可复用/重开/长期保留 |

返回 `workspaceId`、`apkFileName`、`compact.manifest.package/versionName/versionCode`、`compact.count.*`、`compact.capability.*`。

### mt_apk_list

| view | prefix 格式 | 返回 |
|------|----------|------|
| `zip_entries` | `"res/layout/"` | zip_entry 定位器 |
| `dex_classes` | `"Lcom/example/"` 或 `"com.example"` | dex_class 定位器(传给 outline_class) |
| `resource_table` | `"0x7f010000"` / `"string/"` / `"app_name"` | resource 定位器 + 轻量值预览 |

### mt_apk_outline_class

传入 `dex_class:Lcom/example/Foo;` 定位器,返回 `header`(className/super/implements/source/access) + `fields[]`(name/sig/access/locator) + `methods[]`(name/sig/access/interestingStrings/locator)。

### mt_apk_read_text

| locator 前缀 | 读取内容 | 可编辑 |
|------------|---------|-------|
| `zip_entry:` | ZIP文件文本 | ✓(非 resources.arsc) |
| `axml:` | 解码后的 Android XML | ✓ |
| `dex_class:` | 完整类 Smali 源码 | ✓ |
| `dex_method:` | 单方法 Smali | ✓ |
| `dex_field:` | 字段定义 Smali | ✗(只读) |

参数:`limit`(行数,max 2000)、`maxChars`(max 131072)、`startLine`/`startColumn`(0-based)。返回 `textWindow.text` + `targetVersion`(**编辑时必需**)。

### mt_apk_read_resource

批量读取(1-200个),每个 read 含 `locator`(如 `resource:0x7f010000`) + `variant`(如 `default`)。
预算参数:`maxValueChars=4096` / `maxValueXmlChars=32768` / `maxItemsPerValue=50` / `resolveDepth=0`。
返回 `results[].value`(摘要) + `results[].valueXml`(完整可编辑XML) + `results[].targetVersion`。

### mt_apk_xref_dex

查找方法/字段/类的调用者。`methodResolution` 模式:
- `dispatch`(推荐,用于 dex_method):查找可能到达目标的调用
- `exact`:精确匹配 MethodReference
- `slot`:查找可见重写族
- `not_applicable`(用于 dex_field/dex_class):字段/类只支持精确引用

### mt_apk_edit_text

**必须先 `read_text` 获取 `targetVersion`。** `edits[]` 每项含 `mode`/`matchText`/`writeText`:

| mode | 说明 | matchText | writeText |
|------|------|-----------|-----------|
| `write_target` | 替换整个目标/创建新目标(`targetVersion="missing"`) | "" | 完整内容 |
| `delete_target` | 删除整个目标 | "" | "" |
| `replace_match` | 替换匹配文本(空writeText=删除) | 原文本 | 新文本 |
| `insert_before_match` | 在匹配前插入 | 匹配文本 | 插入文本 |
| `insert_after_match` | 在匹配后插入 | 匹配文本 | 插入文本 |

`matchText` 必须在目标中**恰好出现一次**;多次匹配返回 `TEXT_MATCH_AMBIGUOUS`,需用更长上下文重试。单个 locator 的多个编辑是原子操作。

### mt_apk_edit_resource

**必须先 `read_resource` 获取 `locator`/`variant`/`targetVersion`/`valueXml`。** 每次 1-200 项(推荐约20)。不能修改根元素名称/资源ID/变体,不能创建新资源。

### mt_apk_build

`outputName=""` 用默认名 `<原文件名>_mcp_<editSessionId>_sign.apk`(始终覆盖);非空时若文件存在且 `overwrite=false` 返回 `OUTPUT_ALREADY_EXISTS`。输出到 MCP 配置目录,源 APK 不变。

---

## 搜索模式速查

| 目标 | target | queryType | query 示例 |
|------|--------|-----------|-------|
| API URL | `dex_strings` | regex | `https?://[a-zA-Z0-9._/-]+` |
| 按名称查类/方法/字段 | `dex_names` | literal | `onClick` |
| 枚举类 | `dex_names` | regex | `.*Status$\|.*Type$` |
| 静态字段读取 | `smali` | regex | `sget-object.*->FIELD:Lcom/target/.*;` |
| 字段写入 | `smali` | regex | `sput-object\|iput-object.*->FIELD:` |
| 方法调用 | `smali` | regex | `invoke-virtual.*->methodName` |
| 构造函数 | `smali` | regex | `invoke-direct.*-><init>` |
| 字符串常量 | `smali` | regex | `const-string.*"target text"` |
| 字符串资源 | `resource_table_values` | literal | `error_message` |
| 权限/Manifest | `files` | literal | `android.permission` |
| 包范围搜索 | 任意 | 任意 | 任意 + prefix="com/example/pkg" |
| 广搜(未知目标) | `overview` | literal | `keyword` |

> `query` 始终必填。`overview` 模式下 `prefix` 必须为 `""`。`target="smali"` 时 `matchMode` 不能用 `exact`。

---

## 工作流模板

> 省磁盘铁律：纯分析/只读任务一律用 `open(temporary=true)`，完成后 `mt_apk_close(workspaceId)` 释放。
> 只有要反复重开同一 APK 或要编辑打包才用 `temporary=false`。否则 `Android/data/bin.mt.plus*/mcp/` 会堆到好几 GB。

### T1: APK 架构概览

```
1. open(path="mt://current-apk", temporary=true) → workspaceId + manifest
2. read_text(locator="axml:AndroidManifest.xml", editSessionId="", ...) → 组件/权限
3. outline_class(locator="dex_class:<AppClass>", editSessionId="", ...) → 初始化流程
4. search(target="dex_strings", query="http|https|wss", queryType="regex", prefix="", ...) → API域名
5. search(target="dex_strings", query="Retrofit|OkHttp|Glide", prefix="", ...) → 第三方框架
6. list(view="dex_classes", prefix=<mainPkg>, editSessionId="", limit=1) → 主包类数量7. close(workspaceId) → 分析完释放临时工作区（省磁盘）```

### T2: 定位特定功能/字段

```
1. search(target="overview", query="keyword", prefix="", limit=20, ...) → 找引用关键词的类
2. outline_class(locator="dex_class:<hitClass>", editSessionId="", ...) → 理解类结构
3. read_text(locator=<hit.locator>, editSessionId="", maxChars=50000, ...) → 读完整Smali
4. search(target="dex_names", query="fieldName", prefix="relevant/pkg", ...) → 包范围内查同名字段
5. search(target="smali", query="sget.*fieldName|iget.*fieldName", queryType="regex", prefix="", ...) → 追踪字段访问
```

### T3: 网络配置分析

```
1. search(target="dex_names", query="BaseUrl|ApiHost|ServerConfig", queryType="regex", prefix="", ...) → 找配置类
2. read_text(locator="dex_class:<configClass>", editSessionId="", ...) → 提取域名
3. search(target="dex_strings", query="https?://[a-zA-Z0-9._-]+", queryType="regex", prefix="", limit=30, ...) → 提取URL
4. search(target="files", query="network_security_config", prefix="", ...) → 找安全配置文件
5. read_text(locator="axml:res/xml/network_security_config.xml", editSessionId="", ...) → 读安全策略
```

### T4: 安全分析

```
1. read_text(locator="axml:AndroidManifest.xml", editSessionId="", ...) → 权限声明
2. search(target="files", query="CAMERA|RECORD_AUDIO|ACCESS_FINE_LOCATION", queryType="regex", prefix="", ...) → 敏感权限
3. search(target="dex_strings", query="encrypt|decrypt|cipher|AES|RSA", prefix="", ...) → 加密操作
4. search(target="dex_names", query="KeyStore|Cipher|Signature", prefix="", ...) → 安全相关类
5. search(target="dex_strings", query="WebView|loadUrl|javascript", prefix="", ...) → WebView使用
```

### T5: 追踪方法调用链

```
1. outline_class(locator="dex_class:<targetClass>", editSessionId="", ...) → 找方法签名
2. xref_dex(locator="dex_method:<targetClass>-><methodSig>", methodResolution="dispatch", editSessionId="", ...) → 找调用者(推荐dispatch)
3. read_text(locator=<caller.sourceLocator>, editSessionId="", ...) → 读调用上下文
4. search(target="smali", query="invoke.*targetClass;->methodName", queryType="regex", prefix="", ...) → 追踪invoke模式
```

### T6: 编辑修改 APK

```
1. open(path=..., temporary=true) → workspaceId
2. edit_open(workspaceId) → editSessionId
3. read_text(locator="dex_method:...", editSessionId=<editSessionId>, ...) → 获取 targetVersion
4. edit_text(locator=..., targetVersion=..., edits=[{mode:"replace_match", matchText:"const/4 v0, 0x0", writeText:"const/4 v0, 0x1"}], ...) → 修改
5. edit_check(workspaceId, editSessionId, runBuildChecks=true) → 验证构建
6. build(workspaceId, editSessionId, outputName="", overwrite=false) → 构建签名APK
7. close(workspaceId) → 释放临时工作区(可选)
```

---

## 分析场景速查

**功能定位关键词:**

| 场景 | 关键词 | target | 包范围 prefix |
|------|--------|--------|------------|
| 支付 | payment, pay, purchase, order, alipay, wechatpay | dex_strings | 主包 |
| 会员/VIP | vip, premium, member, subscribe, isVip | dex_strings + dex_names | 主包 |
| 登录认证 | login, auth, token, session, credential, oauth | dex_strings | 主包 |
| 网络请求 | http, retrofit, okhttp, api, baseUrl | dex_strings + dex_names | 主包 |
| 数据存储 | sqlite, room, sharedpreferences, database, dao | dex_names | 主包 |
| 推送 | push, fcm, jpush, xiaomi_push, notification | dex_strings | 主包 |
| 广告 | ad, banner, interstitial, reward, admob | dex_strings | 主包 |

**安全审计关键词:**

| 场景 | 关键词 | target |
|------|--------|--------|
| 敏感信息泄露 | password, secret, key, token, api_key | dex_strings |
| 硬编码URL | `https?://[a-zA-Z0-9._-]+` (regex) | dex_strings |
| 加密算法 | AES, RSA, MD5, SHA, Cipher, encrypt | dex_strings + smali |
| 危险权限 | CAMERA, RECORD_AUDIO, READ_PHONE, ACCESS_FINE_LOCATION | files (AXML) |
| WebView风险 | loadUrl, addJavascriptInterface, setJavaScriptEnabled | smali |
| 组件暴露 | exported="true", intent-filter | files (AXML) |

> **大型 APK 优化:** 先 `read_text(axml:AndroidManifest.xml)` 获取包名,再用 `prefix=主包名` 限定搜索范围,排除第三方库(占60-80%代码)。

---

## 进阶分析策略

**锚点扩散法** — 从已知字符串定位功能代码:
```
search(target="dex_strings", query="已知字符串") → 锚点类
→ outline_class(locator="dex_class:<锚点类>") → 了解结构
→ search(target="smali", query="<锚点类Dalvik名>", queryType="regex") → 找引用者
→ 对引用者重复上述步骤,绘制调用关系图
```

**字段生命周期追踪** — 理解状态变量读写:
```
search(target="dex_names", query="isVip") → 找字段定义
→ search(target="smali", query="iget.*isVip|sget.*isVip", queryType="regex") → 读取点
→ search(target="smali", query="iput.*isVip|sput.*isVip", queryType="regex") → 写入点
→ read_text(写入点方法) → 理解赋值逻辑
```

**方法调用链追踪** — 推荐用 xref_dex 而非 smali 搜索:
```
outline_class → 找方法签名
→ xref_dex(locator="dex_method:...", methodResolution="dispatch") → 精确找调用者
→ read_text(caller.sourceLocator) → 读调用上下文
```
`dispatch` 模式能找到接口/抽象方法的所有实现调用,比 smali regex 搜索更准。

**资源反查代码** — 从 UI 资源反推逻辑:
```
search(target="resource_table_names", query="btn_purchase") → 资源ID
→ xref_resource(locator="resource:0x7f...", scopes=["dex","axml","resource_table"]) → 找引用
→ outline_class(引用类) → 找事件处理方法
```

---

## 混淆与反混淆

**混淆特征:** 短类名(a/b/c)、短方法名、短字段名、`source="Unknown"`。

**反混淆策略(按可靠性排序):**
1. **字符串常量** — 混淆不改字符串: `search(target="dex_strings", query="已知文本")` 定位锚点
2. **类层次** — `outline_class` 检查 `header.super`/`implements` 中的已知框架类
3. **框架API** — `search(target="smali", query="Landroid/widget/TextView;->setText")` 找UI代码
4. **资源引用** — `search(target="smali", query="R.string.xxx")` 找资源使用者
5. **入口点** — 从 Manifest 的 Activity 类名追踪

多 DEX 透明处理,搜索自动覆盖所有 DEX。

---

## 架构模式识别

先 `list(view="dex_classes", prefix=主包)` 浏览包结构,判断架构后定向搜索:

| 架构 | 包名特征 | 业务逻辑所在层 |
|------|---------|------------|
| MVVM | `.ui.` `.viewmodel.` `.repository.` | ViewModel |
| MVP | `.presenter.` `.view.` `.contract.` | Presenter |
| Clean | `.domain.` `.data.` `.presentation.` | UseCase/Interactor |
| MVI | `.intent.` `.state.` `.reducer.` | Reducer |

看到 `ui/main/viewmodel/` 目录 → MVVM → VIP逻辑在 `MainViewModel`。

---

## 防御机制识别与绕过

分析时先识别防御机制,修改方案才可行:

| 防御类型 | 识别关键词 | 绕过Smali修改 |
|---------|-----------|-------------|
| 签名校验 | getPackageInfo, GET_SIGNATURES, signatures | 校验方法 `const/4 v0, 0x1` + `return v0` |
| Root检测 | "/su", "Superuser", "isRooted", Magisk | 检测方法 `const/4 v0, 0x0` + `return v0` |
| 模拟器检测 | goldfish, nox, isEmulator, genymotion | 同Root,返回false |
| 调试检测 | isDebuggerConnected, TracerPid | 移除调用或返回false |
| 完整性校验 | CRC32, MessageDigest, checksum | 校验方法返回true |
| Hook检测 | Xposed, frida-server, substrate | 检测方法返回false |

**绕过要点:** 用 `edit_text` 的 `replace_match` 修改条件跳转(`if-eq`→`if-ne`)或方法返回值。多种防御可能分散在不同类,需全面搜索逐一处理。

---

## Dalvik/Smali 速查

**类型映射:** `V`void `Z`boolean `I`int `J`long `F`float `D`double `B`byte `C`char `S`short / `Lcom/pkg/Cls;`类 `[I`int[] `[Ljava/lang/String;`String[]

**方法签名:** `name(ParamTypes)ReturnType` — `onCreate(Landroid/os/Bundle;)V` / `isVip()Z` / `getName(I)Ljava/lang/String;`

**字段访问:**
```
sget-object v0, LCls;->FIELD:LType;   # 读静态字段
sput-object v0, LCls;->FIELD:LType;   # 写静态字段
iget-object v0, v1, LCls;->FIELD:LType;  # 读实例字段(v1=对象)
iput-object v0, v1, LCls;->FIELD:LType;  # 写实例字段
```

**方法调用:**
```
invoke-virtual {v0,v1}, LCls;->method(I)V      # 实例方法
invoke-static {v0}, LCls;->staticMethod(I)I     # 静态方法
invoke-interface {v0}, LIfc;->method()V         # 接口方法
invoke-direct {v0,v1}, LCls;-><init>(I)V        # 构造函数/private
```

**控制流(常见修改点):**
```
if-eqz v0, :label    # v0==null跳转  → 改 if-nez 反转逻辑
if-nez v0, :label    # v0!=null跳转  → 改 if-eqz 反转逻辑
const/4 v0, 0x0      # false          → 改 0x1 为 true
const/4 v0, 0x1      # true           → 改 0x0 为 false
return v0            # 返回值
return-void          # 提前返回(移除广告/跳过校验)
```

**常见修改模式:**
| 需求 | 修改方法 |
|------|---------|
| 跳过VIP验证 | `if-eq` → `if-ne` 或方法直接 `const/4 v0, 0x1` + `return v0` |
| 解锁付费功能 | 状态检查返回 true |
| 移除广告 | 广告加载方法开头加 `return-void` |
| 绕过登录 | 登录状态检查返回 true |
| 禁用更新 | 版本比较逻辑反转 |

---

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| Invalid target | target 非枚举值 | 用 `overview`/`files`/`dex_names`/`dex_strings`/`dex_string_members`/`smali`/`resource_table_*` 之一 |
| Class not found | locator 非 Dalvik 格式 | 用 `dex_class:Lcom/example/Cls;` 而非 `com.example.Cls` |
| Unsupported locator | locator 前缀错误 | read_text 接受 `zip_entry:`/`axml:`/`dex_class:`/`dex_method:`/`dex_field:`;read_resource 接受 `resource:` |
| Missing required field | 缺少必填参数 | 所有参数必填,基础工作区 editSessionId 传 `""` |
| Data truncated | 输出过大 | 增大 maxChars(max 131072) / 用 startLine+limit / 用 continue |
| exact + smali 冲突 | target=smali 且 matchMode=exact | target="smali" 时用 matchMode="contains" |
| TEXT_MATCH_AMBIGUOUS | edit_text matchText 多次匹配 | 提供更长上下文使 matchText 唯一 |
| NOT_TEXT_ENTRY | read_text 读二进制条目 | 改用 mt_apk_read_zip_bytes |
| Stale targetVersion | 编辑时版本号过期 | 重新 read_text/read_resource 获取 targetVersion |
| OUTPUT_ALREADY_EXISTS | build 时文件已存在 | 传 overwrite=true 或换 outputName |

错误码:4401=参数校验错误,400=业务逻辑错误。检查 `recoverable`/`retrySameArguments` 标志和 `nextActions` 数组。

---

## 分页与返回结构

所有调用返回 `{ok, data, error, nextActions}`。当 `pagination.hasMore=true` 时,从 `nextActions[].arguments` 复制 `workspaceId`/`editSessionId`/`nextCursor`/`limit` 调用 `mt_apk_continue`。**游标不透明,不要解析/构造/修改。**

`mt_apk_list_available_apks` 续页时:`workspaceId="available_apks"`, `editSessionId=""`。

## APK 匹配

`mt_apk_open` 的 path 支持模糊匹配:
- `"mt://current-apk"` → 当前APK
- `"com.tencent.mm"` → 包名匹配
- `"微信"` / `"kwyy"` → 模糊匹配文件名或包名
- `"a.apk"` → 精确匹配

若返回 `CURRENT_APK_NOT_AVAILABLE`,先调 `mt_apk_list_available_apks` 获取列表再选择。多匹配时列出结果让用户选择。
