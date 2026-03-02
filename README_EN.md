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

## Pain points solved

1. **Multi-account switching is tedious** (CLI + browser + callback + status checks).
2. **Frequent Xianyu account session drops** require repeated re-login.
3. **Slow troubleshooting** when failures happen.

## One-line install (includes original `cs` command)

This repo includes executable command files: `bin/chatgptswitch` and `bin/cs`.

```bash
curl -fsSL https://raw.githubusercontent.com/anjun/cs-relogin-skill/master/install.sh | bash
```

Verify:

```bash
cs relogin status
```

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
