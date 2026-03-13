#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
import os
import pathlib
import subprocess
import tempfile
import time
import urllib.request
from typing import Optional

STATE_DIR = os.path.expanduser(os.environ.get("OPENCLAW_STATE_DIR", "~/.openclaw"))
SESSIONS_PATH = os.path.join(STATE_DIR, "agents", "main", "sessions", "sessions.json")
AUTH_PROFILES_PATH = os.path.join(STATE_DIR, "agents", "main", "agent", "auth-profiles.json")
PROXYCHAINS_CONF = os.path.expanduser("~/.config/proxychains/openclaw-gateway.conf")
PATCH_MARKER = "async function resolveSessionBoundUsageAuth(params) {"
HELPER_ANCHOR = "//#endregion\n//#region src/auto-reply/reply/commands-status.ts\n"
BUILD_STATUS_ANCHOR = "async function buildStatusReply(params) {"
QUEUE_SETTINGS_ANCHOR = "\tconst queueSettings = resolveQueueSettings({\n"
USAGE_BLOCK_PREFIX = "\tlet usageLine = null;\n"
STATUS_SESSION_PREFIX = "agent:main:feishu:direct:"

HELPER_BLOCK = """async function resolveSessionBoundUsageAuth(params) {\n\tconst profileId = params.sessionEntry?.authProfileOverride?.trim();\n\tif (!profileId) return;\n\ttry {\n\t\tconst store = ensureAuthProfileStore(params.agentDir, { allowKeychainPrompt: false });\n\t\tconst cred = store.profiles[profileId];\n\t\tif (!cred || normalizeProviderId(cred.provider) !== params.provider || cred.type !== \"oauth\" && cred.type !== \"token\") return;\n\t\tconst resolved = await resolveApiKeyForProfile({\n\t\t\tcfg: void 0,\n\t\t\tstore,\n\t\t\tprofileId,\n\t\t\tagentDir: params.agentDir\n\t\t});\n\t\tif (!resolved?.apiKey) return;\n\t\tlet token = resolved.apiKey;\n\t\tif (params.provider === \"google-gemini-cli\") token = parseGoogleToken(resolved.apiKey)?.token ?? resolved.apiKey;\n\t\treturn [{\n\t\t\tprovider: params.provider,\n\t\t\ttoken,\n\t\t\taccountId: cred.type === \"oauth\" && \"accountId\" in cred ? cred.accountId : void 0\n\t\t}];\n\t} catch {\n\t\treturn;\n\t}\n}\n"""

USAGE_BLOCK = """\tlet usageLine = null;\n\tif (currentUsageProvider) try {\n\t\tconst usageAuth = await resolveSessionBoundUsageAuth({\n\t\t\tprovider: currentUsageProvider,\n\t\t\tagentDir: statusAgentDir,\n\t\t\tsessionEntry\n\t\t});\n\t\tconst usageEntry = (await loadProviderUsageSummary({\n\t\t\ttimeoutMs: 3500,\n\t\t\tproviders: [currentUsageProvider],\n\t\t\tagentDir: statusAgentDir,\n\t\t\tauth: usageAuth\n\t\t})).providers[0];\n\t\tif (usageEntry && !usageEntry.error && usageEntry.windows.length > 0) {\n\t\t\tconst summaryLine = formatUsageWindowSummary(usageEntry, {\n\t\t\t\tnow: Date.now(),\n\t\t\t\tmaxWindows: 2,\n\t\t\t\tincludeResets: true\n\t\t\t});\n\t\t\tif (summaryLine) usageLine = `📊 Usage: ${summaryLine}`;\n\t\t}\n\t} catch {\n\t\tusageLine = null;\n\t}\n"""


def read_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def find_compact_file() -> str:
    candidates = []
    for pattern in (
        "/usr/lib/node_modules/openclaw/dist/compact-*.js",
        "/usr/local/lib/node_modules/openclaw/dist/compact-*.js",
    ):
        candidates.extend(glob.glob(pattern))
    candidates = [p for p in sorted(candidates) if "compact-status-test-" not in p]
    if not candidates:
        raise SystemExit("[ERR] OpenClaw compact bundle not found.")
    for path in candidates:
        text = pathlib.Path(path).read_text(encoding="utf-8")
        if BUILD_STATUS_ANCHOR in text:
            return path
    raise SystemExit("[ERR] compact bundle found, but buildStatusReply anchor missing.")


def is_patched(text: str) -> bool:
    return PATCH_MARKER in text and "auth: usageAuth" in text


def apply_patch(compact_path: str) -> dict:
    text = pathlib.Path(compact_path).read_text(encoding="utf-8")
    if is_patched(text):
        return {"changed": False, "backup": None, "path": compact_path, "alreadyPatched": True}
    if HELPER_ANCHOR not in text:
        raise SystemExit("[ERR] helper anchor not found; unsupported OpenClaw bundle layout.")
    build_idx = text.find(BUILD_STATUS_ANCHOR)
    if build_idx < 0:
        raise SystemExit("[ERR] buildStatusReply anchor not found.")
    usage_start = text.find(USAGE_BLOCK_PREFIX, build_idx)
    usage_end = text.find(QUEUE_SETTINGS_ANCHOR, usage_start)
    if usage_start < 0 or usage_end < 0:
        raise SystemExit("[ERR] usage block anchors not found; unsupported status function layout.")
    patched_text = text.replace(HELPER_ANCHOR, HELPER_ANCHOR + HELPER_BLOCK, 1)
    delta = len(patched_text) - len(text)
    text = patched_text[:usage_start + delta] + USAGE_BLOCK + patched_text[usage_end + delta:]
    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = f"{compact_path}.bak.{ts}.status-usage"
    subprocess.run(["sudo", "cp", compact_path, backup], check=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
        tmp.write(text)
        tmp_path = tmp.name
    subprocess.run(["sudo", "install", "-m", "644", tmp_path, compact_path], check=True)
    os.unlink(tmp_path)
    return {"changed": True, "backup": backup, "path": compact_path, "alreadyPatched": False}


def find_session_key(explicit_key: Optional[str]) -> str:
    sessions = read_json(SESSIONS_PATH)
    if explicit_key:
        if explicit_key not in sessions:
            raise SystemExit(f"[ERR] session not found: {explicit_key}")
        return explicit_key
    candidates = []
    for key, entry in sessions.items():
        if not key.startswith(STATUS_SESSION_PREFIX):
            continue
        if key.endswith(":heartbeat") or key.endswith("heartbeat"):
            continue
        if not isinstance(entry, dict):
            continue
        candidates.append((int(entry.get("updatedAt", 0) or 0), key))
    if not candidates:
        raise SystemExit("[ERR] no Feishu direct session found.")
    candidates.sort(reverse=True)
    return candidates[0][1]


def current_session_and_profile(session_key: str):
    sessions = read_json(SESSIONS_PATH)
    session = sessions[session_key]
    profile_id = (session.get("authProfileOverride") or "").strip()
    if not profile_id:
        raise SystemExit("[ERR] session has no authProfileOverride; cannot bind usage to a specific profile.")
    auth = read_json(AUTH_PROFILES_PATH)
    profile = auth.get("profiles", {}).get(profile_id)
    if not isinstance(profile, dict):
        raise SystemExit(f"[ERR] auth profile not found: {profile_id}")
    return session, profile_id, profile


def resolve_proxy_url() -> Optional[str]:
    env_proxy = (os.environ.get("CHATGPTSWITCH_PROXY") or "").strip()
    if env_proxy:
        return env_proxy
    try:
        with open(PROXYCHAINS_CONF, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 3 and parts[0].lower() in {"http", "https", "socks5", "socks4"}:
                    scheme = "http" if parts[0].lower().startswith("http") else "socks5"
                    return f"{scheme}://{parts[1]}:{parts[2]}"
    except FileNotFoundError:
        return None
    return None


def fetch_explicit_codex_usage(profile: dict) -> dict:
    access = (profile.get("access") or "").strip()
    account_id = (profile.get("accountId") or "").strip()
    if not access:
        raise SystemExit("[ERR] selected profile is missing access token.")
    req = urllib.request.Request(
        "https://chatgpt.com/backend-api/wham/usage",
        headers={
            "Authorization": f"Bearer {access}",
            "User-Agent": "CodexBar",
            "Accept": "application/json",
            **({"ChatGPT-Account-Id": account_id} if account_id else {}),
        },
        method="GET",
    )
    proxy_url = resolve_proxy_url()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})) if proxy_url else urllib.request.build_opener()
    with opener.open(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def format_remaining_short(target_ms: Optional[int], now_ms: int) -> Optional[str]:
    if not target_ms:
        return None
    diff_ms = target_ms - now_ms
    if diff_ms <= 0:
        return "now"
    diff_mins = diff_ms // 60000
    if diff_mins < 60:
        return f"{diff_mins}m"
    hours = diff_mins // 60
    mins = diff_mins % 60
    if hours < 24:
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
    days = hours // 24
    if days < 7:
        return f"{days}d {hours % 24}h"
    return time.strftime("%b %d", time.localtime(target_ms / 1000))


def expected_usage_line(profile: dict) -> str:
    data = fetch_explicit_codex_usage(profile)
    rate = data.get("rate_limit") or {}
    primary = rate.get("primary_window") or {}
    limit_window_seconds = int(primary.get("limit_window_seconds") or 10800)
    label = f"{round(limit_window_seconds / 3600)}h"
    used_percent = float(primary.get("used_percent") or 0)
    remaining = max(0, min(100, round(100 - used_percent)))
    reset_at = primary.get("reset_at")
    reset_ms = int(reset_at * 1000) if isinstance(reset_at, (int, float)) else None
    reset_suffix = ""
    remaining_short = format_remaining_short(reset_ms, int(time.time() * 1000))
    if remaining_short:
        reset_suffix = f" ⏱{remaining_short}"
    return f"📊 Usage: {label} {remaining}% left{reset_suffix}"


def actual_status_usage_line(compact_path: str, session_key: str) -> str:
    tmp_js = None
    test_js = None
    try:
        tmp_js = subprocess.check_output(["sudo", "mktemp", os.path.join(os.path.dirname(compact_path), "compact-status-test-XXXXXX.mjs")], text=True).strip()
        subprocess.run(["sudo", "cp", compact_path, tmp_js], check=True)
        subprocess.run(["sudo", "bash", "-lc", f"printf '\nexport {{ buildStatusReply as __buildStatusReply }};\n' >> {tmp_js!s}"], check=True)
        subprocess.run(["sudo", "chmod", "644", tmp_js], check=True)
        fd, test_js = tempfile.mkstemp(prefix="status-test-", suffix=".mjs")
        os.close(fd)
        script = f'''import fs from "fs";\nconst tmp = process.env.TMP_JS;\nconst mod = await import(`file://${{tmp}}`);\nconst sessionsPath = process.env.HOME + "/.openclaw/agents/main/sessions/sessions.json";\nconst cfgPath = process.env.HOME + "/.openclaw/openclaw.json";\nconst sessions = JSON.parse(fs.readFileSync(sessionsPath, "utf8"));\nconst cfg = JSON.parse(fs.readFileSync(cfgPath, "utf8"));\nconst sessionKey = {json.dumps(session_key)};\nconst sessionEntry = sessions[sessionKey];\nconst providerModel = (cfg.agents?.defaults?.model?.primary || "openai-codex/gpt-5.4").split("/");\nconst provider = providerModel[0] || "openai-codex";\nconst model = providerModel.slice(1).join("/") || "gpt-5.4";\nconst reply = await mod.__buildStatusReply({{\n  cfg,\n  command: {{ isAuthorizedSender: true, senderId: "cs-patch", channel: "feishu" }},\n  sessionEntry,\n  sessionKey,\n  parentSessionKey: null,\n  sessionScope: "direct",\n  storePath: sessionsPath,\n  provider,\n  model,\n  contextTokens: 0,\n  resolvedThinkLevel: cfg.agents?.defaults?.thinkingDefault || "medium",\n  resolvedVerboseLevel: "off",\n  resolvedReasoningLevel: null,\n  resolvedElevatedLevel: cfg.agents?.defaults?.elevatedDefault || "elevated",\n  resolveDefaultThinkingLevel: async () => cfg.agents?.defaults?.thinkingDefault || "medium",\n  isGroup: false,\n  defaultGroupActivation: () => "disabled"\n}});\nconsole.log(reply.text.split("\\n").find((line) => line.includes("Usage:")) || "NO_USAGE_LINE");\n'''
        pathlib.Path(test_js).write_text(script, encoding="utf-8")
        cmd = ["node", test_js]
        if os.path.exists(PROXYCHAINS_CONF):
            cmd = ["proxychains4", "-q", "-f", PROXYCHAINS_CONF] + cmd
        env = os.environ.copy()
        env["TMP_JS"] = tmp_js
        return subprocess.check_output(cmd, text=True, env=env).strip()
    finally:
        if test_js and os.path.exists(test_js):
            os.unlink(test_js)
        if tmp_js:
            subprocess.run(["sudo", "rm", "-f", tmp_js], check=False)


def compare_usage(expected: str, actual: str) -> bool:
    def normalize(line: str) -> tuple[str, str]:
        if not line:
            return "", ""
        body = line.replace("📊 Usage: ", "", 1)
        main = body.split(" ⏱", 1)[0]
        parts = main.split()
        if len(parts) >= 3:
            return parts[0], parts[1]
        return main, ""
    return normalize(expected) == normalize(actual)


def cmd_status(compact_path: str, session_key: str):
    text = pathlib.Path(compact_path).read_text(encoding="utf-8")
    print(json.dumps({
        "compactPath": compact_path,
        "patched": is_patched(text),
        "sessionKey": session_key,
    }, ensure_ascii=False))


def cmd_verify(compact_path: str, session_key: str):
    _session, profile_id, profile = current_session_and_profile(session_key)
    expected = expected_usage_line(profile)
    actual = actual_status_usage_line(compact_path, session_key)
    ok = compare_usage(expected, actual)
    print(json.dumps({
        "sessionKey": session_key,
        "profileId": profile_id,
        "expectedUsage": expected,
        "actualUsage": actual,
        "match": ok,
    }, ensure_ascii=False))
    if not ok:
        raise SystemExit(2)


def main():
    parser = argparse.ArgumentParser(description="Patch OpenClaw /status usage to bind to current session auth profile.")
    parser.add_argument("action", choices=["status", "apply", "verify"])
    parser.add_argument("--session-key", default="")
    args = parser.parse_args()

    compact_path = find_compact_file()
    session_key = find_session_key(args.session_key or None)

    if args.action == "status":
        cmd_status(compact_path, session_key)
        return
    if args.action == "apply":
        result = apply_patch(compact_path)
        print(json.dumps({**result, "sessionKey": session_key}, ensure_ascii=False))
        return
    if args.action == "verify":
        cmd_verify(compact_path, session_key)
        return


if __name__ == "__main__":
    main()
