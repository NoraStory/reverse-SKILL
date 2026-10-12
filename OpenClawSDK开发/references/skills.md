# Skills Module Reference

Source: `openclaw_sdk/src/openclaw_sdk/skills/`

## SkillManager

**File:** `manager.py`

Manages OpenClaw skills via two code paths:

- **Gateway RPC methods** (preferred when a gateway is available)
- **CLI methods** (legacy, subprocess-based)

---

### Gateway RPC Methods

These methods require a `GatewayProtocol` instance to be passed at construction time.

| Method | RPC | Description |
|--------|-----|-------------|
| `status()` | `skills.status` | Get full skills status. Returns dict with `workspaceDir`, `managedSkillsDir`, and `skills` array. Raises `RuntimeError` if no gateway is configured. |
| `install_via_gateway(name, install_id)` | `skills.install` | Install a skill via gateway RPC. Args: `name` (skill name), `install_id` (unique installation identifier). Raises `RuntimeError` if no gateway is configured. |
| `update_skill(skill_key)` | `skills.update` | Update a skill via gateway RPC. Args: `skill_key` (skill key identifying the skill). Raises `RuntimeError` if no gateway is configured. |

---

### CLI Methods (Legacy — subprocess-backed)

These methods spawn a subprocess running `openclaw <command> --json`.

| Method | CLI Command | Description |
|--------|-------------|-------------|
| `list_skills()` | `openclaw skills list --json` | List all installed skills. Returns `list[SkillInfo]`. |
| `install_skill(name, source="clawhub", config=None)` | `openclaw skills install <name> [--source <source>]` | Install a skill. Args: `name` (skill name), `source` (default "clawhub"), `config` (optional config dict). Returns `SkillInfo`. |
| `uninstall_skill(name)` | `openclaw skills uninstall <name>` | Uninstall a skill. Returns `bool`. |
| `enable_skill(name)` | `openclaw skills enable <name>` | Enable a skill. Returns `bool`. |
| `disable_skill(name)` | `openclaw skills disable <name>` | Disable a skill. Returns `bool`. |

---

### SkillInfo Model

```python
class SkillInfo(BaseModel):
    name: str
    description: str | None = None
    source: Literal["clawhub", "local", "git"] | None = None
    version: str | None = None
    enabled: bool = True
```

---

## ClawHub

**File:** `clawhub.py`

Browse and discover skills from the ClawHub marketplace via CLI. **CLI-only — there is no gateway RPC for skill discovery.**

All methods spawn a subprocess running `openclaw <command> --json`.

| Method | CLI Command | Description |
|--------|-------------|-------------|
| `search(query, limit=20)` | `openclaw skills search <query>` | Search the marketplace. Returns `list[ClawHubSkill]`. |
| `browse(category=None, limit=20)` | `openclaw skills browse [--category <category>]` | Browse skills by category. Returns `list[ClawHubSkill]`. |
| `get_details(name)` | `openclaw skills info <name>` | Get detailed info for a specific skill. Returns `ClawHubSkill`. |
| `get_categories()` | `openclaw skills categories` | List all available categories. Returns `list[str]`. |
| `get_trending(limit=10)` | `openclaw skills trending` | Get trending skills. Returns `list[ClawHubSkill]`. |

---

### ClawHubSkill Model

```python
class ClawHubSkill(BaseModel):
    name: str
    description: str
    author: str = ""
    version: str = ""
    downloads: int = 0
    rating: float = 0.0
    category: str | None = None
    required_config: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
```
