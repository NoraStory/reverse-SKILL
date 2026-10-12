# NodeManager Reference

Access via `client.nodes` property:

```python
from openclaw_sdk import OpenClawClient

client = await OpenClawClient.connect()
async with client:
    nodes = await client.nodes.list()
```

## Gateway RPC Methods

| Method | RPC | Description |
|--------|-----|-------------|
| `system_presence()` | `system-presence` | Get system presence |
| `list()` | `node.list` | List all nodes |
| `describe(node_id)` | `node.describe` | Get node details |
| `invoke(node_id, action, payload)` | `node.invoke` | Invoke action on node |
| `rename(node_id, display_name)` | `node.rename` | Rename node |
| `pair_request(node_id)` | `node.pair.request` | Request pairing |
| `pair_list()` | `node.pair.list` | List pairing requests |
| `pair_approve(request_id)` | `node.pair.approve` | Approve pairing |
| `pair_reject(request_id)` | `node.pair.reject` | Reject pairing |
| `pair_verify(node_id, token)` | `node.pair.verify` | Verify pairing |

## system_presence()

Return the gateway's system-presence status.

```python
presence = await client.nodes.system_presence()
```

Returns: `dict[str, Any]` — Dict with presence information (online nodes, uptime, etc.)

## list()

List all registered nodes.

```python
nodes = await client.nodes.list()
# [{'id': 'n1', 'name': 'Node 1', 'status': 'online'}, ...]
```

Returns: `list[dict[str, Any]]` — List of node descriptor dicts.

## describe(node_id)

Fetch detailed information about a specific node.

```python
node = await client.nodes.describe("n1")
```

Args:
- `node_id` (str): The node identifier.

Returns: `dict[str, Any]` — Node descriptor dict.

## invoke(node_id, action, payload=None)

Invoke an action on a specific node.

```python
result = await client.nodes.invoke("n1", "status", {"verbose": True})
```

Args:
- `node_id` (str): The node identifier.
- `action` (str): The action name to invoke.
- `payload` (dict[str, Any] | None): Optional parameters for the action.

Returns: `dict[str, Any]` — Gateway response dict.

## rename(node_id, display_name)

Rename a node.

```python
await client.nodes.rename("n1", "My Node")
```

Args:
- `node_id` (str): The node identifier.
- `display_name` (str): The new display name.

Returns: `dict[str, Any]` — Gateway response dict.

## pair_request(node_id)

Request node pairing.

```python
result = await client.nodes.pair_request("n1")
```

Args:
- `node_id` (str): The node identifier to pair.

Returns: `dict[str, Any]` — Gateway response dict.

## pair_list()

List pending and paired nodes.

```python
pairs = await client.nodes.pair_list()
# {'pending': [...], 'paired': [...]}
```

Returns: `dict[str, Any]` — Dict with `pending` and `paired` arrays.

## pair_approve(request_id)

Approve a node pairing request.

```python
await client.nodes.pair_approve("req-123")
```

Args:
- `request_id` (str): The pairing request identifier.

Returns: `dict[str, Any]` — Gateway response dict.

## pair_reject(request_id)

Reject a node pairing request.

```python
await client.nodes.pair_reject("req-123")
```

Args:
- `request_id` (str): The pairing request identifier.

Returns: `dict[str, Any]` — Gateway response dict.

## pair_verify(node_id, token)

Verify a node pairing.

```python
await client.nodes.pair_verify("n1", "token-abc")
```

Args:
- `node_id` (str): The node identifier.
- `token` (str): The verification token.

Returns: `dict[str, Any]` — Gateway response dict.

## Role-Restricted Methods

The following methods require the `node` role and are typically used by node processes themselves:

- `invoke_result(**params)` — Submit an invoke result back to the gateway (RPC: `node.invoke.result`)
- `emit_event(**params)` — Emit a node event (RPC: `node.event`)
