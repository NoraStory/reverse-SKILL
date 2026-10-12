# TTS (Text-to-Speech) Reference

The SDK provides two tiers of TTS support:

1. **Gateway-based TTS** — via `client.tts` (TTSManager), which proxies to the OpenClaw gateway over WebSocket RPC
2. **Direct API TTS** — via `openclaw_sdk.voice.tts` classes (`OpenAITTS`, `ElevenLabsTTS`), which call third-party TTS APIs directly from your code

---

## Gateway-Based TTS: `client.tts` (TTSManager)

Accessed through `OpenClawClient.tts`. All methods are async and communicate with the OpenClaw gateway.

```python
client = await OpenClawClient.connect()
async with client:
    await client.tts.enable()
    voices = await client.tts.providers()
    result = await client.tts.convert("Hello world")
```

### Methods

| Method | RPC | Description |
|--------|-----|-------------|
| `enable()` | `tts.enable` | Enable TTS |
| `disable()` | `tts.disable` | Disable TTS |
| `convert(text)` | `tts.convert` | Text-to-speech conversion |
| `set_provider(provider)` | `tts.setProvider` | Set TTS provider |
| `status()` | `tts.status` | Get TTS status |
| `providers()` | `tts.providers` | List available providers |

#### `enable()`

Enable TTS on the gateway.

```python
await client.tts.enable()
# Returns: {"enabled": True}
```

#### `disable()`

Disable TTS on the gateway.

```python
await client.tts.disable()
# Returns: {"enabled": False}
```

#### `convert(text)`

Convert text to speech audio.

```python
audio = await client.tts.convert("Hello world")
# Returns: audio data dict from the gateway
```

#### `set_provider(provider)`

Set the active TTS provider. Common providers: `"openai"`, `"elevenlabs"`, `"edge"`.

```python
await client.tts.set_provider("openai")
# Returns: {"ok": True}
```

#### `status()`

Get the current TTS status and configuration.

```python
status = await client.tts.status()
```

#### `providers()`

List all available TTS providers on the gateway.

```python
result = await client.tts.providers()
# Returns: {"providers": [...]}
```

---

## Direct API TTS: `openclaw_sdk.voice.tts`

These classes call third-party TTS APIs directly (via `httpx`), bypassing the OpenClaw gateway. They are useful when you need direct control over the API calls or are running outside a gateway context.

### `TTSProvider` (Abstract Base)

```python
class TTSProvider(abc.ABC):
    async def synthesize(self, text: str, *, voice: str | None = None) -> bytes:
        """Synthesize text into audio bytes."""
```

---

### `OpenAITTS`

Synthesizes speech using the OpenAI `/audio/speech` API.

```python
from openclaw_sdk.voice.tts import OpenAITTS

tts = OpenAITTS(api_key="sk-...", model="tts-1", voice="alloy")
audio_bytes = await tts.synthesize("Hello world")
```

**Constructor Args:**

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `api_key` | `str` | — | OpenAI API key (required) |
| `model` | `str` | `"tts-1"` | TTS model name |
| `voice` | `str` | `"alloy"` | Default voice |
| `base_url` | `str` | `"https://api.openai.com/v1"` | API base URL |

**`synthesize()` Args:**

| Arg | Type | Description |
|-----|------|-------------|
| `text` | `str` | Text to synthesize |
| `voice` | `str \| None` | Voice override (uses default from `__init__` if `None`) |

**Returns:** Raw audio bytes (MP3 by default).

---

### `ElevenLabsTTS`

Synthesizes speech using the ElevenLabs `/text-to-speech/{voice_id}` API.

```python
from openclaw_sdk.voice.tts import ElevenLabsTTS

tts = ElevenLabsTTS(api_key="...", voice_id="21m00Tcm4TlvDq8ikWAM")
audio_bytes = await tts.synthesize("Hello world")
```

**Constructor Args:**

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `api_key` | `str` | — | ElevenLabs API key (required) |
| `voice_id` | `str` | `"21m00Tcm4TlvDq8ikWAM"` | Default voice ID (Rachel) |
| `model_id` | `str` | `"eleven_monolingual_v1"` | Model identifier |
| `base_url` | `str` | `"https://api.elevenlabs.io/v1"` | API base URL |

**`synthesize()` Args:**

| Arg | Type | Description |
|-----|------|-------------|
| `text` | `str` | Text to synthesize |
| `voice` | `str \| None` | Voice ID override (uses default `voice_id` if `None`) |

**Returns:** Raw audio bytes (MP3 by default).

---

## Choosing Between Gateway and Direct TTS

| | `client.tts` | Direct API Classes |
|---|---|---|
| **Transport** | OpenClaw gateway (WebSocket RPC) | HTTPS directly to provider |
| **Requires gateway** | Yes | No |
| **Provider keys** | Configured on gateway | Passed to class constructor |
| **Use case** | Agent voice output, integrated pipeline | Standalone synthesis, custom workflows |
