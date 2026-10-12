# Alerting Module

The `openclaw_sdk.alerting` module provides local alerting capabilities for monitoring agent execution. It evaluates rules against execution results and dispatches alerts to configured sinks.

**Important**: Alerting is local-only. It does **not** call the OpenClaw gateway. Alerts are evaluated and dispatched entirely within your application process.

---

## AlertManager

`openclaw_sdk.alerting.manager.AlertManager`

The central coordinator that evaluates rules against execution results and dispatches alerts to sinks. Uses a builder-style API for fluent configuration.

### Methods

#### `add_rule(rule: AlertRule) -> AlertManager`
Adds a rule to evaluate on each execution result. Returns self for chaining.

#### `add_sink(sink: AlertSink) -> AlertManager`
Adds a sink for alert delivery. Returns self for chaining.

#### `set_cooldown(seconds: float) -> AlertManager`
Sets the per-rule cooldown period in seconds. If a rule fires again within this window, the alert is suppressed. Default is 60 seconds.

#### `evaluate(agent_id: str, result: ExecutionResult) -> list[Alert]`
Evaluates all rules against the result and dispatches any alerts. Returns a list of alerts that were actually fired (not suppressed by cooldown).

### Example

```python
from openclaw_sdk.alerting.manager import AlertManager
from openclaw_sdk.alerting.rules import CostThresholdRule, LatencyThresholdRule
from openclaw_sdk.alerting.sinks import LogAlertSink, SlackAlertSink

manager = (
    AlertManager()
    .add_rule(CostThresholdRule(threshold_usd=0.10))
    .add_rule(LatencyThresholdRule(threshold_ms=5000))
    .add_sink(LogAlertSink())
    .add_sink(SlackAlertSink(webhook_url="https://hooks.slack.com/services/..."))
    .set_cooldown(30.0)
)

# After agent execution:
alerts = await manager.evaluate("agent-001", execution_result)
```

---

## Alert Rules

All alert rules inherit from `openclaw_sdk.alerting.rules.AlertRule` and implement the `name` property and `evaluate` method.

### Base Class

```python
class AlertRule(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def evaluate(self, agent_id: str, result: ExecutionResult) -> Alert | None: ...
```

### CostThresholdRule

`openclaw_sdk.alerting.rules.CostThresholdRule`

Fires when the estimated execution cost exceeds a USD threshold. Cost is calculated from token usage: `(input + output) / 1_000_000 * rate`. Default rate is $10/M tokens.

```python
CostThresholdRule(
    threshold_usd: float,
    severity: AlertSeverity = AlertSeverity.WARNING,
    rate_per_million: float = 10.0,
)
```

**Example:**
```python
rule = CostThresholdRule(threshold_usd=0.05, severity=AlertSeverity.CRITICAL)
```

### LatencyThresholdRule

`openclaw_sdk.alerting.rules.LatencyThresholdRule`

Fires when execution latency exceeds the configured threshold in milliseconds.

```python
LatencyThresholdRule(
    threshold_ms: int,
    severity: AlertSeverity = AlertSeverity.WARNING,
)
```

**Example:**
```python
rule = LatencyThresholdRule(threshold_ms=3000)
```

### ErrorRateRule

`openclaw_sdk.alerting.rules.ErrorRateRule`

Fires when the error rate exceeds a threshold within a sliding window. Maintains a fixed-size window of recent results (True = success, False = failure).

```python
ErrorRateRule(
    threshold: float = 0.5,      # Failure rate threshold (0.0 to 1.0)
    window_size: int = 10,       # Number of results to track
    severity: AlertSeverity = AlertSeverity.CRITICAL,
)
```

**Example:**
```python
# Fire when more than 30% of last 20 executions failed
rule = ErrorRateRule(threshold=0.3, window_size=20)
```

### ConsecutiveFailureRule

`openclaw_sdk.alerting.rules.ConsecutiveFailureRule`

Fires after N consecutive failures. Resets on success.

```python
ConsecutiveFailureRule(
    threshold: int = 3,
    severity: AlertSeverity = AlertSeverity.CRITICAL,
)
```

**Example:**
```python
# Fire after 5 consecutive failures
rule = ConsecutiveFailureRule(threshold=5)
```

---

## Alert Sinks

All sinks inherit from `openclaw_sdk.alerting.sinks.AlertSink` and implement the `send` method.

### Base Class

```python
class AlertSink(ABC):
    @abstractmethod
    async def send(self, alert: Alert) -> bool:
        """Return True on success, False on failure."""
        ...
```

### LogAlertSink

`openclaw_sdk.alerting.sinks.LogAlertSink`

Logs alerts via structlog. Always available, no external dependencies. Logs at `warning` level with alert details.

```python
sink = LogAlertSink()
```

### WebhookAlertSink

`openclaw_sdk.alerting.sinks.WebhookAlertSink`

Sends alerts via HTTP POST to an arbitrary URL using httpx.

```python
WebhookAlertSink(
    url: str,                          # Target URL for POST request
    headers: dict[str, str] | None = None,  # Optional HTTP headers
)
```

**Example:**
```python
sink = WebhookAlertSink(
    url="https://example.com/webhook",
    headers={"Authorization": "Bearer token123"},
)
```

### SlackAlertSink

`openclaw_sdk.alerting.sinks.SlackAlertSink`

Sends alerts to Slack via an incoming webhook URL. Formats the alert as a Slack message with severity emoji.

```python
SlackAlertSink(webhook_url: str)
```

Severity emoji mapping:
- `info`: :information_source:
- `warning`: :warning:
- `critical`: :rotating_light:

**Example:**
```python
sink = SlackAlertSink(webhook_url="https://hooks.slack.com/services/T.../B.../xxx")
```

### PagerDutyAlertSink

`openclaw_sdk.alerting.sinks.PagerDutyAlertSink`

Sends alerts to PagerDuty Events API v2.

```python
PagerDutyAlertSink(routing_key: str)  # PagerDuty Integration Key
```

Uses `openclaw-{rule_name}-{agent_id}` as the dedup_key.

**Example:**
```python
sink = PagerDutyAlertSink(routing_key="your-integration-key")
```

---

## Alert Models

### AlertSeverity

`openclaw_sdk.alerting.models.AlertSeverity`

StrEnum with three levels:

| Value | Description |
|-------|-------------|
| `INFO` | Informational alert |
| `WARNING` | Warning condition |
| `CRITICAL` | Critical condition |

### Alert

`openclaw_sdk.alerting.models.Alert`

Pydantic model representing an alert.

```python
class Alert(BaseModel):
    alert_id: str              # Auto-generated unique ID (12 hex chars)
    severity: AlertSeverity    # Alert severity level
    title: str                  # Brief summary
    message: str                # Detailed description
    agent_id: str | None        # Optional agent that triggered the alert
    rule_name: str              # Name of the rule that generated this alert
    timestamp: datetime        # When alert was generated (UTC)
    metadata: dict[str, Any]   # Arbitrary extra context
```

---

## Complete Example

```python
import asyncio
from openclaw_sdk.alerting.manager import AlertManager
from openclaw_sdk.alerting.rules import (
    CostThresholdRule,
    LatencyThresholdRule,
    ErrorRateRule,
    ConsecutiveFailureRule,
)
from openclaw_sdk.alerting.sinks import LogAlertSink, SlackAlertSink, PagerDutyAlertSink
from openclaw_sdk.alerting.models import AlertSeverity
from openclaw_sdk.core.types import ExecutionResult, TokenUsage

async def main():
    manager = (
        AlertManager()
        .add_rule(CostThresholdRule(threshold_usd=0.10))
        .add_rule(LatencyThresholdRule(threshold_ms=5000))
        .add_rule(ErrorRateRule(threshold=0.5, window_size=20))
        .add_rule(ConsecutiveFailureRule(threshold=3))
        .add_sink(LogAlertSink())
        .add_sink(SlackAlertSink(webhook_url="https://hooks.slack.com/services/..."))
        .add_sink(PagerDutyAlertSink(routing_key="your-pagerduty-key"))
        .set_cooldown(60.0)
    )

    # Simulate execution result
    result = ExecutionResult(
        success=False,
        content="Error: Task failed to complete",
        latency_ms=6500,
        token_usage=TokenUsage(input=50000, output=30000),
    )

    alerts = await manager.evaluate("agent-001", result)
    print(f"Fired {len(alerts)} alerts")

asyncio.run(main())
```
