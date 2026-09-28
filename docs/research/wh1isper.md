# Wh1isper/mcp-email-server 审查

核查日期：2026-09-28（Asia/Shanghai）。本报告用于 All Email in Chat 的依赖选型；只读源码审查与合成数据测试，不包含真实邮箱验证。

## 快照与许可证

- 仓库：[Wh1isper/mcp-email-server](https://github.com/Wh1isper/mcp-email-server)。
- 核查 commit：`d364b64d2e89bd3686edb82624e1feb9a5562e1b`，2026-09-14。
- GitHub 最新正式 release：[1.9.1](https://github.com/Wh1isper/mcp-email-server/releases/tag/1.9.1)，发布时间 `2026-09-14T06:49:19Z`；tag 经 API 解引用为上述同一 commit。
- 源码的 `pyproject.toml` 版本为 `0.0.1`，上游 release workflow 在发布隔离构建时盖上 tag 版本；不能把源码安装显示的 0.0.1 当成 PyPI 最新版本。
- 主程序为 [BSD-3-Clause](https://github.com/Wh1isper/mcp-email-server/blob/d364b64d2e89bd3686edb82624e1feb9a5562e1b/LICENSE)。若复制/分发代码，保留版权、条款、免责声明，不能暗示原作者背书。上游插件 manifest 另写 MIT，不应据此把整个后端描述为 MIT。

## 能力与证据

| 能力 | 源码/文档核查结果 | 实际服务商验证 |
|---|---|---|
| MCP / CLI | Python + 官方 `mcp` SDK FastMCP；stdio、SSE、Streamable HTTP；CLI/UI 管账号，MCP 只暴露邮件工作流 | 未验证桌面产品 |
| 收取与搜索 | 分页元数据、IMAP 条件搜索、正文截取；正文默认 `mark_as_read=false` | 未连接真实邮箱 |
| 发送与回复 | SMTP；To/Cc/Bcc、纯文本/HTML、回复 `In-Reply-To`/`References`；显式区分 SMTP 接受与 Sent 副本结果 | 未实际发信 |
| 会话线程 | 返回并接受 RFC Message-ID 相关头；没有把它等同 Gmail 原生线程 API | 未验证客户端呈现 |
| 附件 | 发送附件；读取为 MCP binary resource；下载到文件；两种读取策略独立配置，默认关闭 | 未验证真实附件 |
| 文件夹 / 草稿 | 列目录、移动、归档、保存 MIME 到指定目录、标记、IMAP keyword tags | 未实际远端修改 |
| 多账号 | 一个 TOML 多个 `[[emails]]` 或 managed SQLite catalog | 合成账号契约测试 |
| 凭证 | legacy keyring sentinel；managed macOS 用 OS keyring，Linux/Windows 用受文件权限保护的 SQLite 明文 secret 列 | 不访问真实钥匙串 |
| OAuth | 当前 EmailServer 只有用户名/密码；IMAP/SMTP 使用 `.login()`；未找到 OAuth/token-refresh 实现 | 不宣称支持仅 OAuth 的邮箱 |

关键源码：

- [MCP 工具与 schema](https://github.com/Wh1isper/mcp-email-server/blob/d364b64d2e89bd3686edb82624e1feb9a5562e1b/mcp_email_server/app.py#L289)
- [默认读信行为](https://github.com/Wh1isper/mcp-email-server/blob/d364b64d2e89bd3686edb82624e1feb9a5562e1b/mcp_email_server/app.py#L469)
- [邮件协议实现](https://github.com/Wh1isper/mcp-email-server/blob/d364b64d2e89bd3686edb82624e1feb9a5562e1b/mcp_email_server/emails/classic.py#L921)
- [发送/不确定结果模型](https://github.com/Wh1isper/mcp-email-server/blob/d364b64d2e89bd3686edb82624e1feb9a5562e1b/mcp_email_server/application/mutations.py#L20)
- [安全及凭证存储说明](https://github.com/Wh1isper/mcp-email-server/blob/d364b64d2e89bd3686edb82624e1feb9a5562e1b/docs/security.md)

## 作为首版后端的接口契约

建议以锁定版本的子进程调用，复用已存在的 MCP tool catalog，不导入业务内部实现，也不重写 IMAP/SMTP。

```text
MCP_EMAIL_SERVER_CONFIG_PATH=/absolute/private/directory/config.toml
mcp-email-server stdio
```

`MCP_EMAIL_SERVER_CONFIG_PATH` 在模块导入时解析，因此必须在子进程启动前设定；默认配置会使用真实用户目录，测试必须显式覆盖。独立路径还决定邻接的 bootstrap/catalog 元数据路径。源码依据：[路径解析](https://github.com/Wh1isper/mcp-email-server/blob/d364b64d2e89bd3686edb82624e1feb9a5562e1b/mcp_email_server/config.py#L222)、[stdio 入口](https://github.com/Wh1isper/mcp-email-server/blob/d364b64d2e89bd3686edb82624e1feb9a5562e1b/mcp_email_server/cli.py#L1272)。

Legacy TOML 账号契约（下列仅合成示例；实际凭证不写入聊天或客户端 JSON）：

```toml
credential_storage = "keyring"
allowed_recipients = []

[[emails]]
account_name = "all-email-in-chat-demo"
full_name = "Demo"
email_address = "demo@example.invalid"
save_to_sent = true

[emails.incoming]
user_name = "demo@example.invalid"
password = "__KEYRING__"
host = "imap.example.invalid"
port = 993
use_ssl = true
start_ssl = false
verify_ssl = true
```

发送配置为独立 `[emails.outgoing]`，字段相同。`allowed_recipients=[]` 默认拒绝发送及收件人相关的草稿保存；项目不能静默改成 `*`。设置为 `keyring` 用于持久化时 fail closed；`auto` 在 legacy 模式允许退回 plaintext。参考：[模型](https://github.com/Wh1isper/mcp-email-server/blob/d364b64d2e89bd3686edb82624e1feb9a5562e1b/mcp_email_server/config.py#L261)、[配置说明](https://github.com/Wh1isper/mcp-email-server/blob/d364b64d2e89bd3686edb82624e1feb9a5562e1b/docs/configuration.md#global-settings)。

可以用官方 SDK `mcp.client.stdio.stdio_client(StdioServerParameters(...))` 建立子进程，再用 `ClientSession.initialize/list_tools/call_tool`。需要原样保留结构化结果与 embedded resources，以及 unknown/reconciliation_needed 状态；不能把包装器返回正常等同邮件送达。

### 适配注意点

1. Legacy keyring namespace 并不随 config 路径隔离：service 固定 `mcp-email-server`，entry key 为 `account_name:incoming` / `account_name:outgoing`。项目账号需要唯一前缀，或者采用上游 managed 模式；不能覆盖用户既有上游账号凭证。[源码](https://github.com/Wh1isper/mcp-email-server/blob/d364b64d2e89bd3686edb82624e1feb9a5562e1b/mcp_email_server/keyring_store.py#L13)
2. stdout 是 MCP JSON-RPC，包装器日志只发 stderr。上游有 2 MiB 输入帧、8 MiB 结果等限额，应保留原错误而非无界重试。
3. IMAP 供应商差异仍需真实账号验收；has_attachment 查询依据 MIME header 的启发式，不是完整附件索引。
4. 发送状态中的 succeeded 表示服务器接受，不是收件人已收信；Sent 副本失败后不得重新发送整封邮件。
5. 凭证管理留在用户操作的 CLI/UI；原 MCP 无账号/凭证写工具。不要给 Agent 注入密码收集工具。
6. 不应声称仅加入 provider preset 就覆盖 Outlook 的 OAuth 要求。首版应清楚标注 password/app-password IMAP/SMTP，OAuth 后续采用专门后端。

## 本机验证

核查 clone：`<audit-dir>/wh1isper`。本机 `uv 0.10.7`、`CPython 3.13.12`，使用独立 `.venv`。

先执行 `uv sync --frozen --group dev`，因额外文档/lint 工具下载慢而主动停止（退出 130）；随后 `uv sync --frozen --no-dev` 成功。测试包用 `uv pip install --python .venv/bin/python pytest==8.4.2 pytest-asyncio==1.2.0` 加入，版本与 `uv.lock` 一致。运行依赖保持上游锁文件，包含 `mcp==1.29.1`。

实际定向测试：

```sh
.venv/bin/python -m pytest -q \
  tests/test_stdio_protocol.py \
  tests/test_mcp_tools.py \
  tests/test_mutation_provider_outcomes.py \
  tests/test_scoped_expunge_regression.py \
  tests/test_save_to_sent.py \
  tests/test_rfc_interoperability.py \
  tests/test_imap_starttls.py \
  tests/test_keyring_store.py \
  tests/test_agent_integrations.py
```

结果：**357 passed in 5.03s**，退出 0。上游测试使用合成配置、mock IMAP/SMTP、内存/fail keyring；没有访问真实邮箱或凭证。包含原始 stdio 握手/取消/EOF/非法输入恢复、MCP catalog、SMTP 部分接受/不确定状态、Sent 副本、限定 UID expunge、RFC 与 STARTTLS、钥匙串行为及上游插件契约。没有运行完整测试矩阵、Docker GreenMail E2E、Windows 或真实桌面客户端测试。

另用官方 SDK 启动实际子进程并握手，文件为 clone 内 `audit_fixtures/client_smoke.py`。使用独立 `empty.toml`，先清除继承的 `MCP_EMAIL_SERVER_*` 环境变量再设置路径，以免环境注入真实账号。命令：

```sh
.venv/bin/python audit_fixtures/client_smoke.py
```

实测返回：

```json
{
  "protocol": "2025-11-25",
  "server": {"name": "email", "version": "0.0.1"},
  "tool_count": 18,
  "accounts": {"content": [], "structuredContent": {"result": []}, "isError": false}
}
```

18 个工具包括发送、转发、草稿、列表/搜索、正文、附件、文件夹、标记及归档；不存在旧版 `add_email_account`。日志走 stderr，协议正常结束。证明官方 SDK 能以独立配置复用 stdio 工具面；不证明邮箱网络可达或桌面产品配置已完成。

PyPI 元数据另核对到正式包 1.9.1，wheel SHA-256：`a5de6115dc5de34ed008089068924f89e36d0dce545115788e30f00f06919b7f`；本次运行的是 tag 同 commit 的源码安装，尚未验证 wheel 字节与源码构建一致。

## 结论

首版优先复用它作为 IMAP/SMTP MCP 后端。All Email in Chat 的差异应体现在账号接入、服务商说明、客户端配置导出、诊断、操作授权和可验证兼容矩阵。上游已经覆盖大量邮件边界条件，复制四家的协议实现会扩大维护面，无法自动提高兼容性。
