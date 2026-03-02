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

## What it does

- Runs `cs relogin` and returns fresh OAuth URL
- Accepts pasted callback URL/code and completes relogin
- Reports active account/profile after success
- Surfaces raw command errors first for debugging

## Installation

### Option A: Folder install
Put `skills/cs-relogin` under:

- `~/.openclaw/skills/`

### Option B: Package install
Import `dist/cs-relogin.skill`.

## Typical commands

- `cs relogin`
- `cs relogin '<callback-url-or-code>'`
- `cs relogin status`
- `cs status`

## Structure

```text
skills/
  cs-relogin/
    SKILL.md

dist/
  cs-relogin.skill
```

## Security note

- This skill orchestrates auth login/switch only
- It should never expose full token values
