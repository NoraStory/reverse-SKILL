<div align="center">

# 🔍 MT管理器 MCP APK 分析引擎

**基于 MT管理器 MCP 服务的专业级 APK 深度分析框架**

[![Platform](https://img.shields.io/badge/Platform-Android-green.svg)](https://www.android.com)
[![License](https://img.shields.io/badge/License-Educational-blue.svg)](#许可证)
[![MT Manager](https://img.shields.io/badge/MT%20Manager-Required-orange.svg)](#依赖)

**智能分析 · 安全审计 · 逆向工程 · 自动化报告**

</div>

---

## 📖 项目定位

本项目是一个 **技能分享与逆向分析** 平台，核心提供：

- 🎯 **MT管理器 MCP 服务 APK 分析技能** — 自动化深度分析引擎
- 📊 **结构化分析报告** — 专业级逆向分析文档（附属产出）
- 🔧 **解决方案建议** — 每项分析附带可操作的修改方案
- 🛠️ **编辑重打包能力** — 支持 Smali/资源/AXML 编辑并构建签名 APK

---

## ✨ 核心能力

<table>
<tr>
<td width="50%">

### 🔎 多维度分析

- **功能分析** — 支付/VIP/登录/社交/推送
- **安全审计** — 敏感字符串/加密/权限/组件暴露
- **结构分析** — 入口/继承/调用链/资源引用
- **网络追踪** — API地址/域名配置/安全策略

</td>
<td width="50%">

### 🚀 高级特性

- **智能APK匹配** — 模糊名称识别，无需精确路径
- **混淆对抗** — 字符串锚点/类层次/框架API追踪
- **防御识别** — 签名校验/Root检测/Hook检测绕过
- **架构识别** — MVVM/MVP/MVC/Clean/MVI 自动判断

</td>
</tr>
</table>

---

## 📂 项目结构

```
mt_mcp/
├── 📄 README.md                    # 项目说明文档
├── 📄 SKILL.md                     # 技能定义文件（APK分析核心）
├── 📄 MT_MCP_使用文档.md           # MCP服务使用指南
│
├── 📁 docs/                        # 📚 文档与报告中心
│   ├── Open_Photo_Frame_汉化指南.md       # Flutter应用汉化案例
│   ├── 签名校验问题分析.md                # APK签名校验机制分析
│   ├── Appkey配置错误问题分析与解决方案.md  # DCloud Appkey问题方案
│   ├── 表盘自定义工具_综合分析报告.md       # 表盘工具综合分析
│   ├── 表盘自定义工具_捐赠者功能破解方案.md  # 捐赠者功能分析
│   ├── 表盘自定义工具_6.4.0_终极破解版修改指南.md # 破解修改实战
│   └── 📁 reports/                        # 分析报告库
│       ├── APKPure_分析报告.md             # VIP/支付功能分析
│       ├── Cellular-Z_广告分析报告.md      # 广告SDK检测与移除
│       ├── 酷我音乐_安全分析报告.md         # 第三方注入检测
│       └── 表盘自定义工具_DCloud_Appkey验证机制分析报告.md
│
└── 📁 .trae/                       # ⚙️ Trae 编辑器配置
    ├── mcp.json                       # MCP服务连接配置
    └── 📁 skills/                     # 技能定义目录
        └── mt-mcp-apk-analyzer/
            └── SKILL.md                # 技能源文件
```

---

## 🚀 快速开始

### 1️⃣ 配置 MCP 服务

编辑 `.trae/mcp.json`，配置 MT管理器 MCP 服务地址：

```json
{
  "mcpServers": {
    "MT_MCP": {
      "url": "http://<你的设备IP>:8787/mcp"
    }
  }
}
```

> ⚠️ **重要**：请将 `<你的设备IP>` 替换为运行 MT管理器 MCP 服务的设备实际 IP 地址。

### 2️⃣ 触发分析

在 Trae 编辑器中，输入分析需求即可自动触发 `mt-mcp-apk-analyzer` 技能：

```
分析 微信 的支付功能
分析 抖音 的VIP模块
对 支付宝 进行安全审计
修改 表盘自定义工具 的捐赠者验证逻辑并重打包
```

---

## 📋 分析报告示例

| 报告 | 类型 | 核心发现 |
|------|------|----------|
| [APKPure_分析报告.md](./docs/reports/APKPure_分析报告.md) | 功能分析 | VIP会员系统 + 多支付SDK集成 |
| [Cellular-Z_广告分析报告.md](./docs/reports/Cellular-Z_广告分析报告.md) | 广告检测 | 4个广告SDK + 完整移除方案 |
| [酷我音乐_安全分析报告.md](./docs/reports/酷我音乐_安全分析报告.md) | 安全审计 | ⚠️ 第三方恶意注入 + Hook框架 |
| [Open_Photo_Frame_汉化指南.md](./docs/Open_Photo_Frame_汉化指南.md) | 汉化案例 | Flutter应用本地化方案 |

---

## 🛠️ 关于 .trae 目录

`.trae/` 是 **Trae 编辑器专属** 的智能配置目录：

| 文件 | 作用 |
|------|------|
| `mcp.json` | MCP 服务连接配置，定义可用的外部工具服务 |
| `skills/` | 技能定义目录，存放自动化任务配置 |

> 💡 这些配置仅在 Trae 编辑器中生效，为编辑器提供智能分析能力。

---

## 📚 技术文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](./SKILL.md) | APK分析技能完整定义 — 工具规范/分析场景/工作流模板 |
| [MT_MCP_使用文档.md](./MT_MCP_使用文档.md) | MCP服务基础使用指南 |

---

## ⚡ 性能优化建议

| 策略 | 说明 |
|------|------|
| **前缀过滤** | 使用 `classPrefix` 限定搜索范围，排除第三方库 |
| **特定Scope** | 字符串搜索用 `dex_string`，指令搜索用 `smali` |
| **先Outline后Read** | 先获取类结构，再定向读取目标方法 |
| **缓存WorkspaceId** | 打开APK后复用ID，避免重复初始化 |

---

## 🔗 依赖环境

| 依赖 | 说明 |
|------|------|
| [MT管理器](https://mt2.cn/) | Android 端专业文件管理/APK编辑工具 |
| MT管理器 MCP 服务 | mt_mcp — 提供APK分析API |
| [Trae 编辑器](https://trae.ai/) | AI代码编辑器，支持MCP协议 |

---

## 📜 许可证

本项目仅供 **学习交流** 使用。请遵守相关法律法规，不得用于非法用途。

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star ⭐**

*Made with ❤️ for Android Reverse Engineering*

</div>
