export type Locale = "zh" | "en";
const messages = {
  title: ["邮箱接入", "Email setup"],
  language: ["界面语言", "Language"],
  local: ["本机设置", "Local setup"],
  steps: ["设置进度", "Setup progress"],
  emailStep: ["邮箱", "Email"],
  connectStep: ["连接", "Connect"],
  agentStep: ["Agent", "Agent"],
  startTitle: ["连接你的邮箱", "Connect your email"],
  startHint: [
    "在你常用的 AI Agent 中搜索、阅读和处理邮件。",
    "Search, read and manage email in the AI agent you already use.",
  ],
  email: ["邮箱地址", "Email address"],
  emailHint: [
    "先匹配服务器设置，下一步再填写密码。",
    "We’ll match server settings first. You’ll enter your password next.",
  ],
  continue: ["继续", "Continue"],
  back: ["返回", "Back"],
  savedAccounts: ["已添加的邮箱", "Your accounts"],
  useAccount: ["使用此邮箱", "Use this account"],
  providers: ["支持哪些邮箱？", "Which providers can I connect?"],
  providerIntro: [
    "内置以下服务器预设，也可以手动填写其他 IMAP / SMTP 邮箱。能否登录取决于账号权限和认证方式。",
    "Use a preset below, or enter the servers for another IMAP / SMTP account. Sign-in depends on your account permissions and authentication method.",
  ],
  presetNote: [
    "预设已核对；真实账号兼容性仍待验证。",
    "Preset settings checked; live account compatibility still needs testing.",
  ],
  oauthPending: ["OAuth 尚未接入", "OAuth not yet available"],
  manual: ["手动设置", "Manual setup"],
  settingsTitle: ["连接邮箱", "Connect your account"],
  settingsHint: [
    "核对服务商，在本机保存授权信息并测试收信连接。",
    "Confirm your provider, save credentials locally and test the incoming connection.",
  ],
  matched: ["已识别邮箱服务商", "Email provider recognized"],
  unmatched: [
    "这个域名没有内置预设。请选择服务商，或手动填写服务器。",
    "No preset for this domain. Choose your provider or enter server settings manually.",
  ],
  provider: ["邮箱服务商", "Email provider"],
  providerHint: [
    "企业邮箱的自有域名需要手动选择服务商。",
    "For a custom business domain, choose the service that hosts your email.",
  ],
  auth_app_password: [
    "请先开启 IMAP，并使用客户端专用密码或授权码。",
    "Enable IMAP and use an app password or authorization code.",
  ],
  auth_authorization_code: [
    "在邮箱设置中开启 IMAP / SMTP，生成授权码后填入下方。",
    "Enable IMAP / SMTP in your mail settings, then generate an authorization code and enter it below.",
  ],
  auth_enterprise: [
    "需要管理员允许第三方客户端，并在邮箱中开启 IMAP。请使用客户端安全密码。",
    "Your admin must allow third-party clients and IMAP. Use your mailbox’s client security password.",
  ],
  auth_google_app_password: [
    "当前仅支持应用专用密码：需要开启两步验证，且账号允许生成应用专用密码。Google 一键授权尚未接入。",
    "App passwords only: enable 2-Step Verification and check that your account allows app passwords. Sign in with Google is not implemented yet.",
  ],
  auth_apple_app_password: [
    "请在 Apple 账户中生成 App 专用密码。使用完整邮箱地址登录。",
    "Generate an app-specific password in your Apple Account. Sign in with your full email address.",
  ],
  auth_password: [
    "请使用服务商允许的邮箱密码或应用专用密码。",
    "Use the mailbox password or app password allowed by your provider.",
  ],
  auth_custom: [
    "需要支持 IMAP over TLS 和密码认证。向邮箱管理员获取服务器设置；仅支持 OAuth 的账号暂不可用。",
    "Requires IMAP over TLS and password authentication. Ask your mail admin for server settings. OAuth-only accounts are not supported yet.",
  ],
  auth_oauth_required: [
    "此服务商需要 OAuth 授权。当前版本尚未实现，请暂时使用其他邮箱；无需在这里输入密码。",
    "This provider requires OAuth, which is not implemented yet. Use another email account for now; no password is needed here.",
  ],
  providerHelp: ["查看设置说明", "View setup instructions"],
  password: ["授权码或客户端专用密码", "App password or authorization code"],
  passwordHint: [
    "保存在本机系统钥匙串，不写入 Agent 配置。",
    "Saved in your OS keyring, never in your agent configuration.",
  ],
  showPassword: ["显示密码", "Show password"],
  hidePassword: ["隐藏密码", "Hide password"],
  advanced: ["服务器和更多设置", "Servers and advanced settings"],
  alias: ["账号简称", "Account alias"],
  aliasHint: [
    "Agent 用这个名称区分邮箱；小写字母、数字或连字符。",
    "Your agent uses this name to identify the account. Use lowercase letters, numbers or hyphens.",
  ],
  fullName: ["发件人名称（选填）", "Sender name (optional)"],
  imapHost: ["收信服务器", "Incoming server"],
  smtpHost: ["发信服务器", "Outgoing server"],
  port: ["端口", "Port"],
  tls: [
    "IMAP 使用 TLS；SMTP 587 使用 STARTTLS，其他端口使用 TLS。",
    "IMAP uses TLS. SMTP uses STARTTLS on port 587 and TLS on other ports.",
  ],
  receiveOnly: ["只配置收信服务器", "Configure incoming mail only"],
  smtpPassword: [
    "发信密码（仅与收信密码不同时填写）",
    "SMTP password (only if different)",
  ],
  saveTest: ["保存并测试连接", "Save and test connection"],
  saving: ["正在保存…", "Saving…"],
  testing: ["正在测试收信连接…", "Testing incoming connection…"],
  test: ["测试连接", "Test connection"],
  retry: ["重新测试", "Test again"],
  edit: ["修改设置或密码", "Edit settings or password"],
  policy_read: ["只读", "Read only"],
  policy_draft: ["允许草稿", "Drafts allowed"],
  policy_manage: ["允许管理", "Management allowed"],
  policyHint: [
    "当前权限：{mode}。已有权限保持不变；新配置默认只读。",
    "Current permission: {mode}. Existing policy is preserved; new configurations are read only.",
  ],
  savedHint: [
    "邮箱资料已保存。测试通过后继续连接 Agent。",
    "Account settings saved. Test the connection to continue to your agent.",
  ],
  connected: ["收信连接成功", "Incoming connection successful"],
  folders: [
    "已登录 IMAP 并获取 {count} 个邮件目录。",
    "Signed in to IMAP and listed {count} mail folders.",
  ],
  checkScope: [
    "仅检查登录和目录，不读取正文、不标记已读、不发送邮件。SMTP 尚未测试。",
    "Checks sign-in and folders only. No messages are read, marked or sent. SMTP is not tested.",
  ],
  nextAgent: ["连接 Agent", "Connect an agent"],
  agentTitle: ["选择你的 Agent", "Choose your agent"],
  agentHint: [
    "将邮件工具添加到你常用的桌面客户端。",
    "Add your email tools to the desktop app you use.",
  ],
  clientScope: [
    "此连接使用当前配置中的全部邮箱，遵循当前操作权限。",
    "This connection uses all accounts in this configuration and follows your current permissions.",
  ],
  preview: ["预览配置", "Preview configuration"],
  previewing: ["正在生成预览…", "Preparing preview…"],
  destination: ["配置写入位置", "Configuration destination"],
  configDetails: ["查看配置内容", "View configuration"],
  apply: ["写入配置", "Apply configuration"],
  applying: ["正在写入…", "Applying…"],
  applyHint: [
    "保留其他设置并备份原文件；遇到同名冲突会停止。",
    "Preserves other settings and backs up the original file. Stops on conflicting entries.",
  ],
  clientDocs: ["客户端接入说明", "Client setup instructions"],
  clientEvidence: [
    "配置方式已按官方文档核对；需要在客户端内确认工具实际加载。",
    "Configuration follows the client’s documentation. Confirm that the tools load inside your app.",
  ],
  doneTitle: ["配置已写入", "Configuration applied"],
  doneHint: [
    "重启 {client}，在新对话中确认 email-in-chat 工具已加载。",
    "Restart {client} and confirm the email-in-chat tools are available in a new conversation.",
  ],
  tryPrompt: ["在 Agent 中试试", "Try this in your agent"],
  prompt: [
    "列出 {account} 邮箱最近 5 封邮件的主题，先不要修改任何邮件。",
    "List the subjects of the 5 most recent emails in {account}. Do not modify any messages.",
  ],
  copy: ["复制指令", "Copy prompt"],
  copied: ["已复制", "Copied"],
  anotherAgent: ["连接其他 Agent", "Connect another agent"],
  anotherAccount: ["添加其他邮箱", "Add another email"],
  backup: ["备份位置", "Backup location"],
  closeHint: [
    "完成后可关闭此页，并在终端按 Ctrl+C 停止向导。",
    "When finished, close this page and press Ctrl+C in the terminal to stop the wizard.",
  ],
  footer: [
    "凭证留在本机 · 新配置默认只读",
    "Credentials stay on this device · Read only by default",
  ],
  loading: ["正在打开设置…", "Opening setup…"],
  errorTitle: ["暂时无法继续", "Couldn’t continue"],
  demo: [
    "开发测试模式：使用虚构邮箱，配置只写入测试目录。",
    "Developer test mode: fictional mailboxes; configuration is written to a test directory only.",
  ],
  demoConnected: ["模拟连接检查完成", "Demo connection check complete"],
  demoDone: ["测试配置已写入", "Test configuration applied"],
  demoDoneHint: [
    "仅验证了模拟流程，未连接真实邮箱或修改真实 Agent 设置。",
    "Only the demo flow was tested. No real mailbox was connected and no real agent settings were changed.",
  ],
  demoPrompt: ["模拟指令示例", "Example demo prompt"],
} satisfies Record<string, readonly [string, string]>;
export function copy(locale: Locale) {
  return Object.fromEntries(
    Object.entries(messages).map(([key, value]) => [
      key,
      value[locale === "zh" ? 0 : 1],
    ]),
  ) as Record<keyof typeof messages, string>;
}
export const errors = {
  operation_failed: [
    "操作未完成，请重试。",
    "Couldn’t complete the action. Please try again.",
  ],
  network_error: [
    "无法连接本机服务。请检查终端是否仍在运行向导。",
    "Can’t reach the local service. Check that the wizard is still running in your terminal.",
  ],
  session_expired: [
    "会话已过期，请重新运行 email-in-chat ui。",
    "Session expired. Run email-in-chat ui again.",
  ],
  invalid_session: [
    "启动链接已使用或无效，请重新运行 email-in-chat ui。",
    "Launch link is invalid or already used. Run email-in-chat ui again.",
  ],
  session_required: [
    "请使用终端生成的完整链接打开向导。",
    "Open the full launch link shown in your terminal.",
  ],
  request_rejected: [
    "请求验证失败，请从终端重新打开向导。",
    "Request verification failed. Open a new wizard from your terminal.",
  ],
  not_found: [
    "页面或操作不存在，请重新打开向导。",
    "Page or action not found. Reopen the wizard.",
  ],
  validation_failed: [
    "请检查地址、服务器、端口和账号简称；简称不能与已有邮箱重复。",
    "Check the address, servers, ports and account alias. Use a unique alias for each account.",
  ],
  credential_failed: [
    "邮箱资料已保存，但密码未完整保存。请检查系统钥匙串，重新输入密码并保存。",
    "Account settings were saved, but credentials were not fully saved. Check your OS keyring, then re-enter the password and save again.",
  ],
  system_error: [
    "操作未完成。请检查系统钥匙串或配置文件权限后重试。",
    "Check your OS keyring and configuration file permissions, then try again.",
  ],
  select_account: ["请选择已配置的邮箱。", "Select a configured account."],
  connection_timeout: [
    "连接超时。请检查网络、服务器地址及 IMAP 开关后重试。",
    "Connection timed out. Check your network, server settings and IMAP access, then try again.",
  ],
  connection_failed: [
    "收信连接未通过。请检查授权码、IMAP 权限、服务器地址和网络；可修改设置或密码后重试。",
    "Incoming connection failed. Check your app password, IMAP permissions, servers and network. Edit settings or password, then try again.",
  ],
  invalid_folders: [
    "服务器目录返回无法确认，尚未判定连接成功。请检查设置后重试。",
    "Couldn’t confirm the server’s folder response. Check settings and try again.",
  ],
  stale_preview: [
    "配置预览已失效，请重新预览后再写入。",
    "Preview expired. Preview the configuration again before applying it.",
  ],
  client_failed: [
    "客户端配置操作未完成。请检查同名条目、文件格式和权限，重新预览后再试。",
    "Check existing email-in-chat entries, file format and permissions. Preview again, then retry.",
  ],
  client_conflict: [
    "客户端配置存在冲突、格式无效或使用了符号链接。原设置未覆盖；请检查下方目标文件，处理后重新预览。",
    "The client config has a conflicting entry, invalid format or a symbolic link. Original settings are preserved. Check the destination file below, then preview again.",
  ],
  client_write_failed: [
    "无法写入客户端配置。请检查下方路径的权限及磁盘空间，然后重新预览。",
    "Can’t write client configuration. Check permissions at the destination below and available disk space, then preview again.",
  ],
  clipboard_failed: [
    "无法复制，请手动选中并复制下方指令。",
    "Couldn’t copy. Select and copy the prompt manually.",
  ],
} satisfies Record<string, readonly [string, string]>;
export function errorText(code: string, locale: Locale) {
  return (errors[code as keyof typeof errors] || errors.operation_failed)[
    locale === "zh" ? 0 : 1
  ];
}
export function initialLocale(): Locale {
  try {
    const saved = localStorage.getItem("eic-language");
    if (saved === "zh" || saved === "en") return saved;
  } catch {
    /* Browser storage can be disabled. */
  }
  return navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en";
}
