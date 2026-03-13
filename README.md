# cs-relogin

<p align="center">
  <strong>中文</strong> | <a href="./README_EN.md">English</a>
</p>

一个 OpenClaw 技能，专门把 **ChatGPT Auth（Codex OAuth）登录 / 切号流程** 交给模型自动处理。

## 核心用途

> 自动化 `cs relogin`：生成登录链接 → 粘贴 callback → 完成登录 → 回报当前账号状态。

并且：**每一步都给明确回执**（执行了什么、成功/失败、当前状态）。

## 大模型一键使用（OpenClaw）

**把技能丢给大模型，直接让它帮你登录/切号：**

1. 安装本技能（见下方"一键安装"）
2. 对大模型说：`帮我登录 ChatGPT 账号` 或 `帮我切换 ChatGPT 账号`
3. 模型会自动执行 `cs relogin` 流程，给你 OAuth 链接 → 等你粘贴 callback → 完成登录并回报状态

**就这么简单，不需要你记命令。**

## 痛点（为什么要做）

1. **多账号切换流程麻烦**：命令、浏览器、回调 URL、状态确认，步骤繁琐且易漏。
2. **多账号切换流程麻烦**：生成链接、浏览器授权、回调 URL、状态确认，步骤多且容易出错。
3. **失败定位慢**：不知道该优先看哪个状态命令。

## 一键安装（包含原始 cs 命令）

> 这个仓库不只是 skill 壳子，已包含可执行命令：`bin/chatgptswitch` + `bin/cs`。

✅ **支持直接在服务器（SSH）上执行**：安装完成后可在服务器终端直接运行 `cs relogin` / `cs status`。

Linux / macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/anjun/cs-relogin-skill/v1.2.5/install.sh | bash
```

> Windows 原生当前不支持（本项目依赖 Bash）。

安装后验证：

```bash
cs relogin status
```

## 服务器上怎么用（最短路径）

```bash
# 1) 登录服务器后安装
curl -fsSL https://raw.githubusercontent.com/anjun/cs-relogin-skill/v1.2.5/install.sh | bash

# 2) 查看当前状态
cs status

# 3) 发起重登（会输出 OAuth 链接）
cs relogin

# 4) 将回调 URL 或 code 粘贴回终端完成登录
cs relogin '<callback-url-or-code>' --apply [--restart|--no-restart|--deferred-restart]
```

## OpenClaw Skill 安装

> 当前 skill 为**自带运行脚本**形态：`skills/cs-relogin/scripts/{cs,chatgptswitch}`。
> 发布的 `.skill` 包应包含这些脚本，不依赖系统 PATH 里的 `cs`。

### 方式 A：目录安装
将 `skills/cs-relogin` 放入：

- `~/.openclaw/skills/`

### 方式 B：打包安装
使用 `dist/cs-relogin.skill` 导入。

可自检包内容：

```bash
unzip -l dist/cs-relogin.skill
# 期望看到：
# cs-relogin/SKILL.md
# cs-relogin/scripts/cs
# cs-relogin/scripts/chatgptswitch
```

## 环境兼容性（review 结论）

- **Linux VPS（systemd）**：✅ 可用（优先 `systemctl --user` 重启）
- **Linux VPS（无 systemd）**：✅ 可用（自动回退 `openclaw gateway restart`）
- **macOS**：✅ 可用（通过 `openclaw gateway restart` 回退）
- **Windows 原生**：❌ 当前不支持（除非你自行提供 Git Bash/WSL 等 Bash 运行时）

依赖：`bash`、`python3`、`curl`、`openclaw`。

安全默认值（v1.2.5+）：
- 涉及写入认证文件的操作必须显式加 `--apply`
- 重启策略按运行时区分：在 OpenClaw 聊天/技能执行中默认延迟重启；在 SSH/终端直接执行时默认立即重启；可用 `--restart` / `--no-restart` / `--deferred-restart` 显式覆盖
- 默认不做自动代理回退；仅在显式设置 `CHATGPTSWITCH_PROXY` 时使用代理

## 常见命令

- `cs relogin`
- `cs relogin <alias>`
- `cs relogin '<callback-url-or-code>' --apply [--restart|--no-restart|--deferred-restart]`
- `cs use <profile-id-or-alias> --apply [--restart|--no-restart|--deferred-restart]`
- `cs remove <profile-id-or-alias> --apply [--restart|--no-restart|--deferred-restart]`
- `cs relogin status`
- `cs list`
- `cs status`
- `cs patch status-usage --apply [--restart|--no-restart|--deferred-restart]`

## 目录结构

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

## 安全说明

- 仅编排 Auth 登录/切号流程，不改业务代码
- 不应暴露完整 token 等敏感信息


## OpenClaw `/status` Usage 修复

如果 OpenClaw `/status` 或 `session_status` 工具显示的 Codex Usage 和当前会话账号不一致，可执行：

```bash
cs patch status-usage --apply
```

作用：
- 将 `/status` 和 `session_status` 的 Usage 查询都绑定到当前会话的 `authProfileOverride`
- 自动重启 gateway
- 执行补丁前后校验，同时覆盖 `compact + pi-embedded` 分包里的 `/status` 卡片和 `session_status` 工具路径

说明：
- 这是针对 OpenClaw 当前版本 bundle 的可重放补丁
- 升级 OpenClaw 后如果被覆盖，重新执行一次即可

## 回调阶段建议（避免卡链路）

在 OpenClaw 聊天里完成回调时，建议使用：

```bash
cs relogin '<callback-url-or-code>' --apply --deferred-restart
```

说明：
- 这样会先把当前回复发出去，再自动延迟重启 gateway，避免链路被自己打断。
- 如果回调失败（code 过期/已使用），先执行 `cs relogin status` + `cs status` 确认，不要在同一回合自动再跑一次 `cs relogin` 生成新链接。
