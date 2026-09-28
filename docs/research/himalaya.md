# Pimalaya/Himalaya 审查

核查日期：2026-09-28（Asia/Shanghai）。执行的是独立源码构建、单元测试与合成空配置 CLI 检查；没有读取现有账号、钥匙串或真实邮件。

## 快照与许可证

- 仓库：[pimalaya/himalaya](https://github.com/pimalaya/himalaya)。
- 核查 master commit：`2220706b6e7bb75a21baff1a657f78b9a4f2e645`，2026-09-27。
- 最新正式 release：[v2.1.0](https://github.com/pimalaya/himalaya/releases/tag/v2.1.0)，发布时间 `2026-08-16T20:04:10Z`，tag commit `ca88bee08ad2e92127b46dc6200d1e8201885156`。
- **master 与 release 不同**。源码 Cargo.toml 和编译二进制仍显示 v2.1.0，必须同时记录 commit；此报告对 master 的判断不能全部归给已发布 v2.1.0。
- 许可证：[MIT](https://github.com/pimalaya/himalaya/blob/2220706b6e7bb75a21baff1a657f78b9a4f2e645/LICENSE-MIT) 或 [Apache-2.0](https://github.com/pimalaya/himalaya/blob/2220706b6e7bb75a21baff1a657f78b9a4f2e645/LICENSE-APACHE)，项目采用双许可证任选其一。分发或复制时保留适用版权/许可证及所需 notices。

## 架构与能力

Himalaya 是 Rust CLI，源代码明确只有 binary target，不是可直接导入的邮件 library。它通过 io-imap/io-smtp/io-jmap/io-gmail/io-msgraph 等底层库形成共享邮件 API，再保留各协议的专有命令。参考：[架构头](https://github.com/pimalaya/himalaya/blob/2220706b6e7bb75a21baff1a657f78b9a4f2e645/src/main.rs#L1)、[Cargo features](https://github.com/pimalaya/himalaya/blob/2220706b6e7bb75a21baff1a657f78b9a4f2e645/Cargo.toml#L15)。

| 能力 | 源码/文档核查 | 本次实跑范围 |
|---|---|---|
| CLI / JSON | `--json`；按命令生成输出 JSON Schema；配置可 `-c` 独立指定 | CLI help/version、account list、对应 schema 通过 |
| MCP | 仓库没有原生 MCP server 主入口；需要自己的 adapter | 未实现桥接 |
| 收取/搜索 | 共享 envelope list/search DSL；message read；默认不标为已读 | 解析器/日期/读信渲染单元测试通过 |
| 发送/回复 | compose/reply/forward、原始 MIME send；回复自动建立 References/In-Reply-To | MIME builder 单元测试通过；未发信 |
| 会话线程 | IMAP thread 原生命令、Gmail threads API；共享 envelope 有 Message-ID/父链 | 源码确认，远端未测试 |
| 附件 | list/download/compose attach；文件名净化 | 路径净化单元测试通过，远端未测试 |
| 文件夹/标记 | 共享 mailbox、flag、message copy/move/delete；协议原生命令更丰富 | 源码确认，远端未测试 |
| 多账号 | TOML `accounts.<name>`；默认账号及 `-a`；邮箱别名 | 配置与空账号输出通过 |
| 凭证 | raw 或外部 command 提供 password/token；示例调用密码工具、ortie | 未执行真实 secret command |
| OAuth | IMAP/SMTP oauthbearer/xoauth2；Gmail/Graph token；刷新交给外部 helper | 仅源码/文档，未连接 OAuth |
| 协议 | master 默认 features 含 IMAP、SMTP、Sieve、JMAP、Gmail、Graph、Maildir | 本次仅编译 IMAP+SMTP+rustls-ring |

关键定位：

- [CLI 命令与独立配置](https://github.com/pimalaya/himalaya/blob/2220706b6e7bb75a21baff1a657f78b9a4f2e645/src/cli.rs#L60)
- [JSON Schema 注册表](https://github.com/pimalaya/himalaya/blob/2220706b6e7bb75a21baff1a657f78b9a4f2e645/src/json_schema.rs#L1)
- [读信默认不标记 seen](https://github.com/pimalaya/himalaya/blob/2220706b6e7bb75a21baff1a657f78b9a4f2e645/src/shared/message/read.rs#L37)
- [回复头与引用生成](https://github.com/pimalaya/himalaya/blob/2220706b6e7bb75a21baff1a657f78b9a4f2e645/src/shared/message/reply.rs#L23)
- [OAuth/多协议配置样例](https://github.com/pimalaya/himalaya/blob/2220706b6e7bb75a21baff1a657f78b9a4f2e645/config.sample.toml)

## 本机实际验证

位置：`<audit-dir>/himalaya`。macOS arm64；Cargo `1.98.1 (797e8a9bc 2026-08-05)`；rustc `1.98.1 (48a229cea 2026-09-01)`。工具已存在于 `~/.cargo/bin`，只给本次命令设置 PATH，没有安装全局工具。首次测试下载锁文件依赖；测试本身不连接邮箱。

```sh
PATH="$HOME/.cargo/bin:$PATH" cargo test --locked --no-default-features --features imap,smtp,rustls-ring --bin himalaya
```

结果：`96 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out`。覆盖配置、搜索 DSL、邮件标记、MIME 回复构造、日期解析、附件文件名处理、向导 secret 空值等。没有执行全 feature、native Windows 或真实服务商验收。

```sh
PATH="$HOME/.cargo/bin:$PATH" cargo build --offline --locked --no-default-features --features imap,smtp,rustls-ring --bin himalaya
target/debug/himalaya --version
target/debug/himalaya --help
target/debug/himalaya message read --help
target/debug/himalaya json-schema --help
```

结果：构建退出 0（7.88s）；有一条上游 dead_code 警告，涉及未使用 `is_draft/is_junk/is_important`。版本输出：

```text
himalaya v2.1.0 +rustls-ring +smtp +imap
build: macos  aarch64
git: heads/master, rev 2220706b6e7bb75a21baff1a657f78b9a4f2e645
```

合成空配置仅含 `[accounts]`：

```text
himalaya -c <audit-fixtures/empty.toml> --json account list
stdout: {"accounts":[]}
stderr: <empty>
exit: 0
```

最初的审查脚本错误地假设输出是裸数组，断言失败；核对输出 schema 后改为对象 `{"accounts": []}`，复验通过。这是审查端假设错误，不是上游 bug。`himalaya json-schema himalaya-account-list` 返回合法对象 schema，`required=["accounts"]`；两条 CLI 契约断言均通过。

## 可复用点与风险

1. 学习并采用它的共享接口与 provider-specific 扩展分层；不要为了“通用”丢掉 Gmail 标签、Graph 目录、JMAP 线程等真实语义。接口可以统一，能力不可凭空统一。
2. 作为后续可选 CLI 后端时，使用锁定 commit/版本、固定参数数组、独立配置和 `--json`，依据输出 schema 适配；不要解析人类终端表格。
3. `password.command` / `token.command` 是代码执行能力，配置来源应为用户控制的可信接入流程；不能让邮件内容或模型生成的任意字符串写入此字段。
4. [message handler](https://github.com/pimalaya/himalaya/blob/2220706b6e7bb75a21baff1a657f78b9a4f2e645/src/shared/message/handler.rs#L42) 在同时 `--save` 和发送时 **先保存再发送**。如果发送失败，会存在已保存副本；包装器必须把两个阶段分开记录。成功行也不能证明收件人送达。
5. 每次进程默认建立新的 TCP/TLS/认证会话（上游建议用 sirup 复用），Agent 高频小调用可能增加延迟。先测实际任务，再决定是否增加常驻服务。
6. 最新 master 的配置、命令和 release 存在时间差，发布版本号不足以辨识行为。doctor 应报告完整版本与 feature 集，而非仅检查命令存在。

## 结论

Himalaya 是强的多协议底层参考与候选第二后端，尤其适合后续 OAuth/Gmail/Graph/JMAP 扩展。首版不必同时维护两个邮件行为面：先复用 Wh1isper 的 MCP 工具和结果语义，再根据具体账号需求引入 Himalaya adapter。当前 96 项离线单元测试通过证明本机源码可编译、核心本地逻辑通过，不证明任何邮箱服务商或桌面 Agent 已兼容。
