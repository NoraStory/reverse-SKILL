# SimpleHook 配置生成与修复技能

## 概述

这是一个完整的 AI 技能，用于完成以下两种工作：

1. **配置生成**：根据 Android 应用逆向分析结果（smali 代码、方法签名、字段签名、关键类名等），自动生成 SimpleHook 可识别的标准 Hook 配置 JSON
2. **配置修复**：将非标准或格式错误的 Hook 配置修复为标准 SimpleHook 格式

SimpleHook 是一个基于 Xposed/LSPosed 框架的 Android Hook 工具，项目地址：https://github.com/littleWhiteDuck/SimpleHook

---

## 第一部分：配置格式规范

### 1.1 顶层结构（AppConfig）

```json
{
  "packageName": "目标应用包名",
  "appName": "应用名",
  "versionName": "版本号",
  "description": "描述说明",
  "configs": "[内嵌JSON字符串数组]",
  "enable": true,
  "id": 0
}
```

**关键约束**：

- `configs` 字段必须是 **JSON 字符串**（即 `"configs": "[{\"className\":...}]"` 这种形式），而非直接 JSON 数组
- 不允许有任何代码注释（`//` 或 `/* */`），注释信息统一使用 `desc` 字段
- 所有内层双引号必须正确转义为 `\"`
- 顶层 `id` 字段建议使用随机正整数

### 1.2 内层结构（HookConfig）

每条 Hook 配置支持以下字段：

| 字段 | 类型 | 必填 | 含义 |
|------|------|------|------|
| `mode` | Int | 是 | Hook 模式（0-10），决定 Hook 行为 |
| `className` | String | 是 | 目标类名，支持 Java 和 Smali 语法 |
| `methodName` | String | 条件 | 方法名，构造方法填 `<init>`，所有方法填 `*` |
| `params` | String | 否 | 参数类型，多个用英文逗号分隔，`*` 表示匹配所有 |
| `fieldName` | String | 条件 | 变量名（静态/实例变量 Hook 时使用） |
| `fieldClassName` | String | 条件 | 变量所在类的类名 |
| `resultValues` | String | 条件 | 修改后的值（返回值/参数值/变量值） |
| `hookPoint` | String | 条件 | `before`（方法执行前）或 `after`（方法执行后，默认） |
| `returnClassName` | String | 条件 | 返回值类名，仅 mode=10 时使用 |
| `desc` | String | 否 | 描述/注释，建议写明该字段所有可能取值 |
| `enable` | Boolean | 否 | 是否启用该条 Hook，默认 true |

**严格禁止的字段**：`extraCond`、`condition`、`extra`、`constraint` 等任何非官方字段。

### 1.3 Mode 详解

| mode | 名称 | 含义 | 有效字段组合 |
|------|------|------|-------------|
| `0` | Hook返回值 | 替换目标方法的返回值 | mode, className, methodName, params, resultValues, desc, enable |
| `1` | Hook参数值 | 修改目标方法的参数 | mode, className, methodName, params, resultValues, desc, enable |
| `2` | 中断执行 | 拦截方法，不执行原方法体 | mode, className, methodName, params, desc, enable |
| `3` | Hook静态变量 | 修改静态变量值 | mode, className, methodName, params, fieldName, fieldClassName, resultValues, hookPoint, desc, enable |
| `4` | Hook实例变量 | 修改实例变量值 | mode, className, methodName, params, fieldName, fieldClassName, resultValues, desc, enable |
| `5` | 记录参数值 | 记录方法参数（仅日志） | mode, className, methodName, params, desc, enable |
| `6` | 记录返回值 | 记录方法返回值（仅日志） | mode, className, methodName, params, desc, enable |
| `7` | 记录参返 | 同时记录参数和返回值 | mode, className, methodName, params, desc, enable |
| `8` | 记录静态变量 | 记录静态变量值 | mode, className, methodName, params, fieldName, fieldClassName, desc, enable |
| `9` | 记录实例变量 | 记录实例变量值 | mode, className, methodName, params, fieldName, fieldClassName, desc, enable |
| `10` | Hook返回值+ | 通过 Gson 将 JSON 转为对象后返回 | mode, className, methodName, params, resultValues, returnClassName, desc, enable |

---

## 第二部分：类名与方法名填写规则

### 2.1 类名格式

支持两种语法：

- **Java 语法**：`com.example.utils.VipHelper`
- **Smali 语法**：`Lcom/example/utils/VipHelper;`（必须以 `;` 结尾）

### 2.2 方法名格式

- 普通方法：直接写方法名，如 `isVip`、`getExpiredTime`
- 构造方法：统一填 `<init>`
- 所有方法：填 `*`（Hook 一个类中所有方法）

### 2.3 参数类型格式

多个参数用英文逗号分隔，支持以下写法：

- **Java 语法**：`java.lang.String,android.content.Context,boolean,int`
- **Smali 语法**：`Ljava/lang/String;,Landroid/content/Context;,Z,I`
- 所有同名方法：填 `*`

### 2.4 通配符规则

| 通配符 | 位置 | 含义 |
|--------|------|------|
| `*` | methodName | Hook 一个类中所有方法 |
| `*` | params | Hook 所有同名方法（所有重载） |

---

## 第三部分：resultValues 填写规则

**核心原则：resultValues 的值必须是字符串，不能使用 null 字面量。**

### 3.1 基本类型（通过后缀自动识别）

| Java类型 | Smali类型 | 写法 | 示例 |
|----------|-----------|------|------|
| boolean | Z | `true` / `false` | `true` |
| int | I | 纯数字 | `1`、`99` |
| long | J | 数字 + `L` 或 `l` | `1l`、`120000L` |
| short | S | 数字 + `short` | `1short` |
| char | C | 字符 + `c` | `195c` |
| byte | B | 数字 + `b` | `2b` |
| float | F | 数字 + `f` | `2f`、`3.0f` |
| double | D | 数字 + `d` | `2d`、`3.0d` |

### 3.2 null 值

- 对象类型返回 null：填 `null`（不含引号），如 `"resultValues": "null"`
- 字符串类型不能用 null，用 `nulls` 表示字符串 `"null"`

### 3.3 字符串

不符合基本类型和 null 的全部转为字符串。**特殊情况**：

| 场景 | 正确写法 | 错误写法 | 说明 |
|------|----------|----------|------|
| 纯数字字符串 | `111s` | `111` | 不加 s 会被转为 int |
| 布尔字符串 | `trues` / `falses` | `true` / `false` | 不加 s 会被转为 boolean |
| null 字符串 | `nulls` | `null` | 不加 s 会被转为 null |
| 空字符串 | `empty` 或 `空` | （留空） | 留空无法保存配置 |

### 3.4 多参数值（mode=1 专用）

多个参数值用逗号分隔，不修改的参数留空：

- 只修改第 3 个参数：`"resultValues": ",,99"`
- 修改第 2、3 个参数：`"resultValues": ",啦啦啦,99"`
- 全部修改：`"resultValues": "null,啦啦啦,99"`

### 3.5 随机文本返回值（mode=0 专用）

```json
{"random":"abcdefgh123456789","length":9,"key":"uniqueKey","updateTime":100,"defaultValue":""}
```

| 字段 | 含义 |
|------|------|
| `random` | 随机字符池 |
| `length` | 生成文本长度 |
| `key` | 唯一标识（多个随机返回值时需不同） |
| `updateTime` | 更新间隔（秒），`-1` 表示每次更新 |
| `defaultValue` | 默认值（可选） |

### 3.6 Hook 返回值+（mode=10 专用）

resultValues 填 JSON 对象字符串，如 `{"isHook":false,"level":10000}`。系统通过 Gson 转为 `returnClassName` 指定的类对象后返回。**暂不支持数组**。

---

## 第四部分：配置生成流程（从应用分析到配置）

当用户提供应用逆向分析信息时，按照以下流程生成配置。

### 4.1 信息采集与识别

从用户输入中自动识别以下信息：

| 输入类型 | 识别方法 | 示例 |
|----------|----------|------|
| 包名 | 从 `package` 关键字或 AndroidManifest 提取 | `com.example.app` |
| 类名 | 从 `class` 声明、smali 路径、签名中提取 | `com.example.utils.VipHelper` |
| 方法名 | 从方法声明、函数签名中提取 | `isVip`、`getExpiredTime` |
| 参数类型 | 从方法签名括号内提取 | `(Ljava/lang/String;Z)I` |
| 返回值类型 | 从方法签名括号后提取 | `Z`(boolean)、`I`(int) |
| 字段名 | 从字段声明或字段签名中提取 | `isDebug`、`level` |
| 字段类型 | 从字段签名冒号后提取 | `Z`(boolean)、`I`(int) |

### 4.2 Smali 代码解析规则

当用户提供 smali 代码片段时，按以下规则解析：

**方法调用示例**：
```
invoke-virtual {v0}, Lcom/example/utils/VipHelper;->isVip()Z
```
→ 类名：`com.example.utils.VipHelper`，方法名：`isVip`，返回值类型：`boolean`

**字段签名示例**：
```
Lcom/example/config/GlobalConfig;->isDebug:Z
```
→ 变量所在类名：`com.example.config.GlobalConfig`，字段名：`isDebug`，字段类型：`boolean`

**方法签名示例**：
```
Lcom/example/utils/VipHelper;->getExpiredTime()J
```
→ 类名：`com.example.utils.VipHelper`，方法名：`getExpiredTime`，返回值类型：`long`

**带参数的方法签名示例**：
```
Lcom/example/api/RequestBuilder;->addParam(Ljava/lang/String;Ljava/lang/String;)V
```
→ 类名：`com.example.api.RequestBuilder`，方法名：`addParam`，参数类型：`java.lang.String,java.lang.String`，返回值类型：`void`

### 4.3 根据 Hook 目的选择 Mode

| Hook 目的 | 推荐 mode | 说明 |
|-----------|-----------|------|
| 修改方法返回值（如 isVip→true） | 0 | 最常用，修改布尔/数字/字符串返回值 |
| 修改方法参数 | 1 | 拦截传入参数并修改 |
| 拦截方法执行（不执行原方法） | 2 | 阻止方法执行，可用于去广告、禁用功能 |
| 修改静态变量 | 3 | 直接在方法执行前后修改 static 字段 |
| 修改实例变量 | 4 | 在构造方法或 setter 执行后修改成员变量 |
| 仅记录参数（调试用） | 5 | 不影响执行，只记录日志 |
| 仅记录返回值（调试用） | 6 | 不影响执行，只记录日志 |
| 同时记录参数和返回值（调试用） | 7 | 不影响执行，同时记录 |
| 记录静态变量值（调试用） | 8 | 不影响执行，只记录 |
| 记录实例变量值（调试用） | 9 | 不影响执行，只记录 |
| 将 JSON 转为对象返回 | 10 | 适用于返回自定义数据类的方法 |

### 4.4 常见 Hook 场景模式匹配

| 场景描述 | 典型类名特征 | 典型方法名 | 推荐配置 |
|----------|-------------|-----------|----------|
| VIP 破解 | `*VipHelper*`, `*UserManager*`, `*MemberUtil*` | `isVip`, `isPremium`, `getUserType`, `isMember` | mode=0, resultValues="true" |
| 会员到期时间 | `*VipHelper*`, `*UserManager*` | `getExpiredTime`, `getExpireTime`, `getEndTime` | mode=0, resultValues="9999999999999L" |
| 去广告 | `*AdHelper*`, `*AdManager*`, `*AdUtil*` | `isAdEnabled`, `showAd`, `loadAd`, `getAdConfig` | mode=0(resultValues="false") 或 mode=2 |
| 解锁功能 | `*FeatureManager*`, `*ConfigManager*` | `isFeatureEnabled`, `hasFeature` | mode=0, resultValues="true" |
| 修改用户等级 | `*UserManager*`, `*UserInfo*`, `*UserBean*` | `getLevel`, `getUserLevel` | mode=0, resultValues="999" |
| 修改签到时间 | `*SignIn*`, `*CheckIn*` | `getLastSignTime`, `getSignDays` | mode=0, resultValues="..." |
| 伪造请求参数 | `*RequestBuilder*`, `*HttpHelper*` | `addParam`, `buildRequest` | mode=1 |
| 阻止弹窗 | `*Dialog*`, `*Popup*`, `*Toast*` | `show`, `showDialog`, `showPopup` | mode=2 |
| 修改响应数据 | `*Response*`, `*Result*` | `getData`, `getResult`, `getBody` | mode=0 或 mode=10 |
| 调试/分析 | 任意 | 任意 | mode=5/6/7/8/9 |
| 修改静态配置 | `*Config*`, `*Setting*`, `*Constant*` | `init`, `loadConfig` | mode=3 |

### 4.5 生成后输出格式

生成后的配置必须包含：
1. 完整的 `packageName`、`appName`、`versionName`、`description`
2. `configs` 为正确转义的 JSON 字符串
3. 每条 Hook 配置包含 `mode` 和 `desc` 字段
4. 随机生成的 `id` 值

---

## 第五部分：配置修复流程

当用户提供需要修复的 Hook 配置时，按以下步骤处理：

### 步骤 1：清理非法内容

1. 删除所有 `//` 单行注释和 `/* */` 多行注释
2. 将注释内容（如有价值）移到 `desc` 字段中
3. 删除所有非官方字段：`extraCond`、`condition`、`constraint`、`extra`、`rules` 等
4. 如果非官方字段包含重要逻辑，用 `desc` 字段记录说明

### 步骤 2：修正字段值

1. `resultValues` 中 `null` 字面量改为空字符串 `""`，或根据实际意图改为 `"null"`
2. 确保所有 `resultValues` 值都是字符串类型
3. 修正不正确的类型后缀

### 步骤 3：标准化 JSON 格式

1. 确保 `configs` 字段是 JSON 字符串（内层双引号全部转义为 `\"`）
2. 验证 JSON 格式合法性
3. 确保顶层包含所有必要字段

### 步骤 4：补充 desc 注释

为每条 Hook 配置添加 `desc` 字段，描述用途和可能取值。

---

## 第六部分：输出模板

最终输出必须严格遵循以下模板：

```json
{
  "packageName": "目标应用包名",
  "appName": "应用名称",
  "versionName": "版本号",
  "description": "配置描述",
  "configs": "[{\"mode\":0,\"className\":\"完整类名\",\"methodName\":\"方法名\",\"params\":\"参数类型\",\"resultValues\":\"修改后的值\",\"hookPoint\":\"after\",\"desc\":\"功能描述，列出所有可能取值\"}]",
  "enable": true,
  "id": 随机数字
}
```

---

## 第七部分：Smali 类型速查表

| Smali类型 | Java类型 | 结果值后缀 |
|-----------|----------|-----------|
| `Z` | boolean | 无后缀：`true`/`false` |
| `B` | byte | 后缀 `b`：`2b` |
| `S` | short | 后缀 `short`：`1short` |
| `C` | char | 后缀 `c`：`195c` |
| `I` | int | 无后缀：`1`、`99` |
| `J` | long | 后缀 `L`/`l`：`120000L` |
| `F` | float | 后缀 `f`：`3.0f` |
| `D` | double | 后缀 `d`：`3.0d` |
| `V` | void | 不适用 |
| `Ljava/lang/String;` | String | 普通字符串直接写，特殊情况加 `s` 后缀 |
| `L*;` | 对象类型 | 普通字符串或 `null` |

---

## 第八部分：注意事项

1. **configs 是 JSON 字符串**：这是最常见的错误来源。内层必须用 `\"` 转义。
2. **resultValues 类型后缀**：务必根据实际类型添加正确的后缀，否则会导致目标应用崩溃。
3. **字符串数字和布尔值**：纯数字字符串加 `s` 后缀；布尔字符串用 `trues`/`falses`。
4. **空字符串**：必须写 `empty` 或 `空`，不能留空。
5. **mode=10 的限制**：不支持数组类型返回值。
6. **desc 字段**：虽然不是必填，但强烈建议填写。
7. **配置导入**：生成的配置可在 SimpleHook 应用中导入，或放入 `/data/local/tmp/simpleHook/<包名>/config/` 目录。