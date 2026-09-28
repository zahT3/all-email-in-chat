# codefuturist/email-mcp 审查

核查日期：2026-09-28。目标：为 all-email-in-chat 提取可验证的设计经验，不把上游的功能列表直接当作兼容性承诺。本次未读取真实邮箱、凭证或用户客户端配置，未发送真实邮件，未运行安装器，未提交或推送。

## 版本与证据边界

| 项目 | 本次证据 |
| --- | --- |
| 仓库 | https://github.com/codefuturist/email-mcp |
| 默认 main | `99ce431aa81dd4cafc2879bd35b6ee3acd0f2d74`，2026-05-20，package 0.2.3 |
| 最新 GitHub release | [v0.5.1](https://github.com/codefuturist/email-mcp/releases/tag/v0.5.1)，API 返回发布时间 2026-09-26 16:29:55 UTC |
| 本次主要审查版本 | v0.5.1，`198c047c0bea1838a3d4c7dbef8860893f1e338d`，2026-09-26 |
| 许可证 | [package.json](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/package.json) 声明 `LGPL-3.0-or-later`；仓库附 LGPL LICENSE |
| 本地 clone | `<audit-dir>/codefuturist-email-mcp-v0.5.1`；旧 main 保留在相邻 `codefuturist-email-mcp` |
| 技术栈 | TypeScript，Node >=24，ImapFlow，Nodemailer，MCP TypeScript SDK，TOML，SQLite |

**版本陷阱：默认分支并非最新发布。** 默认 README、主分支源码、发布版本必须分开比较。本表以下以固定的 v0.5.1 commit 为准。

证据分级：**实跑**指本次命令成功；**源码**指固定 commit 的实现；**文档**指上游声明；**未验证**指没有接入服务商/客户端完成验证。

## 能力核对

| 能力 | 结论 | 依据 |
| --- | --- | --- |
| 多账号、IMAP/SMTP 分别配置 | 源码支持账号数组和不同收发服务器；连接按账号复用 | [loader](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/config/loader.ts)、[manager](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/connections/manager.ts) |
| 读取、搜索、分页、文件夹 | 源码支持 mailbox 参数、服务端搜索、文件夹 CRUD、标记、移动、批量操作 | [imap.service](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/services/imap.service.ts) |
| 邮件线程 | 使用 Message-ID / References / In-Reply-To 搜索，单 mailbox，最多 50 封；不能称跨全部文件夹完整会话 | [getThread](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/services/imap.service.ts#L1458-L1475) |
| 发送、回复、转发 | 源码支持纯文本/HTML、To/Cc/Bcc；reply 添加线程头；没有 sendEmail 附件参数 | [smtp.service](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/services/smtp.service.ts#L23-L114) |
| 附件 | 源码支持读取/下载，默认 5 MiB 元数据阈值；下载后返回 base64；不等于支持带附件发信 | [downloadAttachment](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/services/imap.service.ts#L1306-L1377) |
| 标签 | 源码区分 Gmail labels、Proton Bridge 标签文件夹、标准 IMAP keywords | [label-strategy](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/services/label-strategy.ts) |
| 缓存 | SQLite 邮件镜像/FTS，使用 `(account, mailbox, uid, uid_validity)`，64 位计数文本保存 | [cache schema](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/cache/schema.ts#L1-L58) |
| 凭证 | 环境变量或 TOML 中直接存密码、OAuth client secret/refresh token；没有看到系统 keyring 适配 | [schema](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/config/schema.ts#L32-L60)、[保存](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/config/loader.ts#L367-L422) |
| OAuth | Google/Microsoft/custom token endpoint；XOAUTH2 与内存 access token 缓存；上游明确标为 experimental；本次未验证授权/刷新 | [OAuthService](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/services/oauth.service.ts#L20-L103) |
| MCP | 源码支持 stdio + Streamable HTTP；HTTP 默认 loopback，非 loopback 默认要求 bearer token，带 Host 校验 | [HTTP](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/cli/http.ts#L119-L185) |
| CLI 与桌面安装 | CLI 主要用于设置、账号、服务、调度管理；安装器覆盖 Claude Desktop、Cursor、Windsurf；本次未运行安装器 | [install-commands](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/cli/install-commands.ts#L47-L100) |
| Agent 特定能力 | 文档声明采样式 AI triage；不支持 sampling 的客户端会降级。MCP transport 支持不能推出 ChatGPT/Kimi 桌面即插即用 | [hooks](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/services/hooks.service.ts) |

## 实际验证

环境：macOS，Node `v24.14.0`，npm `11.9.0`，pnpm `11.19.0`。安装范围为 clone 的 `node_modules`；无全局安装。显式安装命令使用 `--ignore-scripts`，但后续一次 pnpm 包装调用发生了下述例外。

| 命令 / checkout | 结果 | 能证明什么 |
| --- | --- | --- |
| `npm ci --ignore-scripts --no-audit --no-fund` / main | 成功，647 packages | 旧 main 锁文件能在当前环境安装 |
| `npm run typecheck && npm test` / main | typecheck 成功，15 文件 / 150 测试通过 | 旧 main 的离线单测；不能替代发布版测试 |
| `npm ci --ignore-scripts --no-audit --no-fund` / v0.5.1 | 失败 `EUSAGE`，缺 package-lock | 发布版使用 pnpm 锁文件；改按其锁文件安装 |
| `pnpm install --frozen-lockfile --ignore-scripts` / v0.5.1 | 成功，336 packages；registry 短暂重试后完成 | 发布版 pnpm 锁文件可用 |
| `npm run typecheck && npm test && npm run build` / v0.5.1 | 全部成功，38 文件 / 427 测试通过，构建完成 | 类型、源码单元测试、构建通过；集成目录被默认测试配置排除 |

发布版报告：`<audit-dir>/codefuturist-email-mcp-v0.5.1/reports/test-results.json` 与同目录 `test-results.xml`。`pnpm typecheck` 包装进程意外触发了重复 lockfile 检查和安装，且该次调用没有继承 `--ignore-scripts`，因此执行了 clone 内依赖 postinstall 与本仓库 lefthook prepare（只安装到该审计 clone 的 Git hooks）。可选 cpu-features/ssh2 原生绑定构建出现失败；测试/构建并不依赖它们。发现后已终止该审计产生的 pnpm 进程，改用 npm run 调用已安装的脚本；最终成功结果取自上表 npm 命令。不能声称整个过程均禁用了 lifecycle scripts。

未执行 Docker/testcontainers 集成测试、真实 IMAP/SMTP、真实 OAuth、客户端自动安装或远程部署。测试中的 SQLite experimental warning 和模拟断连日志均来自测试，不代表真实邮箱异常。

## 应吸收的设计与应修复的缺口

| 优先级 | 源码发现 / 影响 | 对我们项目的处理 |
| --- | --- | --- |
| 高 | `read_only` 只用于不注册一部分工具；后台启动仍调用 `schedulerService.checkAndSend()`，Hooks 接收的是 hooks 配置而非全局 readOnly。已有待发调度或写入规则时，不能把这个设置视为可靠的全系统只读边界。属于源码证据，本次没有构造发信重现 | 权限检查放到共享操作入口，CLI/MCP/定时器都走同一检查；默认不启动历史调度。定位：[工具注册](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/tools/register.ts#L59-L101)、[后台](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/app.ts#L183-L229)、[规则写入](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/services/hooks.service.ts#L256-L288) |
| 高 | 密码/token 直接序列化 TOML，保存及 `.bak` 未指定 0600，最终权限依赖环境 umask | 从第一版独立 SecretStore；账号文件只留 secret 引用，备份同样不能混入凭证；避免照抄保存逻辑 |
| 中 | reply 固定发给 `original.from.address`，未遵循 Reply-To；reply-all 仅精确比较主邮箱，无别名集合和大小写归一 | 统一收件人解析，优先 Reply-To，去重并排除所有本账户别名；参照 samihalawa 的测试思路 |
| 中 | SMTP 返回统一 `status: sent`，没有暴露 accepted/rejected；源码未见发送后补 Sent 副本或防重键 | 结果区分服务器接受、部分拒收、传输结果不明和 Sent 副本状态；避免 Agent 自动重发 |
| 中 | 附件上限只先比较服务器元数据；下载循环没有独立累计字节中止 | 流式实际字节上限、文件名处理、按需下载；不能把 base64 大附件直接塞满 Agent 上下文 |
| 中 | 定时任务文件先读再写状态，注释“sequential”只保证单次调用顺序，不提供跨 MCP 进程原子锁 | 多桌面客户端共用邮箱时需要单实例工作进程或数据库原子领取与幂等记录。定位：[scheduler](https://github.com/codefuturist/email-mcp/blob/198c047c0bea1838a3d4c7dbef8860893f1e338d/src/services/scheduler.service.ts#L174-L230) |

最值得学习的是服务层与 MCP 层分离、按服务商选择标签策略、UIDVALIDITY 缓存边界、独立配置验证和本地/HTTP 两种 transport。最新版本额外包含剪贴板验证码、日历、提醒等较宽的系统权限面；它们不属于我们的首版邮件连接目标，不整包引入。

复用结论：**作为固定版本的架构与行为参考；首版不复制或嵌入整套 LGPL 实现。** 如果后续需要直接分发其代码，应单独保留来源及许可并检查分发方式。本次只新增研究文档，没有把上游源码复制到 all-email-in-chat。
