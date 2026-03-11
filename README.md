# Frida Agent MCP

AI 驱动的 Android 动态分析工具。通过 MCP (Model Context Protocol) 让 AI 直接操控 Frida，实现自动化逆向分析。

```
AI (Claude) → MCP Server → Frida CLI → zygisk-gadget (手机) → 结果返回
```

## 前提条件

- Python >= 3.10
- Android 手机已 root，安装 [Magisk](https://github.com/topjohnwu/Magisk)
- 安装 [zygisk-gadget](https://github.com/aspect4/zygisk-gadget) Magisk 模块（固定端口 14725）
- ADB 已连接手机

## 安装

```bash
pip install .
```

安装后运行一键配置（注册 MCP + 安装 Skills）：

```bash
frida-mcp-setup
```

或手动配置，在 `~/.claude.json` 中添加：

```json
{
  "mcpServers": {
    "frida-agent": {
      "command": "frida-mcp"
    }
  }
}
```

## MCP Tools

| 工具 | 说明 |
|------|------|
| `connect` | 建立 ADB 端口转发，连接 zygisk-gadget |
| `list_apps` | 列出设备上的第三方应用 |
| `execute` | 注入 Frida JS 脚本到前台应用（支持 `script` 内联 / `script_file` 文件路径） |
| `spawn_and_inject` | 杀死 → 重启 → 注入，一步完成（适用于需要启动时 hook 的场景） |
| `get_messages` | 获取注入脚本的输出（支持分页、自动文件回退） |
| `logcat` | 查看 Android 日志，排查崩溃原因 |
| `launch_app` | 启动指定应用 |
| `kill_app` | 强制停止指定应用 |
| `reconnect` | 重新建立连接（崩溃后恢复） |
| `detach` | 断开当前注入会话 |

## Skills（Claude Code 技能）

安装后可在 Claude Code 中使用：

- **`/reverse-analyze`** — 逆向分析与动态 Hook，结合 IDA 静态分析 + Frida 动态验证
- **`/trace-vm`** — VM 保护函数分析，指导人工 trace 并由 AI 分析结果

## 使用示例

### 基本 Hook 流程

```
用户: hook 淘宝的 Cipher.doFinal 看看加密参数

AI 自动执行:
1. connect()                    — 建立连接
2. spawn_and_inject(            — 启动并注入
     "com.taobao.taobao",
     "Java.perform(function() { ... })"
   )
3. 提示用户触发操作              — "请点击登录按钮"
4. get_messages()               — 获取 hook 结果
5. 分析并展示加密参数和返回值
```

### 结合 IDA 静态分析

```
用户: /reverse-analyze 分析 libsgmain.so 中 0x1234 处的函数

AI 自动执行:
1. IDA MCP 反编译目标函数，分析参数和返回值类型
2. 生成 Frida Hook 脚本
3. spawn_and_inject 注入
4. 交叉验证静态分析和动态结果
```

## 工作原理

本工具使用 **Frida CLI** 而非 frida-python API，通过 `frida -H 127.0.0.1:14725 -F -l script.js -o output.txt` 注入脚本：

- 脚本中的 `send()` 调用自动转换为 `console.log(JSON.stringify())`
- 所有脚本自动包裹 try-catch 防止注入崩溃
- 输出通过 `-o` 标志写入文件，`get_messages` 时停止 frida 进程以刷新文件

## 项目结构

```
src/frida_mcp/
├── server.py       # MCP Server 入口，10 个工具注册
├── connection.py   # Frida CLI 连接管理，进程生命周期
├── executor.py     # 脚本预处理（send 转换、try-catch 包裹）
├── messages.py     # 消息分页、大数据自动文件回退
├── logcat.py       # Android logcat 封装
├── setup.py        # 一键安装配置
└── skills/         # Claude Code 技能模板
```

## License

MIT
