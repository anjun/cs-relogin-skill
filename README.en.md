# cs-relogin (OpenClaw Skill)

Chinese default: [README.md](./README.md)

A skill that lets the model handle the `cs relogin` account switch/login workflow for you.

## Pain points this solves

1. **Multi-account switching is tedious**: too many manual steps (command, callback URL, status checks).
2. **Frequent re-login for Xianyu account**: sessions drop often and require repeated logins.
3. **Inconsistent troubleshooting**: hard to know which command/state to inspect when login fails.

## What it does

- Triggers on `cs relogin`
- Handles pasted OAuth callback URL/code automatically
- Reports active account status after completion
- Returns raw command errors first for fast debugging

## Structure

```text
skills/
  cs-relogin/
    SKILL.md

dist/
  cs-relogin.skill
```

## Quick install

### Option A: Manual install (folder)
Put `skills/cs-relogin` into your local skills directory, e.g.:

- `~/.openclaw/skills/`

### Option B: Packaged file
Install from `dist/cs-relogin.skill` using your OpenClaw import flow.

## Typical commands

- `cs relogin`
- Paste callback URL (`http://localhost:1455/auth/callback?...`)
- `cs relogin status`
- `cs status`

## Notes

- This skill orchestrates login/switch flow only.
- It should not expose sensitive token values.
