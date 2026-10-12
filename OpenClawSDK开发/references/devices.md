# DeviceManager Reference

Manage device tokens and pairing for multi-device access.

OpenClaw supports multiple connected devices (CLI, web UI, mobile nodes). Each device has an auth token that can be rotated or revoked. Devices can also be paired, approved, rejected, and removed.

**Source:** `openclaw_sdk/devices/manager.py`

## Gateway RPC Methods

| Method | RPC | Description |
|--------|-----|-------------|
| `rotate_token(device_id, role)` | `device.token.rotate` | Rotate auth token |
| `revoke_token(device_id, role)` | `device.token.revoke` | Revoke auth token |
| `list_paired()` | `device.pair.list` | List paired devices |
| `approve_pairing(request_id)` | `device.pair.approve` | Approve pairing |
| `reject_pairing(request_id)` | `device.pair.reject` | Reject pairing |
| `remove_device(device_id)` | `device.pair.remove` | Remove device |

## Method Details

### rotate_token(device_id, role)

Rotate the auth token for a device.

**RPC:** `device.token.rotate`

**Params:**
- `device_id` (str) - The device identifier
- `role` (str) - The device's role (e.g. `"operator"`, `"node"`)

**Returns:** `dict[str, Any]` - Gateway response dict (typically contains the new token)

### revoke_token(device_id, role)

Revoke the auth token for a device.

**RPC:** `device.token.revoke`

**Params:**
- `device_id` (str) - The device identifier
- `role` (str) - The device's role (e.g. `"operator"`, `"node"`)

**Returns:** `dict[str, Any]` - Gateway response dict

### list_paired()

List all pending and paired devices.

**RPC:** `device.pair.list`

**Returns:** `dict[str, Any]` - Dict with `pending` and `paired` arrays

### approve_pairing(request_id)

Approve a device pairing request.

**RPC:** `device.pair.approve`

**Params:**
- `request_id` (str) - The pairing request identifier

**Returns:** `dict[str, Any]` - Gateway response dict

### reject_pairing(request_id)

Reject a device pairing request.

**RPC:** `device.pair.reject`

**Params:**
- `request_id` (str) - The pairing request identifier

**Returns:** `dict[str, Any]` - Gateway response dict

### remove_device(device_id)

Remove a paired device.

**RPC:** `device.pair.remove`

**Params:**
- `device_id` (str) - The device identifier to remove

**Returns:** `dict[str, Any]` - Gateway response dict

## Usage Example

```python
client = await OpenClawClient.connect()
async with client:
    # Token management
    result = await client.devices.rotate_token("device_abc", "operator")
    await client.devices.revoke_token("device_abc", "node")

    # Pairing workflow
    devices = await client.devices.list_paired()
    await client.devices.approve_pairing("req_123")
    await client.devices.reject_pairing("req_456")
    await client.devices.remove_device("device_abc")
```
