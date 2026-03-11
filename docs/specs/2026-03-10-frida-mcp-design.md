# Frida MCP Server 设计文档

## 概述

一个轻量级 MCP Server，封装 Frida 的核心功能，让 AI 能无障碍地进行动态分析。配合 ida-mcp（Native分析）和 jadx-mcp（Java分析）形成完整的 Android 逆向工作流。

## 架构

```
AI (Claude)
    ↓ MCP 协议
frida-agent MCP Server (Python)
    ↓ frida-python
adb forward tcp:14725 → 手机端 zygisk-gadget
```

## 设备连接方式

- 使用 zygisk-gadget 模块（面具模块），非标准 frida-server
- 固定端口：14725
- 连接流程：`adb forward tcp:14725 tcp:14725` → 启动App → `frida -H 127.0.0.1:14725 -F`

## MCP 工具清单（7个）

| 工具 | 参数 | 职责 |
|------|------|------|
| `connect` | 无 | adb forward + 连接 gadget |
| `list_apps` | 无 | 列出运行中的进程 |
| `execute` | `script` | 注入JS脚本，自动try-catch包装，立即返回 |
| `get_messages` | `limit`, `offset`, `save_to_file` | 获取 send() 积累的消息 |
| `logcat` | `filter`, `lines`, `clear` | 查看 Android 日志 |
| `reconnect` | 无 | App崩溃后快速恢复（重新adb forward + 连接） |
| `detach` | 无 | 断开连接 |

## 安全机制

- **脚本包装**：自动给 AI 生成的 JS 脚本加 try-catch，错误通过 send() 返回
- **崩溃恢复**：reconnect 工具一键重连
- **消息管理**：分页获取 + 大消息文件降级（>64KB 写入文件）

## 消息处理策略

- 消息量小（< 4KB）：直接返回
- 消息量中（4KB-64KB）：分页获取（limit/offset）
- 消息量大（> 64KB）：写入文件，返回文件路径 + 摘要

## Skills 技能

| Skill | 触发场景 | 工具组合 |
|-------|---------|---------|
| `reverse-analyze` | 动静态结合分析 | jadx + ida + frida |
| `trace-vm` | 遇到 VM 保护 | ida + frida + 人工协助 |
| `auto-hook` | 快速 hook 一个函数 | jadx/ida + frida |

## 技术栈

- Python 3.10+
- frida-python
- mcp SDK (Python)
- subprocess (adb 调用)

## 项目结构

```
agent-frida/
├── src/frida_mcp/
│   ├── __init__.py
│   ├── server.py          # MCP Server 主入口
│   ├── connection.py      # gadget 连接管理
│   ├── executor.py        # 脚本执行 + try-catch 包装
│   ├── messages.py        # 消息收集 + 分页 + 文件降级
│   └── logcat.py          # logcat 封装
├── skills/
│   ├── reverse-analyze.md
│   ├── trace-vm.md
│   └── auto-hook.md
├── docs/specs/
│   └── 2026-03-10-frida-mcp-design.md
└── pyproject.toml
```
