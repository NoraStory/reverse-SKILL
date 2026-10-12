# Connectors Reference

> **Important**: All connectors in this module call third-party SaaS APIs **directly** — they do NOT route through the OpenClaw gateway. Each connector establishes its own HTTP connection to the vendor's REST API using credentials you provide via `ConnectorConfig`.

All connectors inherit from `Connector` and use `httpx.AsyncClient` for HTTP. They are async context managers.

```python
from openclaw_sdk.connectors.base import ConnectorConfig

config = ConnectorConfig(api_key="...", base_url="...")  # per-connector requirements
async with SomeConnector(config) as conn:
    result = await conn.some_method(...)
```

---

## Base Classes

### ConnectorConfig

| Field | Type | Description |
|---|---|---|
| `api_key` | `str \| None` | Primary API key or OAuth access token |
| `api_secret` | `str \| None` | Secondary secret (e.g. Basic auth password) |
| `base_url` | `str \| None` | Override default API base URL |
| `timeout` | `float` | HTTP request timeout in seconds (default: 30.0) |
| `extra_headers` | `dict[str, str]` | Additional headers merged into every request |

### Connector

Abstract base class. Subclasses must implement `_build_headers()` and `list_actions()`.

- `connect()` — opens the HTTP client
- `close()` — closes the HTTP client
- `__aenter__` / `__aexit__` — async context manager protocol

---

## GitHubConnector

**API**: GitHub REST API v3  
**Base URL**: `https://api.github.com`  
**Auth**: `api_key` = Personal Access Token or GitHub App token (Bearer token)

```python
from openclaw_sdk.connectors.github import GitHubConnector
from openclaw_sdk.connectors.base import ConnectorConfig

config = ConnectorConfig(api_key="ghp_xxx")
async with GitHubConnector(config) as gh:
    repos = await gh.list_repos(org="myorg")
```

### Methods

#### list_repos(org: str | None = None, per_page: int = 30) -> list[dict[str, Any]]
List repositories for the authenticated user or an organisation.

- `org` — if provided, list repos for this organisation
- `per_page` — results per page (max 100)

#### get_repo(owner: str, repo: str) -> dict[str, Any]
Get details of a single repository.

#### create_issue(owner: str, repo: str, title: str, body: str = "", labels: list[str] | None = None) -> dict[str, Any]
Create a new issue on a repository.

#### list_issues(owner: str, repo: str, state: str = "open", per_page: int = 30) -> list[dict[str, Any]]
List issues for a repository.

- `state` — `"open"`, `"closed"`, or `"all"`

#### get_issue(owner: str, repo: str, number: int) -> dict[str, Any]
Get a single issue by number.

---

## SlackConnector

**API**: Slack Web API  
**Base URL**: `https://slack.com/api`  
**Auth**: `api_key` = Bot Token (`xoxb-...`)

```python
from openclaw_sdk.connectors.slack_connector import SlackConnector
from openclaw_sdk.connectors.base import ConnectorConfig

config = ConnectorConfig(api_key="xoxb-xxx")
async with SlackConnector(config) as slack:
    await slack.send_message("#general", "Hello from OpenClaw!")
```

### Methods

#### send_message(channel: str, text: str) -> dict[str, Any]
Send a message to a Slack channel.

- `channel` — channel name (`"#general"`) or ID (`"C01234"`)
- `text` — message text

#### list_channels(limit: int = 100) -> dict[str, Any]
List all public channels in the workspace.

#### post_file(channel: str, content: str, filename: str) -> dict[str, Any]
Upload a text snippet to a channel.

- `channel` — target channel ID or name
- `content` — file content as a string
- `filename` — display filename

#### list_users(limit: int = 100) -> dict[str, Any]
List all users in the workspace.

---

## GmailConnector

**API**: Gmail API v1  
**Base URL**: `https://gmail.googleapis.com/gmail/v1`  
**Auth**: `api_key` = OAuth2 access token (Bearer token)

```python
from openclaw_sdk.connectors.gmail import GmailConnector
from openclaw_sdk.connectors.base import ConnectorConfig

config = ConnectorConfig(api_key="ya29.xxx")
async with GmailConnector(config) as gmail:
    await gmail.send_email("user@example.com", "Hello", "Body text")
```

### Methods

#### send_email(to: str, subject: str, body: str) -> dict[str, Any]
Send an email via Gmail. Body is plain-text; the connector base64url-encodes the RFC 2822 message internally.

#### list_messages(query: str = "", max_results: int = 10) -> dict[str, Any]
List messages matching a Gmail search query.

- `query` — Gmail search syntax (e.g. `"from:user@example.com"`)
- `max_results` — maximum messages to return

#### get_message(message_id: str) -> dict[str, Any]
Get a single message by ID. Returns full message object with headers, body, and metadata.

---

## GoogleSheetsConnector

**API**: Google Sheets API v4  
**Base URL**: `https://sheets.googleapis.com/v4`  
**Auth**: `api_key` = OAuth2 access token (Bearer token)

```python
from openclaw_sdk.connectors.google_sheets import GoogleSheetsConnector
from openclaw_sdk.connectors.base import ConnectorConfig

config = ConnectorConfig(api_key="ya29.xxx")
async with GoogleSheetsConnector(config) as sheets:
    data = await sheets.get_values("spreadsheet_id", "Sheet1!A1:C10")
```

### Methods

#### get_values(spreadsheet_id: str, range_: str) -> dict[str, Any]
Read values from a spreadsheet range (A1 notation).

- `spreadsheet_id` — the spreadsheet ID
- `range_` — e.g. `"Sheet1!A1:C10"`

#### update_values(spreadsheet_id: str, range_: str, values: list[list[Any]]) -> dict[str, Any]
Write values to a spreadsheet range.

- `values` — 2D array of values to write

#### list_sheets(spreadsheet_id: str) -> dict[str, Any]
List all sheets (tabs) in a spreadsheet. Returns `sheets` array with sheet metadata.

---

## NotionConnector

**API**: Notion API  
**Base URL**: `https://api.notion.com/v1`  
**Auth**: `api_key` = Internal Integration Token (Bearer token)

```python
from openclaw_sdk.connectors.notion import NotionConnector
from openclaw_sdk.connectors.base import ConnectorConfig

config = ConnectorConfig(api_key="ntn_xxx")
async with NotionConnector(config) as notion:
    results = await notion.search("Project Plan")
```

### Methods

#### search(query: str = "") -> dict[str, Any]
Search across all pages and databases accessible to the integration.

- `query` — search text; empty string returns recent pages

#### get_page(page_id: str) -> dict[str, Any]
Retrieve a page by ID. Page ID is a UUID (with or without dashes).

#### create_page(parent_id: str, properties: dict[str, Any], is_database: bool = False) -> dict[str, Any]
Create a new page inside a parent page or database.

- `is_database` — if `True`, `parent_id` is treated as a database ID; otherwise as a page ID

#### get_database(database_id: str) -> dict[str, Any]
Retrieve a database by ID. Returns database schema and metadata.

---

## JiraConnector

**API**: Jira Cloud REST API v3  
**Base URL**: Must be set per instance (e.g. `https://yourorg.atlassian.net`)  
**Auth**: `api_key` = email address, `api_secret` = API token — sent as Basic auth

```python
from openclaw_sdk.connectors.jira import JiraConnector
from openclaw_sdk.connectors.base import ConnectorConfig

config = ConnectorConfig(
    api_key="you@company.com",
    api_secret="ATATT3...",
    base_url="https://yourorg.atlassian.net",
)
async with JiraConnector(config) as jira:
    issues = await jira.search_issues("project = DEV")
```

### Methods

#### search_issues(jql: str, max_results: int = 50) -> dict[str, Any]
Search for issues using JQL (Jira Query Language).

#### get_issue(issue_key: str) -> dict[str, Any]
Get a single issue by key (e.g. `"DEV-123"`).

#### create_issue(project_key: str, summary: str, issue_type: str = "Task", description: str = "") -> dict[str, Any]
Create a new Jira issue.

- `project_key` — e.g. `"DEV"`
- `issue_type` — e.g. `"Task"`, `"Bug"`, `"Story"`
- `description` — plain-text description

#### update_issue(issue_key: str, fields: dict[str, Any]) -> None
Update an existing Jira issue.

- `fields` — dictionary of Jira field names and values to update

---

## StripeConnector

**API**: Stripe REST API v1  
**Base URL**: `https://api.stripe.com/v1`  
**Auth**: `api_key` = Secret key (Bearer token). Uses form-encoded request bodies, not JSON.

```python
from openclaw_sdk.connectors.stripe_connector import StripeConnector
from openclaw_sdk.connectors.base import ConnectorConfig

config = ConnectorConfig(api_key="sk_test_xxx")
async with StripeConnector(config) as stripe:
    customers = await stripe.list_customers(limit=10)
```

### Methods

#### list_customers(limit: int = 10) -> dict[str, Any]
List Stripe customers. Returns a Stripe list object with `data` array.

#### create_customer(email: str | None = None, name: str | None = None) -> dict[str, Any]
Create a new Stripe customer. Note: Stripe uses form-encoded data, not JSON.

#### list_charges(limit: int = 10) -> dict[str, Any]
List recent charges. Returns a Stripe list object with `data` array.

#### get_charge(charge_id: str) -> dict[str, Any]
Retrieve a single charge by ID (e.g. `"ch_xxx"`).

---

## ZendeskConnector

**API**: Zendesk Support API v2  
**Base URL**: Must include Zendesk subdomain (e.g. `https://yourorg.zendesk.com/api/v2`)  
**Auth**: `api_key` = agent email, `api_secret` = Zendesk API token — sent as Basic auth with `{email}/token:{api_token}` format

```python
from openclaw_sdk.connectors.zendesk import ZendeskConnector
from openclaw_sdk.connectors.base import ConnectorConfig

config = ConnectorConfig(
    api_key="agent@co.com",
    api_secret="zd_token_xxx",
    base_url="https://myco.zendesk.com/api/v2",
)
async with ZendeskConnector(config) as zd:
    tickets = await zd.list_tickets(status="open")
```

### Methods

#### list_tickets(status: str | None = None, per_page: int = 25) -> dict[str, Any]
List support tickets.

- `status` — filter: `"new"`, `"open"`, `"pending"`, `"solved"`, `"closed"`; `None` returns all

#### get_ticket(ticket_id: int) -> dict[str, Any]
Get a single ticket by ID.

#### create_ticket(subject: str, description: str, priority: str = "normal") -> dict[str, Any]
Create a new support ticket.

- `priority` — `"low"`, `"normal"`, `"high"`, `"urgent"`

#### update_ticket(ticket_id: int, fields: dict[str, Any]) -> dict[str, Any]
Update an existing ticket.

- `fields` — e.g. `{"status": "solved", "priority": "high"}`

---

## HubSpotConnector

**API**: HubSpot CRM API v3  
**Base URL**: `https://api.hubapi.com`  
**Auth**: `api_key` = Private App access token (Bearer token)

```python
from openclaw_sdk.connectors.hubspot import HubSpotConnector
from openclaw_sdk.connectors.base import ConnectorConfig

config = ConnectorConfig(api_key="pat-xxx")
async with HubSpotConnector(config) as hs:
    contacts = await hs.list_contacts(limit=10)
```

### Methods

#### list_contacts(limit: int = 10) -> dict[str, Any]
List CRM contacts. Returns `results` array of contact objects.

#### create_contact(email: str, properties: dict[str, str] | None = None) -> dict[str, Any]
Create a new CRM contact.

- `email` — required
- `properties` — additional properties (e.g. `firstname`, `lastname`, `phone`)

#### list_deals(limit: int = 10) -> dict[str, Any]
List CRM deals. Returns `results` array of deal objects.

#### get_deal(deal_id: str) -> dict[str, Any]
Get a single deal by ID.

---

## SalesforceConnector

**API**: Salesforce REST API (version `v58.0`)  
**Base URL**: Must be set per instance (e.g. `https://yourorg.my.salesforce.com`)  
**Auth**: `api_key` = OAuth access token (Bearer token)

```python
from openclaw_sdk.connectors.salesforce import SalesforceConnector
from openclaw_sdk.connectors.base import ConnectorConfig

config = ConnectorConfig(
    api_key="00Dxx0000...",
    base_url="https://yourorg.my.salesforce.com",
)
async with SalesforceConnector(config) as sf:
    result = await sf.query("SELECT Id, Name FROM Account LIMIT 10")
```

### Methods

#### query(soql: str) -> dict[str, Any]
Execute a SOQL query. Returns `records` array and `totalSize`.

#### get_record(sobject: str, record_id: str) -> dict[str, Any]
Get a single sObject record by ID.

- `sobject` — e.g. `"Account"`, `"Contact"`

#### create_record(sobject: str, fields: dict[str, Any]) -> dict[str, Any]
Create a new sObject record.

- Returns `id` and `success` flag

#### update_record(sobject: str, record_id: str, fields: dict[str, Any]) -> None
Update an existing sObject record. Salesforce PATCH returns 204 No Content on success.
