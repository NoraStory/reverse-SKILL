# OpenClaw SDK Integrations

This document covers the web framework and task queue integrations available in the `openclaw_sdk.integrations` module.

## Installation

Each integration has an optional extra:

```bash
pip install openclaw-sdk[fastapi]   # FastAPI
pip install openclaw-sdk[flask]     # Flask
pip install openclaw-sdk[django]    # Django
pip install openclaw-sdk[streamlit] # Streamlit
pip install openclaw-sdk[jupyter]  # Jupyter/IPython
pip install openclaw-sdk[celery]    # Celery
```

---

## FastAPI

**Module:** `openclaw_sdk.integrations.fastapi`

```python
from openclaw_sdk.integrations.fastapi import (
    get_openclaw_client,
    create_agent_router,
    create_channel_router,
    create_admin_router,
)
```

### `get_openclaw_client()`

Async FastAPI dependency that returns a cached `OpenClawClient`.

Reads from environment variables on first call:

- `OPENCLAW_GATEWAY_WS_URL` — WebSocket gateway URL
- `OPENCLAW_API_KEY` — API key
- `OPENCLAW_OPENAI_BASE_URL` — Optional custom OpenAI base URL

Raises HTTPException 503 if the gateway is unavailable.

```python
from fastapi import FastAPI
from openclaw_sdk.integrations.fastapi import get_openclaw_client

app = FastAPI()

@app.get("/status")
async def status():
    client = await get_openclaw_client()
    return await client.health()
```

### `create_agent_router(client, prefix="/agents")`

Returns an `APIRouter` with agent endpoints.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `{prefix}/health` | Gateway health check |
| `POST` | `{prefix}/{agent_id}/execute` | Execute a query against an agent |

**Execute Request Body:**

```python
{
    "query": str,                    # required
    "session_name": str = "main",    # optional
    "timeout_seconds": int = 300,    # optional
    "idempotency_key": str | None    # optional
}
```

**Execute Response:**

```python
{
    "success": bool,
    "content": str,
    "latency_ms": int
}
```

### `create_channel_router(client, prefix="/channels")`

Returns an `APIRouter` with channel management endpoints.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `{prefix}/status` | All channel statuses |
| `POST` | `{prefix}/{channel}/logout` | Logout a channel |
| `POST` | `{prefix}/{channel}/login/start` | Start QR login flow |
| `POST` | `{prefix}/{channel}/login/wait` | Wait for QR scan (query param: `timeout_ms`) |

### `create_admin_router(client, prefix="/admin")`

Returns an `APIRouter` with administrative endpoints.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `{prefix}/schedules` | List cron jobs |
| `POST` | `{prefix}/schedules` | Create a cron job |
| `DELETE` | `{prefix}/schedules/{job_id}` | Delete a cron job |
| `GET` | `{prefix}/skills` | List installed skills |
| `POST` | `{prefix}/skills/{name}/install` | Install a skill |

---

## Flask

**Module:** `openclaw_sdk.integrations.flask_app`

### `create_agent_blueprint(client, url_prefix="/agents")`

Creates a Flask Blueprint with agent endpoints.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `{url_prefix}/health` | Gateway health check |
| `POST` | `{url_prefix}/{agent_id}/execute` | Execute a query |

**Request body (JSON):**

```python
{"query": "your question here"}
```

**Response (JSON):**

```python
{
    "success": bool,
    "content": str,
    "latency_ms": int
}
```

```python
from flask import Flask
from openclaw_sdk.integrations.flask_app import create_agent_blueprint

app = Flask(__name__)
client = OpenClawClient.connect()
app.register_blueprint(create_agent_blueprint(client, url_prefix="/agents"))
```

### `create_channel_blueprint(client, url_prefix="/channels")`

Creates a Flask Blueprint with channel endpoints.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `{url_prefix}/status` | All channel statuses |

---

## Django

**Module:** `openclaw_sdk.integrations.django_app`

### `setup(client)`

Initialize the Django integration with an `OpenClawClient` instance. Call this during Django app startup.

```python
# somewhere in your Django setup (e.g., AppConfig.ready())
from openclaw_sdk.integrations.django_app import setup

setup(client)
```

### `get_client()`

Returns the configured `OpenClawClient` instance. Raises `RuntimeError` if `setup()` has not been called.

```python
from openclaw_sdk.integrations.django_app import get_client

client = get_client()
```

### `get_urls()`

Returns a list of Django URL patterns for OpenClaw endpoints.

**URLs:**

| Path | View | Method | Description |
|------|------|--------|-------------|
| `openclaw/health/` | `health` | `GET` | Gateway health check |
| `openclaw/agents/<str:agent_id>/execute/` | `execute` | `POST` | Execute a query |

```python
# urls.py
from openclaw_sdk.integrations.django_app import get_urls

urlpatterns += get_urls()
```

**Execute Request:** JSON body with `{"query": "..."}`

**Execute Response:** JSON `{"success": bool, "content": str, "latency_ms": int}`

---

## Streamlit

**Module:** `openclaw_sdk.integrations.streamlit_ui`

### `st_openclaw_chat(agent, **kwargs)`

Renders an interactive chat interface in Streamlit.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `agent` | `Agent` | required | The OpenClaw agent to chat with |
| `title` | `str` | `"OpenClaw Chat"` | Title displayed at the top |
| `placeholder` | `str` | `"Type a message..."` | Chat input placeholder |
| `show_thinking` | `bool` | `False` | Show/hide thinking process in an expander |
| `show_token_usage` | `bool` | `True` | Show token usage and latency after each response |

**Example:**

```python
import streamlit as st
from openclaw_sdk import OpenClawClient
from openclaw_sdk.integrations.streamlit_ui import st_openclaw_chat

client = st.session_state.client
agent = client.get_agent("my-agent")

st_openclaw_chat(agent, title="My AI Assistant", show_thinking=True)
```

---

## Jupyter / IPython

**Module:** `openclaw_sdk.integrations.jupyter_magic`

Requires: `pip install openclaw-sdk[jupyter]`

### Loading the Extension

```python
%load_ext openclaw_sdk.integrations.jupyter_magic
```

**Note:** The extension exposes `load_ipython_extension` which is called automatically by `%load_ext`.

### `%openclaw_connect [ws://gateway-url]`

Line magic to connect to the OpenClaw gateway. If no URL is provided, uses the default or `OPENCLAW_GATEWAY_WS_URL` environment variable.

```python
%openclaw_connect                        # use default
%openclaw_connect ws://localhost:8080   # specify URL
```

### `%openclaw <query>`

Execute a query against the current default agent. Results are displayed as Markdown in the notebook.

```python
result = %openclaw What is the capital of France?
print(result.content)
```

### `%openclaw_agent <agent_id>`

Switch the default agent for subsequent queries.

```python
%openclaw_agent research-bot
```

---

## Celery

**Module:** `openclaw_sdk.integrations.celery_tasks`

### `create_execute_task(celery_app, client)`

Creates a Celery task for executing a single agent query.

**Task name:** `openclaw.execute`

**Arguments:**

- `agent_id: str` — The agent to execute against
- `query: str` — The query string

**Returns:** A Celery task that can be called with `.delay()` or `.apply_async()`.

```python
from openclaw_sdk.integrations.celery_tasks import create_execute_task

execute_agent = create_execute_task(app, client)
result = execute_agent.delay("research-bot", "Find AI trends")
print(result.get())  # {'success': True, 'content': '...', 'latency_ms': 123, 'token_usage': {...}}
```

### `create_batch_task(celery_app, client)`

Creates a Celery task for batch agent execution.

**Task name:** `openclaw.batch`

**Arguments:**

- `agent_id: str` — The agent to execute against
- `queries: list[str]` — List of query strings

**Returns:** A Celery task that returns a list of result dictionaries.

```python
from openclaw_sdk.integrations.celery_tasks import create_batch_task

batch_execute = create_batch_task(app, client)
results = batch_execute.delay("research-bot", ["Query 1", "Query 2", "Query 3"])
print(results.get())
# [{'success': True, 'content': '...', 'latency_ms': 123}, ...]
```
