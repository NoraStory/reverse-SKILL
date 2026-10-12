# Channels Module Reference

**Module**: `openclaw_sdk.channels`
**Source files**:
- `openclaw_sdk/channels/manager.py` — `ChannelManager`
- `openclaw_sdk/channels/sms.py` — `TwilioSMSClient`, `SMSMessage`, `SMSChannelConfig`
- `openclaw_sdk/channels/config.py` — channel configuration models
- `openclaw_sdk/core/constants.py` — `ChannelType` enum

---

## ChannelManager

**文件**: `openclaw_sdk/channels/manager.py`

**说明**: Thin wrapper around gateway channel methods. All methods delegate to the OpenClaw gateway over WebSocket.

### ChannelManager 实例获取

```python
client = await OpenClawClient.connect()
manager = client.channels  # ChannelManager instance
```

### 方法

#### status() -> dict[str, Any]
**说明**: Get status of all configured channels.
**Gateway RPC**: `channels.status`
**参数**: 无

**返回**: `dict` with keys:
- `channelOrder` — list of channel names in order
- `channelLabels` — dict mapping channel name to label
- `channelMeta` — dict of channel metadata
- `channels` — dict mapping channel name to `{configured, linked, ...}` metadata

**代码示例**:
```python
client = await OpenClawClient.connect()
status = await client.channels.status()
print(status["channelOrder"])   # ["telegram", "discord", ...]
print(status["channels"]["telegram"]["linked"])  # True/False
```

#### logout(channel: str) -> bool
**说明**: Log out of the specified channel.
**Gateway RPC**: `channels.logout`
**参数**:
- `channel` — channel name string (e.g. `"whatsapp"`, `"telegram"`)

**返回**: `True` on success.

**代码示例**:
```python
await client.channels.logout("telegram")
```

#### web_login_start() -> dict[str, Any]
**说明**: Start a web-based QR login flow. Returns a QR code as a base64 data URL.
**Gateway RPC**: `web.login.start`
**参数**: 无

**返回**: `dict` with `qrDataUrl` key containing a `data:image/png;base64,...` string.

**代码示例**:
```python
result = await client.channels.web_login_start()
qr_data_url = result["qrDataUrl"]  # base64 PNG data URL
```

#### web_login_wait(timeout_ms: int = 120000) -> dict[str, Any]
**说明**: Wait for QR scan completion during a web login flow.
**Gateway RPC**: `web.login.wait`
**参数**:
- `timeout_ms` — optional timeout in milliseconds (default `120000`, i.e. 2 minutes)

**返回**: `dict` with:
- `connected` — `bool`, `True` if login succeeded
- `message` — `str`, status or error message

**代码示例**:
```python
# Start QR flow
await client.channels.web_login_start()
# Wait up to 60 seconds for scan
result = await client.channels.web_login_wait(timeout_ms=60_000)
print(result["connected"])  # True if scanned successfully
```

#### login() -> dict[str, Any]
**说明**: Alias for `web_login_start()`. Starts a web login flow and returns the QR data URL.
**Gateway RPC**: `web.login.start`

**代码示例**:
```python
result = await client.channels.login()
qr = result["qrDataUrl"]
```

#### request_pairing_code(phone: str | None = None) -> dict[str, Any]
**说明**: Request a numeric pairing code instead of QR code for authentication.
**Gateway RPC**: `web.login.start`
**参数**:
- `phone` — optional phone number in international format (e.g. `"+1234567890"`) for WhatsApp linking

**返回**: `dict`, typically containing a `pairingCode` field.

**代码示例**:
```python
# Request pairing code
result = await client.channels.request_pairing_code()
code = result.get("pairingCode")

# With phone number for WhatsApp
result = await client.channels.request_pairing_code(phone="+1234567890")
```

---

## TwilioSMSClient

**文件**: `openclaw_sdk/channels/sms.py`

**说明**: Async Twilio SMS client using `httpx`. Makes direct calls to the Twilio REST API — does NOT go through the OpenClaw gateway.

### TwilioSMSClient 实例化

```python
from openclaw_sdk.channels.sms import TwilioSMSClient, SMSChannelConfig

config = SMSChannelConfig(
    account_sid="AC...",
    auth_token="...",
    from_number="+1234567890",
    allowed_numbers=["+0987654321"],
)
client = TwilioSMSClient(config)
```

### SMSChannelConfig

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `account_sid` | `str` | — | Twilio Account SID |
| `auth_token` | `str` | — | Twilio Auth Token |
| `from_number` | `str` | — | Sender phone number |
| `allowed_numbers` | `list[str]` | `[]` | Whitelist of recipient numbers |
| `max_message_length` | `int` | `1600` | Max SMS body length |

### SMSMessage

**说明**: Pydantic model representing a sent or received SMS message.

| 字段 | 类型 | 说明 |
|------|------|------|
| `sid` | `str` | Twilio Message SID |
| `from_number` | `str` | Sender phone number |
| `to_number` | `str` | Recipient phone number |
| `body` | `str` | Message body text |
| `status` | `str` | Twilio message status |

### 方法

#### send_message(to: str, body: str) -> SMSMessage
**说明**: Send an SMS message via the Twilio REST API.
**参数**:
- `to` — recipient phone number
- `body` — message body (auto-truncated to `max_message_length`)

**返回**: `SMSMessage` instance.

**Raises**: `ValueError` if `to` is not in `allowed_numbers` (if list is non-empty).

**代码示例**:
```python
sms_client = TwilioSMSClient(config)
message = await sms_client.send_message("+0987654321", "Hello from OpenClaw!")
print(message.sid, message.status)
```

#### parse_incoming_webhook(data: dict[str, Any]) -> SMSMessage  (staticmethod)
**说明**: Parse an incoming Twilio webhook payload into an `SMSMessage`. This is a static method that does not make API calls.
**参数**:
- `data` — Twilio webhook POST data dict (keys: `MessageSid`, `From`, `To`, `Body`, `SmsStatus`)

**返回**: `SMSMessage` instance.

**代码示例**:
```python
# In your Flask/FastAPI webhook handler:
from openclaw_sdk.channels.sms import TwilioSMSClient

@app.route("/webhook/twilio", methods=["POST"])
async def twilio_webhook():
    msg = TwilioSMSClient.parse_incoming_webhook(dict(request.form))
    print(f"From: {msg.from_number}, Body: {msg.body}")
    return "OK", 200
```

---

## Channel Configs

**文件**: `openclaw_sdk/channels/config.py`

### Base Classes

#### ChannelConfig
**说明**: Base Pydantic model for all channel configs.

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `channel_type` | `ChannelType` | — | Channel type enum value |
| `enabled` | `bool` | `True` | Whether channel is active |
| `config` | `dict[str, Any]` | `{}` | Generic config dict |

#### WhatsAppChannelConfig
**说明**: WhatsApp channel configuration. Inherits from `ChannelConfig`.

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `channel_type` | `ChannelType` | `WHATSAPP` | Fixed |
| `dm_policy` | `Literal["all", "contacts", "allowlist"]` | `"contacts"` | DM policy |
| `allow_from` | `list[str]` | `[]` | Allowed phone numbers |
| `auto_reconnect` | `bool` | `True` | Auto reconnect on disconnect |
| `metadata` | `dict[str, Any]` | `{}` | Custom metadata |

**代码示例**:
```python
from openclaw_sdk.channels.config import WhatsAppChannelConfig

cfg = WhatsAppChannelConfig(
    dm_policy="allowlist",
    allow_from=["+1234567890"],
    auto_reconnect=True,
)
```

#### TelegramChannelConfig
**说明**: Telegram channel configuration. Inherits from `ChannelConfig`.

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `channel_type` | `ChannelType` | `TELEGRAM` | Fixed |
| `dm_policy` | `Literal["all", "contacts", "allowlist"]` | `"all"` | DM policy |
| `allow_from` | `list[str]` | `[]` | Allowed Telegram user IDs |
| `auto_reconnect` | `bool` | `True` | Auto reconnect |

#### DiscordChannelConfig
**说明**: Discord channel configuration. Inherits from `ChannelConfig`.

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `channel_type` | `ChannelType` | `DISCORD` | Fixed |
| `dm_policy` | `Literal["all", "contacts", "allowlist"]` | `"contacts"` | DM policy |
| `allow_from` | `list[str]` | `[]` | Allowed Discord guild member IDs |
| `guild_id` | `str \| None` | `None` | Optional guild ID |

#### SlackChannelConfig
**说明**: Slack channel configuration. Inherits from `ChannelConfig`.

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `channel_type` | `ChannelType` | `SLACK` | Fixed |
| `dm_policy` | `Literal["all", "contacts", "allowlist"]` | `"contacts"` | DM policy |
| `allow_from` | `list[str]` | `[]` | Allowed Slack team/user IDs |
| `team_id` | `str \| None` | `None` | Optional Slack team ID |

#### GenericChannelConfig
**说明**: Generic/custom channel configuration. Inherits from `ChannelConfig`.

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `channel_type` | `ChannelType` | `CUSTOM` | Fixed |
| `channel_name` | `str` | `""` | Name for the custom channel |

---

## ChannelType Enum

**文件**: `openclaw_sdk/core/constants.py`

**说明**: String enum representing supported messaging channel types.

```python
from openclaw_sdk.core.constants import ChannelType
```

**可用值**:

| 值 | 说明 |
|----|------|
| `ChannelType.WHATSAPP` | WhatsApp messenger |
| `ChannelType.TELEGRAM` | Telegram |
| `ChannelType.DISCORD` | Discord |
| `ChannelType.SLACK` | Slack |
| `ChannelType.SIGNAL` | Signal |
| `ChannelType.IMESSAGE` | Apple iMessage |
| `ChannelType.SMS` | Generic SMS |
| `ChannelType.TEAMS` | Microsoft Teams |
| `ChannelType.GOOGLE_CHAT` | Google Chat |
| `ChannelType.MATRIX` | Matrix/Element |
| `ChannelType.ZALO` | Zalo (Vietnam) |
| `ChannelType.CUSTOM` | Custom/user-defined channel |

**代码示例**:
```python
from openclaw_sdk.core.constants import ChannelType

print(ChannelType.WHATSAPP)   # "whatsapp"
print(ChannelType.TELEGRAM)    # "telegram"
```
