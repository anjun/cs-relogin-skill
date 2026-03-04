---
name: cs-relogin
description: Self-contained OpenClaw skill for Codex OAuth account switch (relogin/status) without relying on system-wide `cs` install. Use when user says `cs relogin`, asks to switch ChatGPT Codex account, or provides OAuth callback URL/code.
allowed-tools: ["Bash(*cs*)", "Bash(*chatgptswitch*)"]
metadata: {"clawdbot":{"emoji":"🔐"}}
---

# CS Relogin Skill (Self-contained)

Use this skill to perform OpenAI Codex account switching without `openclaw onboard`.

This skill bundles executables in `scripts/`:
- `scripts/cs`
- `scripts/chatgptswitch`

## Hard rules

- Always execute bundled `scripts/cs`; do not depend on global `cs` in PATH.
- Never call `openclaw onboard` for this task.
- Keep flow non-interactive.
- All write operations must pass explicit `--apply`.
- Restart policy: chat runtime defaults to no-restart to avoid interrupting reply delivery; CLI runtime defaults to restart. Use `--restart` / `--no-restart` to force.
- Do not set or auto-enable proxy fallback; only use proxy when user explicitly requests it.
- If user provided callback URL/code, complete relogin immediately with `--apply`.

## Path rule (MUST)

The system prompt provides this skill file path. Resolve skill directory from it and run commands with absolute path.

Example (replace with actual skill dir):
```bash
SKILL_DIR="<dirname-of-this-SKILL.md>"
"$SKILL_DIR/scripts/cs" status
```

## Workflow

1. If user input is exactly `cs relogin`:
   - Run:
     ```bash
     "$SKILL_DIR/scripts/cs" relogin
     ```
   - Return login URL from output.
   - Ask user to complete browser auth and paste callback URL.

2. If user input contains callback URL/code:
   - Run with explicit apply:
     ```bash
     "$SKILL_DIR/scripts/cs" relogin "<callback-url-or-code>" --apply
     ```
   - Do NOT force gateway restart in the same callback reply flow unless user explicitly requests restart now.
   - Return key lines:
     - relogin completed status
     - pending/state check summary
     - active profile/account summary

3. If user asks status/debug:
   - Run:
     ```bash
     "$SKILL_DIR/scripts/cs" relogin status
     "$SKILL_DIR/scripts/cs" status
     ```
   - Summarize pending state and active account.

## Output format

- Keep response concise and actionable.
- Include exact next command when another step is needed.
- Never expose full tokens/secrets.
- On failure, include raw stderr first (do not guess reason).

## Acknowledgement rule (MUST)

- Every successful action must include explicit acknowledgement:
  - what was executed
  - whether it succeeded
  - current state summary (pending relogin / active account)
- If output is missing/flaky, immediately run:
  ```bash
  "$SKILL_DIR/scripts/cs" relogin status
  "$SKILL_DIR/scripts/cs" status
  ```
  then send acknowledgement.
- Never end silently after execution.
