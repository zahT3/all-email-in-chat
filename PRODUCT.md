# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

People who want to manage their email in the desktop AI agent they already use.

## Product Purpose

Configure email once, then expose permitted email operations through a local MCP server to desktop agents. The local web interface completes account setup, tests IMAP connectivity, and previews and installs agent configuration.

## Operating Context

A Python CLI runs locally. Mailbox credentials belong in the operating system keyring. The user uses Claude Code/Desktop, ChatGPT desktop, Codex, Cursor, or Kimi Code Desktop for conversation. The web interface is a setup tool, not an inbox or another chat product.

## Capabilities and Constraints

IMAP/SMTP password and app-password accounts; Aliyun enterprise, Aliyun personal, PrivateEmail and custom server presets. No OAuth, hosted service or background automation yet. Read, draft and manage policies are enforced by the MCP bridge. The UI preserves existing policy; new configurations default to read. Demo data and demo client configuration remain isolated. An IMAP test does not establish SMTP delivery or desktop-agent compatibility.

## Evidence on Hand

Protocol and configuration tests, synthetic email fixtures, public upstream research under docs/research. Live provider and actual desktop product acceptance remain pending.

## Implementation choices

React and TypeScript, packaged static assets served by Python. Chinese-first setup copy. These are implementation defaults for the first wizard; product branding and additional languages remain open.
