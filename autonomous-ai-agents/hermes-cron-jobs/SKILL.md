---
name: hermes-cron-jobs
description: Schedule/edit Hermes cron jobs with Discord delivery.
category: autonomous-ai-agents
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, cron, scheduling, discord, messaging, gateway]
    related_skills: [hermes-agent]
---

# Hermes Cron Jobs & Platform Delivery

## When to Use

Use when the user asks to schedule, edit, test or fix a recurring Hermes job (a morning briefing, digest, monitor, notification) — especially one that must deliver to a messaging platform like Discord, Telegram or Slack. Also when cron delivery fails with a platform-not-configured error, or the gateway won't start.

Create, edit, test and verify recurring Hermes agent jobs, including messaging-platform delivery.

## Workflow

1. **Create** via `cronjob(action="create", name=..., schedule=..., deliver=..., prompt=...)`. Schedules: `"0 8 * * *"` (cron), `"every day at 9am"`, `"30m"`, `"in 2h"`, or an ISO one-shot. `deliver="discord"` posts to the home channel from `DISCORD_HOME_CHANNEL`; `deliver="local"` saves output only. Confirm `next_run_at` is in the user's local timezone.
2. **Prompt must be self-contained** — a cron run executes in a fresh session with no chat context. Include the full task, the exact output format/section order, the output language, the sourcing/verification rules, and the note that the final response is auto-delivered (the agent must NOT send it itself or write it to a file).
3. **Test delivery before relying on it**: `hermes send --to discord "..."` works WITHOUT the gateway running (bot-token platforms). `hermes send --list` shows the discovered targets.
4. **The gateway must be running for cron to fire** — the scheduler ticks inside the gateway daemon. Install once as the host multiplexer from the DEFAULT profile: `hermes -p default gateway install --start-on-login --start-now`. Confirm with `hermes gateway status` and `✓ discord connected` in `logs/gateway.log`.
5. **Verify delivery from the ledger, not from self-reports**: `hermes cron list` shows `last_status`; `cron/executions.db` has a `delivery_outcome` column (`delivered` = confirmed). A delegation/subagent claim of "ok" is not proof — check the ledger.

## Pitfalls

- **Profile mismatch (the big one)**: platform credentials in `%LOCALAPPDATA%/hermes/.env` belong to the DEFAULT profile. The ACTIVE profile reads only its OWN `profiles/<name>/.env` + `config.yaml`. So `hermes send` / a cron job in the active profile fails with "Platform 'discord' is not configured. Looked in: ...profiles/<name>/.env (no DISCORD_BOT_TOKEN)" even though Discord works elsewhere. Fix: copy the `DISCORD_*` lines into the active profile's `.env` AND add the `platforms.discord.*` block via `hermes config set` (never hand-edit config.yaml).
- **One bot token serves one gateway**: two profiles holding the same `DISCORD_BOT_TOKEN` make the gateway log "refusing to start the duplicate (one credential cannot be consumed twice)" and park the second profile's adapter. Harmless for cron delivery (the multiplexer still delivers) — a dedicated token is only needed if you want interactive bot use in both profiles.
- **Per-profile gateway install is refused**: `hermes gateway install` from a non-default profile errors with "Profile 'X' does not get a gateway of its own." Install from `default`; the host multiplexer serves every profile.
- **`hermes cron run <name>` blocks until the run finishes** — long research/generation jobs exceed the 300s foreground timeout. Run it in the background with notify, or via `cronjob(action="run")` and wait for the outcome to re-enter the conversation.
- **A gateway restart mid-run marks the execution `unknown`** in the ledger (not a failure — just undeterminable). Re-run to get a clean test signal.
- **Editing a job replaces the WHOLE prompt** — read the exact stored prompt from `cron/jobs.json` first, then resubmit the full new prompt with ONLY the requested change. Never regenerate it from memory of the conversation; the user may have edited it between sessions.
- **Recurring daily jobs fire only while the host is on at the scheduled time** — if the machine is off, the run is skipped (no catch-up for daily schedules unless `cron.catch_up_missed` is set). Tell the user this up front.

## Template

The user's standing daily AI-morning-briefing prompt (9 sections, French, sourcing rules, Discord formatting) is in `templates/ai-morning-briefing-prompt.md` — copy it and adapt the sections when editing that job.
