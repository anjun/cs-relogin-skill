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

## 能力说明

- 用户发 `cs relogin`：自动执行并返回最新 OAuth 登录 URL
- 用户粘贴 callback URL/code：自动完成 `cs relogin '<callback>'`
- 完成后回报 active profile / account
- 失败时优先返回原始错误，便于快速排障

## 安装

### 方式 A：目录安装
将 `skills/cs-relogin` 放入：

- `~/.openclaw/skills/`

### 方式 B：打包安装
使用 `dist/cs-relogin.skill` 导入。

## 常见命令

- `cs relogin`
- `cs relogin '<callback-url-or-code>'`
- `cs relogin status`
- `cs status`

## 目录结构

```text
skills/
  cs-relogin/
    SKILL.md

dist/
  cs-relogin.skill
```

## 安全说明

- 仅编排 Auth 登录/切号流程，不改业务代码
- 不应暴露完整 token 等敏感信息
