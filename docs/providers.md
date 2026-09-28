# 邮箱服务商 / Email providers

向导先用邮箱域名精确匹配本机预设；不会把邮箱地址发送给第三方发现服务，不查询 MX，也不会根据相似域名猜测服务器。自有域名的企业邮箱需要选择实际服务商；其余邮箱可以手动填写 IMAP / SMTP 设置。

The wizard matches exact domains against bundled presets locally. It does not query MX records or send your address to a discovery service. For a custom business domain, choose the provider that hosts your mail. Other accounts can use manual IMAP / SMTP settings.

**服务器预设已核对，真实账号尚未逐家验收。 / Settings checked; live accounts have not been tested for each provider.**

| Preset | Incoming (TLS) | Outgoing | Authentication / 认证 | Source |
| --- | --- | --- | --- | --- |
| Alibaba Mail business / 阿里企业邮箱 | imap.qiye.aliyun.com:993 | smtp.qiye.aliyun.com:465 TLS | Admin allows third-party clients; client security password / 管理员允许第三方客户端，客户端安全密码 | [Alibaba](https://help.aliyun.com/zh/document_detail/36576.html) |
| Aliyun Mail / 阿里个人邮箱 | imap.aliyun.com:993 | smtp.aliyun.com:465 TLS | Enable IMAP, client password / 开启 IMAP，客户端密码 | [Alibaba](https://help.aliyun.com/zh/document_detail/465790.html) |
| QQ Mail | imap.qq.com:993 | smtp.qq.com:465 TLS | Enable IMAP, authorization code / 开启 IMAP，授权码 | [Thunderbird ISPDB](https://autoconfig.thunderbird.net/v1.1/qq.com), [QQ help](https://service.mail.qq.com/detail/0/339) |
| NetEase 163 | imap.163.com:993 | smtp.163.com:465 TLS | IMAP authorization code / IMAP 授权码 | [Thunderbird ISPDB](https://autoconfig.thunderbird.net/v1.1/163.com) |
| NetEase 126 | imap.126.com:993 | smtp.126.com:465 TLS | IMAP authorization code / IMAP 授权码 | [Thunderbird ISPDB](https://autoconfig.thunderbird.net/v1.1/126.com) |
| NetEase yeah.net | imap.yeah.net:993 | smtp.yeah.net:465 TLS | IMAP authorization code / IMAP 授权码 | [Thunderbird ISPDB](https://autoconfig.thunderbird.net/v1.1/yeah.net) |
| Gmail | imap.gmail.com:993 | smtp.gmail.com:465 TLS | App password only, 2-Step Verification and account eligibility required / 仅应用专用密码，需要两步验证及账号许可 | [Google](https://support.google.com/accounts/answer/185833), [Thunderbird ISPDB](https://autoconfig.thunderbird.net/v1.1/gmail.com) |
| iCloud Mail | imap.mail.me.com:993 | smtp.mail.me.com:587 STARTTLS | Apple app-specific password; full email address / Apple App 专用密码、完整邮箱地址 | [Apple](https://support.apple.com/en-us/102525) |
| PrivateEmail | mail.privateemail.com:993 | mail.privateemail.com:465 TLS | Provider-approved password / 服务商允许的密码 | [Namecheap](https://www.namecheap.com/support/knowledgebase/article.aspx/1179/2175/general-private-email-configuration-for-mail-clients-and-mobile-devices/) |
| Other / 手动设置 | Custom TLS host and port | Custom host; port 587 uses STARTTLS | Password or app password / 密码或应用专用密码 | Your mail administrator / 邮箱管理员 |

Outlook / Microsoft 365 is shown as **OAuth not yet available**. Recognizing `outlook.com` does not mean its authentication is implemented. The wizard does not ask for a password for that selection. [Microsoft’s authentication requirements](https://support.microsoft.com/en-gb/outlook/pop-imap-and-smtp-settings-for-outlook-com).

Outlook / Microsoft 365 显示为 **OAuth 尚未接入**，识别出域名不代表已经支持登录，选择后不会要求填写密码。Google OAuth 和 token 刷新同样尚未实现。Gmail 应用专用密码是有条件的接入路径；组织限制、安全密钥专用配置或高级保护可能使该选项不可用。

Preset selection fills server settings, but never proves login, folder operations or delivery. Providers may impose additional client identification or administrator policy requirements. The wizard's test performs read-only IMAP login and folder listing; it does not test SMTP or send mail.

Last checked: 2026-09-28. Thunderbird ISPDB XML was retrieved for QQ, 163, 126, yeah.net and Gmail; only the server facts above are summarized, no source code or catalog is bundled.
