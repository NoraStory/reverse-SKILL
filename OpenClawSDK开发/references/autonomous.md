# autonomous Module Reference

The `openclaw_sdk.autonomous` module provides building blocks for autonomous goal pursuit: iterative execution loops, multi-agent routing, budget enforcement, and safety watchdog monitoring.

**Source files:**
- `src/openclaw_sdk/autonomous/goal_loop.py`
- `src/openclaw_sdk/autonomous/orchestrator.py`
- `src/openclaw_sdk/autonomous/watchdog.py`
- `src/openclaw_sdk/autonomous/models.py`

---

## GoalLoop

Iterative agent execution until a success predicate passes or the budget is exhausted.

**Import:** `from openclaw_sdk.autonomous.goal_loop import GoalLoop`

### Constructor

```python
GoalLoop(
    agent,
    goal,
    budget,
    *,
    success_predicate=None,
    on_step=None,
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent` | `_AgentLike` | An `Agent` (or any object with `async execute(query) -> ExecutionResult`). Satisfies the `_AgentLike` protocol. |
| `goal` | `Goal` | The `Goal` to pursue. |
| `budget` | `Budget` | Resource budget governing limits. |
| `success_predicate` | `Callable[[ExecutionResult], bool] \| None` | Optional predicate checked against each execution result. If `None`, succeeds on first successful execution. |
| `on_step` | `Callable[[int, ExecutionResult], None] \| None` | Optional callback invoked after every iteration with step number and result. |

### Methods

#### `run() -> Goal`

Executes the goal loop and returns the updated `Goal`. The goal's `status` and `result` fields are mutated in place.

**Execution flow:**
1. Sets `goal.status = GoalStatus.IN_PROGRESS`
2. Iterates up to `goal.max_steps` times:
   - Calls `watchdog.check()` — stops if `WATCHDOG_ACTION.STOP`
   - Calls `agent.execute(goal.description)`
   - Updates `budget.duration_spent`, `budget.tokens_spent`, `budget.tool_calls_spent`
   - Invokes `on_step` callback if provided
   - Checks `result.success` — continues on failure
   - Checks `success_predicate` (or succeeds immediately if not provided)
3. On success: `goal.status = GoalStatus.COMPLETED`, `goal.result = result.content`
4. On budget exhaustion or error: `goal.status = GoalStatus.FAILED`
5. On max steps reached without success: `goal.status = GoalStatus.FAILED`

**Example:**

```python
import asyncio
from openclaw_sdk import OpenClawClient
from openclaw_sdk.autonomous.models import Budget, Goal, GoalStatus
from openclaw_sdk.autonomous.goal_loop import GoalLoop

async def main():
    client = await OpenClawClient.connect()
    agent = client.get_agent("my-agent")

    goal = Goal(description="List all files in /tmp", max_steps=5)
    budget = Budget(max_tool_calls=20, max_tokens=5000)

    loop = GoalLoop(agent, goal, budget)
    completed = await loop.run()

    print(completed.status, completed.result)
    await client.close()

asyncio.run(main())
```

---

## Orchestrator

Manages goal execution across a pool of registered agents with skill-based routing.

**Import:** `from openclaw_sdk.autonomous.orchestrator import Orchestrator`

### Constructor

```python
Orchestrator(client: "OpenClawClient")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `client` | `OpenClawClient` | The SDK client used to retrieve agent instances. |

### Methods

#### `register_agent(agent_id: str, description: str = "", skills: list[str] | None = None) -> None`

Registers an agent's capabilities for routing.

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | `str` | Unique agent identifier. |
| `description` | `str` | Human-readable description of the agent. |
| `skills` | `list[str] \| None` | Skill keywords for goal matching. |

#### `route_goal(goal: Goal) -> str | None`

Scores all registered agents by keyword overlap with the goal description (case-insensitive substring match) and returns the highest-scoring `agent_id`. Returns `None` if no agent has any matching skills.

| Parameter | Type | Description |
|-----------|------|-------------|
| `goal` | `Goal` | The goal to route. |

**Returns:** `agent_id` of best match, or `None`.

#### `execute_goal(goal: Goal, budget: Budget, *, agent_override: str | None = None, success_predicate: Callable[[ExecutionResult], bool] | None = None) -> Goal`

Routes a goal to the best-matching agent (or uses `agent_override` if provided) and executes it via `GoalLoop`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `goal` | `Goal` | The goal to execute. |
| `budget` | `Budget` | Resource budget for execution. |
| `agent_override` | `str \| None` | Optional explicit agent ID, bypassing routing. |
| `success_predicate` | `Callable[[ExecutionResult], bool] \| None` | Optional predicate passed to `GoalLoop`. |

**Returns:** Updated `Goal` after execution.

**Raises:** `ValueError` if no agent can be determined.

**Example:**

```python
import asyncio
from openclaw_sdk.autonomous.models import Budget, Goal
from openclaw_sdk.autonomous.orchestrator import Orchestrator
from openclaw_sdk import OpenClawClient

async def main():
    client = OpenClawClient()
    orch = Orchestrator(client)

    orch.register_agent("researcher", "Deep research", ["research", "analysis"])
    orch.register_agent("writer", "Content writing", ["writing", "editing"])

    goal = Goal(description="Research AI safety papers")
    result = await orch.execute_goal(goal, Budget(max_tokens=10000))
    print(result.status, result.result)

asyncio.run(main())
```

---

## Watchdog

Safety constraints checker that monitors a `Budget` and returns an action indicating whether execution should continue, warn, or stop.

**Import:** `from openclaw_sdk.autonomous.watchdog import Watchdog, WatchdogAction`

### WatchdogAction Enum

| Value | Description |
|-------|-------------|
| `CONTINUE` | Execution may continue normally. |
| `WARN` | A resource limit is over 80% consumed; a warning is logged. |
| `STOP` | The budget is exhausted; execution should stop. |

### Constructor

```python
Watchdog(budget: Budget)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `budget` | `Budget` | The budget to monitor. |

### Methods

#### `check() -> WatchdogAction`

Checks all non-None budget limits and returns the recommended action:

- `STOP` if `budget.is_exhausted` is `True`
- `WARN` if any limit is at least 80% consumed
- `CONTINUE` otherwise

**Example:**

```python
from openclaw_sdk.autonomous.models import Budget
from openclaw_sdk.autonomous.watchdog import Watchdog, WatchdogAction

budget = Budget(max_tool_calls=10)
watchdog = Watchdog(budget)

action = watchdog.check()
if action == WatchdogAction.STOP:
    print("Budget exhausted, stopping")
elif action == WatchdogAction.WARN:
    print("Warning: over 80% of limit consumed")
else:
    print("Continuing")
```

---

## Budget

Pydantic model representing resource limits and consumption tracking for autonomous execution.

**Import:** `from openclaw_sdk.autonomous.models import Budget`

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_cost_usd` | `float \| None` | `None` | Maximum cost in USD. |
| `max_tokens` | `int \| None` | `None` | Maximum token count. |
| `max_duration_seconds` | `float \| None` | `None` | Maximum duration in seconds. |
| `max_tool_calls` | `int \| None` | `None` | Maximum number of tool calls. |
| `cost_spent` | `float` | `0.0` | Accumulated cost. |
| `tokens_spent` | `int` | `0` | Accumulated tokens. |
| `duration_spent` | `float` | `0.0` | Accumulated duration in seconds. |
| `tool_calls_spent` | `int` | `0` | Accumulated tool calls. |

All `max_*` fields are optional — `None` means unlimited for that dimension. The `*_spent` fields track consumption during execution and must be updated by the caller (e.g., via `GoalLoop`).

### Properties

#### `is_exhausted: bool`

Returns `True` if any configured non-None limit has been reached or exceeded.

#### `remaining_cost: float | None`

Remaining cost in USD. Returns `None` if no cost limit is set.

#### `remaining_tokens: int | None`

Remaining tokens. Returns `None` if no token limit is set.

**Example:**

```python
from openclaw_sdk.autonomous.models import Budget

budget = Budget(
    max_cost_usd=0.50,
    max_tokens=8000,
    max_tool_calls=15,
)

print(budget.is_exhausted)       # False
print(budget.remaining_cost)     # 0.50
print(budget.remaining_tokens)   # 8000

# After some execution
budget.tokens_spent = 6000
print(budget.remaining_tokens)   # 2000
print(budget.is_exhausted)       # False
```

---

## Goal

Pydantic model representing an autonomous goal that an agent should accomplish.

**Import:** `from openclaw_sdk.autonomous.models import Goal, GoalStatus`

### GoalStatus Enum

| Value | Description |
|-------|-------------|
| `PENDING` | Goal has not started. |
| `IN_PROGRESS` | Goal is currently executing. |
| `COMPLETED` | Goal succeeded. |
| `FAILED` | Goal failed. |
| `CANCELLED` | Goal was cancelled. |

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | `str` | — | Natural-language description of what to achieve. |
| `status` | `GoalStatus` | `GoalStatus.PENDING` | Current status. |
| `sub_goals` | `list[Goal]` | `[]` | Optional child goals for hierarchical decomposition. |
| `max_steps` | `int` | `10` | Maximum number of execution iterations. |
| `result` | `str \| None` | `None` | Final result string once the goal completes or fails. |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary key/value metadata. |

Goals can be hierarchical — a goal may contain `sub_goals` that must be completed as part of the parent goal. The `result` field is populated by `GoalLoop` upon completion.

**Example:**

```python
from openclaw_sdk.autonomous.models import Goal, GoalStatus

goal = Goal(
    description="Research and summarize the latest developments in AI safety",
    max_steps=5,
    metadata={"priority": "high", "tags": ["AI", "safety"]},
)

print(goal.status)  # GoalStatus.PENDING

# After execution by GoalLoop
goal.status = GoalStatus.COMPLETED
goal.result = "Summary: Recent developments include..."
```

---

## Integrated Example

Using all autonomous components together:

```python
import asyncio
from openclaw_sdk.autonomous.models import Budget, Goal, GoalStatus
from openclaw_sdk.autonomous.orchestrator import Orchestrator
from openclaw_sdk.autonomous.watchdog import Watchdog, WatchdogAction
from openclaw_sdk import OpenClawClient

async def main():
    client = OpenClawClient()
    orch = Orchestrator(client)

    # Register agents with skills for routing
    orch.register_agent(
        "researcher",
        "Deep research and analysis",
        ["research", "analysis", "investigation"],
    )
    orch.register_agent(
        "writer",
        "Content creation and editing",
        ["writing", "editing", "drafting"],
    )

    # Define goal and budget
    goal = Goal(description="Research AI alignment techniques", max_steps=3)
    budget = Budget(max_tokens=12000, max_tool_calls=25)

    # Execute via orchestrator (routes to best-matching agent)
    result = await orch.execute_goal(goal, budget)
    print(f"Status: {result.status}")
    print(f"Result: {result.result}")

asyncio.run(main())
```
