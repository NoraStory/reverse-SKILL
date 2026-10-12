---
name: OpenClaw SDK开发
description: |
  openclaw-sdk 是 Python 包 (pip install openclaw-sdk)，用于连接 OpenClaw 自主 AI Agent 框架。
  当用户提到以下任何一种情况时，必须激活此 skill：
  - 需要连接、管理或与 OpenClaw agent 交互
  - 使用 OpenClaw SDK 进行 Python 开发
  - 需要创建 agent、执行任务、管理渠道、定时任务、技能等
  - 任何涉及 openclaw_sdk 的导入、安装、配置或使用
  - openclaw, openclaw-sdk, OpenClaw SDK 相关的任何问题
  即使用户没有明确说出 "skill"，只要涉及 SDK 使用就应该触发。
  此 skill 不包含实现代码——所有详细 API 参考在 references/ 目录下。
version: 2.1.0
compatibility:
  python: ">=3.11"
  openclaw-sdk: ">=2.1.0"
---

# OpenClaw SDK 使用指南

> 本 skill 是 AI Coding Reference：当 AI Agent 需要为用户编写使用 openclaw-sdk 的代码时，查阅本 skill 获取正确的 API 用法和经过测试的代码示例。
>
> **所有代码示例都经过真实 gateway 测试。**

## 快速概览

openclaw-sdk 提供 Pythonic 接口连接 OpenClaw autonomous AI agent 框架。核心功能：

| 类别 | 功能 |
|------|------|
| Agent 执行 | 同步/流式执行、批量执行、结构化输出 |
| 渠道管理 | WhatsApp, Telegram, SMS, Discord, Slack 等 |
| 定时任务 | Cron 风格调度 |
| 技能管理 | 安装、启用、禁用 agent 技能 |
| 多 Agent | Pipeline、Supervisor、Consensus 协调 |
| 自主执行 | GoalLoop、Orchestrator、Watchdog |
| 工作流 | 状态机工作流引擎 |
| 弹性模式 | Retry、CircuitBreaker、RateLimiter |
| 防护栏 | PII 过滤、内容过滤、成本限制 |
| 评估 | EvalSuite、自动化测试 |

## 核心概念

### Gateway 连接模式

SDK 支持三种 gateway 连接方式：

```python
# 方式 1: 自动检测 (默认)
client = await OpenClawClient.from_env()

# 方式 2: WebSocket (ProtocolGateway)
client = await OpenClawClient.connect(
    gateway_ws_url="ws://127.0.0.1:18789/gateway"
)

# 方式 3: OpenAI 兼容 HTTP (无 WebSocket)
client = await OpenClawClient.connect(
    openai_base_url="https://api.openclaw.example/v1"
)
```

### 认证

Token 从环境变量 `OPENCLAW_GATEWAY_TOKEN` 或 `~/.openclaw/openclaw.json` 读取。

## 核心使用模式

### 1. 连接并创建 Agent

```python
from openclaw_sdk import OpenClawClient, AgentConfig

# 连接
client = await OpenClawClient.from_env()

# 创建 agent
agent = await client.create_agent(
    config=AgentConfig(
        agent_id="my-agent",
        name="My Assistant",
        system_prompt="你是一个有用的助手。",
        llm_model="claude-sonnet-4-20250514"
    )
)
```

### 2. 执行查询（同步）

```python
result = await agent.execute("你好，请介绍一下你自己")
print(result.content)        # str: 文本内容
print(result.success)       # bool: 是否成功
print(result.token_usage)    # TokenUsage: token 消耗
print(result.files)         # list[GeneratedFile]: 生成的文件
```

### 3. 流式执行

```python
async for event in agent.execute_stream("写一首关于月亮的诗"):
    if event.event_type == EventType.CONTENT:
        print(event.text, end="", flush=True)
    elif event.event_type == EventType.THINKING:
        print(f"[思考中...]{event.thinking}")
    elif event.event_type == EventType.TOOL_CALL:
        print(f"[工具调用: {event.tool} => {event.input}]")
    elif event.event_type == EventType.DONE:
        print(f"\n[完成: {event.stop_reason}]")
```

### 4. 批量执行

```python
results = await agent.batch([
    "1 + 1 等于多少？",
    "世界上最深的海是什么？",
    "Python 的创始人是谁？"
])
for r in results:
    print(r.content)
```

### 5. 结构化输出（Pydantic）

```python
from pydantic import BaseModel
from openclaw_sdk import OpenClawClient

client = await OpenClawClient.from_env()
agent = client.get_agent("my-agent")

class WeatherResult(BaseModel):
    city: str
    temperature: float
    condition: str

result = await agent.execute_structured(
    "北京今天的天气怎么样？",
    output_model=WeatherResult
)
print(result.city)         # "北京"
print(result.temperature)  # 23.5
```

### 6. 文件操作

```python
# 上传文件给 agent
await agent.set_file("context.txt", "这是 agent 的上下文文件")

# 列出文件
files = await agent.list_files()

# 读取文件
content = await agent.get_file("context.txt")
```

### 7. 渠道登录 (WhatsApp/Telegram QR 码)

```python
# 获取 QR 码
result = await client.channels.web_login_start()
qr_data_url = result["qrDataUrl"]  # base64 PNG

# 等待扫码完成
result = await client.channels.web_login_wait(timeout_ms=120000)
print(result["connected"])  # True if scanned
```

## 参考文档索引

以下是所有详细 API 参考。按需查阅：

| 参考文档 | 内容 |
|----------|------|
| `references/core.md` | OpenClawClient, Agent, ExecutionResult, TypedStreamEvent, ClientConfig, AgentConfig, ExecutionOptions |
| `references/channels.md` | ChannelManager (status, logout, web_login_start/wait, request_pairing_code), TwilioSMSClient |
| `references/scheduling.md` | ScheduleManager (list_schedules, create_schedule, update_schedule, delete_schedule, run_now, get_runs, wake) |
| `references/skills.md` | SkillManager (status, install_via_gateway, update_skill, CLI方法), ClawHub (search, browse, get_details, categories, trending) |
| `references/approvals.md` | ApprovalManager (resolve, request, wait_decision, get/set_settings, node_settings) |
| `references/devices.md` | DeviceManager (rotate/revoke token, pair list/approve/reject/remove) |
| `references/autonomous.md` | GoalLoop, Orchestrator, Watchdog, Budget, Goal |
| `references/coordination.md` | Supervisor, AgentRouter, ConsensusGroup |
| `references/workflows.md` | Workflow, WorkflowStep, StepType, StepStatus, WorkflowResult, 预设工作流 |
| `references/pipeline.md` | Pipeline, ConditionalPipeline |
| `references/voice.md` | VoicePipeline, STT (Whisper, Deepgram), TTS (OpenAI, ElevenLabs) |
| `references/evaluation.md` | EvalSuite, EvalCase, EvalReport, ContainsEvaluator, ExactMatchEvaluator, RegexEvaluator |
| `references/output.md` | StructuredOutput, OutputParsingError |
| `references/connectors.md` | GitHub, Slack, Gmail, GoogleSheets, Notion, Jira, Stripe, Zendesk, HubSpot, Salesforce |
| `references/integrations.md` | FastAPI, Flask, Django, Streamlit, Jupyter, Celery |
| `references/guardrails.md` | PIIGuardrail, ContentFilterGuardrail, CostLimitGuardrail, MaxTokensGuardrail, RegexFilterGuardrail |
| `references/resilience.md` | RetryPolicy, CircuitBreaker, RateLimiter, retry_async |
| `references/alerting.md` | AlertManager, AlertRule, AlertSink, CostThresholdRule, LatencyThresholdRule, ErrorRateRule |
| `references/nodes.md` | NodeManager (list, describe, invoke, rename, pair) |
| `references/tts.md` | TTSManager (enable, disable, convert, set_provider, status, providers) |

## 重要约定

### 异常处理

```python
from openclaw_sdk.core.exceptions import (
    OpenClawError,
    AgentNotFoundError,
    GatewayError,
    TimeoutError,
    AuthenticationError
)

try:
    result = await agent.execute("...")
except GatewayError as e:
    print(f"Gateway 连接错误: {e}")
except TimeoutError as e:
    print(f"执行超时: {e}")
except AuthenticationError as e:
    print(f"认证失败: {e}")
```

### 超时和选项

```python
from openclaw_sdk import ExecutionOptions

options = ExecutionOptions(
    timeout_seconds=60,      # 默认 300
    stream=False,           # 是否流式
    max_tool_calls=30,      # 最多工具调用次数
    thinking=True,          # 启用思考过程
    attachments=[]           # 附件文件
)

result = await agent.execute("...", options=options)
```

### 会话管理

每个 agent 有一个 `session_key`，用于：
- 获取对话历史: `gateway.chat_history(session_key)`
- 重置记忆: `agent.reset_memory()`
- 中止执行: `gateway.chat_abort(session_key)`

### Gateway 直接调用

对于 SDK 高级用户，可以直接调用 gateway RPC 方法：

```python
# 通过 client
await client.gateway.call("sessions.list", {})

# 通过 agent
await agent.gateway.call("chat.history", {"sessionKey": agent.session_key})
```

### 流式事件类型参考

```python
from openclaw_sdk.core.constants import EventType

# SDK 级别事件
EventType.CONTENT       # 内容块
EventType.THINKING      # 思考过程
EventType.TOOL_CALL     # 工具调用
EventType.TOOL_RESULT   # 工具结果
EventType.FILE_GENERATED # 文件生成
EventType.DONE          # 执行完成
EventType.ERROR         # 错误

# Gateway 推送事件
EventType.CHAT          # 对话事件
EventType.AGENT         # Agent 生命周期
EventType.PRESENCE      # 在线状态
EventType.HEALTH        # 健康检查
EventType.CRON          # 定时任务
```

## 调试技巧

```python
import structlog
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
)
# 设置环境变量 OPENCLAW_LOG_LEVEL=DEBUG 查看详细日志
```

## 依赖安装

```bash
# 基础
pip install openclaw-sdk

# 可选 extras
pip install "openclaw-sdk[fastapi]"      # FastAPI 集成
pip install "openclaw-sdk[mcp]"           # MCP 支持
pip install "openclaw-sdk[dashboard]"     # Dashboard
pip install "openclaw-sdk[data-postgres]"  # PostgreSQL
pip install "openclaw-sdk[data-mysql]"    # MySQL
pip install "openclaw-sdk[alerting]"       # 告警
pip install "openclaw-sdk[all]"            # 全部依赖
```
