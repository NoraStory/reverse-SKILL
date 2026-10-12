# Guardrails Reference

All guardrails perform **local validation** on text. They do **not** call the OpenClaw gateway or make external requests. They run synchronously or asynchronously within the local process to inspect strings before agent execution (`check_input`) or after (`check_output`).

---

## `GuardrailResult`

```python
from openclaw_sdk.guardrails.base import GuardrailResult
```

Returned by every guardrail check.

| Field | Type | Description |
|---|---|---|
| `passed` | `bool` | `True` if the check passed; `False` if blocked |
| `guardrail_name` | `str` | Name of the guardrail that produced this result |
| `message` | `str` | Human-readable explanation |
| `modified_text` | `str \| None` | Rewritten content (e.g. PII redaction); `None` when unmodified |

---

## `Guardrail` (Abstract Base)

```python
from openclaw_sdk.guardrails.base import Guardrail
```

Abstract base class. Subclasses must implement both `check_input` and `check_output`.

### Properties

- **`name: str`** — Returns the guardrail name. Defaults to the class name (`type(self).__name__`).

### Methods

- **`check_input(query: str) -> GuardrailResult`** — Validate the input query **before** agent execution. Return `passed=False` to block the agent run.
- **`check_output(response: str) -> GuardrailResult`** — Validate the agent's output **after** execution. Return `passed=False` to reject the response.

---

## `PIIGuardrail`

```python
from openclaw_sdk.guardrails.builtin import PIIGuardrail
```

Detects and optionally redacts personally-identifiable information.

**Detects:** email addresses, US phone numbers, SSNs (xxx-xx-xxxx), and 16-digit credit card numbers.

### Constructor

```python
PIIGuardrail(action: Literal["block", "redact", "warn"] = "block")
```

| Action | Behavior |
|---|---|
| `"block"` (default) | Returns `passed=False` — blocks the query/response |
| `"redact"` | Replaces PII with `[REDACTED]` and returns `passed=True` with `modified_text` set |
| `"warn"` | Returns `passed=True` with a warning message |

### Example

```python
# Block on PII detection
guardrail = PIIGuardrail(action="block")

result = await guardrail.check_input("Send invoice to john.doe@example.com")
print(result.passed)        # False
print(result.message)      # "PII detected (email). Blocked."

# Redact PII instead
guardrail = PIIGuardrail(action="redact")
result = await guardrail.check_input("Contact me at 555-123-4567")

print(result.passed)        # True
print(result.modified_text)  # "Contact me at [REDACTED]"
```

---

## `ContentFilterGuardrail`

```python
from openclaw_sdk.guardrails.builtin import ContentFilterGuardrail
```

Blocks queries or responses that contain any banned word from a configurable list.

### Constructor

```python
ContentFilterGuardrail(
    blocked_words: list[str],
    case_sensitive: bool = False,
)
```

### Example

```python
guardrail = ContentFilterGuardrail(
    blocked_words=["secret", "confidential", "classified"],
    case_sensitive=False,
)

result = await guardrail.check_input("Tell me the secret password")
print(result.passed)  # False
print(result.message)  # "Blocked words detected: secret."

# Case-sensitive mode
guardrail_cs = ContentFilterGuardrail(
    blocked_words=["Secret"],
    case_sensitive=True,
)
result = await guardrail_cs.check_input("Tell me the Secret password")
print(result.passed)  # False
```

---

## `CostLimitGuardrail`

```python
from openclaw_sdk.guardrails.builtin import CostLimitGuardrail
```

Blocks execution when the cumulative session cost (tracked by a `CostTracker`) exceeds the configured budget.

Only the `check_input` check can block — by the time `check_output` runs, cost has already been incurred.

### Constructor

```python
CostLimitGuardrail(
    max_cost_usd: float,
    tracker: CostTracker | None = None,
)
```

If `tracker` is `None`, the guardrail always passes (no cost data available).

### Example

```python
from openclaw_sdk.tracking.cost import CostTracker

tracker = CostTracker()
guardrail = CostLimitGuardrail(max_cost_usd=0.50, tracker=tracker)

# Assuming prior agent calls have accumulated cost
result = await guardrail.check_input("Run another task")
print(result.passed)  # False if total cost >= $0.50
print(result.message)  # e.g. "Cost limit exceeded: $0.5210 >= $0.5000."
```

---

## `MaxTokensGuardrail`

```python
from openclaw_sdk.guardrails.builtin import MaxTokensGuardrail
```

Limits the character count of agent responses. `check_input` always passes.

### Constructor

```python
MaxTokensGuardrail(max_chars: int = 10_000)
```

### Example

```python
guardrail = MaxTokensGuardrail(max_chars=100)

result = await guardrail.check_output("A" * 150)
print(result.passed)  # False
print(result.message)  # "Response too long: 150 chars > 100 max."

result = await guardrail.check_output("Short reply.")
print(result.passed)  # True
print(result.message)  # "Response length OK: 11 chars."
```

---

## `RegexFilterGuardrail`

```python
from openclaw_sdk.guardrails.builtin import RegexFilterGuardrail
```

Custom regex-based blocking. Any pattern match triggers the configured action.

### Constructor

```python
RegexFilterGuardrail(
    patterns: list[str],
    action: Literal["block", "warn"] = "block",
)
```

Patterns are compiled with `re.compile()`. Matching is performed via `pattern.search()`.

### Example

```python
# Block on internal reference pattern
guardrail = RegexFilterGuardrail(
    patterns=[r"REF-\d{6}", r"INTERNAL-ONLY"],
    action="block",
)

result = await guardrail.check_input("The ticket REF-123456 was updated")
print(result.passed)  # False
print(result.message)  # "Regex patterns matched: REF-\d{6}. Blocked."

# Warn-only mode
guardrail = RegexFilterGuardrail(
    patterns=[r"\d{4}-\d{4}-\d{4}-\d{4}"],  # generic card-like pattern
    action="warn",
)
result = await guardrail.check_output("Card: 1234-5678-9012-3456")
print(result.passed)  # True (warn, not block)
print(result.message)  # "Regex patterns matched: ... Warning only."
```
