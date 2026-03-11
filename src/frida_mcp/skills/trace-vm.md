---
name: trace-vm
description: Use when encountering VM-protected (virtualized/obfuscated) functions that cannot be directly analyzed. Guides human-assisted tracing and AI analysis of trace results.
---

# Trace VM - VM 保护函数分析

## 触发条件
- IDA 反编译结果为 dispatcher/handler 循环（典型 VM 特征）
- 函数逻辑被虚拟化，无法直接理解
- 遇到 VMP、OLLVM handler 等保护方案

## 工作流程

### 1. 识别 VM 保护
通过 ida-mcp 分析，识别 VM 特征：
- 大型 switch-case 或跳转表（handler dispatch）
- 字节码数组引用
- 不符合正常编译器输出的控制流

### 2. 请求人工 Trace
当确认目标被 VM 保护时，指导用户：

```
请对函数 0xXXXX 进行 trace，建议工具：
- unidbg（推荐，可离线模拟执行）
- frida-stalker
- Trace 工具

请将 trace 结果保存到项目目录：
  /Volumes/Realtek/project/agent-frida/traces/trace_XXXX.log

需要记录的信息：
1. 每条指令的地址和操作
2. 寄存器状态变化
3. 内存读写记录
```

### 3. 分析 Trace 结果
用户完成 trace 后：
1. 读取 trace 日志文件
2. 识别 VM 指令模式（opcode → handler 映射）
3. 还原字节码语义
4. 结合 IDA 中的 handler 代码理解每个 opcode 的功能

### 4. 验证还原结果
使用 frida-mcp hook 验证还原的逻辑：
- Hook VM 入口，捕获输入
- Hook VM 出口，捕获输出
- 对比 trace 分析的预期结果与实际结果

## 注意事项
- Trace 文件可能很大，分段分析
- 关注 handler dispatch 逻辑，这是 VM 的核心
- 记录 opcode → handler 的映射关系，方便后续分析同一 VM 保护的其他函数
