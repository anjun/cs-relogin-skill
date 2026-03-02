# cs-relogin

<p align="center">
  <a href="#中文">中文</a> · <a href="#english">English</a>
</p>

---

## 中文

**cs-relogin 是一个给 OpenClaw 用的技能，核心用途是：**

> 把 **ChatGPT Auth（Codex OAuth）登录/切号** 这套麻烦流程交给模型执行。

### 为什么需要它（痛点）

1. **多账号切换太烦**：手动跑命令、开浏览器、贴 callback URL、再检查状态，步骤碎且容易漏。
2. **某鱼号容易掉线**：需要频繁重新登录，重复劳动。
3. **失败不好排查**：不知道该看 `cs relogin status` 还是 `cs status`。

### 这个技能做什么

- 用户发 `cs relogin` → 自动执行并返回新的 OAuth 登录链接
- 用户贴 callback URL/code → 自动完成 `cs relogin '<callback>'`
- 登录后自动回报当前 active account / profile 状态
- 失败时优先返回原始错误输出，便于定位

### 目录结构

```text
skills/
  cs-relogin/
    SKILL.md

dist/
  cs-relogin.skill
```

### 安装方式

#### 方式 A：目录安装
把 `skills/cs-relogin` 放进：

- `~/.openclaw/skills/`

#### 方式 B：打包安装
使用 `dist/cs-relogin.skill` 导入安装。

### 常见用法

- `cs relogin`
- 粘贴浏览器回调 URL：`http://localhost:1455/auth/callback?...`
- `cs relogin status`
- `cs status`

### 安全说明

- 仅编排登录/切号流程，不改业务代码
- 不应输出完整 token 等敏感信息

---

## English

**cs-relogin is an OpenClaw skill focused on one thing:**

> Let the model handle **ChatGPT Auth (Codex OAuth) login/account switching** end-to-end.

### Pain points solved

1. **Multi-account switch is tedious** (command + browser auth + callback URL + status checks).
2. **Frequent re-login for Xianyu account** due to session drops.
3. **Troubleshooting is inconsistent** when login fails.

### What it does

- Runs `cs relogin` and returns a fresh OAuth login URL
- Accepts pasted callback URL/code and completes relogin
- Reports active profile/account after completion
- Surfaces raw command errors first for debugging

### Install

- Folder install: put `skills/cs-relogin` under `~/.openclaw/skills/`
- Package install: import `dist/cs-relogin.skill`

### Typical commands

- `cs relogin`
- callback URL: `http://localhost:1455/auth/callback?...`
- `cs relogin status`
- `cs status`
