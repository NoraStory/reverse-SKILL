# Voice Module

The `openclaw_sdk.voice` module provides a three-stage voice pipeline (STT -> Agent -> TTS) and concrete provider implementations for speech-to-text and text-to-speech.

**Important:** All STT and TTS providers make **direct HTTP calls to third-party APIs** (OpenAI, Deepgram, ElevenLabs) — they do **not** route through the OpenClaw gateway. API keys for these providers must be provided directly to each provider class.

---

## VoicePipeline

**File:** `openclaw_sdk/voice/pipeline.py`

Chains an STT provider, an OpenClaw agent, and an optional TTS provider into a single `process()` call.

### `__init__(agent, stt, tts)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent` | `_AgentLike` | An object with `async execute(query) -> ExecutionResult`. |
| `stt` | `STTProvider` | A speech-to-text provider instance. |
| `tts` | `TTSProvider \| None` | Optional text-to-speech provider. When `None`, the pipeline returns text-only results. |

### `process(audio_bytes, language, synthesize)`

Runs the full pipeline and returns a `VoiceResult`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio_bytes` | `bytes` | — | Raw input audio to transcribe. |
| `language` | `str \| None` | `None` | Optional BCP-47 language hint passed to the STT provider (e.g., `"en"`). |
| `synthesize` | `bool` | `True` | Whether to run TTS on the agent response. Ignored when no TTS provider is configured. |

**Returns:** `VoiceResult` with fields:
- `transcript: str` — transcribed text from audio
- `agent_response: str` — agent's textual response
- `audio_bytes: bytes \| None` — synthesized audio, or `None` if TTS was skipped
- `latency_ms: int` — end-to-end latency in milliseconds

**Pipeline stages:**
1. STT — `stt.transcribe(audio_bytes, language=language)`
2. Agent — `agent.execute(transcript)`
3. TTS — `tts.synthesize(agent_response)` (when `synthesize=True` and TTS is configured)

### Example

```python
from openclaw_sdk.voice import VoicePipeline, WhisperSTT, OpenAITTS

pipeline = VoicePipeline(
    agent=agent,
    stt=WhisperSTT(api_key="sk-..."),
    tts=OpenAITTS(api_key="sk-..."),
)

result = await pipeline.process(audio_bytes)
print(result.transcript)        # "What is the weather?"
print(result.agent_response)    # "It's sunny in San Francisco."
print(len(result.audio_bytes))  # 24576
```

---

## STT Providers

**File:** `openclaw_sdk/voice/stt.py`

All STT providers are async and make **direct HTTPS calls** to the provider's API. They do not use the OpenClaw gateway.

### `STTProvider` (abstract base)

```python
class STTProvider(abc.ABC):
    async def transcribe(self, audio_bytes: bytes, *, language: str | None = None) -> str
```

---

### WhisperSTT

**API:** OpenAI Whisper — `POST /audio/transcriptions`

Uses the OpenAI Whisper API directly via HTTPS.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | — | **Required.** OpenAI API key. |
| `model` | `str` | `"whisper-1"` | Whisper model name. |
| `base_url` | `str` | `"https://api.openai.com/v1"` | API base URL. |

```python
from openclaw_sdk.voice import WhisperSTT

stt = WhisperSTT(api_key="sk-...")
text = await stt.transcribe(audio_bytes, language="en")
```

---

### DeepgramSTT

**API:** Deepgram Nova — `POST /listen`

Uses the Deepgram API directly via HTTPS.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | — | **Required.** Deepgram API key. |
| `model` | `str` | `"nova-2"` | Deepgram model name. |
| `base_url` | `str` | `"https://api.deepgram.com/v1"` | API base URL. |

```python
from openclaw_sdk.voice import DeepgramSTT

stt = DeepgramSTT(api_key="your-deepgram-key")
text = await stt.transcribe(audio_bytes, language="en")
```

---

## TTS Providers

**File:** `openclaw_sdk/voice/tts.py`

All TTS providers are async and make **direct HTTPS calls** to the provider's API. They do not use the OpenClaw gateway.

### `TTSProvider` (abstract base)

```python
class TTSProvider(abc.ABC):
    async def synthesize(self, text: str, *, voice: str | None = None) -> bytes
```

---

### OpenAITTS

**API:** OpenAI TTS — `POST /audio/speech`

Uses the OpenAI TTS API directly via HTTPS.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | — | **Required.** OpenAI API key. |
| `model` | `str` | `"tts-1"` | TTS model name. |
| `voice` | `str` | `"alloy"` | Default voice identifier. |
| `base_url` | `str` | `"https://api.openai.com/v1"` | API base URL. |

Available voices: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`.

```python
from openclaw_sdk.voice import OpenAITTS

tts = OpenAITTS(api_key="sk-...")
audio = await tts.synthesize("Hello, world!", voice="alloy")
```

To override the default voice per call:

```python
audio = await tts.synthesize("Hello, world!", voice="nova")
```

---

### ElevenLabsTTS

**API:** ElevenLabs — `POST /text-to-speech/{voice_id}`

Uses the ElevenLabs API directly via HTTPS.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | — | **Required.** ElevenLabs API key. |
| `voice_id` | `str` | `"21m00Tcm4TlvDq8ikWAM"` | Default voice ID (Rachel). |
| `model_id` | `str` | `"eleven_monolingual_v1"` | Model identifier. |
| `base_url` | `str` | `"https://api.elevenlabs.io/v1"` | API base URL. |

```python
from openclaw_sdk.voice import ElevenLabsTTS

tts = ElevenLabsTTS(api_key="your-elevenlabs-key")
audio = await tts.synthesize("Hello, world!")
```

To override the voice per call:

```python
audio = await tts.synthesize("Hello, world!", voice="your-voice-id")
```

---

## API Key Requirements Summary

| Provider | API Called Directly | Key Environment Variable |
|----------|---------------------|--------------------------|
| `WhisperSTT` | OpenAI Whisper API | `OPENAI_API_KEY` |
| `DeepgramSTT` | Deepgram Nova API | `DEEPGRAM_API_KEY` |
| `OpenAITTS` | OpenAI TTS API | `OPENAI_API_KEY` |
| `ElevenLabsTTS` | ElevenLabs API | `ELEVENLABS_API_KEY` |
