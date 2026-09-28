# Desktop agent connections

This project exposes a local MCP server. Each desktop agent starts the same
`email-in-chat` executable through stdio; client profiles translate that launch
instruction into each product's configuration format. The desktop agent supplies
the model and conversation. Mailbox connection, credentials, and mail operations
belong to the email service, not to the client configuration.

## Compatibility evidence

Official documentation was checked on **2026-09-28**. A documented configuration
path is not an end-to-end compatibility test. The profile tests cover generation,
parsing, preservation of existing settings, and refusal of unsafe writes. They do
not launch any desktop product or verify a real mailbox. MCP transport tests are
a separate layer and likewise do not establish desktop UI compatibility.

| Profile | Configuration target | Evidence and remaining validation |
| --- | --- | --- |
| `claude-code` | `~/.claude.json`, top-level `mcpServers` | Official docs say CLI and local Desktop Code sessions share it. Desktop end-to-end test pending. |
| `claude-desktop` | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` | Official local-server guide documents this JSON file. Desktop end-to-end test pending. |
| `claude-desktop-windows` | Windows: `%APPDATA%\Claude\claude_desktop_config.json` | Documented Windows path; verify the actual file using Settings → Developer → Edit Config. Windows end-to-end test pending. |
| `cursor` | `~/.cursor/mcp.json`, `mcpServers`, `type: "stdio"` | Official global configuration and stdio schema verified. Desktop end-to-end test pending. |
| `kimi-code` | `~/.kimi-code/mcp.json`, `mcpServers` | Kimi Code Desktop shares CLI configuration. New sessions load updates. Desktop end-to-end test pending. |
| `chatgpt-desktop` | `~/.codex/config.toml`, `[mcp_servers.email-in-chat]` | Current official OpenAI docs describe shared local configuration and stdio. Installed app/version/organization policy still requires validation. |
| `codex` | `~/.codex/config.toml`, `[mcp_servers.email-in-chat]` | Official local configuration documented. Client end-to-end test pending. |
| `chatgpt-web` | No local file | Needs a remote MCP/plugin connection or Secure MCP Tunnel for developer testing. No deploy or tunnel is provided by this installer. |

Sources: [Claude Code Desktop](https://code.claude.com/docs/en/desktop),
[Claude Code MCP schema](https://code.claude.com/docs/en/mcp),
[Claude Desktop local server guide](https://modelcontextprotocol.io/docs/develop/connect-local-servers),
[Cursor MCP](https://cursor.com/docs/mcp),
[Kimi Code Desktop settings](https://www.kimi.com/code/docs/en/kimi-code-desktop/settings-and-extensions.html),
[Kimi MCP schema](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/mcp.html),
[OpenAI MCP configuration](https://learn.chatgpt.com/docs/extend/mcp),
[OpenAI connection and testing](https://developers.openai.com/plugins/deploy/connect-chatgpt).

The ordinary Kimi chat application is outside this compatibility claim. ChatGPT
web does not read local Codex configuration. Secure MCP Tunnel can bridge a private
stdio or HTTP server for development, subject to account/workspace availability;
public plugin submission requires a public HTTPS endpoint. The current local
profile renderer does not implement hosting, OAuth for a remote service, tunnels,
or marketplace submission.

## Generate and install safely

Use an **absolute executable path** from the installed environment. GUI apps may
not inherit a terminal's PATH. Paths with spaces are ordinary string values; do
not add shell quotes inside `command` or individual `args` values. Never put
mailbox passwords or app passwords in these arguments.

The Python API renders configuration without reading the filesystem:

```python
from email_in_chat.clients import render_config

preview = render_config(
    "cursor",
    "/absolute/path/to/email-in-chat",
    ["serve"],
)
print(preview["content"])
```

`client_profiles()` returns independent metadata dictionaries. `CLIENTS` lists
the accepted profile identifiers. Every render result contains `client`,
`target_path`, `format`, `content`, `instructions`, `evidence_status`, and
`source_url`. Paths are templates, intentionally not expanded by these pure
functions. The Windows profile's `%APPDATA%` must be expanded by the caller on
Windows; when using a custom `CODEX_HOME`, supply its actual configuration path.

The installer accepts an explicit target and **previews by default**:

```python
from pathlib import Path
from email_in_chat.clients import install_config

result = install_config(
    "cursor",
    "/absolute/path/to/email-in-chat",
    ["serve"],
    target=Path("~/.cursor/mcp.json"),
    apply=False,
)
```

Set `apply=True` only when applying the reviewed installation. It merges only
`email-in-chat`, preserves other settings, refuses a different existing entry,
and treats an identical entry as an unchanged success. JSON values are retained
but whitespace is normalized; TOML comments and formatting are preserved with
`tomlkit`. Invalid JSON/TOML, duplicate JSON keys, non-file targets, and symlink
targets or parent directories are rejected.

An update writes a private backup beside the original before atomically replacing
the configuration. The result reports the backup path and status, never the
existing configuration or its secrets. `content` is always only the generated
snippet, including during preview. Keep backups private because they contain the
original configuration. The installer checks for changes before replacement;
avoid editing client configuration concurrently with installation.

After applying, follow the profile's restart/new-session instructions. A minimal
desktop acceptance run should record product version, OS, successful MCP tool
discovery, an account-list call, a synthetic read request, and denial of a write
that has not been authorized. Do not label a product "tested" until those steps
actually run in that product.
