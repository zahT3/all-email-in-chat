# 本地接入向导

安装后运行：

```sh
email-in-chat ui
```

也可以使用 `email-in-chat --config /absolute/path/accounts.toml ui` 指定独立配置；加 `--no-open` 只在终端显示启动链接。

1. **添加邮箱**：选择阿里企业邮箱、阿里个人邮箱、PrivateEmail，或填写自定义 IMAP/SMTP 服务器。密码在本机页面填写，由 Python 服务写入操作系统钥匙串。新配置默认只读。
2. **测试连接**：实际调用受只读权限限制的 `list_mailboxes`，验证 IMAP 登录和目录返回。不读正文、不修改已读状态、不发送测试邮件；SMTP 仍标为未测试。
3. **接入 Agent**：选择客户端，先看配置片段和目标路径，再明确点击写入。只合并本项目条目，保留其他配置并创建备份。遇到不同的同名条目会拒绝覆盖。最后在客户端新会话中确认工具加载。

已有账号可以选中后测试，点击“编辑邮箱与服务器”修正地址、端口及发件信息，或展开“更新客户端专用密码”重试凭证保存。如果系统钥匙串写入失败，账号资料会保留，页面会明确显示未完成；不要重复创建同名账号。

## 离线体验

首次打开时可以点击“使用模拟邮箱”。向导在当前配置旁创建独立的 `demo-<random>/accounts.toml`，使用虚构邮件后端；Agent 配置写入该演示目录的 `demo-clients/`，不会修改真实客户端设置。演示文件会保留以便检查。重新运行不带演示路径的 `email-in-chat ui` 即可接入真实邮箱。

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
