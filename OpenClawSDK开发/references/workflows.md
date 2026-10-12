# Workflows Module

The `workflows/` module provides a branching state-machine workflow engine that complements the linear `Pipeline` with conditional routing, human approvals, and context transformations.

**Source files:**
- `/home/kali/Desktop/openclaw_sdk/src/openclaw_sdk/workflows/engine.py`
- `/home/kali/Desktop/openclaw_sdk/src/openclaw_sdk/workflows/models.py`
- `/home/kali/Desktop/openclaw_sdk/src/openclaw_sdk/workflows/presets.py`

---

## `StepType` (Enum)

Defines the type of each workflow step.

| Value | Description |
|---|---|
| `AGENT` | Calls an agent via `agent_factory` with configured `agent_id` and `query`. |
| `CONDITION` | Evaluates a condition on the workflow context and routes to `next_on_success` or `next_on_failure`. |
| `APPROVAL` | Checks `auto_approve` config; in production waits for human approval. |
| `TRANSFORM` | Applies a transformation function or key mapping to the workflow context. |

```python
from openclaw_sdk.workflows.models import StepType

StepType.AGENT     # "agent"
StepType.CONDITION # "condition"
StepType.APPROVAL  # "approval"
StepType.TRANSFORM # "transform"
```

---

## `StepStatus` (Enum)

Tracks the execution state of a workflow step.

| Value | Description |
|---|---|
| `PENDING` | Step has not yet executed. |
| `RUNNING` | Step is currently executing. |
| `COMPLETED` | Step finished successfully. |
| `FAILED` | Step encountered an error. |
| `SKIPPED` | Step was skipped due to branching. |

---

## `WorkflowStep`

Represents a single step in a workflow.

```python
class WorkflowStep(BaseModel):
    name: str
    step_type: StepType
    config: dict[str, Any] = Field(default_factory=dict)
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    next_on_success: str | None = None
    next_on_failure: str | None = None
```

### Fields

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Unique identifier for the step within the workflow. |
| `step_type` | `StepType` | How this step should be executed. |
| `config` | `dict[str, Any]` | Step-specific configuration (e.g., `agent_id`, `query`, `key`, `operator`). |
| `status` | `StepStatus` | Current execution status. Defaults to `PENDING`. |
| `result` | `Any` | Output from the step execution. |
| `next_on_success` | `str \| None` | Step name to jump to on success. `None` means continue sequentially. |
| `next_on_failure` | `str \| None` | Step name to jump to on failure. `None` means halt workflow. |

### Step Configuration by Type

**AGENT:**
```python
config = {
    "agent_id": "my-agent",       # Agent ID passed to agent_factory
    "query": "Review: {document}" # Query template; context values are substituted
}
```

**CONDITION:**
```python
config = {
    "key": "review_passed",       # Context key to evaluate
    "operator": "eq",             # Comparison operator
    "value": True                # Expected value
}
```
Supported operators: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `contains`.

**APPROVAL:**
```python
config = {"auto_approve": False}  # True to skip manual approval
```

**TRANSFORM:**
```python
# Option 1: Key mapping (rename context keys)
config = {"mapping": {"research": "findings"}}

# Option 2: Callable transform
config = {"transform": lambda ctx: {"key": ctx.get("old_key")}}
```

---

## `Workflow`

Branching state-machine workflow engine with support for conditional routing, approvals, and context transforms.

```python
class Workflow:
    def __init__(self, name: str, steps: list[WorkflowStep]) -> None:
        ...
```

### Constructor

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Human-readable workflow name. |
| `steps` | `list[WorkflowStep]` | Ordered list of step definitions. |

### Methods

#### `run(context, *, agent_factory=None) -> WorkflowResult`

Execute the workflow asynchronously.

| Parameter | Type | Description |
|---|---|---|
| `context` | `dict[str, Any]` | Mutable dict shared across all steps. Step results are stored under the step's name. |
| `agent_factory` | `Callable[[str], _AgentLike] \| None` | Callable that takes an `agent_id` string and returns an agent-like object with `async execute(query)`. Required for workflows containing `AGENT` steps. |

### WorkflowResult

```python
class WorkflowResult(BaseModel):
    success: bool
    steps: list[WorkflowStep]
    final_output: Any = None
    latency_ms: int = 0
```

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | `True` if the workflow completed without failures. |
| `steps` | `list[WorkflowStep]` | All steps with their final statuses and results. |
| `final_output` | `Any` | Result of the last executed step. |
| `latency_ms` | `int` | Total wall-clock time in milliseconds. |

### Workflow Execution Logic

1. Steps execute in insertion order unless a step redirects via `next_on_success` or `next_on_failure`.
2. AGENT steps call `agent_factory(agent_id).execute(query)`, where `query` is formatted with context values.
3. CONDITION steps evaluate `context[key] operator value` and branch accordingly.
4. APPROVAL steps return `auto_approve` config value.
5. TRANSFORM steps apply key mappings or callable transforms to the context.
6. A step that fails without a `next_on_failure` target halts the workflow.

### Example: Creating and Running a Workflow

```python
import asyncio
from openclaw_sdk.workflows import Workflow, WorkflowStep, StepType
from openclaw_sdk.workflows.models import StepStatus

# Define steps
steps = [
    WorkflowStep(
        name="review",
        step_type=StepType.AGENT,
        config={"agent_id": "reviewer", "query": "Review: {document}"},
        next_on_success="check_pass",
    ),
    WorkflowStep(
        name="check_pass",
        step_type=StepType.CONDITION,
        config={"key": "review_passed", "operator": "eq", "value": True},
        next_on_success="done",
        next_on_failure="revise",
    ),
    WorkflowStep(
        name="revise",
        step_type=StepType.AGENT,
        config={"agent_id": "author", "query": "Revise based on: {review}"},
        next_on_success="done",
    ),
    WorkflowStep(
        name="done",
        step_type=StepType.TRANSFORM,
        config={"mapping": {"review": "final_output"}},
    ),
]

wf = Workflow(name="review", steps=steps)

# Agent factory
class MockAgent:
    async def execute(self, query):
        return type("Result", (), {"success": True, "content": f"Done: {query}"})()

agent_registry = {"reviewer": MockAgent(), "author": MockAgent()}
factory = lambda agent_id: agent_registry[agent_id]

# Run workflow
async def main():
    context = {"document": "my document content"}
    result = await wf.run(context, agent_factory=factory)
    print(f"Success: {result.success}")
    print(f"Latency: {result.latency_ms}ms")
    for step in result.steps:
        print(f"  {step.name}: {step.status.value} -> {step.result}")

asyncio.run(main())
```

---

## Preset Factory Functions

The `presets.py` module provides pre-built workflow configurations for common patterns.

### `review_workflow(reviewer_agent_id, author_agent_id) -> Workflow`

Code/document review workflow with revision loop.

| Parameter | Type | Description |
|---|---|---|
| `reviewer_agent_id` | `str` | Agent ID for the reviewer. |
| `author_agent_id` | `str` | Agent ID for the author/reviser. |

**Steps:**
1. `review` (AGENT) - Reviewer agent reviews the content.
2. `check_pass` (CONDITION) - Checks if `review_passed` is `True` in context.
3. `revise` (AGENT) - On failure, author agent revises based on feedback.

```python
from openclaw_sdk.workflows.presets import review_workflow

wf = review_workflow(reviewer_agent_id="reviewer", author_agent_id="author")
```

### `research_workflow(researcher_agent_id, summarizer_agent_id) -> Workflow`

Research-and-summarize workflow.

| Parameter | Type | Description |
|---|---|---|
| `researcher_agent_id` | `str` | Agent ID for the researcher. |
| `summarizer_agent_id` | `str` | Agent ID for the summarizer. |

**Steps:**
1. `research` (AGENT) - Researcher agent gathers information.
2. `extract` (TRANSFORM) - Extracts findings from research result into `findings` context key.
3. `summarize` (AGENT) - Summarizer agent creates a summary.

```python
from openclaw_sdk.workflows.presets import research_workflow

wf = research_workflow(researcher_agent_id="researcher", summarizer_agent_id="summarizer")
```

### `support_workflow(triage_agent_id, support_agent_id) -> Workflow`

Customer support triage workflow.

| Parameter | Type | Description |
|---|---|---|
| `triage_agent_id` | `str` | Agent ID for the triage agent. |
| `support_agent_id` | `str` | Agent ID for the detailed support agent. |

**Steps:**
1. `triage` (AGENT) - Triage agent classifies the issue.
2. `check_priority` (CONDITION) - Checks if `priority` equals `"high"`.
3. `detailed_support` (AGENT) - On high priority, support agent provides detailed assistance.

```python
from openclaw_sdk.workflows.presets import support_workflow

wf = support_workflow(triage_agent_id="triage", support_agent_id="support")
```
