# 架构与范围

## 一次请求怎样执行

1. 用户在桌面 Agent 中说“搜索今天的客户邮件”。Agent 根据 MCP 工具说明生成结构化调用。
2. 客户端以 stdio 启动 `email-in-chat --config ... serve`。凭证不在这个配置里。
3. `config.py` 校验账号配置，生成带独立 namespace 的后端快照。普通配置和快照只保存 keyring 占位符。
4. `bridge.py` 启动锁定版本的 Wh1isper 子进程，发现工具；按当前模式过滤列表，并在每次调用入口再次检查权限、账号 alias 和参数 schema。
5. Wh1isper 从 keyring 取出认证信息，使用 IMAP/SMTP + TLS 执行操作，将结果通过 MCP 返回。
6. Agent 根据结果回答用户。模型如何解释邮件、需要确认什么，仍受用户要求及客户端行为影响。

`demo.py` 可以替代真实后端，完全在内存中提供虚构邮件。所有返回都有模拟标记，方便体验与自动化测试。

## 代码分工

| 文件 | 责任 |
| --- | --- |
| `src/email_in_chat/cli.py` | 安装后入口、诊断、搜索/读信/草稿/发送、客户端操作 |
| `src/email_in_chat/config.py` | 账号、服务商预设、keyring 写入、权限和后端快照 |
| `src/email_in_chat/bridge.py` | MCP 子进程、工具发现与调用、权限检查、账号别名 |
| `src/email_in_chat/clients.py` | 各客户端配置生成、预览、备份与合并 |
| `src/email_in_chat/demo.py` | 无凭证的合成邮件后端 |

读信统一强制 `mark_as_read=false`；标已读是独立写工具。管理模式没有删除工具；草稿模式只允许草稿目录。白名单交给固定版本后端对收件人执行，包括 To/Cc/Bcc。工具描述提醒模型把邮件当作外部数据，这不是对 prompt injection 的完全防护。

## 复用边界

首版只把 Wh1isper 作为运行依赖。Himalaya 是候选第二后端，codefuturist 和 samihalawa 是经过测试的设计参考；没有复制三者源码或把它们一起打包。相同邮件动作在不同产品上的细节需要分别验证，不能靠统一函数名消除 Gmail 标签、IMAP 文件夹和 Graph 目录的差异。

目前公开工具沿用 Wh1isper schema，属于版本锁定的契约。后续新增后端前需要定义能力发现、分页、消息 ID、线程头、错误和发送结果的统一模型，保留 provider-specific 扩展。

## MVP 边界

- 当前是本地 stdio 服务，没有自己的模型、聊天窗口、持续后台任务或远程 HTTP 服务。
- 当前支持 IMAP/SMTP 密码或 app password，没有 OAuth 浏览器授权和刷新。
- 没有持久化发送去重台账；超时可能发生在服务商已接受之后，错误不能直接解释成未发送。
- 后端业务结果可能包含 `unknown` 或 `reconciliation_needed`；CLI `ok` 只表示调用没有协议/工具错误，不等于操作全部成功，更不等于收件人送达。查看结果正文中的业务状态。
- 当前保留结构化结果；错误文本做概括，避免异常把凭证带入 Agent。诊断粒度仍需改善。
- 读取邮件会把请求的正文交给所选 Agent；模型服务的数据处理规则由对应产品决定。
- 一个用户配置下，各桌面客户端共用同一权限模式。不同权限需求应建立不同配置；运行中的实例只在重启后更新。
- 已识别的明文 keyring 后端会被拒绝；Linux 需要可用的桌面 secret service，Windows/其他环境仍待完整验收。

## 后续顺序

1. 使用测试邮箱在阿里企业邮箱、PrivateEmail 完成真实读信、草稿、发送与不确定结果核对。
2. 对 Claude Code、ChatGPT 桌面、Kimi Code Desktop、Cursor 逐一记录实际版本和 UI 验收。
3. 增加逐次授权/操作审计和发送去重设计，再扩展自动处理场景。
4. 基于具体账号需求实现 OAuth 和第二后端，重点评估 Himalaya。
5. 需要浏览器端接入时再实现 Streamable HTTP、服务授权和部署；需要定时运行时再实现持久队列、去重与任务恢复。

MCP 适合统一工具入口，但这些运行能力都需要项目自己或可靠依赖提供。
