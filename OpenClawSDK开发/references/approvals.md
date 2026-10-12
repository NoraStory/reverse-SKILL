# ApprovalManager Reference

Manage pending execution approvals in the OpenClaw SDK.

When an agent operates in `"confirm"` permission mode it pauses before executing dangerous tools (shell commands, file writes, etc.) and emits an `approval.requested` push event via `Gateway.subscribe()`.

## Installation

```python
from openclaw_sdk import OpenClaw
from openclaw_sdk.approvals import ApprovalManager
```

## Access via Client

```python
client = OpenClaw(...)
manager: ApprovalManager = client.approvals
```

## Gateway RPC Methods

| Method | RPC | Description |
|--------|-----|-------------|
| `resolve(request_id, decision)` | `exec.approval.resolve` | Approve or deny a pending request |
| `request(command, *, timeout_ms, agent_id, session_key, node_id)` | `exec.approval.request` | Request approval for a command (blocks until resolved) |
| `wait_decision(approval_id)` | `exec.approval.waitDecision` | Wait for an approval decision by ID |
| `get_settings()` | `exec.approvals.get` | Get approval settings |
| `set_settings(file, base_hash)` | `exec.approvals.set` | Set approval rules |
| `get_node_settings(node_id)` | `exec.approvals.node.get` | Get node-level settings |
| `set_node_settings(node_id, file, base_hash)` | `exec.approvals.node.set` | Set node-level settings |

---

## `resolve(request_id, decision)`

Approve or deny a pending execution request.

**Gateway method:** `exec.approval.resolve`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `request_id` | `str` | The approval request identifier (from the push event) |
| `decision` | `Literal["approve", "deny"]` | The decision |

**Returns:** `dict[str, Any]` — Gateway response dict

**Example:**

```python
result = await client.approvals.resolve(request_id, "approve")
```

---

## `request(command, *, timeout_ms=None, agent_id=None, session_key=None, node_id=None)`

Request approval for a command execution. Blocks until resolved.

**Gateway method:** `exec.approval.request`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `command` | `str` | The command string to request approval for |
| `timeout_ms` | `int \| None` | Optional timeout in milliseconds |
| `agent_id` | `str \| None` | Optional agent identifier |
| `session_key` | `str \| None` | Optional session key |
| `node_id` | `str \| None` | Optional node identifier |

**Returns:** `dict[str, Any]` — `{id, decision, createdAtMs, expiresAtMs}`

Decision values: `"allow-once"` | `"allow-always"` | `"deny"` | `null` (expired)

**Example:**

```python
result = await client.approvals.request(
    "rm -rf /tmp/files",
    timeout_ms=30000,
    agent_id="agent-123"
)
```

---

## `wait_decision(approval_id)`

Wait for an approval decision. Blocks until resolved.

**Gateway method:** `exec.approval.waitDecision`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `approval_id` | `str` | The approval request identifier |

**Returns:** `dict[str, Any]` — `{id, decision, createdAtMs, expiresAtMs}`

**Example:**

```python
result = await client.approvals.wait_decision(approval_id)
```

---

## `get_settings()`

Get the approval settings/config.

**Gateway method:** `exec.approvals.get`

**Returns:** `dict[str, Any]` — `{path, exists, hash, file: {version, socket, defaults, agents}}`

**Example:**

```python
settings = await client.approvals.get_settings()
```

---

## `set_settings(file, base_hash=None)`

Set approval settings with optimistic concurrency.

**Gateway method:** `exec.approvals.set`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `file` | `dict[str, Any]` | The approval settings object (must include `version`) |
| `base_hash` | `str \| None` | Optional hash for optimistic concurrency control |

**Returns:** `dict[str, Any]` — Same structure as `get_settings()`

**Example:**

```python
result = await client.approvals.set_settings(
    file={"version": "1.0", "defaults": {...}},
    base_hash="abc123"
)
```

---

## `get_node_settings(node_id)`

Get node-level approval settings. Proxied to node. Unavailable if the node is not connected.

**Gateway method:** `exec.approvals.node.get`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `node_id` | `str` | The target node identifier |

**Returns:** `dict[str, Any]` — Node-specific approval settings

**Example:**

```python
settings = await client.approvals.get_node_settings("node-456")
```

---

## `set_node_settings(node_id, file, base_hash=None)`

Set node-level approval settings. Proxied to node.

**Gateway method:** `exec.approvals.node.set`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `node_id` | `str` | The target node identifier |
| `file` | `dict[str, Any]` | The approval settings object (must include `version`) |
| `base_hash` | `str \| None` | Optional hash for optimistic concurrency control |

**Returns:** `dict[str, Any]` — Updated node-specific approval settings

**Example:**

```python
result = await client.approvals.set_node_settings(
    "node-456",
    file={"version": "1.0", "defaults": {...}},
    base_hash="def456"
)
```

---

## Typical Workflow

```python
# 1. Subscribe for approval events
async for event in await client.gateway.subscribe(["approval.requested"]):
    request_id = event.data["id"]
    # 2. Decide whether to approve or deny
    result = await client.approvals.resolve(request_id, "approve")
```

## Notes

- Approval settings use optimistic concurrency via `base_hash`. Provide the hash from a prior `get_settings()` call to prevent conflicting updates.
- Node-level settings (`get_node_settings` / `set_node_settings`) are proxied through the gateway to the target node and require the node to be connected.
- The `request()` method blocks until the approval is resolved or the timeout expires.
