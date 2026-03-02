# cs-relogin

<p align="center">
  <strong>中文</strong> | <a href="./README_EN.md">English</a>
</p>

一个 OpenClaw 技能，专门把 **ChatGPT Auth（Codex OAuth）登录 / 切号流程** 交给模型自动处理。

## 核心用途

> 自动化 `cs relogin`：生成登录链接 → 粘贴 callback → 完成登录 → 回报当前账号状态。

## 痛点（为什么要做）

1. **多账号切换流程麻烦**：命令、浏览器、回调 URL、状态确认，步骤繁琐且易漏。
2. **某鱼号容易掉线**：需要频繁重新登录，重复操作浪费时间。
3. **失败定位慢**：不知道该优先看哪个状态命令。

## 一键安装（包含原始 cs 命令）

> 这个仓库不只是 skill 壳子，已包含可执行命令：`bin/chatgptswitch` + `bin/cs`。

Linux / macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/anjun/cs-relogin-skill/master/install.sh | bash
```

Windows（PowerShell，要求有 Git Bash 或 WSL 的 `bash`）：

```powershell
iwr -useb https://raw.githubusercontent.com/anjun/cs-relogin-skill/master/install.sh | bash
```

安装后验证：

```bash
cs relogin status
```

## OpenClaw Skill 安装

### 方式 A：目录安装
将 `skills/cs-relogin` 放入：

- `~/.openclaw/skills/`

### 方式 B：打包安装
使用 `dist/cs-relogin.skill` 导入。

## 环境兼容性（review 结论）

- **Linux VPS（systemd）**：✅ 可用（优先 `systemctl --user` 重启）
- **Linux VPS（无 systemd）**：✅ 可用（自动回退 `openclaw gateway restart`）
- **macOS**：✅ 可用（通过 `openclaw gateway restart` 回退）
- **Windows 原生**：❌ 当前不支持（除非你自行提供 Git Bash/WSL 等 Bash 运行时）

依赖：`bash`、`python3`、`curl`、`openclaw`。

## 常见命令

- `cs relogin`
- `cs relogin '<callback-url-or-code>'`
- `cs relogin status`
- `cs status`

## 目录结构

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

## 安全说明

- 仅编排 Auth 登录/切号流程，不改业务代码
- 不应暴露完整 token 等敏感信息
