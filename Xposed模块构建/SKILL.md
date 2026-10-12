---
name: Xposed模块构建
description: 指挥 AI 生成完整的 Xposed/LSPosed 模块工程（供安全研究/自有应用的 hook 与定制）。当用户想"写一个模块 hook 某 App 的某方法""改返回值/参数""做个 LSPosed 插件"时使用。AI 按标准结构逐个创建文件（Manifest、xposed_init、hook 源码），产出可直接导入 IDA/AIDE/Android Studio 编译打包的完整工程。
---

# Xposed / LSPosed 模块生成

用户想让你**写好一个完整的 Xposed 模块工程**，他自己最后用 IDA/AIDE/Android Studio 打包成 APK。你的任务：按下面的标准结构，用文件工具（create_file / write_file）在工作区**逐个文件创建**，产出一个能直接编译的模块。

## 一、先问清楚（信息不全就先确认）
1. 目标 App 包名（如 `com.tencent.mm`）
2. 要 hook 的类名 + 方法名（如 `com.xxx.Pay.isVip`）
3. 想要的效果（改返回值为 true / 改参数 / 替换实现 / 打印日志）
4. 模块包名（如 `com.chiyuan.mymodule`）、模块名

不清楚 hook 哪里时，建议先用逆向技能（jadx/SOMCP/frida）分析定位，再回来写模块。

## 二、标准模块目录结构（照此逐个创建）

```
<模块名>/
├── AndroidManifest.xml
├── assets/
│   └── xposed_init
├── src/main/java/<包名路径>/
│   └── HookEntry.kt
├── build.gradle（如用 Gradle 编译）
└── README.md（说明 hook 了什么、怎么用）
```

## 三、各文件模板

### 1. AndroidManifest.xml
关键是 `<meta-data>` 三件套（xposedmodule / xposeddescription / xposedminversion）：
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.chiyuan.mymodule">
    <application
        android:label="我的模块"
        android:icon="@mipmap/ic_launcher">
        <meta-data
            android:name="xposedmodule"
            android:value="true" />
        <meta-data
            android:name="xposeddescription"
            android:value="hook xxx 实现 yyy" />
        <meta-data
            android:name="xposedminversion"
            android:value="82" />
    </application>
</manifest>
```

### 2. assets/xposed_init
一行，写 hook 入口类的全限定名：
```
com.chiyuan.mymodule.HookEntry
```

### 3. 入口类 HookEntry.kt
实现 `IXposedHookLoadPackage`：
```kotlin
package com.chiyuan.mymodule

import de.robv.android.xposed.IXposedHookLoadPackage
import de.robv.android.xposed.XposedHelpers
import de.robv.android.xposed.callbacks.XC_LoadPackage
import de.robv.android.xposed.XC_MethodReplacement
import de.robv.android.xposed.XC_MethodHook

class HookEntry : IXposedHookLoadPackage {
    override fun handleLoadPackage(lpparam: XC_LoadPackage.LoadPackageParam) {
        // 只 hook 目标 App
        if (lpparam.packageName != "com.tencent.mm") return

        // 示例：让某方法直接返回 true
        XposedHelpers.findAndHookMethod(
            "com.xxx.Pay",           // 目标类
            lpparam.classLoader,
            "isVip",                  // 目标方法
            // 若方法有参数，在此依次列出参数类型，如 String::class.java
            object : XC_MethodReplacement() {
                override fun replaceHookedMethod(param: MethodHookParam): Any {
                    return true
                }
            }
        )
    }
}
```

## 四、常见 hook 写法（按需选用）

### 改返回值（最常用）
```kotlin
XposedHelpers.findAndHookMethod(clazz, cl, "method", object : XC_MethodHook() {
    override fun afterHookedMethod(param: MethodHookParam) {
        param.result = true   // 强制返回 true
    }
})
```

### 改入参
```kotlin
override fun beforeHookedMethod(param: MethodHookParam) {
    param.args[0] = "newValue"   // 改第一个参数
}
```

### 完全替换实现
```kotlin
object : XC_MethodReplacement() {
    override fun replaceHookedMethod(param: MethodHookParam): Any? { return null }
}
```

### hook 构造方法
```kotlin
XposedHelpers.findAndHookConstructor(clazz, cl, /*参数类型...,*/ object : XC_MethodHook(){ ... })
```

### 打印日志/调用栈（先摸清逻辑）
```kotlin
XposedBridge.log("参数: ${param.args.joinToString()}")
```

## 五、依赖说明（写进 README，供编译时配置）
- 编译依赖 Xposed API：`compileOnly "de.robv.android.xposed:api:82"`（仅编译期，不打进包）
- LSPosed 兼容 Xposed API，同样适用
- 新版可选用 LSPosed 的 modernxp / rikka 生态，但经典 `IXposedHookLoadPackage` 通用性最好

## 六、工作流
1. 确认目标包名 / 类 / 方法 / 效果
2. 逐个 create_file：AndroidManifest.xml → assets/xposed_init → HookEntry.kt → README.md
3. 告诉用户："工程已生成在 <目录>，用 IDA/AIDE/Android Studio 打开，配置 Xposed API 依赖后编译打包即可"
4. 提醒：需目标机装 LSPosed/Xposed 框架并在模块列表勾选、勾选目标 App 作用域、重启生效

## 边界
用于对自有或已授权应用的 hook、定制、调试与安全研究、学习。不协助破解他人付费功能牟利或未授权侵权。
