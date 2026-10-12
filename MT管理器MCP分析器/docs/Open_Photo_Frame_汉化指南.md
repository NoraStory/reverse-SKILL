# Open Photo Frame 汉化指南

## 基本信息

| 项目 | 值 |
|------|------|
| APK名称 | Open Photo Frame_1.8.1.apk |
| 包名 | io.github.micw.openphotoframe |
| 版本 | 1.8.1 (121) |
| 最低SDK | 24 (Android 7.0) |
| 目标SDK | 37 (Android 17) |
| 应用类型 | **Flutter 应用** |
| 类数量 | 1530 |
| 应用标签 | Open Photo Frame |

## 重要发现

### ⚠️ Flutter 应用特性

本应用是使用 **Flutter 框架** 开发的，这意味着：

1. **UI 字符串位置**：主要在 Dart 代码中，编译后存储在 `lib/armeabi-v7a/libapp.so`（Native 库）
2. **Android 资源表**：仅包含 Android 系统组件的多语言字符串（如 AppCompat、Material 等）
3. **无 ARB 文件**：未发现 Flutter 标准的本地化文件（.arb）
4. **硬编码字符串**：部分字符串在 DEX 代码中

### 资源表多语言支持

资源表已包含 **86 种语言** 的 Android 系统组件翻译，包括：
- 中文（简体/繁体）
- 日语、韩语
- 欧洲多种语言
- 中东、南亚、东南亚语言

---

## 需要汉化的内容

### 1. 应用名称

| 位置 | 当前值 | 建议汉化 |
|------|--------|----------|
| AndroidManifest.xml | `android:label="Open Photo Frame"` | 开放相框 / 照片相框 |

### 2. DEX 代码中的硬编码字符串

| 字符串 | 所在类 | 含义 | 建议汉化 |
|--------|--------|------|----------|
| `Open Photo Frame needs Device Admin permission to turn off the screen at night and wake it up in the morning.` | `LZ0/u;` | 设备管理员权限说明 | 开放相框需要设备管理员权限才能在夜间关闭屏幕并在早晨唤醒。 |
| `Keeping app running for continuous slideshow` | `Lio/github/micw/openphotoframe/KeepAliveService;` | 保持服务运行 | 保持应用运行以进行连续幻灯片播放 |

### 3. Flutter Dart 代码中的字符串

**⚠️ 重要**：Flutter 应用的主要 UI 字符串在 `libapp.so` 中，无法直接通过 MT 管理器修改。

---

## 汉化方案

### 方案一：MT 管理器修改（有限汉化）

**适用范围**：仅能修改 DEX 中的少量硬编码字符串和应用名称

#### 步骤 1：修改应用名称

```
1. MT管理器 → 打开 APK
2. 查看 AndroidManifest.xml
3. 找到 android:label="Open Photo Frame"
4. 修改为 android:label="开放相框"
5. 保存并退出 → 自动签名
```

#### 步骤 2：修改 DEX 字符串

**字符串 1：设备管理员权限说明**

```
1. MT管理器 → 打开 APK → Dex编辑器++
2. 搜索 → 字符串搜索
3. 输入：Open Photo Frame needs Device Admin permission
4. 找到后点击 → 转到定义
5. 长按字符串 → 编辑
6. 修改为：开放相框需要设备管理员权限才能在夜间关闭屏幕并在早晨唤醒。
7. 保存
```

**字符串 2：服务运行提示**

```
1. Dex编辑器++ → 搜索 → 字符串搜索
2. 输入：Keeping app running for continuous slideshow
3. 找到后 → 编辑
4. 修改为：保持应用运行以进行连续幻灯片播放
5. 保存并退出 → 自动签名
```

#### 方案一局限性

- ❌ 无法修改 Flutter UI 中的大部分字符串
- ❌ 无法修改设置页面、对话框等 UI 文本
- ❌ 无法修改错误提示、状态信息等
- ✅ 可以修改应用名称
- ✅ 可以修改少量 DEX 硬编码字符串

---

### 方案二：获取源码并添加本地化（推荐）

**适用范围**：完整汉化所有 UI 文本

#### 步骤 1：获取源码

本项目是开源项目，源码地址：
- GitHub: https://github.com/micw/open-photo-frame

```bash
git clone https://github.com/micw/open-photo-frame.git
cd open-photo-frame
```

#### 步骤 2：添加 Flutter 本地化支持

**2.1 添加依赖（pubspec.yaml）**

```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_localizations:
    sdk: flutter
  intl: ^0.18.0
```

**2.2 创建中文语言文件**

创建 `lib/l10n/app_zh.arb`：

```json
{
  "@@locale": "zh",
  "appName": "开放相框",
  "settings": "设置",
  "slideDuration": "幻灯片时长",
  "transitionDuration": "过渡动画时长",
  "blurBorders": "模糊边框",
  "syncInterval": "同步间隔",
  "deleteOrphaned": "删除孤立文件",
  "activeSource": "当前源",
  "nextcloudSettings": "Nextcloud 设置",
  "serverUrl": "服务器地址",
  "username": "用户名",
  "password": "密码",
  "folderSyncMode": "文件夹同步模式",
  "allFolders": "所有文件夹",
  "selectedFolders": "选定文件夹",
  "deviceAdminPermission": "开放相框需要设备管理员权限才能在夜间关闭屏幕并在早晨唤醒。",
  "grantPermission": "授予权限",
  "cancel": "取消",
  "ok": "确定",
  "error": "错误",
  "success": "成功",
  "loading": "加载中..."
}
```

**2.3 配置 l10n.yaml**

```yaml
arb-dir: lib/l10n
template-arb-file: app_en.arb
output-localization-file: app_localizations.dart
```

**2.4 修改 main.dart**

```dart
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en'),
        Locale('zh'),
      ],
      locale: const Locale('zh'), // 强制中文
      title: '开放相框',
      home: const MainScreen(),
    );
  }
}
```

**2.5 替换硬编码字符串**

将代码中的硬编码字符串替换为本地化调用：

```dart
// 修改前
Text('Settings')

// 修改后
Text(AppLocalizations.of(context)!.settings)
```

#### 步骤 3：重新编译

```bash
flutter build apk --release
```

---

### 方案三：使用 Frida 动态 Hook（高级）

**适用范围**：运行时动态替换字符串，无需修改 APK

```javascript
Java.perform(function() {
    // Hook Flutter 字符串加载
    // 需要根据具体实现编写 Hook 脚本
});
```

---

## 推荐方案

| 需求 | 推荐方案 | 原因 |
|------|----------|------|
| 仅修改应用名称 | 方案一（MT管理器） | 简单快速 |
| 完整汉化 | 方案二（源码修改） | Flutter 应用标准做法 |
| 不想重新编译 | 方案三（Frida） | 需要技术能力 |

---

## 注意事项

### 1. Flutter 应用汉化特点

- Flutter 应用的 UI 字符串不在 Android 的 `strings.xml` 中
- 主要字符串在 `libapp.so`（编译后的 Dart 代码）中
- 直接修改 APK 只能改少量 DEX 字符串

### 2. 签名问题

- 修改 APK 后需要重新签名
- 原应用签名会失效
- 如有签名校验需要额外处理

### 3. 开源优势

本应用是开源项目，建议通过源码方式进行完整汉化：
- 可以添加完整的本地化支持
- 可以提交 PR 贡献给社区
- 可以自定义所有 UI 文本

---

## 附录：APK 结构

```
Open Photo Frame_1.8.1.apk
├── AndroidManifest.xml
├── classes.dex              # Android 原生代码
├── lib/
│   └── armeabi-v7a/
│       ├── libapp.so        # Flutter Dart 代码（主要 UI 字符串）
│       └── libflutter.so    # Flutter 引擎
├── assets/
│   └── flutter_assets/
│       ├── assets/
│       │   └── config.json  # 应用配置
│       └── FontManifest.json
├── res/                     # Android 资源
│   ├── values/              # 默认字符串（英文）
│   ├── values-zh/           # 中文字符串（系统组件）
│   └── ...
└── resources.arsc           # 资源表（已含86种语言）
```

---

## 总结

**Open Photo Frame** 是一个 Flutter 开发的开源相框应用。由于 Flutter 应用的特性，直接通过 MT 管理器修改 APK 只能实现有限的汉化（应用名称和少量 DEX 字符串）。

**推荐方案**：
1. 从 GitHub 获取源码
2. 添加 Flutter 本地化支持（ARB 文件）
3. 创建中文翻译
4. 重新编译 APK

这是 Flutter 应用汉化的标准做法，可以实现完整、可维护的本地化。

---

*报告生成时间: 2026-05-27*
*分析工具: mt_mcp APK Analyzer*
