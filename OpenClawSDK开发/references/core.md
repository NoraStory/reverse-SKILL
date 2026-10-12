# Core Module Reference

**Module**: `openclaw_sdk.core`
**Source files**:
- `openclaw_sdk/core/client.py` — `OpenClawClient`
- `openclaw_sdk/core/agent.py` — `Agent`
- `openclaw_sdk/core/types.py` — data models
- `openclaw_sdk/core/config.py` — `ClientConfig`, `AgentConfig`, `ExecutionOptions`
- `openclaw_sdk/core/constants.py` — enums
- `openclaw_sdk/gateway/base.py` — `Gateway` abstract base and facade methods

---

## OpenClawClient

**文件**: `openclaw_sdk/core/client.py`

**说明**: Top-level client for the OpenClaw SDK. Connects to an OpenClaw gateway (local, protocol, or OpenAI-compatible) and provides access to agents, channels, scheduling, skills, and other management features.

### 工厂方法

#### `OpenClawClient.connect(**kwargs) -> OpenClawClient`
**说明**: Auto-detect and connect to an OpenClaw gateway. Auto-detection order: (1) `gateway_ws_url` kwarg → ProtocolGateway, (2) `openai_base_url` kwarg → OpenAICompatGateway, (3) local OpenClaw at `ws://127.0.0.1:18789` → LocalGateway, (4) raises `ConfigurationError`.

**参数**:
- `gateway_ws_url` — WebSocket URL for a protocol gateway (e.g. `"ws://127.0.0.1:18789/gateway"`)
- `openai_base_url` — Base URL for OpenAI-compatible gateway
- `api_key` — API key token
- `mode` — one of `"auto"`, `"local"`, `"protocol"`, `"openai_compat"`
- `timeout` — request timeout in seconds (1–3600, default 300)
- `callbacks` — list of `CallbackHandler` instances
- Any `ClientConfig` field

**返回**: Connected `OpenClawClient` instance.

**代码示例**:
```python
# Direct connection to local gateway
client = await OpenClawClient.connect(gateway_ws_url="ws://127.0.0.1:18789/gateway")

# From environment variables (OPENCLAW_GATEWAY_URL, OPENCLAW_API_KEY, etc.)
client = await OpenClawClient.connect()

# Async context manager
async with await OpenClawClient.connect() as client:
    agent = client.get_agent("my-agent")
    result = await agent.execute("Hello")
```

#### `ClientConfig.from_env() -> ClientConfig`
**说明**: Create a `ClientConfig` from `OPENCLAW_*` environment variables.

**环境变量**:
- `OPENCLAW_GATEWAY_URL` or `OPENCLAW_GATEWAY_WS_URL` → `gateway_ws_url`
- `OPENCLAW_API_KEY` → `api_key`
- `OPENCLAW_MODE` → `mode` (`"auto"`, `"local"`, `"protocol"`, `"openai_compat"`)
- `OPENCLAW_TIMEOUT` → `timeout` (integer seconds)
- `OPENCLAW_LOG_LEVEL` → `log_level` (`"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`)

**代码示例**:
```python
config = ClientConfig.from_env()
client = await OpenClawClient.connect()
```

### Agent 管理

#### `client.get_agent(agent_id: str, session_name: str = "main") -> Agent`
**说明**: Return an `Agent` for `agent_id`. This is a lightweight factory — no network call is made. The `session_key` sent to the gateway is `"{agent_id}:{session_name}"`.

**Gateway 调用**: None (local factory)

**参数**:
- `agent_id` — The agent's identifier (e.g. `"my-agent"`)
- `session_name` — Session name within the agent (default `"main"`)

**代码示例**:
```python
agent = client.get_agent("my-agent", session_name="main")
# session_key == "agent:my-agent:main"
```

#### `client.create_agent(config: AgentConfig, *, workspace: str | None = None) -> Agent`
**说明**: Create a new agent on the gateway using `agents.create` RPC.

**Gateway 调用**: `agents.create`

**参数**:
- `config` — `AgentConfig` for the new agent
- `workspace` — Optional workspace path (defaults to `"."` if not provided)

**返回**: `Agent` connected to the new agent.

**代码示例**:
```python
config = AgentConfig(agent_id="new-bot", name="New Bot")
agent = await client.create_agent(config)
```

#### `client.list_agents() -> list[AgentSummary]`
**说明**: List all agents known to the gateway.

**Gateway 调用**: `agents.list`

**返回**: List of `AgentSummary` objects with `agent_id`, `name`, `status`.

**代码示例**:
```python
agents = await client.list_agents()
for a in agents:
    print(a.agent_id, a.name, a.status)
```

#### `client.delete_agent(agent_id: str) -> bool`
**说明**: Delete an agent from the gateway.

**Gateway 调用**: `agents.delete`

**返回**: `True` on success.

**代码示例**:
```python
await client.delete_agent("old-bot")
```

### Channel 管理

#### `client.configure_channel(config: ChannelConfig) -> dict[str, Any]`
**说明**: Configure a messaging channel via read-modify-write on the gateway config.

**Gateway 调用**: `config.get` + `config.set`

**参数**:
- `config` — `ChannelConfig` instance

**返回**: Gateway response dict.

#### `client.list_channels() -> list[dict[str, Any]]`
**说明**: List all configured channels and their status.

**Gateway 调用**: `channels.status`

**返回**: List of dicts with channel status fields.

**代码示例**:
```python
channels = await client.list_channels()
for ch in channels:
    print(ch["name"], ch.get("linked"))
```

#### `client.remove_channel(channel_name: str) -> bool`
**说明**: Log out / remove a channel from the gateway.

**Gateway 调用**: `channels.logout`

**返回**: `True` on success.

### 健康与生命周期

#### `client.health() -> HealthStatus`
**说明**: Delegate to the underlying gateway health check.

**Gateway 调用**: `health`

**返回**: `HealthStatus` with `healthy`, `latency_ms`, `version`, `details`.

**代码示例**:
```python
health = await client.health()
print(health.healthy, health.version)
```

#### `client.close() -> None`
**说明**: Close the gateway connection.

**代码示例**:
```python
await client.close()
```

### Manager 属性

The client exposes these manager properties (lazy-initialized):

| 属性 | 类型 | 说明 |
|------|------|------|
| `client.channels` | `ChannelManager` | Messaging channel operations |
| `client.scheduling` / `client.schedules` | `ScheduleManager` | Cron/scheduled jobs |
| `client.skills` | `SkillManager` | Installed skills |
| `client.clawhub` | `ClawHub` | ClawHub marketplace |
| `client.webhooks` | `WebhookManager` | Webhook operations |
| `client.config_mgr` | `ConfigManager` | Runtime configuration |
| `client.approvals` | `ApprovalManager` | Execution approvals |
| `client.nodes` | `NodeManager` | Node/presence operations |
| `client.ops` | `OpsManager` | Logs, updates, usage |
| `client.devices` | `DeviceManager` | Device token operations |
| `client.tts` | `TTSManager` | Text-to-speech |

**代码示例**:
```python
client = await OpenClawClient.connect()
channels = client.channels
schedules = client.scheduling
```

---

## Agent

**文件**: `openclaw_sdk/core/agent.py`

**说明**: Represents a single OpenClaw agent and exposes execution methods. Obtain via `client.get_agent()`.

### 属性

#### `agent.session_key -> str`
**说明**: Gateway session key, e.g. `"agent:main:main"`.

**代码示例**:
```python
print(agent.session_key)  # "agent:my-agent:main"
```

### 执行方法

#### `agent.execute(query: str, options: ExecutionOptions | None = None, callbacks: list[CallbackHandler] | None = None, idempotency_key: str | None = None) -> ExecutionResult`
**说明**: Send a query to the agent and return the final result. For WebSocket gateways, subscribes to push events and waits for `DONE` or `ERROR`. For HTTP-only gateways, uses the response body directly.

**Gateway 调用**: `chat.send`

**参数**:
- `query` — The message to send to the agent
- `options` — Optional `ExecutionOptions` (timeout, streaming, attachments, thinking)
- `callbacks` — Per-call callbacks merged with client-level callbacks
- `idempotency_key` — Optional idempotency key forwarded to the gateway

**返回**: `ExecutionResult`

**Raises**: `AgentExecutionError` on failure; `TimeoutError` if agent times out.

**代码示例**:
```python
result = await agent.execute("What is 2+2?")
print(result.content)
print(result.success, result.stop_reason, result.latency_ms)
```

#### `agent.execute_stream(query: str, options: ExecutionOptions | None = None, callbacks: list[CallbackHandler] | None = None, idempotency_key: str | None = None) -> AsyncIterator[StreamEvent]`
**说明**: Send a query and yield raw push events until the agent finishes. Requires a WebSocket-capable gateway.

**Gateway 调用**: `chat.send` + `subscribe`

**参数**: Same as `execute`.

**返回**: `AsyncIterator[StreamEvent]` — yields until `DONE` or `ERROR`.

**代码示例**:
```python
async for event in agent.execute_stream("Tell me a story"):
    print(event.event_type, event.data)
```

#### `agent.execute_stream_typed(query: str, options: ExecutionOptions | None = None, idempotency_key: str | None = None) -> AsyncIterator[TypedStreamEvent]`
**说明**: Send a query and yield strongly-typed events instead of raw dicts. Yields `ContentEvent`, `ThinkingEvent`, `ToolCallEvent`, `ToolResultEvent`, `FileEvent`, `DoneEvent`, `ErrorEvent`.

**Gateway 调用**: `chat.send` + `subscribe`

**参数**: Same as `execute` (no `callbacks` param).

**返回**: `AsyncIterator[TypedStreamEvent]`

**代码示例**:
```python
async for event in agent.execute_stream_typed("Hello"):
    if isinstance(event, ContentEvent):
        print(event.text, end="")
    elif isinstance(event, DoneEvent):
        print(f"\nDone: {event.stop_reason}")
```

#### `agent.batch(queries: list[str], options: ExecutionOptions | None = None, callbacks: list[CallbackHandler] | None = None, max_concurrency: int | None = None) -> list[ExecutionResult]`
**说明**: Execute multiple queries in parallel.

**参数**:
- `queries` — List of query strings
- `options` — Shared execution options
- `callbacks` — Shared callbacks
- `max_concurrency` — Max parallel executions (default: unlimited)

**返回**: List of `ExecutionResult` in same order as queries.

**代码示例**:
```python
results = await agent.batch(["Query 1", "Query 2", "Query 3"])
```

#### `agent.execute_structured(query: str, output_model: Type[T], options: ExecutionOptions | None = None, max_retries: int = 2) -> T`
**说明**: Execute a query and parse the response into a Pydantic model using `StructuredOutput`.

**参数**:
- `query` — The user query
- `output_model` — Pydantic model class to validate against
- `options` — Optional execution controls
- `max_retries` — Extra attempts on parse failure (default 2)

**返回**: Validated `output_model` instance.

**代码示例**:
```python
from pydantic import BaseModel

class Summary(BaseModel):
    title: str
    bullet_points: list[str]

result = await agent.execute_structured("Summarise the news", Summary)
print(result.title, result.bullet_points)
```

### Workspace 文件

#### `agent.get_file(name: str) -> dict[str, Any]`
**说明**: Get an agent workspace file by name.

**Gateway 调用**: `agents.files.get`

**参数**:
- `name` — Exact filename (case-sensitive), e.g. `"SOUL.md"`

**返回**: Gateway response dict with file metadata and content.

**代码示例**:
```python
file_data = await agent.get_file("SOUL.md")
content = file_data.get("content", "")
```

#### `agent.list_files() -> dict[str, Any]`
**说明**: List all workspace files for this agent.

**Gateway 调用**: `agents.files.list`

**返回**: Gateway response dict with file listing.

**代码示例**:
```python
files = await agent.list_files()
for f in files.get("files", []):
    print(f["name"], f.get("size"))
```

#### `agent.set_file(name: str, content: str) -> dict[str, Any]`
**说明**: Create or overwrite an agent workspace file.

**Gateway 调用**: `agents.files.set`

**参数**:
- `name` — Filename (case-sensitive)
- `content` — File content as string

**返回**: Gateway response dict.

**代码示例**:
```python
await agent.set_file("NOTES.md", "# My Notes\nHello world")
```

### 身份与内存

#### `agent.get_identity() -> dict[str, Any]`
**说明**: Get the identity of this agent.

**Gateway 调用**: `agent.identity.get`

**返回**: Gateway response dict with `agentId`, `name`, `avatar`, `emoji`.

**代码示例**:
```python
identity = await agent.get_identity()
print(identity.get("name"), identity.get("emoji"))
```

#### `agent.reset_memory() -> bool`
**说明**: Clear the agent's conversation memory / session history.

**Gateway 调用**: `sessions.reset`

**返回**: `True` on success.

**代码示例**:
```python
await agent.reset_memory()
```

#### `agent.get_memory_status() -> dict[str, Any]`
**说明**: Return memory / session state for this agent.

**Gateway 调用**: `sessions.preview`

**返回**: Gateway response dict with session preview.

#### `agent.get_status() -> AgentStatus`
**说明**: Return the current `AgentStatus` for this agent's session.

**Gateway 调用**: `sessions.resolve`

**返回**: `AgentStatus` enum value (`"created"`, `"running"`, `"idle"`, `"error"`, `"deleted"`).

**代码示例**:
```python
status = await agent.get_status()
print(status.value)
```

### 运行时配置

#### `agent.wait_for_run(run_id: str) -> dict[str, Any]`
**说明**: Wait for a specific agent run to complete.

**Gateway 调用**: `agent.wait`

**参数**:
- `run_id` — Run ID from a `chat.send` response

**返回**: Gateway response dict with run result.

#### `agent.set_tool_policy(policy: ToolPolicy) -> dict[str, Any]`
**说明**: Set the tool policy for this agent at runtime via `config.patch`.

**参数**:
- `policy` — `ToolPolicy` instance

**返回**: Gateway response dict.

#### `agent.deny_tools(*tools: str) -> dict[str, Any]`
**说明**: Add tools to the agent's deny list at runtime.

**参数**:
- `*tools` — Tool names to deny (e.g. `"browser"`, `"group:runtime"`)

**返回**: Gateway response dict.

**代码示例**:
```python
await agent.deny_tools("browser", "group:runtime")
```

#### `agent.allow_tools(*tools: str) -> dict[str, Any]`
**说明**: Add tools to the agent's `alsoAllow` list at runtime.

**参数**:
- `*tools` — Tool names to additionally allow

**返回**: Gateway response dict.

#### `agent.add_mcp_server(name: str, server: StdioMcpServer | HttpMcpServer) -> dict[str, Any]`
**说明**: Add or replace an MCP server in the agent's config.

**参数**:
- `name` — Server name (e.g. `"postgres"`)
- `server` — Server config from `McpServer`

**返回**: Gateway response dict.

#### `agent.remove_mcp_server(name: str) -> dict[str, Any]`
**说明**: Remove an MCP server from the agent's config.

**参数**:
- `name` — Server name to remove

**返回**: Gateway response dict.

### Skills 运行时配置

#### `agent.set_skills(skills: SkillsConfig) -> dict[str, Any]`
**说明**: Set the skills configuration for this agent at runtime.

**参数**:
- `skills` — `SkillsConfig` to apply

**返回**: Gateway response dict.

#### `agent.configure_skill(name: str, entry: SkillEntry) -> dict[str, Any]`
**说明**: Add or update a single skill's configuration at runtime.

**参数**:
- `name` — Skill name (e.g. `"web-scraper"`)
- `entry` — `SkillEntry` per-skill config

**返回**: Gateway response dict.

#### `agent.disable_skill(name: str) -> dict[str, Any]`
**说明**: Disable a specific skill at runtime.

**参数**:
- `name` — Skill name to disable

**返回**: Gateway response dict.

#### `agent.enable_skill(name: str) -> dict[str, Any]`
**说明**: Enable a previously disabled skill at runtime.

**参数**:
- `name` — Skill name to enable

**返回**: Gateway response dict.

---

## ExecutionResult

**文件**: `openclaw_sdk/core/types.py`

**说明**: The result of a synchronous agent execution (`agent.execute()`). Contains the final content, files, tool calls, token usage, and metadata.

### 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | `bool` | Whether execution succeeded |
| `content` | `str` | Flat text response |
| `content_blocks` | `list[ContentBlock]` | Polymorphic content blocks |
| `files` | `list[GeneratedFile]` | Files generated by the agent |
| `tool_calls` | `list[ToolCall]` | Tool invocations made during execution |
| `thinking` | `str \| None` | Thinking/reasoning trace if enabled |
| `latency_ms` | `int` | Wall-clock execution time in ms |
| `token_usage` | `TokenUsage` | LLM token consumption |
| `completed_at` | `datetime` | UTC timestamp of completion |
| `stop_reason` | `str \| None` | `"complete"`, `"aborted"`, `"error"`, `"timeout"` |
| `error_message` | `str \| None` | Error details on failure |

### 属性

#### `result.has_files -> bool`
**说明**: `True` if the agent generated any files.

**代码示例**:
```python
result = await agent.execute("Create a report")
if result.has_files:
    for f in result.files:
        print(f.name, f.path)
```

---

## TypedStreamEvent

**文件**: `openclaw_sdk/core/types.py`

**说明**: Base class for typed stream events used with `agent.execute_stream_typed()`. Subclasses provide typed fields for each gateway event kind.

### 子类

#### `ContentEvent`
**说明**: A content/text chunk from the agent.

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_type` | `EventType` | `EventType.CONTENT` |
| `text` | `str` | Text content chunk |

#### `ThinkingEvent`
**说明**: A thinking/reasoning chunk from the agent.

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_type` | `EventType` | `EventType.THINKING` |
| `thinking` | `str` | Reasoning chunk |

#### `ToolCallEvent`
**说明**: The agent is invoking a tool.

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_type` | `EventType` | `EventType.TOOL_CALL` |
| `tool` | `str` | Tool name |
| `input` | `str` | Tool input (JSON string) |

#### `ToolResultEvent`
**说明**: The result from a tool invocation.

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_type` | `EventType` | `EventType.TOOL_RESULT` |
| `tool` | `str` | Tool name |
| `output` | `str` | Tool output (JSON string) |
| `duration_ms` | `int` | Execution time |

#### `FileEvent`
**说明**: A file generated by the agent.

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_type` | `EventType` | `EventType.FILE_GENERATED` |
| `name` | `str` | File name |
| `path` | `str` | File path |
| `size_bytes` | `int` | File size |
| `mime_type` | `str` | MIME type |

#### `DoneEvent`
**说明**: Agent execution completed (terminal event).

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_type` | `EventType` | `EventType.DONE` |
| `content` | `str` | Final text content |
| `token_usage` | `TokenUsage` | Token consumption |
| `stop_reason` | `str` | `"complete"`, `"aborted"`, etc. |

#### `ErrorEvent`
**说明**: Agent execution error (terminal event).

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_type` | `EventType` | `EventType.ERROR` |
| `message` | `str` | Error message |

**代码示例**:
```python
async for event in agent.execute_stream_typed("Hello"):
    print(f"[{event.event_type.value}]", event.model_dump(exclude={"event_type"}))
```

---

## TokenUsage

**文件**: `openclaw_sdk/core/types.py`

**说明**: LLM token consumption data.

### 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `input` | `int` | Input tokens consumed |
| `output` | `int` | Output tokens generated |
| `cache_read` | `int` | Cached tokens read |
| `cache_write` | `int` | Cached tokens written |
| `total_tokens` | `int` | Total tokens (alias: `totalTokens`) |

### 属性

#### `usage.total -> int`
**说明**: Total tokens. Uses `total_tokens` if non-zero, else `input + output`.

### 方法

#### `TokenUsage.from_gateway(data: dict[str, Any]) -> TokenUsage`
**说明**: Create from gateway response with camelCase field names.

**代码示例**:
```python
tu = TokenUsage.from_gateway({"input": 100, "output": 200, "cacheRead": 50})
print(tu.total)  # 300
```

---

## GeneratedFile

**文件**: `openclaw_sdk/core/types.py`

**说明**: A file generated by an agent during execution.

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | File name |
| `path` | `str` | File path |
| `size_bytes` | `int` | File size in bytes |
| `mime_type` | `str` | MIME type |

---

## ToolCall

**文件**: `openclaw_sdk/core/types.py`

**说明**: A tool invocation made during agent execution.

| 字段 | 类型 | 说明 |
|------|------|------|
| `tool` | `str` | Tool name |
| `input` | `str` | Tool input (JSON string) |
| `output` | `str \| None` | Tool output |
| `duration_ms` | `int \| None` | Execution time in ms |

---

## ContentBlock

**文件**: `openclaw_sdk/core/types.py`

**说明**: A single content block from polymorphic gateway responses.

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | `str` | Block type (e.g. `"text"`, `"thinking"`) |
| `text` | `str \| None` | Text content |
| `thinking` | `str \| None` | Thinking content |

### 属性

#### `block.value -> str`
**说明**: Return the first non-None text value (`text` or `thinking`).

---

## StreamEvent

**文件**: `openclaw_sdk/core/types.py`

**说明**: Raw stream event from the gateway. Used with `agent.execute_stream()`.

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_type` | `EventType` | Event type enum |
| `data` | `dict[str, Any]` | Raw event payload |

---

## ClientConfig

**文件**: `openclaw_sdk/core/config.py`

**说明**: Pydantic model for OpenClaw client configuration.

### 字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `mode` | `Literal["local", "protocol", "openai_compat", "auto"]` | `"auto"` | Connection mode |
| `openclaw_path` | `str` | `"openclaw"` | Path to openclaw binary |
| `work_dir` | `Path` | `Path("./.openclaw")` | Working directory |
| `gateway_ws_url` | `str \| None` | `None` | WebSocket gateway URL |
| `openai_base_url` | `str \| None` | `None` | OpenAI-compatible base URL |
| `api_key` | `str \| None` | `None` | API key token |
| `timeout` | `int` | `300` | Request timeout in seconds (1–3600) |
| `max_retries` | `int` | `3` | Max retries (0–10) |
| `retry_policy` | `RetryPolicy \| None` | `None` | Optional retry policy |
| `log_level` | `Literal["DEBUG", "INFO", "WARNING", "ERROR"]` | `"INFO"` | Log level |

---

## AgentConfig

**文件**: `openclaw_sdk/core/config.py`

**说明**: Pydantic model for OpenClaw agent configuration.

### 字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `agent_id` | `str` | (required) | Agent identifier (pattern: `^[a-zA-Z0-9_-]+$`) |
| `name` | `str \| None` | `None` | Human-readable name |
| `system_prompt` | `str` | `"You are a helpful assistant."` | System prompt |
| `llm_provider` | `Literal["anthropic", "openai", "gemini", "ollama"]` | `"anthropic"` | LLM provider |
| `llm_model` | `str` | `"claude-sonnet-4-20250514"` | Model name |
| `llm_api_key` | `str \| None` | `None` | LLM API key override |
| `channels` | `list[str]` | `[]` | Enabled channels |
| `enable_memory` | `bool` | `True` | Enable conversation memory |
| `memory_backend` | `Literal["memory", "redis"]` | `"memory"` | Memory backend |
| `permission_mode` | `Literal["accept", "confirm", "reject"]` | `"accept"` | Permission mode |
| `tool_policy` | `ToolPolicy \| None` | `None` | Tool policy |
| `mcp_servers` | `dict[str, StdioMcpServer \| HttpMcpServer] \| None` | `None` | MCP server configs |
| `skills` | `SkillsConfig \| None` | `None` | Skills configuration |

### 方法

#### `config.to_openclaw_agent() -> dict[str, Any]`
**说明**: Serialize to OpenClaw's native agent config JSON structure.

---

## ExecutionOptions

**文件**: `openclaw_sdk/core/config.py`

**说明**: Pydantic model for execution control options passed to `agent.execute()`.

### 字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `timeout_seconds` | `int` | `300` | Timeout in seconds (1–3600) |
| `stream` | `bool` | `False` | Whether to stream (used by execute_stream) |
| `max_tool_calls` | `int` | `50` | Max tool calls allowed (1–200) |
| `attachments` | `list[Attachment \| str \| Path]` | `[]` | File attachments |
| `thinking` | `bool \| str` | `False` | Thinking mode: `False`, `True`, `"enabled"`, `"disabled"`, `"auto"`, or budget string like `"10000"` |
| `deliver` | `bool \| None` | `None` | Deliver to channel (None = gateway default) |

**代码示例**:
```python
opts = ExecutionOptions(
    timeout_seconds=60,
    max_tool_calls=25,
    thinking=True,
    attachments=["/path/to/file.pdf"],
)
result = await agent.execute("Analyse this", options=opts)
```

---

## Gateway Facade Methods

**文件**: `openclaw_sdk/gateway/base.py`

**说明**: `Gateway` is the abstract base for all gateway implementations. All facade methods are typed wrappers over the `call()` and `subscribe()` primitives. They delegate to the OpenClaw gateway over WebSocket or HTTP.

### Chat Facade

#### `gateway.chat_history(session_key: str, limit: int = 100) -> list[dict[str, Any]]`
**Gateway 调用**: `chat.history`
**参数**: `session_key` (str), `limit` (int, default 100)
**返回**: List of message dicts.

#### `gateway.chat_abort(session_key: str) -> dict[str, Any]`
**Gateway 调用**: `chat.abort`
**参数**: `session_key` (str)
**返回**: Gateway response dict.

#### `gateway.chat_inject(session_key: str, message: str) -> dict[str, Any]`
**Gateway 调用**: `chat.inject`
**参数**: `session_key` (str), `message` (str)
**返回**: Gateway response dict.

### Sessions Facade

#### `gateway.sessions_list() -> list[dict[str, Any]]`
**Gateway 调用**: `sessions.list`
**返回**: List of session descriptors.

#### `gateway.sessions_preview(keys: list[str]) -> dict[str, Any]`
**Gateway 调用**: `sessions.preview`
**参数**: `keys` (list of session key strings)
**返回**: Preview dict.

#### `gateway.sessions_resolve(key: str) -> dict[str, Any]`
**Gateway 调用**: `sessions.resolve`
**参数**: `key` (session key)
**返回**: Session descriptor.

#### `gateway.sessions_patch(key: str, patch: dict[str, Any]) -> dict[str, Any]`
**Gateway 调用**: `sessions.patch`
**参数**: `key` (str), `patch` (dict of partial session updates)
**返回**: Gateway response dict.

#### `gateway.sessions_reset(key: str) -> dict[str, Any]`
**Gateway 调用**: `sessions.reset`
**参数**: `key` (session key)
**返回**: Gateway response dict.

#### `gateway.sessions_delete(key: str) -> dict[str, Any]`
**Gateway 调用**: `sessions.delete`
**参数**: `key` (session key)
**返回**: Gateway response dict.

#### `gateway.sessions_compact(key: str) -> dict[str, Any]`
**Gateway 调用**: `sessions.compact`
**参数**: `key` (session key)
**返回**: Gateway response dict.

### Config Facade

#### `gateway.config_get() -> dict[str, Any]`
**Gateway 调用**: `config.get`
**返回**: Full runtime configuration dict.

#### `gateway.config_schema() -> dict[str, Any]`
**Gateway 调用**: `config.schema`
**返回**: JSON Schema for runtime configuration.

#### `gateway.config_set(raw: str) -> dict[str, Any]`
**Gateway 调用**: `config.set`
**参数**: `raw` (str, full config JSON string)
**返回**: Gateway response dict.

#### `gateway.config_patch(raw: str, base_hash: str | None = None) -> dict[str, Any]`
**Gateway 调用**: `config.patch`
**参数**: `raw` (str), `base_hash` (str, optional optimistic concurrency control)
**返回**: Gateway response dict.

#### `gateway.config_apply(raw: str, base_hash: str | None = None) -> dict[str, Any]`
**Gateway 调用**: `config.apply`
**参数**: `raw` (str), `base_hash` (str, optional)
**返回**: Gateway response dict.

### Agents Facade

#### `gateway.agents_list() -> dict[str, Any]`
**Gateway 调用**: `agents.list`
**返回**: Dict with `agents` array.

#### `gateway.agents_create(name: str, workspace: str | None = None) -> dict[str, Any]`
**Gateway 调用**: `agents.create`
**参数**: `name` (str), `workspace` (str, optional)
**返回**: Gateway response dict.

#### `gateway.agents_update(agent_id: str, **patch: Any) -> dict[str, Any]`
**Gateway 调用**: `agents.update`
**参数**: `agentId` (str), additional patch fields
**返回**: Gateway response dict.

#### `gateway.agents_delete(agent_id: str) -> dict[str, Any]`
**Gateway 调用**: `agents.delete`
**参数**: `agentId` (str)
**返回**: Gateway response dict.

#### `gateway.agents_files_list(agent_id: str) -> dict[str, Any]`
**Gateway 调用**: `agents.files.list`
**参数**: `agentId` (str)
**返回**: File listing dict.

#### `gateway.agents_files_get(agent_id: str, name: str) -> dict[str, Any]`
**Gateway 调用**: `agents.files.get`
**参数**: `agentId` (str), `name` (str)
**返回**: File content dict.

#### `gateway.agents_files_set(agent_id: str, name: str, content: str) -> dict[str, Any]`
**Gateway 调用**: `agents.files.set`
**参数**: `agentId` (str), `name` (str), `content` (str)
**返回**: Gateway response dict.

#### `gateway.agent_identity_get() -> dict[str, Any]`
**Gateway 调用**: `agent.identity.get`
**返回**: Agent identity dict.

### Approvals Facade

#### `gateway.resolve_approval(request_id: str, decision: str) -> dict[str, Any]`
**Gateway 调用**: `exec.approval.resolve`
**参数**: `id` (str), `decision` (str: `"allow-once"`, `"allow-always"`, `"deny"`)
**返回**: Gateway response dict.

#### `gateway.exec_approval_request(command: str, *, timeout_ms: int | None = None, agent_id: str | None = None, session_key: str | None = None, node_id: str | None = None) -> dict[str, Any]`
**Gateway 调用**: `exec.approval.request`
**返回**: Dict with `id`, `decision`, `createdAtMs`, `expiresAtMs`.

#### `gateway.exec_approval_wait_decision(approval_id: str) -> dict[str, Any]`
**Gateway 调用**: `exec.approval.waitDecision`
**返回**: Dict with decision details.

#### `gateway.exec_approvals_get() -> dict[str, Any]`
**Gateway 调用**: `exec.approvals.get`
**返回**: Dict with `{path, exists, hash, file: {version, socket, defaults, agents}}`.

#### `gateway.exec_approvals_set(file: dict[str, Any], base_hash: str | None = None) -> dict[str, Any]`
**Gateway 调用**: `exec.approvals.set`
**参数**: `file` (dict), `baseHash` (str, optional)
**返回**: Gateway response dict.

### Node Facade

#### `gateway.system_presence() -> dict[str, Any]`
**Gateway 调用**: `system-presence`
**返回**: System-presence status dict.

#### `gateway.node_list() -> list[dict[str, Any]]`
**Gateway 调用**: `node.list`
**返回**: List of node descriptors.

#### `gateway.node_describe(node_id: str) -> dict[str, Any]`
**Gateway 调用**: `node.describe`
**参数**: `id` (str)
**返回**: Node details dict.

#### `gateway.node_invoke(node_id: str, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]`
**Gateway 调用**: `node.invoke`
**参数**: `id` (str), `action` (str), `payload` (dict, optional)
**返回**: Gateway response dict.

#### `gateway.node_rename(node_id: str, display_name: str) -> dict[str, Any]`
**Gateway 调用**: `node.rename`
**参数**: `nodeId` (str), `displayName` (str)
**返回**: Gateway response dict.

#### `gateway.node_pair_request(node_id: str) -> dict[str, Any]`
**Gateway 调用**: `node.pair.request`
**参数**: `nodeId` (str)
**返回**: Gateway response dict.

#### `gateway.node_pair_list() -> dict[str, Any]`
**Gateway 调用**: `node.pair.list`
**返回**: Dict with `pending` and `paired` arrays.

#### `gateway.node_pair_approve(request_id: str) -> dict[str, Any]`
**Gateway 调用**: `node.pair.approve`
**参数**: `requestId` (str)
**返回**: Gateway response dict.

#### `gateway.node_pair_reject(request_id: str) -> dict[str, Any]`
**Gateway 调用**: `node.pair.reject`
**参数**: `requestId` (str)
**返回**: Gateway response dict.

#### `gateway.node_pair_verify(node_id: str, token: str) -> dict[str, Any]`
**Gateway 调用**: `node.pair.verify`
**参数**: `nodeId` (str), `token` (str)
**返回**: Gateway response dict.

### Ops / Logs Facade

#### `gateway.logs_tail() -> dict[str, Any]`
**Gateway 调用**: `logs.tail`
**返回**: Dict with `file`, `cursor`, `size`, `lines`.

#### `gateway.usage_summary() -> dict[str, Any]`
**说明**: Aggregates usage data from `sessions.list`. Not a real RPC method.
**返回**: Dict with `totalInputTokens`, `totalOutputTokens`, `totalTokens`, `sessionCount`.

#### `gateway.usage_status() -> dict[str, Any]`
**Gateway 调用**: `usage.status`
**返回**: Dict with `updatedAt`, `providers`.

#### `gateway.usage_cost() -> dict[str, Any]`
**Gateway 调用**: `usage.cost`
**返回**: Dict with `updatedAt`, `days`, `daily`, `totals`.

#### `gateway.sessions_usage() -> dict[str, Any]`
**Gateway 调用**: `sessions.usage`
**返回**: Dict with per-session usage analytics.

### Device Facade

#### `gateway.device_token_rotate(device_id: str, role: str) -> dict[str, Any]`
**Gateway 调用**: `device.token.rotate`
**参数**: `deviceId` (str), `role` (str)
**返回**: Gateway response dict.

#### `gateway.device_token_revoke(device_id: str, role: str) -> dict[str, Any]`
**Gateway 调用**: `device.token.revoke`
**参数**: `deviceId` (str), `role` (str)
**返回**: Gateway response dict.

#### `gateway.device_pair_list() -> dict[str, Any]`
**Gateway 调用**: `device.pair.list`
**返回**: Dict with `pending` and `paired` arrays.

#### `gateway.device_pair_approve(request_id: str) -> dict[str, Any]`
**Gateway 调用**: `device.pair.approve`
**参数**: `requestId` (str)
**返回**: Gateway response dict.

#### `gateway.device_pair_reject(request_id: str) -> dict[str, Any]`
**Gateway 调用**: `device.pair.reject`
**参数**: `requestId` (str)
**返回**: Gateway response dict.

#### `gateway.device_pair_remove(device_id: str) -> dict[str, Any]`
**Gateway 调用**: `device.pair.remove`
**参数**: `deviceId` (str)
**返回**: Gateway response dict.

### Discovery Facade

#### `gateway.models_list() -> dict[str, Any]`
**Gateway 调用**: `models.list`
**返回**: Dict with `models` array (each with `id`, `name`, `provider`, `contextWindow`, `reasoning`).

#### `gateway.tools_catalog() -> dict[str, Any]`
**Gateway 调用**: `tools.catalog`
**返回**: Dict with `agentId`, `profiles`, `groups`.

#### `gateway.system_status() -> dict[str, Any]`
**Gateway 调用**: `status`
**返回**: Dict with `linkChannel`, `heartbeat`, `channelSummary`, `queuedSystemEvents`, `sessions`.

#### `gateway.doctor_memory_status() -> dict[str, Any]`
**Gateway 调用**: `doctor.memory.status`
**返回**: Dict with `agentId`, `provider`, `embedding` (containing `ok` and optional `error`).

### Skills Facade

#### `gateway.skills_status() -> dict[str, Any]`
**Gateway 调用**: `skills.status`
**返回**: Dict with `workspaceDir`, `managedSkillsDir`, `skills` array.

#### `gateway.skills_bins() -> dict[str, Any]`
**Gateway 调用**: `skills.bins`
**返回**: Skills binary information dict.

#### `gateway.skills_install(name: str, install_id: str) -> dict[str, Any]`
**Gateway 调用**: `skills.install`
**参数**: `name` (str), `installId` (str)
**返回**: Gateway response dict.

#### `gateway.skills_update(skill_key: str) -> dict[str, Any]`
**Gateway 调用**: `skills.update`
**参数**: `skillKey` (str)
**返回**: Gateway response dict.

### TTS Facade

#### `gateway.tts_enable() -> dict[str, Any]`
**Gateway 调用**: `tts.enable`
**返回**: `{enabled: true}`.

#### `gateway.tts_disable() -> dict[str, Any]`
**Gateway 调用**: `tts.disable`
**返回**: `{enabled: false}`.

#### `gateway.tts_convert(text: str) -> dict[str, Any]`
**Gateway 调用**: `tts.convert`
**参数**: `text` (str)
**返回**: Gateway response dict.

#### `gateway.tts_set_provider(provider: str) -> dict[str, Any]`
**Gateway 调用**: `tts.setProvider`
**参数**: `provider` (str: `"openai"`, `"elevenlabs"`, `"edge"`)
**返回**: Gateway response dict.

#### `gateway.tts_status() -> dict[str, Any]`
**Gateway 调用**: `tts.status`
**返回**: TTS status dict.

#### `gateway.tts_providers() -> dict[str, Any]`
**Gateway 调用**: `tts.providers`
**返回**: Available TTS providers dict.

### Wizard Facade

#### `gateway.wizard_start() -> dict[str, Any]`
**Gateway 调用**: `wizard.start`
**返回**: Gateway response dict.

#### `gateway.wizard_next(session_id: str) -> dict[str, Any]`
**Gateway 调用**: `wizard.next`
**参数**: `sessionId` (str)
**返回**: Gateway response dict.

#### `gateway.wizard_cancel(session_id: str) -> dict[str, Any]`
**Gateway 调用**: `wizard.cancel`
**参数**: `sessionId` (str)
**返回**: Gateway response dict.

#### `gateway.wizard_status(session_id: str) -> dict[str, Any]`
**Gateway 调用**: `wizard.status`
**参数**: `sessionId` (str)
**返回**: Wizard session state dict.

### Voice Wake Facade

#### `gateway.voicewake_get() -> dict[str, Any]`
**Gateway 调用**: `voicewake.get`
**返回**: `{triggers: string[]}`.

#### `gateway.voicewake_set(triggers: list[str]) -> dict[str, Any]`
**Gateway 调用**: `voicewake.set`
**参数**: `triggers` (list of trigger strings)
**返回**: Gateway response dict.

### System Facade

#### `gateway.system_event(text: str) -> dict[str, Any]`
**Gateway 调用**: `system-event`
**参数**: `text` (str)
**返回**: Gateway response dict.

#### `gateway.send_message(to: str, idempotency_key: str) -> dict[str, Any]`
**Gateway 调用**: `send`
**参数**: `to` (str), `idempotencyKey` (str)
**返回**: Gateway response dict.

#### `gateway.browser_request(method: str, path: str) -> dict[str, Any]`
**Gateway 调用**: `browser.request`
**参数**: `method` (str), `path` (str)
**返回**: Gateway response dict.

#### `gateway.last_heartbeat() -> dict[str, Any]`
**Gateway 调用**: `last-heartbeat`
**返回**: `{ts, status, reason, durationMs}`.

#### `gateway.set_heartbeats(enabled: bool) -> dict[str, Any]`
**Gateway 调用**: `set-heartbeats`
**参数**: `enabled` (bool)
**返回**: Gateway response dict.

#### `gateway.update_run() -> dict[str, Any]`
**Gateway 调用**: `update.run`
**返回**: Dict with `{ok, result: {status, mode, ...}, restart, sentinel}`.

#### `gateway.secrets_reload() -> dict[str, Any]`
**Gateway 调用**: `secrets.reload`
**返回**: `{ok, warningCount}`.

---

## Constants

**文件**: `openclaw_sdk/core/constants.py`

### AgentStatus

**说明**: String enum for agent runtime status.

| 值 | 说明 |
|----|------|
| `AgentStatus.CREATED` | Agent created |
| `AgentStatus.RUNNING` | Agent running |
| `AgentStatus.IDLE` | Agent idle |
| `AgentStatus.ERROR` | Agent error |
| `AgentStatus.DELETED` | Agent deleted |

### EventType

**说明**: String enum for stream event types.

**SDK-level events** (used in MockGateway and tests):

| 值 | 说明 |
|----|------|
| `EventType.THINKING` | Thinking/reasoning chunk |
| `EventType.TOOL_CALL` | Tool invocation |
| `EventType.TOOL_RESULT` | Tool result |
| `EventType.FILE_GENERATED` | File generated |
| `EventType.CONTENT` | Text content chunk |
| `EventType.ERROR` | Error event |
| `EventType.DONE` | Execution complete |

**Real gateway event types**:

| 值 | 说明 |
|----|------|
| `EventType.AGENT` | Agent stream delta |
| `EventType.CHAT` | Chat state transition |
| `EventType.PRESENCE` | Presence event |
| `EventType.HEALTH` | Health event |
| `EventType.TICK` | Tick event |
| `EventType.HEARTBEAT` | Heartbeat event |
| `EventType.CRON` | Cron event |
| `EventType.SHUTDOWN` | Shutdown event |

### MemoryBackend

**说明**: String enum for memory backend options.

| 值 | 说明 |
|----|------|
| `MemoryBackend.LOCAL` / `"memory"` | In-memory backend |
| `MemoryBackend.REDIS` / `"redis"` | Redis backend |
| `MemoryBackend.QDRANT` / `"qdrant"` | Qdrant backend |
| `MemoryBackend.CHROMA` / `"chroma"` | Chroma backend |
| `MemoryBackend.PGVECTOR` / `"pgvector"` | pgvector backend |

---

## Additional Types

### AgentSummary

**文件**: `openclaw_sdk/core/types.py`

**说明**: Lightweight agent entry from `agents.list`.

| 字段 | 类型 | 说明 |
|------|------|------|
| `agent_id` | `str` | Agent identifier |
| `name` | `str \| None` | Human-readable name |
| `status` | `AgentStatus` | Current status |

### HealthStatus

**文件**: `openclaw_sdk/core/types.py`

**说明**: Gateway health check result.

| 字段 | 类型 | 说明 |
|------|------|------|
| `healthy` | `bool` | Whether gateway is healthy |
| `latency_ms` | `float \| None` | Round-trip latency |
| `version` | `str \| None` | OpenClaw version |
| `details` | `dict[str, Any]` | Additional details |

### AgentListItem

**文件**: `openclaw_sdk/core/types.py`

**说明**: Lightweight agent entry from `agents.list`.

### AgentListResponse

**文件**: `openclaw_sdk/core/types.py`

**说明**: Response from `agents.list`.

| 字段 | 类型 | 说明 |
|------|------|------|
| `default_id` | `str \| None` | Default agent ID |
| `main_key` | `str \| None` | Main session key |
| `scope` | `str \| None` | Scope |
| `agents` | `list[AgentListItem]` | List of agents |

### AgentIdentity

**文件**: `openclaw_sdk/core/types.py`

**说明**: Response from `agent.identity.get`.

| 字段 | 类型 | 说明 |
|------|------|------|
| `agent_id` | `str` | Agent identifier |
| `name` | `str \| None` | Name |
| `avatar` | `str \| None` | Avatar URL |
| `emoji` | `str \| None` | Emoji |

### AgentFileInfo

**文件**: `openclaw_sdk/core/types.py`

**说明**: File metadata from `agents.files.list`.

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | File name |
| `path` | `str \| None` | File path |
| `missing` | `bool` | Whether file is missing |
| `size` | `int \| None` | File size in bytes |
| `updated_at_ms` | `int \| None` | Last updated timestamp |

### AgentFileContent

**文件**: `openclaw_sdk/core/types.py`

**说明**: File with content from `agents.files.get`. Inherits from `AgentFileInfo`.

| 字段 | 类型 | 说明 |
|------|------|------|
| `content` | `str \| None` | File content |

### SessionInfo

**文件**: `openclaw_sdk/core/types.py`

**说明**: Real session object shape from the OpenClaw gateway.

| 字段 | 类型 | 说明 |
|------|------|------|
| `key` | `str` | Session key (e.g. `"agent:main:main"`) |
| `kind` | `str \| None` | Session kind |
| `chat_type` | `str \| None` | Chat type |
| `session_id` | `str \| None` | Session ID |
| `updated_at` | `int \| None` | Last updated timestamp |
| `system_sent` | `bool \| None` | Whether system message was sent |
| `aborted_last_run` | `bool \| None` | Whether last run was aborted |
| `input_tokens` | `int \| None` | Input token count |
| `output_tokens` | `int \| None` | Output token count |
| `total_tokens` | `int \| None` | Total token count |
| `model_provider` | `str \| None` | LLM provider |
| `model` | `str \| None` | Model name |
| `context_tokens` | `int \| None` | Context token count |
| `delivery_context` | `dict[str, Any] \| None` | Delivery context |
| `last_channel` | `str \| None` | Last channel used |

### Attachment

**文件**: `openclaw_sdk/core/types.py`

**说明**: A file attachment sent with a query. Gateway accepts any MIME type.

| 字段 | 类型 | 说明 |
|------|------|------|
| `file_path` | `str` | Path to the file |
| `mime_type` | `str \| None` | MIME type (auto-detected from extension if not set) |
| `name` | `str \| None` | Override file name |
| `content_base64` | `str \| None` | Base64-encoded content (alternative to file_path) |

#### `Attachment.from_path(path: str | Path, mime_type: str | None = None) -> Attachment`
**说明**: Create an `Attachment` from a local file path with auto-detected MIME type.

#### `attachment.to_gateway() -> dict[str, Any]`
**说明**: Serialize to gateway `chat.send` payload format.

**代码示例**:
```python
from openclaw_sdk.core.types import Attachment

att = Attachment.from_path("/path/to/document.pdf")
opts = ExecutionOptions(attachments=[att])
result = await agent.execute("Summarise this document", options=opts)
```
