# Scheduling Module Reference

> All code examples tested against the OpenClaw gateway.

## Overview

The `scheduling` module (`openclaw_sdk.scheduling`) provides cron-style job scheduling via the `ScheduleManager` class. All business logic lives in the OpenClaw gateway; this module only translates Python calls into gateway RPC calls.

**Source:** `src/openclaw_sdk/scheduling/manager.py`

**Import:**
```python
from openclaw_sdk.scheduling.manager import ScheduleManager, ScheduleConfig, CronJob
# or via client
client = await OpenClawClient.connect()
sm = client.scheduling  # returns ScheduleManager
```

---

## Models

### ScheduleConfig

Input model for creating a new cron job. Field names match the real OpenClaw gateway API.

```python
class ScheduleConfig(BaseModel):
    name: str                          # Job display name
    schedule: str                      # Cron expression, e.g. "0 9 * * *"
    session_target: str                # Session key like "agent:main:main"
    payload: str                       # Message string sent when job fires
    enabled: bool = True               # Whether the job is active
    model_config = {"populate_by_name": True}
```

**Example:**
```python
config = ScheduleConfig(
    name="daily-report",
    schedule="0 9 * * *",          # 9 AM every day
    session_target="agent:main:main",
    payload="Generate the daily sales report",
    enabled=True,
)
```

**Important notes from source code:**
- `schedule` is the cron expression string (not `cron_expression`)
- `session_target` is the session key like `"agent:main:main"` (not `agent_id`)
- `payload` is the message string (not `query`)

---

### CronJob

Returned by gateway after creating or listing jobs.

```python
class CronJob(BaseModel):
    id: str | None = None
    name: str
    schedule: str | dict[str, Any]        # Cron expression or schedule object
    session_target: str = Field(alias="sessionTarget", default="")
    payload: str | dict[str, Any] = ""     # Message string or payload object
    enabled: bool = True
    last_run: int | None = Field(default=None, alias="lastRun")
    next_run: int | None = Field(default=None, alias="nextRun")
    model_config = {"populate_by_name": True}
```

---

## ScheduleManager Methods

### `list_schedules()`

**RPC:** `cron.list`

List all cron jobs registered with the gateway.

```python
async def list_schedules(self) -> list[CronJob]
```

**Returns:** `list[CronJob]` — all registered cron jobs.

**Example:**
```python
jobs = await sm.list_schedules()
for job in jobs:
    print(f"{job.name}: {job.schedule} (enabled={job.enabled})")
```

---

### `cron_status()`

**RPC:** `cron.status`

Get scheduler engine status.

```python
async def cron_status(self) -> dict[str, Any]
```

**Returns:** `dict[str, Any]` — raw gateway response with scheduler state.

**Example:**
```python
status = await sm.cron_status()
print(status)
```

---

### `create_schedule(config)`

**RPC:** `cron.add`

Create a new cron job.

```python
async def create_schedule(self, config: ScheduleConfig) -> CronJob
```

**Parameters:**
- `config: ScheduleConfig` — job configuration

**Returns:** `CronJob` — the created job with gateway-assigned `id`.

**Example:**
```python
config = ScheduleConfig(
    name="morning-briefing",
    schedule="0 8 * * 1-5",       # 8 AM, Monday to Friday
    session_target="agent:main:main",
    payload="Give me the morning news summary",
    enabled=True,
)
job = await sm.create_schedule(config)
print(f"Created job with id: {job.id}")
```

**Internal transformation (from source):**
- `schedule` string is converted to `{"kind": "cron", "expr": config.schedule}`
- `payload` string is converted to `{"message": config.payload}`

---

### `update_schedule(job_id, patch)`

**RPC:** `cron.update`

Update an existing cron job.

```python
async def update_schedule(self, job_id: str, patch: dict[str, Any]) -> dict[str, Any]
```

**Parameters:**
- `job_id: str` — the job ID to update
- `patch: dict[str, Any]` — partial fields to update

**Returns:** `dict[str, Any]` — raw gateway response.

**Example:**
```python
# Disable a job
result = await sm.update_schedule(job_id, {"enabled": False})

# Change schedule
result = await sm.update_schedule(job_id, {"schedule": "0 10 * * *"})
```

---

### `delete_schedule(job_id)`

**RPC:** `cron.remove`

Delete a cron job.

```python
async def delete_schedule(self, job_id: str) -> bool
```

**Parameters:**
- `job_id: str` — the job ID to delete

**Returns:** `True` on success.

**Example:**
```python
await sm.delete_schedule(job_id)
print("Job deleted")
```

---

### `run_now(job_id)`

**RPC:** `cron.run`

Trigger a cron job immediately (outside its schedule).

```python
async def run_now(self, job_id: str) -> dict[str, Any]
```

**Parameters:**
- `job_id: str` — the job ID to run

**Returns:** `dict[str, Any]` — raw gateway response.

**Example:**
```python
result = await sm.run_now(job_id)
print(f"Run triggered: {result}")
```

---

### `get_runs(job_id)`

**RPC:** `cron.runs`

Get execution history for a cron job.

```python
async def get_runs(self, job_id: str) -> list[dict[str, Any]]
```

**Parameters:**
- `job_id: str` — the job ID

**Returns:** `list[dict[str, Any]]` — list of run records from the gateway.

**Example:**
```python
runs = await sm.get_runs(job_id)
for run in runs:
    print(f"Run at {run.get('timestamp')}: {run.get('status')}")
```

---

### `wake(mode, text)`

**RPC:** `wake`

Wake or interrupt the agent/scheduler.

```python
async def wake(self, mode: str = "now", text: str = "") -> dict[str, Any]
```

**Parameters:**
- `mode: str` — wake mode (e.g. `"now"`)
- `text: str` — optional text/payload to send with wake

**Returns:** `dict[str, Any]` — raw gateway response.

**Example:**
```python
result = await sm.wake(mode="now", text="ping")
print(f"Wake result: {result}")
```

---

## Full Workflow Example

```python
import asyncio
from openclaw_sdk import OpenClawClient
from openclaw_sdk.scheduling.manager import ScheduleConfig

async def main():
    client = await OpenClawClient.connect()
    sm = client.scheduling

    # Check scheduler status
    status = await sm.cron_status()
    print(f"Scheduler: {status}")

    # List existing jobs
    jobs = await sm.list_schedules()
    print(f"Found {len(jobs)} existing jobs")

    # Create a new job
    config = ScheduleConfig(
        name="daily-report",
        schedule="0 9 * * *",
        session_target="agent:main:main",
        payload="Generate the daily sales report",
        enabled=True,
    )
    job = await sm.create_schedule(config)
    print(f"Created job: {job.id}")

    # Trigger it immediately
    await sm.run_now(job.id)

    # Check runs
    runs = await sm.get_runs(job.id)
    print(f"Run history: {runs}")

    # Disable the job
    await sm.update_schedule(job.id, {"enabled": False})

    # Clean up
    await sm.delete_schedule(job.id)

    await client.close()

asyncio.run(main())
```

---

## RPC Method Map

| Python Method | Gateway RPC | Description |
|---------------|-------------|-------------|
| `list_schedules()` | `cron.list` | List all cron jobs |
| `cron_status()` | `cron.status` | Get scheduler status |
| `create_schedule(config)` | `cron.add` | Create a new cron job |
| `update_schedule(job_id, patch)` | `cron.update` | Update a cron job |
| `delete_schedule(job_id)` | `cron.remove` | Delete a cron job |
| `run_now(job_id)` | `cron.run` | Trigger job immediately |
| `get_runs(job_id)` | `cron.runs` | Get execution history |
| `wake(mode, text)` | `wake` | Wake/interrupt agent |
