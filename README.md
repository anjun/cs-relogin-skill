# cs-relogin（OpenClaw 技能）

> 默认中文文档。English: [README.en.md](./README.en.md)

一个把 `cs relogin` 登录/切号流程交给模型自动处理的技能。

## 解决什么痛点

1. **多账号切换麻烦**：手动执行命令、复制回调 URL、确认状态，步骤碎。
2. **某鱼号容易掉线**：需要频繁重新登录，重复操作浪费时间。
3. **排障不稳定**：失败时不知道看哪条命令和状态。

## 能做什么

- 收到 `cs relogin` 时自动触发登录流程
- 自动识别并处理你粘贴的 callback URL/code
- 登录完成后检查并回报当前账号状态
- 失败时优先返回原始错误，方便定位

## 目录结构

```text
skills/
  cs-relogin/
    SKILL.md

dist/
  cs-relogin.skill
```

## 快速使用

### 方式 A：手动安装（开发目录）
把 `skills/cs-relogin` 放到你的 skills 目录，例如：

- `~/.openclaw/skills/`

### 方式 B：用打包文件安装
使用 `dist/cs-relogin.skill` 进行安装（按你的 OpenClaw 安装方式导入）。

## 典型对话

- `cs relogin`
- 粘贴浏览器回调 URL（`http://localhost:1455/auth/callback?...`）
- `cs relogin status`
- `cs status`

## 说明

- 本技能只负责 **登录/切号流程编排**，不改你的业务逻辑。
- 不会主动暴露 token 等敏感信息。
