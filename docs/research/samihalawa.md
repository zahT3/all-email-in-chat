# samihalawa/email-smtp-imap-mcp 审查

核查日期：2026-09-28。本次只访问公开源码、安装 clone 内依赖并运行其离线测试；未使用真实邮箱、凭证或用户客户端配置，无提交/推送。

## 固定版本

| 项目 | 本次证据 |
| --- | --- |
| 仓库 | https://github.com/samihalawa/email-smtp-imap-mcp |
| HEAD / release | `6b9610d0c74450e938aa0428d08dbdefa02f4b7f`，tag [v2.2.0](https://github.com/samihalawa/email-smtp-imap-mcp/releases/tag/v2.2.0)，2026-08-11 |
| 最新 release 发布时间 | GitHub API：2026-08-11 00:32:57 UTC |
| 许可证 | [MIT](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/LICENSE)，Copyright (c) 2025 Sami Halawa |
| 本地 clone | `<audit-dir>/samihalawa-email-smtp-imap-mcp` |
| 技术栈 | TypeScript，Node >=20，MCP SDK，ImapFlow，Nodemailer，mailparser，dotenv |

## 能力与限制

| 能力 | 实际范围 | 证据层级与定位 |
| --- | --- | --- |
| MCP 接口 | 6 工具：accounts_list、emails_find、emails_modify、email_send、email_respond、folders_list；stdio transport | 源码 + 实跑 tools/list：[index](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/index.ts#L71-L146) |
| 多账号 | `EMAIL_ACCOUNTS_JSON` 对象，或单账号环境变量；支持独立 SMTP/IMAP user/password，默认账号与 sender aliases | 源码 + 实跑：[accountManager](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/accountManager.ts) |
| 凭证 | `.env` / 明确 `EMAIL_ENV_FILE` / 环境变量；没有 keyring 或 OAuth 实现；校验必须有密码 | 源码：[environment](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/environment.ts)、[validateAccount](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/accountManager.ts#L72-L84) |
| 搜索与读取 | subject/body/from/to 多字段搜索，日期、未读、星标、附件过滤；最多 100；搜索与指定 UID 读取都限定 INBOX | 源码 + 本地协议实跑：[search](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/imapService.ts#L84-L211)、[get by UID](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/imapService.ts#L356-L387) |
| 文件夹与归档 | 能列文件夹，能把 INBOX 邮件移到指定文件夹；没有任意源文件夹搜索/修改参数，没有文件夹 CRUD | 源码：[modifyEmails](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/imapService.ts#L218-L279) |
| 发送与附件 | SMTP To/Cc/Bcc，纯文本/HTML，base64 附件，发件别名限制；默认 HTML | 源码 + 本地 SMTP 实跑：[sendEmail](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/smtpService.ts#L84-L143) |
| 回复/转发 | 支持 Reply-To、回复所有人、排除自身别名；发信加 In-Reply-To；References 仅保留直接父邮件 Message-ID | 源码 + recipient 单测和本地回复实跑：[reply recipients](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/smtpService.ts#L51-L78)、[reply](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/smtpService.ts#L149-L200) |
| 会话线程 | 返回可用的 provider threadId；没有通用跨文件夹线程重建工具，不能等同完整会话管理 | 源码：[mapMessage](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/imapService.ts#L396-L438) |
| 草稿/调度/审计权限 | 没有完整草稿工作流、持久授权、防重、规则调度或结构化操作账本 | 在 8 个 src 文件范围内核查；本项目应独立设计 |
| CLI / HTTP / 桌面适配 | npm bin 启动 MCP server；不是逐操作 CLI；未见 HTTP transport 或自动安装器 | 源码：[package.json](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/package.json)、[stdio](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/index.ts#L144-L146) |

## 本次实跑

环境：macOS，Node `v24.14.0`，npm `11.9.0`。

```sh
git clone --depth 1 --branch v2.2.0 https://github.com/samihalawa/email-smtp-imap-mcp.git ./samihalawa-email-smtp-imap-mcp
cd ./samihalawa-email-smtp-imap-mcp
npm ci --ignore-scripts --no-audit --no-fund
npm test
```

安装成功（151 packages）。`npm test` 执行 `npm run build && node --test test/*.test.mjs`；构建成功，**15 个测试全部通过，0 fail、0 skip，测试总时长约 3.75 秒**。

测试覆盖了：多账号解析及非法配置、精确 IMAP UID、stdio tools/list 与 isError、显式 `.env` 文件、完整本地 SMTP/IMAP 工具调用、搜索条件、别名校验、Reply-To 与 reply-all 去重。MCP 集成测试真正启动子进程，通过 SDK 调用工具，并连接测试创建的 `127.0.0.1` SMTP/IMAP 服务；这比只 mock service 更强，但仍不证明阿里/Gmail/PrivateEmail 兼容。

可复现测试源：[mcp.test.mjs](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/test/mcp.test.mjs#L233-L350)。其他本地测试验证了账号/搜索/发件人/UID 单元行为。测试后 `git status --short` 无 tracked diff。

未验证：真实服务商连接、真实 TLS 证书与 STARTTLS、OAuth（无实现）、任何桌面客户端、远程传输、附件大小极限和异常重试。

## 风险与学习点

| 优先级 | 发现与影响 | 我们的实现要求 |
| --- | --- | --- |
| 高 | 工具发信即时执行，无持久授权或审批状态；任意兼容 Agent 接上即可调用已配置账号。支持 MCP 本身不等于安全自动管理 | 操作层处理权限与发送状态，工具只暴露最小必要参数；只读模式要贯穿所有入口 |
| 高 | 附件是完整 base64 进出；`validateAttachments` 只验证类型，无实际大小上限；读取用 simpleParser 完整解析原邮件，容易内存及上下文膨胀 | 分离附件元数据/下载，流式限额与本地文件引用；发送前检查实际字节。定位：[validation](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/emailHandlers.ts#L47-L55)、[parse](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/imapService.ts#L404-L413) |
| 中 | INBOX 硬编码使归档后的邮件不能经同一工具查回、继续回复；裸 UID 不带 mailbox/UIDVALIDITY，不能作为跨邮箱稳定标识 | 使用 account + mailbox + UIDVALIDITY + UID，跨文件夹定位独立实现 |
| 中 | SMTP 非隐式 TLS 时没有显式 `requireTLS`；是否安全升级依赖 Nodemailer/服务器行为。错误文案还建议切换 imap_secure 处理 TLS 失败 | 默认要求 TLS 或强制 STARTTLS，证书失败不建议关闭加密。定位：[transport](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/smtpService.ts#L12-L31)、[error](https://github.com/samihalawa/email-smtp-imap-mcp/blob/6b9610d0c74450e938aa0428d08dbdefa02f4b7f/src/imapService.ts#L46-L58) |
| 中 | 发信 `success` 只看 messageId，未返回 accepted/rejected 或 Sent 副本结果；无防重 ID | 返回细分状态并记录稳定请求 ID，遇到结果不明时不盲目重发 |
| 中 | 邮件正文默认优先 HTML，缺少统一净化后的纯文本视图 | 原始邮件与安全展示/模型文本分离，明确其是外部不可信数据 |
| 中 | 每次 IMAP 操作创建连接，timeout 为 Promise.race，未清理 timer 或取消正在进行的 I/O | 统一连接生命周期和取消机制；多客户端/大邮箱压力测试后再扩大并发 |

可学习：6 个紧凑工具让新手容易理解、账号解析相互独立、收发凭证可分离、Reply-To 和自身别名去重、真实本地协议测试。MIT 代码若直接复制，需要保留版权及许可；本次只写研究文档，没有复制实现。

结论：**适合作为精简 MCP 测试样例与行为参考，不适合作为完整邮箱管理产品直接换名发布。** all-email-in-chat 首版应保留清晰工具面，但补足权限、凭证存储、文件夹定位、结果状态和桌面适配层。
