# Pipeline Module

> Source: `openclaw_sdk.pipeline.pipeline`

Two classes provide agent orchestration: `Pipeline` for linear sequential execution and `ConditionalPipeline` for branching, parallel, and fallback control flow.

---

## Pipeline

Linear sequential execution of agent steps. Each step's output is stored as a variable available to all subsequent steps.

### Constructor

```python
Pipeline(client: OpenClawClient)
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `client` | `OpenClawClient` | Client that provides `get_agent(agent_id)` returning an agent with `async execute(prompt) -> ExecutionResult` |

### `add_step`

```python
def add_step(
    self,
    name: str,
    agent_id: str,
    prompt: str,
    output_key: str = "content",
) -> Pipeline
```

Adds a step and returns `self` for method chaining.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Unique step name; becomes a variable key for downstream steps |
| `agent_id` | `str` | — | Agent identifier to invoke |
| `prompt` | `str` | — | Prompt template with `{variable}` placeholders |
| `output_key` | `str` | `"content"` | Which field of `ExecutionResult` to expose as the step's output variable |

### `run`

```python
async def run(self, **initial_variables: str) -> PipelineResult
```

Executes all steps sequentially. Stops immediately on the first failure.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `**initial_variables` | `str` | Initial variable values; also seed variables for the first step's template |

**Returns** — `PipelineResult`

```python
class PipelineResult(BaseModel):
    success: bool
    steps: dict[str, ExecutionResult]   # keyed by step name
    final_result: ExecutionResult
    total_latency_ms: int
    all_files: list[GeneratedFile]
```

**Variable substitution** — `{var_name}` in any prompt is replaced with:
- An `initial_variables` kwarg matching the name, or
- The `output_key` value of a previously executed step

**Error handling**
- Raises `PipelineError` if called with no steps.
- Returns `PipelineResult(success=False)` if a step's `ExecutionResult.success` is `False`.
- Returns `PipelineResult(success=False)` if a `{variable}` is missing and cannot be resolved.

### Example — variable passing between steps

```python
import asyncio
from openclaw_sdk import OpenClawClient
from openclaw_sdk.pipeline.pipeline import Pipeline

async def main():
    client = await OpenClawClient.connect()

    pipeline = (
        Pipeline(client)
        .add_step("summarize", "summarizer-agent", "Summarize: {input}")
        .add_step("translate", "translator-agent", "Translate this to French: {summarize}")
        .add_step("reply", "composer-agent", "Draft a response using: {translate}")
    )

    result = await pipeline.run(input="The product arrived damaged and I want a refund.")
    print(result.final_result.content)   # final step output
    print(result.steps["summarize"].content)  # first step output
    print(result.total_latency_ms)
    await client.close()

asyncio.run(main())
```

---

## ConditionalPipeline

Extends `Pipeline` with branching, parallel, and fallback step types. All builder methods return `self` for fluent chaining.

### Constructor

```python
ConditionalPipeline(client: OpenClawClient)
```

### `add_step`

```python
def add_step(
    self,
    name: str,
    agent_id: str,
    prompt_template: str,
    *,
    output_key: str = "content",
) -> ConditionalPipeline
```

Identical to `Pipeline.add_step`. Adds a sequential step executed in order.

### `add_branch`

```python
def add_branch(
    self,
    after_step: str,
    condition: Callable[[ExecutionResult], bool],
    if_true: tuple[str, str, str],
    if_false: tuple[str, str, str],
) -> ConditionalPipeline
```

Adds a conditional branch evaluated against a previously executed step's result.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `after_step` | `str` | Name of a previously added step whose result is tested |
| `condition` | `Callable[[ExecutionResult], bool]` | Predicate called with the referenced step's result |
| `if_true` | `tuple[str, str, str]` | `(name, agent_id, prompt_template)` executed when condition is `True` |
| `if_false` | `tuple[str, str, str]` | `(name, agent_id, prompt_template)` executed when condition is `False` |

### `add_parallel`

```python
def add_parallel(
    self,
    steps: list[tuple[str, str, str]],
) -> ConditionalPipeline
```

Runs multiple agent calls concurrently via `asyncio.gather`.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `steps` | `list[tuple[str, str, str]]` | List of `(name, agent_id, prompt_template)` tuples executed concurrently |

All parallel sub-steps receive an identical snapshot of variables taken at the moment the parallel step begins. Results are stored individually by sub-step name.

### `add_fallback`

```python
def add_fallback(
    self,
    name: str,
    agent_id: str,
    prompt_template: str,
    *,
    fallback_agent_id: str,
    fallback_prompt: str,
) -> ConditionalPipeline
```

Attempts the primary step; if it raises an exception or returns `success=False`, the fallback step runs instead.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Primary step name; also used as the variable key after execution |
| `agent_id` | `str` | Primary agent |
| `prompt_template` | `str` | Primary prompt |
| `fallback_agent_id` | `str` | Fallback agent used on primary failure |
| `fallback_prompt` | `str` | Fallback prompt |

After a fallback is used, both `variables[primary_name]` and `variables[fallback_name]` are set to the fallback result (so downstream templates can reference either name).

### `run`

```python
async def run(self, **initial_variables: str) -> PipelineResult
```

Executes the pipeline. Step dispatch is based on step type:

| Step Type | Behavior |
|-----------|----------|
| `_SequentialStep` | Execute single agent, store result |
| `_BranchStep` | Evaluate condition on referenced step result; execute `if_true` or `if_false` |
| `_ParallelStep` | `asyncio.gather` on all sub-steps concurrently |
| `_FallbackStep` | Try primary; on exception or `success=False`, run fallback |

Returns the same `PipelineResult` structure as `Pipeline.run`.

---

## Example — branching and variable passing

```python
import asyncio
from openclaw_sdk import OpenClawClient
from openclaw_sdk.pipeline.pipeline import ConditionalPipeline

async def main():
    client = await OpenClawClient.connect()
    pipeline = ConditionalPipeline(client)
    pipeline.add_step("classify", "classifier-agent", "Is '{input}' a complaint? Reply yes or no.")
    pipeline.add_branch(
        "classify",
        condition=lambda result: "yes" in result.content.lower(),
        if_true=("handle_complaint", "support-agent", "Handle this complaint: {classify}"),
        if_false=("answer_question", "faq-bot", "Answer this inquiry: {classify}"),
    )
    pipeline.add_step("log", "logger-agent", "Logged: {classify}")

    result = await pipeline.run(input="I want a refund")
    print(result.final_result.content)
    await client.close()

asyncio.run(main())
```

## Example — parallel execution

```python
import asyncio
from openclaw_sdk import OpenClawClient
from openclaw_sdk.pipeline.pipeline import ConditionalPipeline

async def main():
    client = await OpenClawClient.connect()
    pipeline = ConditionalPipeline(client)
    pipeline.add_step("prep", "prep-agent", "Prepare context: {input}")
    pipeline.add_parallel([
        ("search_web",  "web-search-agent",  "Search the web: {prep}"),
        ("search_docs",  "docs-agent",         "Search docs: {prep}"),
        ("search_db",    "db-agent",           "Query database: {prep}"),
    ])
    pipeline.add_step("synthesize", "synth-agent", "Combine: {search_web} {search_docs} {search_db}")

    result = await pipeline.run(input="OpenClaw SDK pricing")
    await client.close()

asyncio.run(main())
```

## Example — fallback

```python
import asyncio
from openclaw_sdk import OpenClawClient
from openclaw_sdk.pipeline.pipeline import ConditionalPipeline

async def main():
    client = await OpenClawClient.connect()
    pipeline = ConditionalPipeline(client)
    pipeline.add_fallback(
        "premium",
        "premium-agent",
        "Handle with premium support: {input}",
        fallback_agent_id="basic-agent",
        fallback_prompt="Handle basic support: {input}",
    )
    pipeline.add_step("notify", "notifier-agent", "Ticket resolved: {premium}")

    result = await pipeline.run(input="My enterprise account is locked")
    await client.close()

asyncio.run(main())
```

---

## Shared Behavior

- Both classes use the same `PipelineResult` return type.
- All step outputs (or fallback outputs) are stored back into the shared `variables` dict, making them available as `{step_name}` in any downstream prompt.
- If any step returns `ExecutionResult.success == False`, the pipeline stops and returns `PipelineResult(success=False)` immediately.
- `asyncio.gather` is used for parallel execution with `return_exceptions=True`; any exception causes the whole pipeline to fail fast.
