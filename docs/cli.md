# CLI 契约

全局参数 `--json`、`--config` 放在子命令前。配置路径优先级：`--config` → `EMAIL_IN_CHAT_CONFIG` → `$XDG_CONFIG_HOME/all-email-in-chat/accounts.toml`，默认等于 `~/.config/all-email-in-chat/accounts.toml`。

| 用途 | 示例 |
| --- | --- |
| 离线初始化 | `email-in-chat --config ~/.config/all-email-in-chat-demo/accounts.toml init --demo` |
| 查看预设/客户端 | `email-in-chat --json providers` / `email-in-chat --json clients list` |
| 查看账号/权限 | `email-in-chat --json accounts list` / `email-in-chat policy show` |
| 添加账号 | `email-in-chat accounts add work --provider aliyun-enterprise --email you@example.com` |
| 私人终端录入凭证 | `email-in-chat accounts auth work`；SMTP 独立密码加 `--separate-smtp` |
| 诊断 / 协议检查 | `email-in-chat --json doctor` / `email-in-chat --json doctor --smoke` |
| 搜索邮件 | `email-in-chat --json messages search --account work --subject invoice --limit 10 --page 1` |
| 读指定 UID | `email-in-chat --json messages read --account work --mailbox INBOX --id 101` |
| 保存草稿 | `email-in-chat draft --request examples/message.json` |
| 预览 / 发送 | `email-in-chat send --request examples/message.json`；实际提交加 `--execute` |
| 工具名与账号发现 | `email-in-chat --json tools` |
| 原始调用 | `email-in-chat --json tool-call list_mailboxes --arguments '{"account_name":"work"}'` |
| 导出客户端配置 | `email-in-chat clients config kimi-code` |
| 预览 / 合并配置 | `email-in-chat clients install kimi-code`；应用加 `--apply` |
| MCP 服务 | `email-in-chat serve`（stdout 专用于 JSON-RPC） |

工具参数 schema 通过 MCP `tools/list` 获取；`tools` CLI 返回获准的工具名与协议检查结果。原始调用和 MCP 调用使用相同权限检查。

`messages search` 默认 INBOX、第一页、10 封，支持 `--unread`、`--text`、`--from-address`、`--mailbox`。`--limit` 为 1..100；邮箱内容变化时页码可能漂移。消息 UID 必须和账号、文件夹一起使用，移动后重新发现 UID。

## JSON 与退出码

普通成功：

```json
{"ok": true, "data": {"mode": "read", "allowed_recipients": [], "effective_on": "next server start"}}
```

邮件工具调用保留 MCP `content`、`structuredContent`、`isError` 等字段，外层带 `demo`。不要把协议成功等同业务成功。

```json
{"ok": true, "data": {"content": [], "structuredContent": {"result": []}, "isError": false}, "demo": false}
```

本地参数或配置错误：

```json
{"ok": false, "error": {"code": "invalid_request", "message": "Arguments must be a JSON object."}}
```

退出码：0 表示正常返回；1 表示调用或协议检查失败；2 表示参数/配置无效；130 表示用户中断。`--help` 是 argparse 的帮助文本。每次命令不自动重试写操作。

发送预览仅回显待发送请求，**不验证连接、收件人权限或最终可发送性**。实际调用才进行 schema、模式、账号和后端权限检查。请求文件可能包含私人正文，请保存在私人目录，不要提交进仓库。

## 配置与更新

`init` 不覆盖现有文件，`accounts add` 不覆盖同名账号。凭证保存到 keyring，键包含随机配置 namespace，避免不同配置互相覆盖。复制整个配置会复制 namespace，因此不要把它当作创建新配置的方法。

后端快照只含 keyring 占位符；客户端原配置的备份可能含其他服务的秘密，必须保持私人权限。不要手工编辑 runtime 快照，更新账号配置后重新启动 MCP。

在项目根目录升级本地安装：`uv tool install --reinstall --python 3.12 .`，然后重启客户端中的 MCP 服务。若 `email-in-chat` 不在 PATH，使用 `uv tool update-shell` 后打开新终端。若 `CODEX_HOME` 被自定义，使用 `clients install codex --target /absolute/path/config.toml`。
