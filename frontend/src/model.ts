export type Provider = {
  name: { zh: string; en: string };
  imap?: string;
  smtp?: string;
  imap_port?: number;
  smtp_port?: number;
  domains: string[];
  auth: string;
  available: boolean;
  source_url?: string;
};
export function matchProvider(
  email: string,
  providers: Record<string, Provider>,
): string {
  const parts = email.trim().toLowerCase().split("@");
  if (parts.length !== 2 || !parts[0]) return "custom";
  return (
    Object.entries(providers).find(([, p]) =>
      p.domains.includes(parts[1]),
    )?.[0] || "custom"
  );
}
export function suggestAlias(email: string, existing: string[]): string {
  const base =
    email
      .split("@")[0]
      .toLowerCase()
      .replace(/[^a-z0-9-]/g, "-")
      .replace(/^[^a-z]+/, "")
      .slice(0, 30) || "mail";
  let candidate = base;
  for (let i = 2; existing.includes(candidate); i++) candidate = `${base}-${i}`;
  return candidate;
}
