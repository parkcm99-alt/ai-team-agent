# CLAUDE.md

This file gives Claude and other coding agents local project guidance.

## Project Intent

Create an AI team agent system with clear role boundaries before adding implementation or external integrations.

## Language Policy

- Internal commands, file names, and system prompts must be written in English.
- User-facing outputs, reports, summaries, notifications, and explanations must be written in Korean.
- When in doubt, treat files under `agents/*/system_prompt.md`, internal command names, schemas, and code identifiers as internal.
- Treat README-style explanations, reports, user notifications, and final summaries as user-facing.

## Current Scope

- Structure only.
- No external API connections.
- No secrets, tokens, credentials, or live service calls.
- Prefer placeholders, TODO sections, and sample-free scaffolding until integration requirements are approved.

## Agent Directories

- `agents/supervisor`: Coordinates tasks, delegates work, enforces policy, and consolidates outputs.
- `agents/assistant`: Handles general assistance and user request shaping.
- `agents/document`: Produces and reviews structured documents.
- `agents/communication`: Prepares communication workflows for email, chat, and notifications.
- `agents/workflow`: Defines task state, routing, and repeatable process flow.
- `agents/harness`: Owns evaluation, fixtures, and regression checks.
- `agents/instagram`: Prepares Instagram-specific content workflows without connecting to Instagram yet.

## Integration TODOs

### Google Sheets

- Define sheet schemas for task tracking, reporting, and agent outputs.
- Add mock fixtures before connecting live APIs.
- Keep credentials outside the repository.
- Google Sheets write actions must never run automatically.
- Google Sheets write actions require explicit user approval.
- Before writing, show the target spreadsheet, target tab, target row/column, source value, and proposed value.
- After writing, verify the written value and report the result in Korean.

### Gmail

- Define inbox triage, reply drafting, and approval boundaries.
- Require explicit user approval before any send action.
- Add sample-based harness cases before live access.

### Slack

- Define channel summary, DM reply, and notification-priority behavior.
- Require explicit user approval before posting.
- Add representative message fixtures.

### Telegram

- Define bot command names in English.
- Keep all user-facing bot responses in Korean.
- Use environment variables for tokens once integration begins.
- Telegram notifications require explicit user approval until the notification policy is fully defined.
- No external notification should be sent automatically in the MVP stage.
- Telegram may be used for draft alerts, approval requests, and personal reports only after user approval.

### Instagram

- Define content planning, caption drafting, and approval flow.
- Do not publish automatically in the first integration pass.
- Add asset validation rules before API work.

### Reporting

- Define common status names, report sections, and Korean summary format.
- Capture per-agent outcomes in a shared reporting schema.
- Add golden examples before implementing report generation.

## Development Notes

- Keep new implementation small and role-oriented.
- Do not add a framework until a concrete runtime requirement exists.
- Document any new folder or file that changes the architecture.
