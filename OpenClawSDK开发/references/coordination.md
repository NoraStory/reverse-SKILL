# Coordination Module

The `coordination` module provides multi-agent coordination primitives: `Supervisor`, `AgentRouter`, and `ConsensusGroup`.

```python
from openclaw_sdk.coordination import Supervisor, AgentRouter, ConsensusGroup
```

---

## Supervisor

Coordinates multiple worker agents under a supervisor pattern. Dispatches tasks to workers, collects results, and synthesizes a final response.

```python
supervisor = Supervisor(client, supervisor_agent_id="manager")
supervisor.add_worker("researcher", description="Research tasks")
supervisor.add_worker("writer", description="Writing tasks")
result = await supervisor.delegate(
    "Research AI trends and write a report",
    strategy="sequential",
)
```

### `__init__(client, supervisor_agent_id)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `client` | `OpenClawClient` | The OpenClaw client instance. |
| `supervisor_agent_id` | `str \| None` | Optional supervisor agent identifier. |

### `add_worker(agent_id, description)`

Registers a worker agent.

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | `str` | The worker agent's identifier. |
| `description` | `str` | Human-readable description of the worker's purpose (default `""`). |

**Returns:** `self` for fluent chaining.

### `delegate(task, strategy, max_rounds)`

Delegates a task to worker agents.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task` | `str` | — | The task description to delegate. |
| `strategy` | `str` | `"sequential"` | Execution strategy. |
| `max_rounds` | `int` | `1` | Number of full passes through workers (sequential only). |

**Strategies:**

- `"sequential"` — Workers execute in registration order; each sees previous results as context.
- `"parallel"` — All workers execute concurrently on the same task.
- `"round-robin"` — Workers are tried in order; first success wins.

**Returns:** `SupervisorResult` with aggregated outcomes.

**Raises:** `ValueError` if no route matches and no default agent is set.

### Internal Methods

#### `_run_sequential(task, max_rounds)`

Workers execute in order, accumulating context. Each worker's output is appended to the context for the next worker.

#### `_run_parallel(task)`

All workers execute concurrently via `asyncio.gather`. Results are collected and the last result is used as the final result.

#### `_run_round_robin(task)`

Workers are tried in order. The first worker to return a successful result terminates execution and returns immediately.

### `SupervisorResult`

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether the final result was successful. |
| `final_result` | `ExecutionResult \| None` | The last worker's result. |
| `worker_results` | `dict[str, ExecutionResult]` | Results from each worker. |
| `delegations` | `list[str]` | Ordered list of agents that handled work. |
| `latency_ms` | `int` | Total execution time in milliseconds. |

---

## AgentRouter

Routes queries to different agents based on content using condition functions.

```python
router = AgentRouter(client)
router.add_route(lambda q: "code" in q.lower(), "code-reviewer")
router.add_route(lambda q: "data" in q.lower(), "data-analyst")
router.set_default("assistant")
result = await router.route("Review this code snippet")
```

### `__init__(client)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `client` | `OpenClawClient` | The OpenClaw client instance. |

### `add_route(condition, agent_id)`

Adds a routing rule. Routes are evaluated in registration order.

| Parameter | Type | Description |
|-----------|------|-------------|
| `condition` | `Callable[[str], bool]` | A callable that takes a query string and returns `True` if this route matches. |
| `agent_id` | `str` | The agent to route to when condition matches. |

**Returns:** `self` for fluent chaining.

### `set_default(agent_id)`

Sets the default agent for unmatched queries.

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | `str` | The fallback agent identifier. |

**Returns:** `self` for fluent chaining.

### `resolve(query)`

Determines which agent should handle the query without executing it.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user query. |

**Returns:** The matched agent identifier.

**Raises:** `ValueError` if no route matches and no default agent is set.

### `route(query)`

Resolves the query to an agent and executes it.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user query to route and execute. |

**Returns:** `ExecutionResult` from the matched agent.

---

## ConsensusGroup

Runs the same query through multiple agents and determines a consensus answer through voting.

```python
group = ConsensusGroup(client, ["analyst-1", "analyst-2", "analyst-3"])
result = await group.vote("What is 2+2?", method="majority")
```

### `__init__(client, agent_ids)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `client` | `OpenClawClient` | The OpenClaw client instance. |
| `agent_ids` | `list[str]` | List of agent identifiers to include in the group. |

### `vote(query, method, scorer)`

Runs the query through all agents and determines consensus.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | — | The query to execute. |
| `method` | `str` | `"majority"` | Voting method. |
| `scorer` | `Callable[[ExecutionResult], str] \| None` | `None` | Function to extract a comparable key from results. Defaults to stripped, lowercased content. |

**Voting Methods:**

- `"majority"` — More than half of agents must agree (default).
- `"unanimous"` — All agents must produce the same answer.
- `"any"` — Success if at least one agent succeeds.

**Returns:** `ConsensusResult` with voting details.

### `ConsensusResult`

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether consensus was achieved per the specified method. |
| `chosen_result` | `ExecutionResult \| None` | The winning result. |
| `all_results` | `dict[str, ExecutionResult]` | Results from every agent. |
| `votes` | `dict[str, int]` | Vote counts by score key. |
| `agreement_ratio` | `float` | Ratio of votes for the winner (0.0 to 1.0). |

---

## Usage Examples

### Supervisor with Sequential Strategy

```python
from openclaw_sdk.coordination import Supervisor

supervisor = Supervisor(client, supervisor_agent_id="team-lead")
supervisor.add_worker("researcher", description="Gather information")
supervisor.add_worker("writer", description="Create deliverables")
supervisor.add_worker("reviewer", description="Quality assurance")

result = await supervisor.delegate(
    "Research quantum computing trends and create a summary report",
    strategy="sequential",
    max_rounds=1,
)

print(f"Success: {result.success}")
print(f"Latency: {result.latency_ms}ms")
for agent_id, worker_result in result.worker_results.items():
    print(f"{agent_id}: {worker_result.content[:100]}")
```

### Supervisor with Parallel Strategy

```python
result = await supervisor.delegate(
    "Analyze this data set from multiple perspectives",
    strategy="parallel",
)
# All workers execute concurrently
```

### Supervisor with Round-Robin Strategy

```python
result = await supervisor.delegate(
    "Find a working solution to the integration issue",
    strategy="round-robin",
)
# First successful worker wins
```

### AgentRouter with Multiple Routes

```python
from openclaw_sdk.coordination import AgentRouter

router = AgentRouter(client)
router.add_route(lambda q: "refactor" in q.lower() or "code" in q.lower(), "code-agent")
router.add_route(lambda q: "data" in q.lower() or "analytics" in q.lower(), "data-agent")
router.add_route(lambda q: "deploy" in q.lower() or "infrastructure" in q.lower(), "devops-agent")
router.set_default("general-assistant")

# Resolve without executing
agent_id = router.resolve("Can you refactor the authentication module?")
print(f"Routing to: {agent_id}")  # Output: Routing to: code-agent

# Route and execute
result = await router.route("Generate analytics for Q1 sales")
```

### ConsensusGroup with Majority Voting

```python
from openclaw_sdk.coordination import ConsensusGroup

group = ConsensusGroup(client, ["expert-1", "expert-2", "expert-3", "expert-4"])

# Using default scorer (content comparison)
result = await group.vote(
    "What is the best approach for scaling a Python web application?",
    method="majority",
)

print(f"Agreement: {result.agreement_ratio * 100}%")
print(f"Winner votes: {result.votes}")
```

### ConsensusGroup with Custom Scorer

```python
def extract_sentiment_key(execution_result):
    """Extract a sentiment label from the result."""
    content = execution_result.content.lower()
    if "positive" in content:
        return "positive"
    elif "negative" in content:
        return "negative"
    return "neutral"

result = await group.vote(
    "Analyze the sentiment of customer feedback: 'Great product, fast delivery!'",
    method="unanimous",
    scorer=extract_sentiment_key,
)
```
