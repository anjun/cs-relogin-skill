#!/usr/bin/env bash
set -euo pipefail

CS_RELOGIN_REF="${CS_RELOGIN_REF:-v1.2.1}"
REPO_RAW_DEFAULT="https://raw.githubusercontent.com/anjun/cs-relogin-skill/${CS_RELOGIN_REF}"
REPO_RAW="${CS_RELOGIN_RAW_BASE:-$REPO_RAW_DEFAULT}"
INSTALL_DIR="${CS_RELOGIN_INSTALL_DIR:-$HOME/.local/bin}"
SHARE_DIR="${CS_RELOGIN_SHARE_DIR:-$HOME/.local/share/cs-relogin}"

mkdir -p "$INSTALL_DIR" "$SHARE_DIR"

curl -fsSL "$REPO_RAW/bin/chatgptswitch" -o "$INSTALL_DIR/chatgptswitch"
curl -fsSL "$REPO_RAW/bin/cs" -o "$INSTALL_DIR/cs"
curl -fsSL "$REPO_RAW/scripts/patch_openclaw_status_usage.py" -o "$SHARE_DIR/patch_openclaw_status_usage.py"
chmod +x "$INSTALL_DIR/chatgptswitch" "$INSTALL_DIR/cs" "$SHARE_DIR/patch_openclaw_status_usage.py"

if ! echo ":$PATH:" | grep -q ":$INSTALL_DIR:"; then
  echo "[WARN] $INSTALL_DIR is not in PATH"
  echo "Add this line to your shell profile (~/.bashrc or ~/.zshrc):"
  echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
fi

echo "[OK] Installed: $INSTALL_DIR/chatgptswitch"
echo "[OK] Installed: $INSTALL_DIR/cs"
echo "[OK] Installed: $SHARE_DIR/patch_openclaw_status_usage.py"

echo
cs_bin="$(command -v cs || true)"
if [ -n "$cs_bin" ]; then
  echo "[OK] cs detected at: $cs_bin"
  echo "Try: cs relogin status"
else
  echo "[INFO] Open a new shell then run: cs relogin status"
fi
