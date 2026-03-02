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
2. Tell the model: `Help me login to ChatGPT` or `Switch to my Xianyu account`
3. The model runs `cs relogin` automatically, gives you the OAuth URL → waits for callback → completes login and reports status

**That's it. No need to remember commands.**

## Pain points solved

1. **Multi-account switching is tedious** (CLI + browser + callback + status checks).
2. **Frequent Xianyu account session drops** require repeated re-login.
3. **Slow troubleshooting** when failures happen.

## One-line install (includes original `cs` command)

This repo includes executable command files: `bin/chatgptswitch` and `bin/cs`.

✅ **You can run it directly on a remote server (SSH shell)** after installation (`cs relogin` / `cs status`).

Linux / macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/anjun/cs-relogin-skill/master/install.sh | bash
```

> Native Windows is not supported for now (this project depends on Bash).

Verify:

```bash
cs relogin status
```

## Server usage (quick path)

```bash
# 1) Install on the server shell
curl -fsSL https://raw.githubusercontent.com/anjun/cs-relogin-skill/master/install.sh | bash

# 2) Check current account status
cs status

# 3) Start relogin (prints OAuth URL)
cs relogin

# 4) Paste callback URL/code to finish
cs relogin '<callback-url-or-code>'
```

## Compatibility review

- **Linux VPS (systemd)**: ✅ works (prefers `systemctl --user` restart)
- **Linux VPS (no systemd)**: ✅ works (falls back to `openclaw gateway restart`)
- **macOS**: ✅ works (uses OpenClaw CLI restart fallback)
- **Windows native**: ❌ not supported for now (unless you bring your own Bash runtime such as Git Bash/WSL)

Dependencies: `bash`, `python3`, `curl`, `openclaw`.

## OpenClaw Skill install

- Folder install: put `skills/cs-relogin` under `~/.openclaw/skills/`
- Package install: import `dist/cs-relogin.skill`

## Typical commands

- `cs relogin`
- `cs relogin '<callback-url-or-code>'`
- `cs relogin status`
- `cs status`

## Structure

```text
bin/
  chatgptswitch
  cs

skills/
  cs-relogin/
    SKILL.md

dist/
  cs-relogin.skill

install.sh
```

## Security note

- This tool orchestrates auth login/switch only
- It should never expose full token values
