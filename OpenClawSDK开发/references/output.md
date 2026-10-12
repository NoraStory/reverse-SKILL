# `output/` Module: StructuredOutput

The `openclaw_sdk.output.structured` module provides utilities for extracting typed, Pydantic-validated data from LLM responses.

---

## `StructuredOutput`

**Import:**

```python
from openclaw_sdk.output.structured import StructuredOutput
from openclaw_sdk.core.exceptions import OutputParsingError
```

---

### `schema_prompt(model)` (static)

Returns a prompt suffix that instructs the LLM to reply with JSON conforming to the given Pydantic model's schema.

```python
@staticmethod
def schema_prompt(model: Type[T]) -> str
```

**Parameters:**

| Parameter    | Type          | Description                        |
|--------------|---------------|------------------------------------|
| `model`      | `Type[T]`     | A Pydantic `BaseModel` subclass    |

**Returns:** `str` -- A prompt fragment appendable to a user query.

**Example:**

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

prompt_suffix = StructuredOutput.schema_prompt(Person)
print(prompt_suffix)
# \n\nRespond with valid JSON matching this schema:\n# ```json\n# {"properties": {"age": {"type": "integer"}, "name": {"type": "string"}}, ...}\n# ```
```

---

### `parse(response, model)` (static)

Extracts the first JSON block from an LLM response string and validates it against the given Pydantic model.

```python
@staticmethod
def parse(response: str, model: Type[T]) -> T
```

**Search order:**

1. A fenced `` ```json ... ``` `` block.
2. A bare ``{...}`` JSON object.

**Parameters:**

| Parameter   | Type          | Description                        |
|-------------|---------------|------------------------------------|
| `response`  | `str`         | Raw LLM response text             |
| `model`     | `Type[T]`     | A Pydantic `BaseModel` subclass   |

**Returns:** An instance of `model` validated against the extracted JSON.

**Raises:** `OutputParsingError` -- If no valid JSON is found or Pydantic validation fails.

**Example:**

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

raw_response = 'Here is the data:\n```json\n{"name": "Alice", "age": 30}\n```'
person = StructuredOutput.parse(raw_response, Person)
print(person.name)  # Alice
print(person.age)   # 30
```

---

### `execute(agent, query, output_model, max_retries)` (static, async)

Executes a query against an agent, appends the schema prompt, and parses the result.

```python
@staticmethod
async def execute(
    agent: _AgentLike,
    query: str,
    output_model: Type[T],
    max_retries: int = 2,
) -> T
```

**Parameters:**

| Parameter      | Type          | Description                                      |
|----------------|---------------|--------------------------------------------------|
| `agent`        | `_AgentLike`  | Any object with `async execute(query: str) -> ExecutionResult` |
| `query`        | `str`         | The user query to send                           |
| `output_model` | `Type[T]`     | A Pydantic `BaseModel` subclass to validate against |
| `max_retries`  | `int`         | Extra attempts after the first parse failure (default: 2) |

**Returns:** A validated instance of `output_model`.

**Raises:** `OutputParsingError` -- After all attempts are exhausted.

**Example:**

```python
import asyncio
from pydantic import BaseModel
from openclaw_sdk.output.structured import StructuredOutput
from openclaw_sdk.core.exceptions import OutputParsingError

class WeatherResult(BaseModel):
    city: str
    temperature_celsius: float
    condition: str

async def main():
    # agent is an openclaw_sdk.Agent instance
    # result = await StructuredOutput.execute(
    #     agent,
    #     query="What is the weather in Tokyo?",
    #     output_model=WeatherResult,
    #     max_retries=2,
    # )
    # print(result.city, result.temperature_celsius, result.condition)
    pass

asyncio.run(main())
```

---

## `OutputParsingError`

**Import:**

```python
from openclaw_sdk.core.exceptions import OutputParsingError
```

Raised when:

- No JSON is found in the LLM response (neither a fenced block nor a bare object).
- The extracted JSON fails Pydantic validation.

---

## Agent Convenience Method: `execute_structured`

The `Agent` class exposes `execute_structured` as a convenience wrapper that delegates to `StructuredOutput.execute`:

```python
async def execute_structured(
    self,
    query: str,
    output_model: Type[T],
    options: ExecutionOptions | None = None,
    max_retries: int = 2,
) -> T
```

---

## Complete Example

```python
import asyncio
from pydantic import BaseModel
from openclaw_sdk import Agent
from openclaw_sdk.core.exceptions import OutputParsingError


# 1. Define your output model
class BookInfo(BaseModel):
    title: str
    author: str
    year: int
    genres: list[str]
    rating: float | None = None


async def main():
    # 2. Create or obtain an agent
    agent = Agent(name="book-assistant")

    # 3. Call execute_structured on the agent
    try:
        result: BookInfo = await agent.execute_structured(
            query="Tell me about the book 'Dune' by Frank Herbert.",
            output_model=BookInfo,
            max_retries=2,
        )
        # 4. Handle the result (fully typed)
        print(f"Title:   {result.title}")
        print(f"Author:  {result.author}")
        print(f"Year:    {result.year}")
        print(f"Genres:  {result.genres}")
        print(f"Rating:  {result.rating}")

    except OutputParsingError as exc:
        print(f"Failed to parse response: {exc}")


asyncio.run(main())
```

**Flow:**

1. `execute_structured` appends the JSON schema prompt to the query.
2. The agent processes the combined prompt.
3. `StructuredOutput.parse` extracts and validates the JSON from the response.
4. A validated `BookInfo` instance is returned, or `OutputParsingError` is raised after `max_retries` attempts.
