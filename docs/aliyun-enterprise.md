# 阿里企业邮箱接入

本项目已有 `aliyun-enterprise` 预设，使用 IMAP/SMTP 和客户端安全密码。官方连接参数已核对；尚未用真实阿里企业邮箱完成收发验收。

| 用途 | 主机 | 端口 | 加密 |
| --- | --- | --- | --- |
| 收信与邮件管理 | `imap.qiye.aliyun.com` | 993 | TLS |
| 发信 | `smtp.qiye.aliyun.com` | 465 | TLS |

阿里当前未开放 SMTP 587，使用上表即可。[官方参数](https://help.aliyun.com/zh/document_detail/36576.html)（2026-09-28 核对）。

## 先准备账号权限

请管理员确认该账号允许第三方客户端登录，并开启 IMAP/SMTP。新购邮箱可能受默认的第三方客户端访问限制影响；可以为目标账号配置例外。企业如果限制登录 IP，运行 Agent 的网络也需要在允许范围内。[官方访问控制说明](https://help.aliyun.com/zh/document_detail/606337.html)。

然后在网页版邮箱的账户与安全设置中生成第三方客户端安全密码；启用这项功能后，客户端应使用它而不是网页登录密码。[官方操作说明](https://help.aliyun.com/zh/document_detail/444269.html)。

## 添加和只读验证

已安装 `email-in-chat` 后，用独立配置添加阿里账号。将示例地址换成自己的完整邮箱地址：

```sh
email-in-chat --config ~/.config/all-email-in-chat-aliyun/accounts.toml init
email-in-chat --config ~/.config/all-email-in-chat-aliyun/accounts.toml accounts add work \
  --provider aliyun-enterprise --email you@example.com
email-in-chat --config ~/.config/all-email-in-chat-aliyun/accounts.toml accounts auth work
email-in-chat --config ~/.config/all-email-in-chat-aliyun/accounts.toml doctor --smoke
email-in-chat --config ~/.config/all-email-in-chat-aliyun/accounts.toml messages search --account work --limit 5
```

`accounts auth` 由用户在私人终端隐藏输入安全密码，保存到本机 keyring；不把密码发送给聊天里的 Agent。`doctor --smoke` 仅证明后端初始化与账号发现，最后一步搜索才尝试连接真实邮箱。读取默认不改变未读状态。

搜索成功后，使用相同 `--config` 执行 `clients install cursor` 或其他 profile，预览后加 `--apply` 应用。其他 Agent 的命令见[客户端说明](clients.md)。

默认模式不能发信。需要草稿或发送时，按 [README 的权限说明](../README.md#操作权限)设置对应模式与精确收件人，再重启 MCP 服务。

如果认证失败，依次核对完整邮箱地址、客户端安全密码、第三方登录权限、IMAP/SMTP 权限与企业 IP 限制。不要通过关闭 TLS 证书校验来解决登录问题。
