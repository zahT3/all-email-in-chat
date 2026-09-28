import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronDown,
  Circle,
  Copy,
  ExternalLink,
  LockKeyhole,
  Mail,
  Monitor,
  ShieldCheck,
} from "lucide-react";
import "./style.css";
type Account = {
  name: string;
  email: string;
  provider: string;
  full_name?: string;
  imap_host?: string;
  smtp_host?: string;
  imap_port?: number;
  smtp_port?: number;
};
type Profile = { client: string; source_url: string };
type State = {
  initialized: boolean;
  demo: boolean;
  mode: string;
  accounts: Account[];
  providers: Record<string, { imap?: string; smtp?: string }>;
  clients: Profile[];
  csrf: string;
};
type Preview = {
  content: string;
  target_path: string;
  preview_token: string;
  status: string;
  backup_path?: string;
};
type Result = { demo: boolean; folder_count: number };
const names: Record<string, string> = {
  "claude-code": "Claude Code",
  "claude-desktop": "Claude Desktop",
  "claude-desktop-windows": "Claude Desktop",
  cursor: "Cursor",
  "kimi-code": "Kimi Code Desktop",
  "chatgpt-desktop": "ChatGPT 桌面端",
  codex: "Codex",
};
const providers: Record<string, string> = {
  "aliyun-enterprise": "阿里企业邮箱",
  privateemail: "PrivateEmail",
  "aliyun-personal": "阿里个人邮箱",
  custom: "其他 IMAP 邮箱",
};
const steps = ["添加邮箱", "测试连接", "接入 Agent"];
let csrf = "";
async function api<T>(action: string, body?: unknown): Promise<T> {
  const response = await fetch(`api/${action}`, {
    method: body === undefined ? "GET" : "POST",
    credentials: "same-origin",
    cache: "no-store",
    headers: { "Content-Type": "application/json", "X-EIC-CSRF": csrf },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const value = await response.json();
  if (!response.ok) throw new Error(value.error || "操作未完成，请重试。");
  return value;
}
function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
      {hint && <small>{hint}</small>}
    </label>
  );
}
function App() {
  const [state, setState] = useState<State>();
  const [step, setStep] = useState(0);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [fatal, setFatal] = useState(false);
  const [account, setAccount] = useState("");
  const [provider, setProvider] = useState("aliyun-enterprise");
  const [receiveOnly, setReceiveOnly] = useState(false);
  const [check, setCheck] = useState<Result>();
  const [client, setClient] = useState("claude-code");
  const [preview, setPreview] = useState<Preview>();
  const [installed, setInstalled] = useState<Preview>();
  const [copied, setCopied] = useState(false);
  const [editing, setEditing] = useState<Account>();
  const heading = useRef<HTMLHeadingElement>(null);
  const errorRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const token = new URLSearchParams(location.hash.slice(1)).get("token");
    history.replaceState(null, "", location.pathname);
    (async () => {
      if (token) {
        const s = await api<{ csrf: string }>("session", { token });
        csrf = s.csrf;
      }
      const s = await api<State>("state");
      csrf = s.csrf;
      setState(s);
      setAccount(s.accounts[0]?.name || "");
    })().catch((e) => {
      setError(e.message);
      setFatal(true);
    });
  }, []);
  useEffect(() => {
    if (state) heading.current?.focus();
  }, [step, installed]);
  useEffect(() => {
    if (error) errorRef.current?.focus();
  }, [error]);
  async function run(label: string, task: () => Promise<void>) {
    setBusy(label);
    setError("");
    try {
      await task();
    } catch (e) {
      setError(e instanceof Error ? e.message : "操作未完成，请重试。");
    } finally {
      setBusy("");
    }
  }
  function choose(name: string) {
    setEditing(undefined);
    setAccount(name);
    setCheck(undefined);
    setPreview(undefined);
    setInstalled(undefined);
    setError("");
  }
  async function save(event: FormEvent<HTMLFormElement>, existing = false) {
    event.preventDefault();
    const form = event.currentTarget;
    const f = new FormData(form);
    const password = String(f.get("password") || "");
    const smtp = String(f.get("smtp_password") || "");
    const body = existing
      ? { name: account, password, ...(smtp ? { smtp_password: smtp } : {}) }
      : {
          name: String(f.get("name")),
          email: String(f.get("email")),
          provider,
          full_name: String(f.get("full_name") || ""),
          password,
          imap_host: String(
            f.get("imap_host") || state?.providers[provider]?.imap || "",
          ),
          smtp_host: receiveOnly
            ? undefined
            : String(
                f.get("smtp_host") || state?.providers[provider]?.smtp || "",
              ),
          imap_port: Number(f.get("imap_port") || 993),
          smtp_port: Number(f.get("smtp_port") || 465),
          receive_only: receiveOnly,
          ...(smtp ? { smtp_password: smtp } : {}),
        };
    await run("正在保存到本机…", async () => {
      const r = await api<{
        state: State;
        credential_saved: boolean;
        error?: string;
      }>(
        existing ? "credentials" : editing ? "account-update" : "account",
        body,
      );
      setState(r.state);
      setAccount(body.name);
      setEditing(undefined);
      setPreview(undefined);
      setInstalled(undefined);
      setCheck(undefined);
      form
        .querySelectorAll<HTMLInputElement>("input[type=password]")
        .forEach((i) => {
          i.value = "";
        });
      if (!r.credential_saved) throw new Error(r.error);
      setStep(1);
    });
  }
  const selected = state?.accounts.find((a) => a.name === account);
  const prompt = `列出 ${account} 邮箱最近 5 封邮件的主题，先不要修改任何邮件。`;
  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href={location.pathname}>
          <Mail size={23} strokeWidth={1.7} />
          <span>All Email in Chat</span>
        </a>
        <span className="local-label">
          <LockKeyhole size={14} />
          本地接入向导
        </span>
      </header>
      <div className="workspace">
        <aside className="sidebar">
          <p className="sidebar-title">把邮箱带进对话</p>
          <p className="sidebar-copy">
            连接一次，在你熟悉的
            <br />
            Agent 中管理邮件。
          </p>
          <nav aria-label="设置进度">
            <ol className="steps">
              {steps.map((text, i) => (
                <li
                  key={text}
                  className={
                    step === i
                      ? "current"
                      : step > i || installed
                        ? "complete"
                        : ""
                  }
                  aria-current={step === i ? "step" : undefined}
                >
                  <span className="step-number">
                    {step > i || installed ? <Check size={15} /> : i + 1}
                  </span>
                  <span>{text}</span>
                </li>
              ))}
            </ol>
          </nav>
          <div className="sidebar-note">
            <ShieldCheck size={20} />
            <p>
              密码保存在系统钥匙串。
              <br />
              Agent 配置里不含密码。
            </p>
          </div>
        </aside>
        <main className="main">
          {state?.demo && (
            <div className="demo-banner">
              <span className="demo-dot" />
              离线演示 · 虚构邮件 · 配置写入独立测试目录
            </div>
          )}
          <div className="content">
            {error && (
              <div
                className="notice error"
                role="alert"
                tabIndex={-1}
                ref={errorRef}
              >
                {error}
              </div>
            )}
            {!state ? (
              fatal ? (
                <div className="empty">
                  <h1>重新打开接入向导</h1>
                  <p>
                    在本机终端运行 <code>email-in-chat ui</code>
                    ，使用新生成的链接。启动链接只能使用一次，会话持续 30 分钟。
                  </p>
                </div>
              ) : (
                <div className="loading" role="status">
                  正在打开本地设置…
                </div>
              )
            ) : (
              <>
                <div className="page-heading">
                  <h1 ref={heading} tabIndex={-1}>
                    {installed
                      ? state.demo
                        ? "演示配置已完成"
                        : "配置已写入，去 Agent 里试试"
                      : steps[step]}
                  </h1>
                  <p>
                    {installed
                      ? state.demo
                        ? "演示已完成；真实接入后再到客户端检查。"
                        : "最后一步：打开对应客户端，确认邮件工具已加载。"
                      : step === 0
                        ? "选择服务商，使用邮箱的客户端专用密码连接。"
                        : step === 1
                          ? "验证收信连接后，再把邮箱交给你的 Agent。"
                          : "选择你使用的客户端，预览后写入连接配置。"}
                  </p>
                </div>
                {state.mode !== "read" && (
                  <div className="notice">
                    当前权限：{state.mode}
                    。向导保留已有权限设置；全部已配置邮箱会共用此模式。
                  </div>
                )}
                {step === 0 && (
                  <>
                    {state.accounts.length > 0 && !editing && (
                      <section className="existing">
                        <Field label="已配置的邮箱">
                          <select
                            value={account}
                            disabled={!!busy}
                            onChange={(e) => choose(e.target.value)}
                          >
                            {state.accounts.map((a) => (
                              <option value={a.name} key={a.name}>
                                {a.name} · {a.email}
                              </option>
                            ))}
                            {!state.demo && (
                              <option value="">添加另一个邮箱…</option>
                            )}
                          </select>
                        </Field>
                        {selected && (
                          <>
                            <div className="actions">
                              <button
                                disabled={!!busy}
                                onClick={() => setStep(1)}
                              >
                                测试这个邮箱
                                <ArrowRight size={16} />
                              </button>
                            </div>
                            {!state.demo && (
                              <button
                                className="text-button"
                                disabled={!!busy}
                                onClick={() => {
                                  setEditing(selected);
                                  setProvider(selected.provider);
                                  setReceiveOnly(!selected.smtp_host);
                                  setCheck(undefined);
                                  setPreview(undefined);
                                }}
                              >
                                编辑邮箱与服务器
                              </button>
                            )}
                            {!state.demo && (
                              <details>
                                <summary>
                                  更新客户端专用密码
                                  <ChevronDown size={15} />
                                </summary>
                                <form onSubmit={(e) => save(e, true)}>
                                  <fieldset disabled={!!busy}>
                                    <Field label="新的客户端专用密码">
                                      <input
                                        name="password"
                                        type="password"
                                        required
                                        autoComplete="new-password"
                                        maxLength={4096}
                                      />
                                    </Field>
                                    <Field label="独立 SMTP 密码（可选）">
                                      <input
                                        name="smtp_password"
                                        type="password"
                                        autoComplete="new-password"
                                        maxLength={4096}
                                      />
                                    </Field>
                                    <button type="submit" className="secondary">
                                      保存密码并继续
                                    </button>
                                  </fieldset>
                                </form>
                              </details>
                            )}
                          </>
                        )}
                      </section>
                    )}
                    {(!selected || editing) && !state.demo && (
                      <form
                        key={editing?.name || "new"}
                        onSubmit={(e) => save(e)}
                      >
                        {editing && (
                          <p className="notice">
                            正在编辑 {editing.name}
                            。保存后需要重新测试连接；请再次输入客户端专用密码。
                            <button
                              type="button"
                              className="text-button"
                              disabled={!!busy}
                              onClick={() => setEditing(undefined)}
                            >
                              取消编辑
                            </button>
                          </p>
                        )}
                        <fieldset disabled={!!busy}>
                          <Field label="邮箱服务商">
                            <select
                              value={provider}
                              onChange={(e) => setProvider(e.target.value)}
                            >
                              {Object.entries(providers).map(([key, label]) => (
                                <option key={key} value={key}>
                                  {label}
                                </option>
                              ))}
                            </select>
                          </Field>
                          {provider === "aliyun-enterprise" && (
                            <p className="field-note">
                              请先在阿里邮箱开启 IMAP /
                              SMTP；如已启用安全密码，请填写客户端专用密码。
                              <a
                                href="https://help.aliyun.com/zh/document_detail/606337.html"
                                target="_blank"
                                rel="noreferrer"
                              >
                                设置说明
                                <ExternalLink size={12} />
                              </a>
                            </p>
                          )}
                          {provider === "custom" && (
                            <p className="field-note">
                              适用于允许 IMAP 密码认证的邮箱。当前不提供 OAuth
                              授权。
                            </p>
                          )}
                          <div className="field-grid">
                            <Field label="邮箱地址">
                              <input
                                name="email"
                                defaultValue={editing?.email || ""}
                                type="email"
                                required
                                autoComplete="username"
                                placeholder="you@company.com"
                                maxLength={254}
                              />
                            </Field>
                            <Field
                              label="账号简称"
                              hint="Agent 通过这个名称区分邮箱。"
                            >
                              <input
                                name="name"
                                required
                                pattern={"[a-z][a-z0-9\\-]{0,39}"}
                                defaultValue={editing?.name || "work"}
                                readOnly={Boolean(editing)}
                                maxLength={40}
                                title="以小写字母开头，可包含小写字母、数字和连字符"
                              />
                            </Field>
                          </div>
                          <Field
                            label="客户端专用密码"
                            hint="仅提交到本机服务并存入系统钥匙串。请勿粘贴到 Agent 对话中。"
                          >
                            <input
                              name="password"
                              type="password"
                              required
                              autoComplete="new-password"
                              placeholder="输入邮箱密码或客户端专用密码"
                              maxLength={4096}
                            />
                          </Field>
                          <details
                            key={provider}
                            open={provider === "custom" || undefined}
                          >
                            <summary>
                              服务器与发件设置
                              <ChevronDown size={16} />
                            </summary>
                            <div className="advanced">
                              <div className="field-grid server">
                                <Field label="IMAP 服务器">
                                  <input
                                    name="imap_host"
                                    defaultValue={
                                      (editing?.provider === provider
                                        ? editing.imap_host
                                        : undefined) ||
                                      state.providers[provider]?.imap ||
                                      ""
                                    }
                                    required={provider === "custom"}
                                    placeholder="imap.example.com"
                                    maxLength={253}
                                  />
                                </Field>
                                <Field label="端口（TLS）">
                                  <input
                                    name="imap_port"
                                    type="number"
                                    defaultValue={editing?.imap_port || 993}
                                    min={1}
                                    max={65535}
                                    required
                                  />
                                </Field>
                              </div>
                              <label className="checkbox">
                                <input
                                  type="checkbox"
                                  checked={receiveOnly}
                                  onChange={(e) =>
                                    setReceiveOnly(e.target.checked)
                                  }
                                />
                                只配置收信服务器
                              </label>
                              {!receiveOnly && (
                                <>
                                  <div className="field-grid server">
                                    <Field label="SMTP 服务器">
                                      <input
                                        name="smtp_host"
                                        defaultValue={
                                          (editing?.provider === provider
                                            ? editing.smtp_host
                                            : undefined) ||
                                          state.providers[provider]?.smtp ||
                                          ""
                                        }
                                        required={provider === "custom"}
                                        placeholder="smtp.example.com"
                                        maxLength={253}
                                      />
                                    </Field>
                                    <Field label="端口">
                                      <input
                                        name="smtp_port"
                                        type="number"
                                        defaultValue={editing?.smtp_port || 465}
                                        min={1}
                                        max={65535}
                                        required
                                      />
                                    </Field>
                                  </div>
                                  <Field label="发件人名称（可选）">
                                    <input
                                      name="full_name"
                                      defaultValue={editing?.full_name || ""}
                                      maxLength={100}
                                      autoComplete="name"
                                    />
                                  </Field>
                                  <Field
                                    label="独立 SMTP 密码（可选）"
                                    hint="留空时与收信密码相同。465 使用 TLS，587 使用 STARTTLS；阿里企业邮箱请用 465。"
                                  >
                                    <input
                                      name="smtp_password"
                                      type="password"
                                      autoComplete="new-password"
                                      maxLength={4096}
                                    />
                                  </Field>
                                </>
                              )}
                            </div>
                          </details>
                          <p className="permission-note">
                            <ShieldCheck size={16} />
                            新配置默认只读。填写发件服务器不会自动开启发信权限。
                          </p>
                          <div className="actions">
                            <button type="submit">
                              保存邮箱，继续
                              <ArrowRight size={16} />
                            </button>
                          </div>
                        </fieldset>
                      </form>
                    )}
                    {!state.initialized && (
                      <div className="demo-entry">
                        <span>先体验，不连接真实邮箱</span>
                        <button
                          className="text-button"
                          disabled={!!busy}
                          onClick={() =>
                            run("准备模拟邮箱…", async () => {
                              const s = await api<State>("init", {
                                demo: true,
                              });
                              setState(s);
                              setAccount(s.accounts[0].name);
                              setStep(1);
                            })
                          }
                        >
                          使用模拟邮箱
                          <ArrowRight size={15} />
                        </button>
                      </div>
                    )}
                  </>
                )}
                {step === 1 && (
                  <>
                    <div className="account-summary">
                      <Mail size={24} />
                      <div>
                        <strong>{selected?.email}</strong>
                        <p>
                          {account} ·{" "}
                          {state.demo
                            ? "模拟邮箱"
                            : providers[selected?.provider || ""] ||
                              "IMAP 邮箱"}
                        </p>
                      </div>
                      <button
                        className="text-button"
                        onClick={() => setStep(0)}
                        disabled={!!busy}
                      >
                        更换 / 编辑
                      </button>
                    </div>
                    <ul className="checks">
                      <li>
                        <CheckCircle2 size={19} />
                        账号配置已保存
                      </li>
                      <li>
                        {check ? (
                          <CheckCircle2 size={19} />
                        ) : (
                          <Circle size={19} />
                        )}
                        <span>
                          {check
                            ? `${check.demo ? "模拟连接通过" : "IMAP 登录成功"} · 已确认 ${check.folder_count} 个目录`
                            : "等待测试 IMAP 登录与目录读取"}
                        </span>
                      </li>
                      <li className="muted">
                        <Circle size={19} />
                        SMTP 发信未测试；不会发送测试邮件
                      </li>
                    </ul>
                    <div className="notice">
                      {state.demo
                        ? "此步骤会连接项目内置的模拟后端，不访问真实邮箱。"
                        : "测试只登录邮箱并列出目录，不读取邮件正文，也不修改已读状态。"}
                    </div>
                    <div className="actions">
                      <button
                        disabled={!!busy}
                        className={check ? "secondary" : ""}
                        onClick={() =>
                          run("正在测试收信连接，最多约 35 秒…", async () => {
                            setCheck(undefined);
                            setCheck(
                              await api<Result>("check", { name: account }),
                            );
                          })
                        }
                      >
                        {check ? "重新测试" : "测试收信连接"}
                      </button>
                      {check && (
                        <button disabled={!!busy} onClick={() => setStep(2)}>
                          选择 Agent
                          <ArrowRight size={16} />
                        </button>
                      )}
                    </div>
                    <button
                      className="text-button back"
                      disabled={!!busy}
                      onClick={() => setStep(0)}
                    >
                      <ArrowLeft size={14} />
                      返回邮箱设置
                    </button>
                  </>
                )}
                {step === 2 && !installed && (
                  <>
                    <fieldset disabled={!!busy}>
                      <legend className="sr-only">选择桌面 Agent</legend>
                      <div className="client-grid">
                        {state.clients.map((p) => (
                          <label
                            className={`client-option ${client === p.client ? "selected" : ""}`}
                            key={p.client}
                          >
                            <input
                              type="radio"
                              name="client"
                              value={p.client}
                              checked={client === p.client}
                              onChange={() => {
                                setClient(p.client);
                                setPreview(undefined);
                                setError("");
                              }}
                            />
                            <Monitor size={18} />
                            <span>{names[p.client]}</span>
                          </label>
                        ))}
                      </div>
                    </fieldset>
                    <p className="field-note">
                      按官方配置方式生成。实际可用性仍需在你的客户端中确认。
                      <a
                        href={
                          state.clients.find((p) => p.client === client)
                            ?.source_url
                        }
                        target="_blank"
                        rel="noreferrer"
                      >
                        官方说明
                        <ExternalLink size={12} />
                      </a>
                    </p>
                    <p className="field-note">
                      本次接入共享配置中的全部 {state.accounts.length} 个邮箱。
                    </p>
                    <div className="actions">
                      <button
                        className={preview ? "secondary" : ""}
                        disabled={!!busy}
                        onClick={() =>
                          run("正在检查配置…", async () =>
                            setPreview(
                              await api<Preview>("preview", { client }),
                            ),
                          )
                        }
                      >
                        预览连接配置
                      </button>
                    </div>
                    {preview && (
                      <section className="preview">
                        <h2>
                          {state.demo ? "将写入演示目录" : "将添加到客户端配置"}
                        </h2>
                        <p className="path">{preview.target_path}</p>
                        <pre>
                          <code>{preview.content}</code>
                        </pre>
                        <p className="field-note">
                          只合并 email-in-chat
                          条目；保留其他设置，修改前创建备份。不同的同名条目会拒绝覆盖。
                        </p>
                        <button
                          disabled={!!busy}
                          onClick={() =>
                            run("正在写入配置…", async () =>
                              setInstalled(
                                await api<Preview>("install", {
                                  client,
                                  preview_token: preview.preview_token,
                                }),
                              ),
                            )
                          }
                        >
                          {state.demo ? "写入演示配置" : "确认写入配置"}
                          <ArrowRight size={16} />
                        </button>
                      </section>
                    )}
                    <button
                      className="text-button back"
                      disabled={!!busy}
                      onClick={() => setStep(1)}
                    >
                      <ArrowLeft size={14} />
                      返回连接测试
                    </button>
                  </>
                )}
                {installed && (
                  <>
                    <div className="success-line">
                      <CheckCircle2 size={26} />
                      <div>
                        <strong>
                          {names[client]} ·{" "}
                          {state.demo
                            ? "演示文件已保存"
                            : installed.status === "unchanged"
                              ? "配置已存在，无需修改"
                              : "配置已保存"}
                        </strong>
                        <p className="path">{installed.target_path}</p>
                      </div>
                    </div>
                    {state.demo && (
                      <div className="notice">
                        没有修改真实 Agent 的设置。连接真实邮箱时，重新运行{" "}
                        <code>email-in-chat ui</code>
                        ，完成接入后再写入客户端配置。
                      </div>
                    )}
                    <ol className="next-steps">
                      <li>重启 {names[client]}，或创建一个新会话。</li>
                      <li>
                        在 MCP 设置中确认 <code>email-in-chat</code>{" "}
                        已启用、工具已加载。
                      </li>
                      <li>从一次只读查询开始，确认邮箱和返回结果。</li>
                    </ol>
                    {state.demo && (
                      <p className="field-note">
                        上面的客户端检查适用于真实接入；本次演示未执行。
                      </p>
                    )}
                    <div className="prompt">
                      <p>可以这样开始对话</p>
                      <blockquote>{prompt}</blockquote>
                      <button
                        className="secondary"
                        onClick={() =>
                          run("正在复制…", async () => {
                            await navigator.clipboard.writeText(prompt);
                            setCopied(true);
                          })
                        }
                      >
                        {copied ? <Check size={15} /> : <Copy size={15} />}{" "}
                        {copied ? "已复制" : "复制这句话"}
                      </button>
                    </div>
                    {installed.backup_path && (
                      <p className="field-note">
                        原配置备份：
                        <span className="path">{installed.backup_path}</span>
                      </p>
                    )}
                    <div className="actions">
                      <button
                        className="secondary"
                        onClick={() => {
                          setInstalled(undefined);
                          setPreview(undefined);
                        }}
                      >
                        接入另一个 Agent
                      </button>
                      <button
                        className="text-button"
                        onClick={() => {
                          setStep(0);
                          setInstalled(undefined);
                          setPreview(undefined);
                        }}
                      >
                        返回邮箱设置
                      </button>
                    </div>
                  </>
                )}
                {busy && (
                  <p className="busy" role="status">
                    {busy}
                  </p>
                )}
              </>
            )}
          </div>
          <footer>
            <span>
              <LockKeyhole size={13} />
              仅在本机运行
            </span>
            <span>设置完成后，可关闭终端中的向导。</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
