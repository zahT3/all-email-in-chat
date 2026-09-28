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
  ChevronRight,
  Copy,
  ExternalLink,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  Plus,
  RotateCw,
} from "lucide-react";
import { copy, errorText, initialLocale, type Locale } from "./i18n";
import { matchProvider, suggestAlias, type Provider } from "./model";
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
type State = {
  initialized: boolean;
  demo: boolean;
  mode: string;
  accounts: Account[];
  providers: Record<string, Provider>;
  clients: { client: string; source_url: string }[];
  csrf: string;
};
type Preview = {
  content: string;
  target_path: string;
  preview_token: string;
  backup_path?: string;
};
type Result = { demo: boolean; folder_count: number };
type View = "email" | "settings" | "check" | "agent";
const clientNames: Record<string, string> = {
  "claude-code": "Claude Code",
  "claude-desktop": "Claude Desktop",
  "claude-desktop-windows": "Claude Desktop",
  cursor: "Cursor",
  "kimi-code": "Kimi Code Desktop",
  "chatgpt-desktop": "ChatGPT Desktop",
  codex: "Codex",
};
class ApiError extends Error {
  targetPath?: string;
  constructor(code: string, path?: unknown) {
    super(code);
    if (typeof path === "string") this.targetPath = path;
  }
}
let csrf = "";
async function api<T>(action: string, body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`api/${action}`, {
      method: body === undefined ? "GET" : "POST",
      credentials: "same-origin",
      cache: "no-store",
      headers: { "Content-Type": "application/json", "X-EIC-CSRF": csrf },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
  } catch {
    throw new Error("network_error");
  }
  let value;
  try {
    value = await response.json();
  } catch {
    throw new Error("operation_failed");
  }
  if (!response.ok)
    throw new ApiError(value.code || "operation_failed", value.target_path);
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
  const [locale, setLocale] = useState<Locale>(initialLocale);
  const c = copy(locale);
  const [state, setState] = useState<State>();
  const [view, setView] = useState<View>("email");
  const [email, setEmail] = useState("");
  const [provider, setProvider] = useState("custom");
  const [account, setAccount] = useState("");
  const [editing, setEditing] = useState<Account>();
  const [busy, setBusy] = useState<
    "" | "saving" | "testing" | "previewing" | "applying"
  >("");
  const [error, setError] = useState("");
  const [errorPath, setErrorPath] = useState("");
  const [fatal, setFatal] = useState(false);
  const [advanced, setAdvanced] = useState(false);
  const [receiveOnly, setReceiveOnly] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [check, setCheck] = useState<Result>();
  const [client, setClient] = useState("claude-code");
  const [preview, setPreview] = useState<Preview>();
  const [installed, setInstalled] = useState<Preview>();
  const [copied, setCopied] = useState(false);
  const heading = useRef<HTMLHeadingElement>(null);
  const errorRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const token = new URLSearchParams(location.hash.slice(1)).get("token");
    history.replaceState(null, "", location.pathname);
    (async () => {
      if (token)
        csrf = (await api<{ csrf: string }>("session", { token })).csrf;
      const s = await api<State>("state");
      csrf = s.csrf;
      setState(s);
    })().catch((e) => {
      setError(e.message);
      setFatal(true);
    });
  }, []);
  useEffect(() => {
    document.documentElement.lang = locale === "zh" ? "zh-CN" : "en";
    document.title = `${c.title} · All Email in Chat`;
    try {
      localStorage.setItem("eic-language", locale);
    } catch {
      /* Optional preference only. */
    }
  }, [locale, c.title]);
  useEffect(() => {
    if (state) heading.current?.focus();
  }, [view, installed, Boolean(state)]);
  useEffect(() => {
    if (error) errorRef.current?.focus();
  }, [error]);
  async function run(
    label: Exclude<typeof busy, "">,
    task: () => Promise<void>,
  ) {
    setBusy(label);
    setError("");
    setErrorPath("");
    try {
      await task();
    } catch (e) {
      setError(e instanceof Error ? e.message : "operation_failed");
      setErrorPath(e instanceof ApiError ? e.targetPath || "" : "");
    } finally {
      setBusy("");
    }
  }
  function resetConnection() {
    setCheck(undefined);
    setPreview(undefined);
    setInstalled(undefined);
    setError("");
    setCopied(false);
  }
  function selectAccount(a: Account) {
    resetConnection();
    setAccount(a.name);
    setEditing(undefined);
    setEmail(a.email);
    setView("check");
  }
  function editAccount(a: Account) {
    resetConnection();
    setEditing(a);
    setEmail(a.email);
    setProvider(a.provider);
    setReceiveOnly(a.smtp_host === "");
    setAdvanced(false);
    setShowPassword(false);
    setView("settings");
  }
  function addAnother() {
    resetConnection();
    setEditing(undefined);
    setAccount("");
    setEmail("");
    setView("email");
  }
  function continueEmail(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!state) return;
    resetConnection();
    setEmail(email.trim());
    setEditing(undefined);
    setProvider(matchProvider(email, state.providers));
    setReceiveOnly(false);
    setAdvanced(false);
    setShowPassword(false);
    setView("settings");
  }
  async function test(name: string) {
    setBusy("testing");
    setCheck(undefined);
    setCheck(await api<Result>("check", { name }));
  }
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!state) return;
    const form = event.currentTarget;
    const fields = new FormData(form);
    const smtpPassword = String(fields.get("smtp_password") || "");
    const body = {
      name: String(fields.get("name")),
      email: email.trim(),
      provider,
      full_name: String(fields.get("full_name") || ""),
      password: String(fields.get("password") || ""),
      imap_host: String(fields.get("imap_host") || ""),
      smtp_host: String(fields.get("smtp_host") || ""),
      imap_port: Number(fields.get("imap_port") || 993),
      smtp_port: Number(
        fields.get("smtp_port") || state.providers[provider]?.smtp_port || 465,
      ),
      receive_only: receiveOnly,
      ...(smtpPassword ? { smtp_password: smtpPassword } : {}),
    };
    await run("saving", async () => {
      const r = await api<{
        state: State;
        credential_saved: boolean;
        code?: string;
      }>(editing ? "account-update" : "account", body);
      setState(r.state);
      setAccount(body.name);
      resetConnection();
      setEditing(r.state.accounts.find((a) => a.name === body.name));
      form
        .querySelectorAll<HTMLInputElement>("input[data-secret]")
        .forEach((input) => {
          input.value = "";
        });
      setShowPassword(false);
      if (!r.credential_saved) throw new Error(r.code || "credential_failed");
      setView("check");
      await test(body.name);
    });
  }
  const selected = state?.accounts.find((a) => a.name === account);
  const p = state?.providers[provider];
  const defaults = editing?.provider === provider ? editing : undefined;
  const step = view === "email" ? 0 : view === "agent" ? 2 : 1;
  const mode =
    c[`policy_${state?.mode || "read"}` as keyof typeof c] || c.policy_read;
  const prompt = c.prompt.replace("{account}", account);
  const authHint = p ? c[`auth_${p.auth}` as keyof typeof c] : "";
  const headline = installed
    ? state?.demo
      ? c.demoDone
      : c.doneTitle
    : view === "email"
      ? c.startTitle
      : view === "agent"
        ? c.agentTitle
        : check
          ? state?.demo
            ? c.demoConnected
            : c.connected
          : c.settingsTitle;
  return (
    <div className="app-shell">
      <header className="topbar">
        <span className="brand">
          <Mail size={22} strokeWidth={1.7} aria-hidden="true" />
          All Email in Chat
        </span>
        <div className="languages" role="group" aria-label={c.language}>
          <button
            type="button"
            lang="zh-CN"
            aria-pressed={locale === "zh"}
            onClick={() => setLocale("zh")}
          >
            中文
          </button>
          <button
            type="button"
            lang="en"
            aria-pressed={locale === "en"}
            onClick={() => setLocale("en")}
          >
            English
          </button>
        </div>
      </header>
      <main className="wizard" aria-busy={!!busy}>
        <nav aria-label={c.steps}>
          <ol className="steps">
            {[c.emailStep, c.connectStep, c.agentStep].map((label, i) => (
              <li
                key={i}
                className={step === i ? "current" : i < step ? "complete" : ""}
                aria-current={step === i ? "step" : undefined}
              >
                <span className="step-number">
                  {i < step || installed ? (
                    <Check size={13} aria-hidden="true" />
                  ) : (
                    i + 1
                  )}
                </span>
                <span>{label}</span>
              </li>
            ))}
          </ol>
        </nav>
        {state?.demo && <p className="notice demo-note">{c.demo}</p>}
        <section className="surface">
          {view !== "email" && !installed && !fatal && (
            <button
              className="back"
              disabled={!!busy}
              onClick={() => {
                setError("");
                setView(view === "agent" ? "check" : "email");
              }}
            >
              <ArrowLeft size={16} />
              {c.back}
            </button>
          )}
          <div className="heading">
            <h1 ref={heading} tabIndex={-1}>
              {headline}
            </h1>
            <p>
              {view === "email"
                ? c.startHint
                : view === "settings"
                  ? c.settingsHint
                  : view === "agent" && !installed
                    ? c.agentHint
                    : null}
            </p>
          </div>
          {error && (
            <div className="error" role="alert" tabIndex={-1} ref={errorRef}>
              <strong>{c.errorTitle}</strong>
              <p>{errorText(error, locale)}</p>
              {errorPath && <code className="path">{errorPath}</code>}
            </div>
          )}
          {!state && !fatal && <p role="status">{c.loading}</p>}
          {state && !fatal && (
            <>
              {view === "email" && (
                <>
                  {!state.demo && (
                    <form onSubmit={continueEmail}>
                      <Field label={c.email} hint={c.emailHint}>
                        <input
                          name="email"
                          type="email"
                          autoComplete="email"
                          autoCapitalize="none"
                          spellCheck={false}
                          placeholder="you@example.com"
                          required
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                        />
                      </Field>
                      <button className="primary full" type="submit">
                        {c.continue}
                        <ArrowRight size={17} />
                      </button>
                    </form>
                  )}
                  {state.accounts.length > 0 && (
                    <section className="account-list">
                      <h2>{c.savedAccounts}</h2>
                      {state.accounts.map((a) => (
                        <button
                          key={a.name}
                          type="button"
                          onClick={() => selectAccount(a)}
                          aria-label={`${c.useAccount}: ${a.email}`}
                        >
                          <Mail size={19} />
                          <span>
                            <strong>{a.email}</strong>
                            <small>{a.name}</small>
                          </span>
                          <ChevronRight size={18} />
                        </button>
                      ))}
                    </section>
                  )}
                  <details className="support">
                    <summary>{c.providers}</summary>
                    <p>{c.providerIntro}</p>
                    <ul className="provider-list">
                      {Object.entries(state.providers).map(([key, item]) => (
                        <li key={key}>
                          <span>{item.name[locale]}</span>
                          {!item.available && <small>{c.oauthPending}</small>}
                        </li>
                      ))}
                    </ul>
                    <p className="muted">{c.presetNote}</p>
                  </details>
                </>
              )}
              {view === "settings" && p && (
                <>
                  <div className="account-heading">
                    <Mail size={19} aria-hidden="true" />
                    <strong>{email}</strong>
                  </div>
                  <p className="match-note">
                    {matchProvider(email, state.providers) === "custom"
                      ? c.unmatched
                      : c.matched}
                  </p>
                  <Field label={c.provider} hint={c.providerHint}>
                    <select
                      value={provider}
                      disabled={!!busy}
                      onChange={(e) => {
                        setProvider(e.target.value);
                        setAdvanced(false);
                        setError("");
                      }}
                    >
                      {Object.entries(state.providers).map(([key, item]) => (
                        <option key={key} value={key}>
                          {item.name[locale]}
                          {!item.available ? ` — ${c.oauthPending}` : ""}
                        </option>
                      ))}
                    </select>
                  </Field>
                  <div className="auth-help">
                    <p>{authHint}</p>
                    {p.source_url && (
                      <a href={p.source_url} target="_blank" rel="noreferrer">
                        {c.providerHelp}
                        <ExternalLink size={13} />
                      </a>
                    )}
                  </div>
                  {p.available && (
                    <form
                      key={`${provider}-${editing?.name || "new"}`}
                      onSubmit={save}
                      onInvalidCapture={() => setAdvanced(true)}
                    >
                      <fieldset disabled={!!busy}>
                        <Field label={c.password} hint={c.passwordHint}>
                          <span className="password-input">
                            <input
                              name="password"
                              data-secret
                              type={showPassword ? "text" : "password"}
                              autoComplete="new-password"
                              required
                            />
                            <button
                              type="button"
                              className="eye"
                              onClick={() => setShowPassword(!showPassword)}
                              aria-label={
                                showPassword ? c.hidePassword : c.showPassword
                              }
                            >
                              {showPassword ? (
                                <EyeOff size={18} />
                              ) : (
                                <Eye size={18} />
                              )}
                            </button>
                          </span>
                        </Field>
                        <details
                          className="advanced"
                          open={advanced || provider === "custom"}
                          onToggle={(e) => setAdvanced(e.currentTarget.open)}
                        >
                          <summary>{c.advanced}</summary>
                          {editing && (
                            <Field label={c.email}>
                              <input
                                type="email"
                                value={email}
                                required
                                onChange={(e) => setEmail(e.target.value)}
                                autoComplete="email"
                              />
                            </Field>
                          )}
                          <Field label={c.alias} hint={c.aliasHint}>
                            <input
                              name="name"
                              defaultValue={
                                editing?.name ||
                                suggestAlias(
                                  email,
                                  state.accounts.map((a) => a.name),
                                )
                              }
                              readOnly={!!editing}
                              required
                              pattern="[a-z][a-z0-9-]{0,39}"
                              maxLength={40}
                              autoCapitalize="none"
                              spellCheck={false}
                            />
                          </Field>
                          <div className="server-row">
                            <Field label={`${c.imapHost} (IMAP)`}>
                              <input
                                name="imap_host"
                                defaultValue={
                                  defaults?.imap_host || p.imap || ""
                                }
                                required
                                autoCapitalize="none"
                                spellCheck={false}
                              />
                            </Field>
                            <Field label={c.port}>
                              <input
                                name="imap_port"
                                type="number"
                                min="1"
                                max="65535"
                                defaultValue={
                                  defaults?.imap_port || p.imap_port || 993
                                }
                                required
                              />
                            </Field>
                          </div>
                          <label className="checkbox">
                            <input
                              type="checkbox"
                              checked={receiveOnly}
                              onChange={(e) => setReceiveOnly(e.target.checked)}
                            />
                            {c.receiveOnly}
                          </label>
                          {!receiveOnly && (
                            <>
                              <div className="server-row">
                                <Field label={`${c.smtpHost} (SMTP)`}>
                                  <input
                                    name="smtp_host"
                                    defaultValue={
                                      defaults?.smtp_host || p.smtp || ""
                                    }
                                    required
                                    autoCapitalize="none"
                                    spellCheck={false}
                                  />
                                </Field>
                                <Field label={c.port}>
                                  <input
                                    name="smtp_port"
                                    type="number"
                                    min="1"
                                    max="65535"
                                    defaultValue={
                                      defaults?.smtp_port || p.smtp_port || 465
                                    }
                                    required
                                  />
                                </Field>
                              </div>
                              <Field label={c.fullName}>
                                <input
                                  name="full_name"
                                  defaultValue={editing?.full_name || ""}
                                />
                              </Field>
                              <Field label={c.smtpPassword}>
                                <input
                                  name="smtp_password"
                                  data-secret
                                  type="password"
                                  autoComplete="new-password"
                                />
                              </Field>
                            </>
                          )}
                          <p className="muted">{c.tls}</p>
                        </details>
                        <p className="policy">
                          <LockKeyhole size={14} />
                          {c.policyHint.replace("{mode}", mode)}
                        </p>
                        <button className="primary full" type="submit">
                          {busy ? c[busy] : c.saveTest}
                          {!busy && <ArrowRight size={17} />}
                        </button>
                      </fieldset>
                    </form>
                  )}
                </>
              )}
              {view === "check" && selected && (
                <>
                  <div className="account-heading">
                    <Mail size={20} />
                    <span>
                      <strong>{selected.email}</strong>
                      <small>{selected.name}</small>
                    </span>
                  </div>
                  {check ? (
                    <div className="success">
                      <CheckCircle2 size={22} />
                      <p>
                        {c.folders.replace(
                          "{count}",
                          String(check.folder_count),
                        )}
                      </p>
                    </div>
                  ) : (
                    <p>{busy ? c[busy] : c.savedHint}</p>
                  )}
                  <p className="muted check-scope">{c.checkScope}</p>
                  <p className="policy">
                    <LockKeyhole size={14} />
                    {c.policyHint.replace("{mode}", mode)}
                  </p>
                  {check ? (
                    <button
                      className="primary full"
                      disabled={!!busy}
                      onClick={() => {
                        setError("");
                        setView("agent");
                      }}
                    >
                      {c.nextAgent}
                      <ArrowRight size={17} />
                    </button>
                  ) : (
                    <button
                      className="primary full"
                      disabled={!!busy}
                      onClick={() => run("testing", () => test(account))}
                    >
                      {busy ? c[busy] : error ? c.retry : c.test}
                      {!busy && <RotateCw size={16} />}
                    </button>
                  )}
                  {!state.demo && (
                    <button
                      className="text-button full"
                      disabled={!!busy}
                      onClick={() => editAccount(selected)}
                    >
                      {c.edit}
                    </button>
                  )}
                </>
              )}
              {view === "agent" && !installed && (
                <>
                  <fieldset className="client-list" disabled={!!busy}>
                    <legend className="sr-only">{c.agentTitle}</legend>
                    {state.clients.map((item) => (
                      <label key={item.client}>
                        <input
                          type="radio"
                          name="client"
                          value={item.client}
                          checked={client === item.client}
                          onChange={() => {
                            setClient(item.client);
                            setPreview(undefined);
                            setError("");
                          }}
                        />
                        <span>{clientNames[item.client] || item.client}</span>
                      </label>
                    ))}
                  </fieldset>
                  <p className="muted">{c.clientScope}</p>
                  <button
                    className={preview ? "secondary full" : "primary full"}
                    disabled={!!busy}
                    onClick={() =>
                      run("previewing", async () => {
                        setPreview(await api<Preview>("preview", { client }));
                      })
                    }
                  >
                    {busy === "previewing" ? c.previewing : c.preview}
                  </button>
                  {preview && (
                    <section className="config-preview">
                      <h2>{c.destination}</h2>
                      <code className="path">{preview.target_path}</code>
                      <details>
                        <summary>{c.configDetails}</summary>
                        <pre>{preview.content}</pre>
                      </details>
                      <p className="muted">{c.applyHint}</p>
                      <button
                        className="primary full"
                        disabled={!!busy}
                        onClick={() =>
                          run("applying", async () => {
                            setInstalled(
                              await api<Preview>("install", {
                                client,
                                preview_token: preview.preview_token,
                              }),
                            );
                          })
                        }
                      >
                        {busy === "applying" ? c.applying : c.apply}
                        <Check size={17} />
                      </button>
                    </section>
                  )}
                  <p className="muted client-evidence">{c.clientEvidence}</p>
                  <a
                    href={
                      state.clients.find((item) => item.client === client)
                        ?.source_url
                    }
                    target="_blank"
                    rel="noreferrer"
                  >
                    {c.clientDocs}
                    <ExternalLink size={13} />
                  </a>
                </>
              )}
              {installed && (
                <div className="completion">
                  <CheckCircle2 className="done-icon" size={36} />
                  <p>
                    {state.demo
                      ? c.demoDoneHint
                      : c.doneHint.replace("{client}", clientNames[client])}
                  </p>
                  <h2>{state.demo ? c.demoPrompt : c.tryPrompt}</h2>
                  <blockquote>{prompt}</blockquote>
                  <button
                    className="secondary full"
                    onClick={async () => {
                      try {
                        await navigator.clipboard.writeText(prompt);
                        setCopied(true);
                      } catch {
                        setError("clipboard_failed");
                      }
                    }}
                  >
                    {copied ? <Check size={16} /> : <Copy size={16} />}
                    {copied ? c.copied : c.copy}
                  </button>
                  <details className="completion-details">
                    <summary>{c.destination}</summary>
                    <code className="path">{installed.target_path}</code>
                    {installed.backup_path && (
                      <>
                        <h2>{c.backup}</h2>
                        <code className="path">{installed.backup_path}</code>
                      </>
                    )}
                  </details>
                  <div className="completion-actions">
                    <button
                      className="text-button"
                      onClick={() => {
                        setInstalled(undefined);
                        setPreview(undefined);
                        setError("");
                        setCopied(false);
                      }}
                    >
                      {c.anotherAgent}
                    </button>
                    {!state.demo && (
                      <button className="text-button" onClick={addAnother}>
                        <Plus size={15} />
                        {c.anotherAccount}
                      </button>
                    )}
                  </div>
                  <p className="muted">{c.closeHint}</p>
                </div>
              )}
            </>
          )}
          {busy && (
            <span className="sr-only" role="status">
              {c[busy]}
            </span>
          )}
        </section>
        <footer>
          <LockKeyhole size={13} />
          {c.footer}
        </footer>
      </main>
    </div>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
