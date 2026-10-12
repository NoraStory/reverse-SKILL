# MT MCP APK 分析服务使用文档

## 服务信息

- 服务名称: mt_mcp
- 服务地址: 配置于 `.trae/mcp.json`
- 功能: APK 文件分析与解析

---

## 方法列表

### 1. mt_apk_open - 打开 APK 工作区

打开一个 APK 文件进行分析，返回工作区 ID 和基本信息。

#### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| path | string | 是 | APK 路径，使用 `mt://current-apk` 打开当前 APK，或使用相对路径 |
| workspaceId | string | 否 | 已存在的工作区 ID，用于重新打开 |
| reuseWorkspaceByPath | boolean | 否 | 是否复用相同 APK 的已有工作区，默认 true |

#### 示例

```json
{
  "path": "mt://current-apk"
}
```

#### 返回

```json
{
  "workspaceId": "crf71js2",
  "apkFileName": "a.apk",
  "packageName": "com.example.app",
  "versionName": "1.0.0",
  "versionCode": "100",
  "minSdk": "21",
  "targetSdk": "34",
  "appLabel": "Example App",
  "counts": {
    "zipEntries": 4462,
    "dexEntries": 3,
    "xmlEntries": 3133,
    "classes": 31521
  },
  "capabilities": {
    "canReadAxml": true,
    "canSearchDexNames": true,
    "canSearchDexStrings": true,
    "canReadResourceTable": true
  },
  "nextActions": [
    {
      "tool": "mt_apk_read",
      "purpose": "inspect",
      "description": "Read decoded AndroidManifest.xml",
      "arguments": {
        "workspaceId": "crf71js2",
        "locator": { "kind": "axml", "path": "AndroidManifest.xml" }
      }
    }
  ]
}
```

#### 返回字段说明

| 字段 | 说明 |
|------|------|
| workspaceId | 工作区 ID，后续操作必需 |
| apkFileName | APK 文件名 |
| packageName | 包名 |
| versionName | 版本名 |
| versionCode | 版本号 |
| minSdk | 最低 SDK 版本 |
| targetSdk | 目标 SDK 版本 |
| appLabel | 应用名称 |
| counts | 各类条目数量统计 |
| capabilities | 服务能力标识 |
| nextActions | 推荐的下一步操作 |

---

### 2. mt_apk_list - 列出 APK 内容

分页列出 APK 的各类内容：ZIP 条目、DEX 类、类大纲、资源表条目。

#### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| workspaceId | string | 是 | 工作区 ID |
| view | string | 是 | 视图类型，见下表 |
| limit | integer | 否 | 每页数量，默认 200，最大 1000 |
| prefix | string | 否 | 前缀过滤 |
| className | string | 条件 | 类名，view=dex_class_outline 时必填 |

#### view 类型

| 值 | 说明 |
|----|------|
| zip_entries | ZIP 文件条目列表 |
| dex_classes | DEX 类列表 |
| dex_class_outline | 类大纲（字段和方法），需指定 className |
| resource_table_entries | 资源表条目列表 |

#### 示例 - 列出 DEX 类

```json
{
  "workspaceId": "crf71js2",
  "view": "dex_classes",
  "limit": 200,
  "prefix": "com/example"
}
```

#### 返回 - DEX 类列表

```json
{
  "workspaceId": "crf71js2",
  "view": "dex_classes",
  "data": [
    {
      "locator": { "kind": "dex_class", "className": "Lcom/example/MainActivity;" },
      "javaName": "com.example.MainActivity",
      "fieldCount": 4,
      "methodCount": 20
    }
  ],
  "pagination": {
    "hasMore": true,
    "returnedCount": 10,
    "limitMax": 1000,
    "totalAvailableCount": 4186,
    "nextCursor": "AwEK6AcCC2NvbS9hcGtwdXJlCoxO"
  },
  "nextActions": [
    {
      "tool": "mt_apk_continue",
      "purpose": "continue",
      "description": "Continue listing next page",
      "arguments": { "workspaceId": "crf71js2", "nextCursor": "xxx", "limit": 10 }
    }
  ]
}
```

#### 示例 - 查看类大纲

```json
{
  "workspaceId": "crf71js2",
  "view": "dex_class_outline",
  "className": "Lcom/example/MainActivity;"
}
```

#### 返回 - 类大纲

```json
{
  "workspaceId": "crf71js2",
  "view": "dex_class_outline",
  "locator": { "kind": "dex_class", "className": "Lcom/example/MainActivity;" },
  "javaName": "com.example.MainActivity",
  "header": {
    "className": "Lcom/example/MainActivity;",
    "javaName": "com.example.MainActivity",
    "implements": [],
    "class": ".class public final Lcom/example/MainActivity;",
    "super": "Ljava/lang/Object;",
    "source": "MainActivity.kt"
  },
  "fields": [
    {
      "name": "banners",
      "sig": "banners:Ljava/util/List;",
      "access": "private final",
      "classSmaliStartLine": 68,
      "classSmaliEndLine": 76,
      "lineCount": 9,
      "locator": { "kind": "dex_field", "className": "Lcom/example/MainActivity;", "fieldSig": "banners:Ljava/util/List;" }
    }
  ],
  "methods": [
    {
      "name": "getBanners",
      "sig": "getBanners()Ljava/util/List;",
      "access": "public final",
      "classSmaliStartLine": 407,
      "classSmaliEndLine": 423,
      "lineCount": 17,
      "instructionCount": 2,
      "stringRefCount": 0,
      "resourceRefCount": 0,
      "invokeCount": 0,
      "interestingStrings": [],
      "interestingInvokes": [],
      "locator": { "kind": "dex_method", "className": "Lcom/example/MainActivity;", "methodSig": "getBanners()Ljava/util/List;" }
    }
  ],
  "membersReturned": 26,
  "totalMembers": 26
}
```

#### 类大纲方法字段说明

| 字段 | 说明 |
|------|------|
| instructionCount | 指令数量 |
| stringRefCount | 字符串引用数量 |
| resourceRefCount | 资源引用数量 |
| invokeCount | 方法调用数量 |
| interestingStrings | 有意义的字符串常量 |
| interestingInvokes | 有意义的方法调用 |

---

### 3. mt_apk_read - 读取内容

读取指定定位器指向的内容。

#### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| workspaceId | string | 是 | 工作区 ID |
| locator | object | 是 | 定位器对象 |
| limit | integer | 否 | 行数限制，默认 500，最大 2000 |
| maxChars | integer | 否 | 字符数限制，默认 49152，最大 131072 |
| includeLineNumbers | boolean | 否 | 是否包含行号，默认 false |
| format | string | 否 | 格式，text 或 hex（仅 zip_entry） |
| startLine | integer | 否 | 起始行号（从 1 开始） |
| startColumn | integer | 否 | 起始列号（从 1 开始） |
| maxBytes | integer | 否 | hex 格式时的字节数限制，默认 256，最大 4096 |
| hexOffset | integer | 否 | hex 格式时的字节偏移 |
| perValueTextMaxChars | integer | 否 | 资源表条目每个值的最大字符数，默认 4096 |
| valueOffset | integer | 否 | 资源表条目值偏移 |

#### locator 类型

| kind | 必填字段 | 说明 |
|------|----------|------|
| zip_entry | path | ZIP 条目路径 |
| axml | path | Android XML 路径 |
| dex_class | className | 类名（描述符格式） |
| dex_method | className, methodSig | 类名 + 方法签名 |
| dex_field | className, fieldSig | 类名 + 字段签名 |
| resource_table_entry | resourceTableId | 资源表 ID |

#### 示例 - 读取 AndroidManifest

```json
{
  "workspaceId": "crf71js2",
  "locator": {
    "kind": "axml",
    "path": "AndroidManifest.xml"
  }
}
```

#### 示例 - 读取类代码

```json
{
  "workspaceId": "crf71js2",
  "locator": {
    "kind": "dex_class",
    "className": "Lcom/example/MainActivity;"
  }
}
```

#### 示例 - 读取方法代码

```json
{
  "workspaceId": "crf71js2",
  "locator": {
    "kind": "dex_method",
    "className": "Lcom/example/MainActivity;",
    "methodSig": "onCreate(Landroid/os/Bundle;)V"
  }
}
```

#### 示例 - 读取资源表条目

```json
{
  "workspaceId": "crf71js2",
  "locator": {
    "kind": "resource_table_entry",
    "resourceTableId": "0x7f010000"
  }
}
```

#### 示例 - 以 HEX 格式读取 ZIP 条目

```json
{
  "workspaceId": "crf71js2",
  "locator": {
    "kind": "zip_entry",
    "path": "AndroidManifest.xml"
  },
  "format": "hex",
  "maxBytes": 100
}
```

#### 示例 - 带行号读取

```json
{
  "workspaceId": "crf71js2",
  "locator": {
    "kind": "dex_method",
    "className": "Lcom/example/MainActivity;",
    "methodSig": "onCreate(Landroid/os/Bundle;)V"
  },
  "includeLineNumbers": true
}
```

#### 示例 - 从指定行开始读取

```json
{
  "workspaceId": "crf71js2",
  "locator": {
    "kind": "axml",
    "path": "AndroidManifest.xml"
  },
  "startLine": 100,
  "limit": 20
}
```

---

### 4. mt_apk_search - 搜索内容

在 APK 中搜索指定内容。

#### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| workspaceId | string | 是 | 工作区 ID |
| query | string | 是 | 搜索查询 |
| queryType | string | 是 | 查询类型：literal 或 regex |
| caseSensitive | boolean | 是 | 是否区分大小写 |
| scopes | string/array | 是 | 搜索范围，见下表（多范围用 JSON 数组） |
| limit | integer | 否 | 结果数量限制，默认 50，最大 200 |
| matchMode | string | 否 | 匹配模式：contains 或 exact |
| includeSnippet | boolean | 否 | 是否包含代码片段，默认 true |
| includeMatchOffsets | boolean | 否 | 是否包含匹配位置信息，默认 false |
| classPrefix | string | 否 | 类前缀过滤（DEX 相关范围） |
| zipEntryPrefix | string | 否 | ZIP 条目前缀过滤 |
| resourceTableTypes | string | 否 | 资源表类型过滤（如 layout、anim） |
| dexStringGranularity | string | 否 | dex_string 范围的粒度：class 或 member |
| snippetMaxChars | integer | 否 | 代码片段最大字符数，默认 240，最大 1000 |

#### scopes 类型

| 值 | 说明 |
|----|------|
| zip_entries | ZIP 条目路径 |
| axml | 解码后的 Android XML |
| resource_table_id | 资源表 ID |
| resource_table_name | 资源表名称 |
| resource_table_value | 资源表值 |
| dex_class | DEX 类名 |
| dex_field | DEX 字段名 |
| dex_method | DEX 方法名 |
| dex_string | DEX 字符串值（字面量） |
| smali | Smali 反汇编代码 |

#### 示例 - 搜索字符串

```json
{
  "workspaceId": "crf71js2",
  "query": "payment",
  "queryType": "literal",
  "caseSensitive": false,
  "scopes": "dex_string"
}
```

#### 示例 - 多范围搜索

```json
{
  "workspaceId": "crf71js2",
  "query": "config",
  "queryType": "literal",
  "caseSensitive": false,
  "scopes": ["dex_string", "smali", "axml"]
}
```

#### 示例 - 正则搜索敏感字符串

```json
{
  "workspaceId": "crf71js2",
  "query": "password|token|secret|key",
  "queryType": "regex",
  "caseSensitive": false,
  "scopes": "dex_string"
}
```

#### 示例 - 搜索类名（精确匹配）

```json
{
  "workspaceId": "crf71js2",
  "query": "AdConfig",
  "queryType": "literal",
  "caseSensitive": true,
  "matchMode": "exact",
  "scopes": "dex_class"
}
```

#### 示例 - 带匹配位置信息搜索

```json
{
  "workspaceId": "crf71js2",
  "query": "AdConfig",
  "queryType": "literal",
  "caseSensitive": false,
  "scopes": "smali",
  "includeMatchOffsets": true
}
```

#### 示例 - 使用类前缀过滤

```json
{
  "workspaceId": "crf71js2",
  "query": "config",
  "queryType": "literal",
  "caseSensitive": false,
  "scopes": "dex_string",
  "classPrefix": "Lcom/example/"
}
```

#### 示例 - 使用资源类型过滤

```json
{
  "workspaceId": "crf71js2",
  "query": "layout",
  "queryType": "literal",
  "caseSensitive": false,
  "scopes": "resource_table_name",
  "resourceTableTypes": "layout"
}
```

#### 示例 - DEX 字符串搜索（成员粒度）

```json
{
  "workspaceId": "crf71js2",
  "query": "password",
  "queryType": "literal",
  "caseSensitive": false,
  "scopes": "dex_string",
  "dexStringGranularity": "member"
}
```

#### 返回示例

```json
{
  "workspaceId": "crf71js2",
  "data": [
    {
      "locator": { "kind": "dex_class", "className": "Lcom/example/MainActivity;" },
      "searchScope": "dex_string",
      "matchKind": "string",
      "snippet": "PASSWORD_INVALID",
      "matchCount": 1,
      "matchedStrings": [
        { "text": "PASSWORD_INVALID", "textTruncated": false }
      ]
    }
  ],
  "pagination": {
    "hasMore": true,
    "returnedCount": 10,
    "limitMax": 200,
    "nextCursor": "xxx"
  }
}
```

#### 带匹配位置的返回示例

```json
{
  "data": [
    {
      "locator": { "kind": "dex_class", "className": "Lcom/example/MainActivity;" },
      "searchScope": "smali",
      "matchKind": "smali",
      "snippet": ".class public final Lcom/example/MainActivity;",
      "line": 1,
      "column": 44,
      "matchTarget": "smaliText",
      "matchStart": 43,
      "matchEnd": 51,
      "matchedText": "MainActivity",
      "matchedTextTruncated": false
    }
  ]
}
```

---

### 5. mt_apk_continue - 继续分页

继续获取上一页的后续内容。

#### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| workspaceId | string | 是 | 工作区 ID |
| nextCursor | string | 是 | 上一页返回的 nextCursor |
| limit | integer | 否 | 每页数量覆盖 |

#### 示例

```json
{
  "workspaceId": "crf71js2",
  "nextCursor": "AwMyyAEHdXBncmFkZQEAAYACAfABAQAAAAABAAD56AEBAAgr"
}
```

---

## 常用场景

### 场景1: 分析收费功能

```json
// 1. 打开 APK
mt_apk_open({ "path": "mt://current-apk" })

// 2. 搜索支付关键词
mt_apk_search({
  "workspaceId": "xxx",
  "query": "payment",
  "queryType": "literal",
  "caseSensitive": false,
  "scopes": "dex_string"
})

// 3. 搜索 VIP 关键词
mt_apk_search({
  "workspaceId": "xxx",
  "query": "vip",
  "queryType": "literal",
  "caseSensitive": false,
  "scopes": "dex_string"
})
```

### 场景2: 查看类结构

```json
// 1. 列出类
mt_apk_list({
  "workspaceId": "xxx",
  "view": "dex_classes",
  "prefix": "com/example"
})

// 2. 查看类大纲
mt_apk_list({
  "workspaceId": "xxx",
  "view": "dex_class_outline",
  "className": "Lcom/example/MainActivity;"
})

// 3. 读取方法代码
mt_apk_read({
  "workspaceId": "xxx",
  "locator": {
    "kind": "dex_method",
    "className": "Lcom/example/MainActivity;",
    "methodSig": "onCreate(Landroid/os/Bundle;)V"
  }
})
```

### 场景3: 读取 AndroidManifest

```json
mt_apk_read({
  "workspaceId": "xxx",
  "locator": {
    "kind": "axml",
    "path": "AndroidManifest.xml"
  }
})
```

### 场景4: 搜索敏感字符串

```json
mt_apk_search({
  "workspaceId": "xxx",
  "query": "password|token|secret|key",
  "queryType": "regex",
  "caseSensitive": false,
  "scopes": "dex_string"
})
```

### 场景5: 分析特定包的代码

```json
// 1. 使用类前缀过滤搜索
mt_apk_search({
  "workspaceId": "xxx",
  "query": "config",
  "queryType": "literal",
  "caseSensitive": false,
  "scopes": ["dex_string", "smali"],
  "classPrefix": "Lcom/example/"
})

// 2. 列出该包下的类
mt_apk_list({
  "workspaceId": "xxx",
  "view": "dex_classes",
  "prefix": "com/example"
})
```

### 场景6: 查找资源引用

```json
// 1. 搜索资源 ID
mt_apk_search({
  "workspaceId": "xxx",
  "query": "0x7f010000",
  "queryType": "literal",
  "caseSensitive": false,
  "scopes": "resource_table_id"
})

// 2. 搜索资源名称
mt_apk_search({
  "workspaceId": "xxx",
  "query": "abc_fade_in",
  "queryType": "literal",
  "caseSensitive": false,
  "scopes": "resource_table_name"
})

// 3. 读取资源详情
mt_apk_read({
  "workspaceId": "xxx",
  "locator": {
    "kind": "resource_table_entry",
    "resourceTableId": "0x7f010000"
  }
})
```

### 场景7: 分析 XML 布局

```json
// 1. 搜索 XML 中的内容
mt_apk_search({
  "workspaceId": "xxx",
  "query": "MainActivity",
  "queryType": "literal",
  "caseSensitive": false,
  "scopes": "axml"
})

// 2. 读取 XML 文件
mt_apk_read({
  "workspaceId": "xxx",
  "locator": {
    "kind": "axml",
    "path": "res/layout/activity_main.xml"
  }
})
```

---

## 类名格式说明

- **描述符格式**: `Lcom/example/MainActivity;`（以 L 开头，以 ; 结尾）
- **Java 格式**: `com.example.MainActivity`

搜索和定位器中通常使用描述符格式。

---

## 错误处理

当请求出错时，返回包含以下字段：

| 字段 | 说明 |
|------|------|
| errorCode | 错误代码 |
| message | 错误消息 |
| recoverable | 是否可恢复 |
| errorSeverity | 错误严重程度：warning、fatal |
| argument | 错误参数名 |
| badValue | 错误的参数值 |
| allowedValues | 允许的值列表 |
| example | 正确示例 |

### 常见错误

| errorCode | 说明 |
|-----------|------|
| CURRENT_APK_NOT_AVAILABLE | 当前 APK 不可用 |
| INVALID_ARGUMENT | 参数无效 |
| WORKSPACE_NOT_FOUND | 工作区不存在 |

---

## 最佳实践

1. **复用工作区**: 使用 `reuseWorkspaceByPath: true` 避免重复解析
2. **分页处理**: 大量数据使用 `limit` 和 `nextCursor` 分页获取
3. **精确搜索**: 使用 `classPrefix`、`zipEntryPrefix`、`resourceTableTypes` 缩小搜索范围
4. **性能优化**: 仅请求需要的 `scopes`，避免全范围搜索
5. **使用 nextActions**: 返回的 `nextActions` 提供了推荐的下一步操作
6. **多范围搜索**: 使用 JSON 数组格式传递多个 scopes，如 `["dex_string", "smali"]`
7. **精确匹配**: 需要精确匹配时使用 `matchMode: "exact"`
8. **定位分析**: 使用 `includeMatchOffsets: true` 获取精确的匹配位置

---

## 更新日期

- 文档日期: 2026-05-24
- 服务版本: mt_mcp
