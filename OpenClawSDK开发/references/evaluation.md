# Evaluation Module

The `openclaw_sdk.evaluation` module provides a framework for systematic agent testing. It includes `EvalSuite` for managing test cases, `EvalCase` for individual tests, `EvalReport` for aggregating results, and several built-in evaluators for common validation patterns.

---

## EvalCase

A single evaluation case pairing a query with an evaluator.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `query` | `str` | The input query to send to the agent |
| `evaluator` | `Evaluator` | The evaluator to judge the response |
| `name` | `str \| None` | Optional human-readable name for the case |
| `tags` | `list[str]` | Optional tags for categorizing cases (default: empty list) |

```python
from openclaw_sdk.evaluation import EvalCase, ContainsEvaluator

case = EvalCase(
    query="What is the capital of France?",
    evaluator=ContainsEvaluator("Paris"),
    name="Capital of France",
    tags=["geography", "simple"]
)
```

---

## EvalCaseResult

Result of running a single evaluation case.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `case` | `EvalCase` | The eval case that was run |
| `passed` | `bool` | Whether the case passed evaluation |
| `result` | `ExecutionResult` | The raw execution result from the agent |

---

## EvalReport

Aggregated report from running an evaluation suite.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Name of the evaluation suite |
| `total` | `int` | Total number of cases run |
| `passed` | `int` | Number of cases that passed |
| `failed` | `int` | Number of cases that failed |
| `case_results` | `list[EvalCaseResult]` | Individual case results |

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `pass_rate` | `float` | Fraction of cases that passed (0.0 to 1.0) |

---

## EvalSuite

A collection of evaluation cases that can be run against an agent.

### `__init__(name: str)`

Creates a new evaluation suite with the given name.

```python
from openclaw_sdk.evaluation import EvalSuite

suite = EvalSuite(name="Geography Tests")
```

### `add_case(case: EvalCase) -> None`

Adds an evaluation case to the suite.

```python
suite.add_case(case)
```

### `run(agent) -> EvalReport`

Runs all cases against an agent and returns an evaluation report. The agent must have an async `execute(query: str)` method that returns an `ExecutionResult`.

```python
report = await suite.run(agent)
print(f"Passed: {report.passed}/{report.total}")
print(f"Pass rate: {report.pass_rate:.1%}")
```

### `evaluate(results: list[ExecutionResult]) -> EvalReport`

Evaluates a list of pre-collected execution results against the registered cases. Raises `ValueError` if the number of results does not match the number of cases.

---

## Built-in Evaluators

All evaluators inherit from `Evaluator` and implement `evaluate(result: ExecutionResult) -> bool`.

### ContainsEvaluator(expected: str, case_sensitive: bool = False)

Checks whether the result content contains an expected substring.

```python
from openclaw_sdk.evaluation.evaluators import ContainsEvaluator

# Case-insensitive substring match (default)
eval_case = EvalCase(
    query="What is Python?",
    evaluator=ContainsEvaluator("programming language")
)

# Case-sensitive match
eval_case = EvalCase(
    query="What is Python?",
    evaluator=ContainsEvaluator("Python", case_sensitive=True)
)
```

### ExactMatchEvaluator(expected: str, strip: bool = True)

Checks whether the result content exactly matches an expected string.

```python
from openclaw_sdk.evaluation.evaluators import ExactMatchEvaluator

eval_case = EvalCase(
    query="What is 2 + 2?",
    evaluator=ExactMatchEvaluator("4")
)
```

### RegexEvaluator(pattern: str)

Checks whether the result content matches a regular expression pattern.

```python
from openclaw_sdk.evaluation.evaluators import RegexEvaluator

eval_case = EvalCase(
    query="What is your email?",
    evaluator=RegexEvaluator(r"[\w.-]+@[\w.-]+\.\w+")
)
```

### LengthEvaluator(min_length: int = 0, max_length: int | None = None)

Checks whether the result content length falls within bounds.

```python
from openclaw_sdk.evaluation.evaluators import LengthEvaluator

# Response must be at least 10 characters
eval_case = EvalCase(
    query="Tell me a story",
    evaluator=LengthEvaluator(min_length=10)
)

# Response must be between 50 and 500 characters
eval_case = EvalCase(
    query="Summarize the report",
    evaluator=LengthEvaluator(min_length=50, max_length=500)
)
```

---

## Complete Example

```python
import asyncio
from openclaw_sdk.evaluation import EvalSuite, EvalCase
from openclaw_sdk.evaluation.evaluators import (
    ContainsEvaluator,
    ExactMatchEvaluator,
    RegexEvaluator,
    LengthEvaluator,
)


async def main():
    # Create evaluation suite
    suite = EvalSuite(name="Agent Evaluation")

    # Add test cases
    suite.add_case(EvalCase(
        query="What is the capital of France?",
        evaluator=ContainsEvaluator("Paris"),
        name="Capital of France"
    ))

    suite.add_case(EvalCase(
        query="What is 2 + 2?",
        evaluator=ExactMatchEvaluator("4")
    ))

    suite.add_case(EvalCase(
        query="What is your email?",
        evaluator=RegexEvaluator(r"[\w.-]+@[\w.-]+\.\w+")
    ))

    suite.add_case(EvalCase(
        query="Introduce yourself",
        evaluator=LengthEvaluator(min_length=10, max_length=500)
    ))

    # Run against an agent (agent must have async execute() method)
    # report = await suite.run(agent)

    # Access results
    # print(f"Total: {report.total}")
    # print(f"Passed: {report.passed}")
    # print(f"Failed: {report.failed}")
    # print(f"Pass Rate: {report.pass_rate:.1%}")


asyncio.run(main())
```
