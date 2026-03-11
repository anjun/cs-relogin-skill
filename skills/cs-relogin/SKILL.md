---
name: cs-relogin
description: Self-contained OpenClaw skill for Codex OAuth account switch (relogin/use/status/remove) without relying on system-wide `cs` install. Use when user says `cs relogin`, asks to switch ChatGPT Codex account, asks to switch to a saved alias, or provides OAuth callback URL/code.
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

1. If user asks to switch to an existing saved alias:
   - Run:
     ```bash
     "$SKILL_DIR/scripts/cs" use "<alias>" --apply --no-restart
     ```
   - Return:
     - switched alias
     - active profile/account summary

2. If user input is exactly `cs relogin` or asks to add/login a new account alias:
   - Run:
     ```bash
     "$SKILL_DIR/scripts/cs" relogin
     ```
   - Return login URL from output.
   - Ask user to complete browser auth and paste callback URL.

3. If user input contains callback URL/code:
   - Run with explicit apply:
     ```bash
     "$SKILL_DIR/scripts/cs" relogin "<callback-url-or-code>" --apply --no-restart
     ```
   - Prefer delayed restart in the same callback reply flow so the acknowledgement can be delivered first; only force immediate restart if user explicitly requests restart now.
   - Return key lines:
     - relogin completed status
     - pending/state check summary
     - active profile/account summary

4. If user asks to delete a saved alias:
   - Run:
     ```bash
     "$SKILL_DIR/scripts/cs" remove "<alias>" --apply --no-restart
     ```
   - Return:
     - removed alias
     - active profile/account summary

5. If user asks status/debug:
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


## Failure policy (MUST)

- If callback apply fails with OAuth code errors (expired/used/invalid):
  - Report raw stderr first.
  - Run `cs relogin status` and `cs status` for confirmation.
  - Do **NOT** auto-run `cs relogin` to generate a new URL unless user explicitly asks.
- Never execute `cs relogin` (no-arg) in the same callback message turn after an apply attempt.
