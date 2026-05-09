# AGENTS.md

## Purpose

This repository contains the initial structure for an AI team agent system. Coding agents should preserve the structure-first approach until the project owner approves implementation work.

## Global Rules

- Write internal commands, file names, code identifiers, schemas, and system prompts in English.
- Write user-facing outputs, reports, summaries, notifications, and explanations in Korean.
- Do not connect external APIs yet.
- Do not add credentials, tokens, or private configuration files.
- Do not send email, chat messages, social posts, or notifications without explicit user approval.

## Project Layout

- `agents/supervisor`: supervisor agent prompt and future configuration.
- `agents/assistant`: assistant agent prompt and future configuration.
- `agents/document`: document agent prompt and future configuration.
- `agents/communication`: communication agent prompt and future configuration.
- `agents/workflow`: workflow agent prompt and future configuration.
- `agents/harness`: harness agent prompt and future configuration.
- `agents/instagram`: instagram agent prompt and future configuration.
- `templates`: reusable user-facing output templates.
- `tests/harness`: harness test case definitions.
- `examples/golden`: expected high-quality examples.
- `examples/failure`: known bad or risky examples.
- `docs`: user-facing project documentation.

## Output Contract

Every agent must return user-facing content in Korean. If an agent needs to include internal metadata, keep keys and enum values in English while keeping explanatory text in Korean.

Example status keys:

```json
{
  "status": "pending",
  "summary": "사용자 검토가 필요합니다."
}
```

## External Integration Backlog

### Google Sheets

- Define schemas and permissions before implementation.
- Add mock data and harness cases first.
- Never run Google Sheets write actions automatically.
- Require explicit user approval before any Google Sheets write action.
- Before writing, show the target spreadsheet, target tab, target row/column, source value, and proposed value.
- After writing, verify the written value and report the result in Korean.

### Gmail

- Define read, draft, and send boundaries.
- Require user approval before sending.

### Slack

- Define read, draft, and post boundaries.
- Require user approval before posting.

### Telegram

- Define bot commands in English.
- Return all bot responses in Korean.
- Require explicit user approval for Telegram notifications until the notification policy is fully defined.
- Do not send any external notification automatically in the MVP stage.
- Use Telegram for draft alerts, approval requests, and personal reports only after user approval.

### Instagram

- Define content, asset, and publishing approval workflow.
- Do not auto-publish in the initial integration.

### Reporting

- Define shared report schema.
- Add golden examples and failure cases before implementation.

## Change Guidance

- Prefer adding documentation and examples before runtime code.
- Keep each agent role narrow and explicit.
- Add tests when behavior is introduced.
- Update `docs/architecture.md` when responsibilities or data flow change.
