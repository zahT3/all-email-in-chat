# Third-party dependencies and research

All Email in Chat's original source is MIT licensed. Dependency licenses remain
their own; MIT does not relicense them.

The email runtime is the separately installed
[Wh1isper/mcp-email-server 1.9.1](https://github.com/Wh1isper/mcp-email-server/tree/1.9.1),
under [BSD-3-Clause](https://github.com/Wh1isper/mcp-email-server/blob/1.9.1/LICENSE).
It performs IMAP/SMTP operations; this project provides configuration,
policy, onboarding and a stdio bridge around its public MCP interface.
This repository does not vendor its source. Preserve its license and notices
when redistributing that dependency.

Runtime dependencies are declared in `pyproject.toml`; `uv.lock` records exact
development resolution, including transitive dependencies. Their distributions
contain their own licensing information. No upstream author endorsement is implied.

The following projects were researched and tested separately. They are not
runtime dependencies, and their source is not copied into this repository:

- [pimalaya/himalaya](https://github.com/pimalaya/himalaya): MIT OR Apache-2.0.
- [codefuturist/email-mcp](https://github.com/codefuturist/email-mcp): LGPL-3.0.
- [samihalawa/email-smtp-imap-mcp](https://github.com/samihalawa/email-smtp-imap-mcp): MIT.

See `docs/research/` for precise commits, evidence, and the design lessons used.
