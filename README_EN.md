# cs-relogin

<p align="center">
  <a href="./README.md">中文</a> | <strong>English</strong>
</p>

An OpenClaw skill focused on one thing:

> Automate **ChatGPT Auth (Codex OAuth) login/account switching** with `cs relogin`.

## Core use case

Handle the full relogin flow for you:

1. Generate OAuth login URL
2. Accept callback URL/code
3. Complete relogin
4. Report active profile/account status
5. Give explicit acknowledgement for each step (action + result + current state)

## One-click use with AI (OpenClaw)

**Let the AI model handle login/account switching for you:**

1. Install this skill (see "One-line install" below)
2. Tell the model: `Help me login to ChatGPT` or `Switch my ChatGPT account`
3. The model runs `cs relogin` automatically, gives you the OAuth URL → waits for callback → completes login and reports status

**That's it. No need to remember commands.**

## Pain points solved

1. **Multi-account switching is tedious** (CLI + browser + callback + status checks).
2. **Multi-account switching is tedious**: login URL, browser auth, callback URL, and status checks are easy to get wrong.
3. **Slow troubleshooting** when failures happen.

## One-line install (includes original `cs` command)

This repo includes executable command files: `bin/chatgptswitch` and `bin/cs`.

✅ **You can run it directly on a remote server (SSH shell)** after installation (`cs relogin` / `cs status`).

Linux / macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/anjun/cs-relogin-skill/v1.2.6/install.sh | bash
```

> Native Windows is not supported for now (this project depends on Bash).

Verify:

```bash
cs relogin status
```

## Server usage (quick path)

```bash
# 1) Install on the server shell
curl -fsSL https://raw.githubusercontent.com/anjun/cs-relogin-skill/v1.2.6/install.sh | bash

# 2) Check current account status
cs status

# 3) Start relogin (prints OAuth URL)
cs relogin

# 4) Paste callback URL/code to finish
cs relogin '<callback-url-or-code>' --apply [--restart|--no-restart|--deferred-restart]
```

## Compatibility review

- **Linux VPS (systemd)**: ✅ works (prefers `systemctl --user` restart)
- **Linux VPS (no systemd)**: ✅ works (falls back to `openclaw gateway restart`)
- **macOS**: ✅ works (uses OpenClaw CLI restart fallback)
- **Windows native**: ❌ not supported for now (unless you bring your own Bash runtime such as Git Bash/WSL)

Dependencies: `bash`, `python3`, `curl`, `openclaw`.

Safe defaults (v1.2.6+):
- Write operations require explicit `--apply`
- Restart policy is runtime-aware: default deferred restart in OpenClaw chat/skill execution, default immediate restart in direct shell/SSH usage; override via `--restart` / `--no-restart` / `--deferred-restart`
- No automatic proxy fallback; proxy is used only when `CHATGPTSWITCH_PROXY` is explicitly set

## OpenClaw Skill install

> This skill is now **self-contained**: `skills/cs-relogin/scripts/{cs,chatgptswitch}` are bundled with the skill.
> The published `.skill` package should include these scripts (no global `cs` PATH dependency).

- Folder install: put `skills/cs-relogin` under `~/.openclaw/skills/`
- Package install: import `dist/cs-relogin.skill`

Package self-check:

```bash
unzip -l dist/cs-relogin.skill
# expected:
# cs-relogin/SKILL.md
# cs-relogin/scripts/cs
# cs-relogin/scripts/chatgptswitch
```

## Typical commands

- `cs relogin`
- `cs relogin <alias>`
- `cs relogin '<callback-url-or-code>' --apply [--restart|--no-restart|--deferred-restart]`
- `cs use <profile-id-or-alias> --apply [--restart|--no-restart|--deferred-restart]`
- `cs remove <profile-id-or-alias> --apply [--restart|--no-restart|--deferred-restart]`
- `cs relogin status`
- `cs list`
- `cs status`
- `cs usage [profile-id-or-alias]`
- `cs patch status-usage --apply [--restart|--no-restart|--deferred-restart]`

## Structure

```text
bin/
  chatgptswitch
  cs

skills/
  cs-relogin/
    SKILL.md
    scripts/
      chatgptswitch
      cs

dist/
  cs-relogin.skill

scripts/
  patch_openclaw_status_usage.py

install.sh
```

## Security note

- This tool orchestrates auth login/switch only
- It should never expose full token values


## OpenClaw `/status` Usage Fix

If you only need the real quota for the current account, prefer the non-invasive command first:

```bash
cs usage
```

If OpenClaw `/status` or the `session_status` tool still shows a mismatched Codex usage value, run:

```bash
cs patch status-usage --apply
```

What it does:
- binds both `/status` and `session_status` usage lookup to the session's current `authProfileOverride`
- restarts the gateway
- runs a before/after verification across the `compact + pi-embedded` bundle paths that serve `/status` and `session_status`

Notes:
- this is a replayable patch against the current OpenClaw bundle
- if an OpenClaw upgrade overwrites it, just run the command again

## Callback Flow Recommendation (avoid reply-chain stalls)

When finishing callback inside OpenClaw chat, prefer:

```bash
cs relogin '<callback-url-or-code>' --apply --deferred-restart
```

Why:
- Lets the current reply finish first, then schedules a delayed gateway restart to avoid interrupting delivery.
- If callback fails (expired/used code), run `cs relogin status` + `cs status` first; do not auto-run `cs relogin` again in the same turn.
