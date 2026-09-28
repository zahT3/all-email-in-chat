# 上游验证与复用决定

核查日期：2026-09-28。测试运行在独立审查目录，没有真实邮箱或客户数据。以下结果不能相加成为本项目的测试覆盖率。

| 项目 | 核查版本 | 已执行验证 | 本项目如何使用 |
| --- | --- | --- | --- |
| [Wh1isper/mcp-email-server](wh1isper.md) | 1.9.1；`d364b64d` | 357 项定向测试；真实 stdio 握手、18 工具、空账号列表 | **唯一邮件运行后端**，依赖固定为 1.9.1；学习错误和发送结果语义 |
| [pimalaya/himalaya](himalaya.md) | master `2220706b`；区别于 v2.1.0 tag | 96 项测试、IMAP/SMTP feature 构建、JSON/schema CLI | 多协议/OAuth 的候选后端；当前没有集成运行 |
| [codefuturist/email-mcp](codefuturist.md) | v0.5.1 `198c047`；区别于旧 main | typecheck、build、427 项 mock 测试 | 借鉴接入体验和能力组织；调用入口权限检查是本项目重点 |
| [samihalawa/email-smtp-imap-mcp](samihalawa.md) | v2.2.0 `6b9610d` | build、15 项测试，包含本机合成 SMTP/IMAP | 借鉴精简工具面、回复行为与集成验证方式 |

选择一个运行后端能减少协议行为不一致和重复维护。自己的价值在于一次配置、多 Agent 接入、可执行权限、诊断和可信兼容矩阵。

上游许可证分别为 BSD-3-Clause、MIT/Apache-2.0、LGPL-3.0 和 MIT。这里没有引入后三者源码。后续任何源码复用都需要重新核对对应版本许可证，见[第三方说明](../../THIRD_PARTY_NOTICES.md)。

关键发现：

- 只隐藏写工具不等于禁止直接调用或后台写入；本项目在发现与调用两处检查。
- 版本标签和默认分支不一定一致；Himalaya 与 codefuturist 均须记录实际 commit。
- “保存在 Sent”不证明 SMTP 已接受；SMTP 接受也不证明对方收到。
- 支持 IMAP/SMTP 不等于完成 OAuth 或服务商特殊策略的适配。
- 上游测试通过、本项目协议通过、桌面端通过、真实邮箱通过是四类独立证据。
