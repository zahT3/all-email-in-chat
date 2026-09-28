# 本地接入向导

安装后运行：

```sh
email-in-chat ui
```

也可以使用 `email-in-chat --config /absolute/path/accounts.toml ui` 指定独立配置；加 `--no-open` 只在终端显示启动链接。

右上角可随时切换中文 / English。初始语言跟随浏览器，选择保存在浏览器本地；切换时保留正在填写的表单。

1. **邮箱**：输入地址，仅在本机精确匹配服务商预设。企业邮箱自有域名需手动选择服务商，未知域名进入手动设置。
2. **连接**：查看所选服务商的认证说明，填写授权码或客户端专用密码；服务器、端口和账号简称放在高级设置中。保存到系统钥匙串后立即测试 IMAP 登录和目录返回，不读正文、不标记已读、不发信。SMTP 未测试。
3. **Agent**：选择客户端，先预览目标路径及配置，再点击写入。保留其他配置并备份原文件，遇到同名冲突停止。重启客户端，在新对话中确认工具已加载。

已有邮箱在首页列表中，可直接测试或修改设置和密码。钥匙串保存失败会保留账号资料并显示恢复说明；再次提交会更新原账号，不会重复创建。错误提示也随语言切换。

可配置的 9 个服务商预设、手动设置及 OAuth 限制详见[服务商说明](providers.md)。端点预设不代表真实账号已经验收。

## 开发者：模拟邮箱

普通向导不再展示模拟入口。模拟后端供自动化测试、贡献者学习和无凭证回归检查使用，保留虚构邮件和隔离的客户端写入路径。显式开启：

```sh
email-in-chat --config ~/.config/all-email-in-chat-demo/accounts.toml init --demo
email-in-chat --config ~/.config/all-email-in-chat-demo/accounts.toml ui
```

页面始终标注开发测试模式；客户端配置只写该配置旁的 `demo-clients/`，不会修改真实 Agent 设置。测试通过不能替代真实邮箱或桌面客户端验收。

## 设计参考

采用 [Thunderbird 的账号匹配及手动回退流程](https://support.mozilla.org/en-US/kb/automatic-account-configuration) 与 [Apple Internet Accounts 的邮箱优先入口](https://support.apple.com/en-sg/guide/mac-help/mh43559/mac)。本项目只实现本机域名预设匹配，不提供 Thunderbird 的完整自动发现能力。

## English quick start

Run `email-in-chat ui`, then choose **English** in the header. Enter your email, confirm the matched provider (or use manual setup), enter an app password, and save and test. After the IMAP check succeeds, select an agent, preview its configuration and apply it. Restart the agent and confirm that the tools load. Advanced server settings are optional for known providers. The developer demo is opt-in via a separate `init --demo` configuration as shown above.

## 本机边界

- 仅绑定 `127.0.0.1` 的随机端口，无公网监听选项；它不是远程 MCP 服务。
- 随机路径及一次性启动令牌。令牌通过 URL fragment 交给页面，随即移除；换取 HttpOnly、SameSite=Strict 会话 cookie。会话从服务启动起有效 30 分钟。
- 写请求验证 Origin 和 CSRF token，所有请求校验 Host、外部 Origin 和跨站来源；无 CORS 放行。页面禁止 iframe 嵌入，响应禁止缓存；关闭 HTTP 访问日志。
- 密码不返回浏览器、不进入 Agent 配置、MCP 参数或普通 TOML。页面不加载外部脚本、字体或统计代码。
- 使用系统钥匙串前仍要求安全后端可用；本机已被攻陷、恶意浏览器扩展和同用户恶意进程不在此服务的隔离保证内。
- Ctrl+C 停止向导。关闭网页不会停止终端中的进程；过期后 API 会拒绝继续操作。

## 开发与打包

前端为 React + TypeScript + Vite；Python 使用 Starlette/Uvicorn 服务已编译资源。安装用户不需要 Node。静态产物提交到 `src/email_in_chat/static/`，以支持直接从 GitHub 安装；修改前端后必须重建。

```sh
cd frontend
npm ci
npm run build
npm run format:check
cd ..
uv run email-in-chat --config /absolute/private/test/accounts.toml ui
uv run pytest tests/test_ui.py -q
uv build
python3 scripts/check_publication.py
```

Vite 的开发命令仅提供前端资源；完整鉴权和 API 验收需要使用 Python 向导。CI 重新构建前端并确认提交的静态资源与源码一致，然后运行测试和打包检查。

编辑邮箱时保留账号简称和凭证 namespace，并要求再次输入密码、重新测试；已有 Agent 需要重启才读取更新后的配置。此版本没有收件箱页面、OAuth 登录、权限编辑页或账号删除。Kimi 配置针对 Kimi Code Desktop。
