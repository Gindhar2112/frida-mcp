---
name: reverse-analyze
description: Use when analyzing Android app functions, hooking functions, or performing reverse engineering. Combines static analysis (IDA/JADX) with dynamic analysis (Frida). Covers both quick hooks and full analysis workflows.
---

# Reverse Analyze - 逆向分析与动态 Hook

## 触发条件
- 需要 hook 某个函数观察参数和返回值
- 需要验证函数的实际行为
- 静态分析结果需要动态确认
- 分析加密、签名、协议等需要真实数据的场景
- 已知函数地址或 Java 类名/方法名，需要快速 hook

## 工作流程

### 1. 静态分析（确定目标）
- **Java 层**：使用 jadx-mcp 反编译，找到目标类和方法
- **Native 层**：使用 ida-mcp 分析 so 库，拿到函数地址和签名
- 记录关键信息：函数地址、参数类型、返回值类型

### 2. 自动生成 Hook 脚本

**Java 层 Hook：**
```javascript
Java.perform(function() {
    var cls = Java.use("com.example.TargetClass");
    // 处理重载：cls.method.overload("java.lang.String", "int")
    cls.targetMethod.implementation = function(arg1, arg2) {
        send({method: "targetMethod", args: [arg1.toString(), arg2.toString()]});
        var ret = this.targetMethod(arg1, arg2);
        send({method: "targetMethod", ret: ret.toString()});
        return ret;
    };
});
```

**Native 层 Hook：**
```javascript
Interceptor.attach(Module.findBaseAddress("libtarget.so").add(0x1234), {
    onEnter: function(args) {
        send({func: "sub_1234", arg0: args[0].toInt32(), arg1: args[1]});
    },
    onLeave: function(retval) {
        send({func: "sub_1234", ret: retval.toInt32()});
    }
});
```

**常用数据格式化：**
```javascript
// Buffer 转 hex
function bufToHex(buf) {
    return Array.from(new Uint8Array(buf)).map(b => ('0'+b.toString(16)).slice(-2)).join('');
}
// 读取指针指向的字符串
function readStr(ptr) {
    try { return ptr.readUtf8String(); } catch(e) { return ptr.toString(); }
}
// 打印 hexdump
function hexdump(ptr, len) {
    return hexdump(ptr, {offset: 0, length: len, header: false, ansi: false});
}
```

### 3. 注入与触发
1. 使用 `spawn_and_inject(package, script)` 一步完成（需要启动时 hook）
2. 或 `execute(script)` 注入到已运行的 App（支持 script_file 参数加载大脚本）
3. 告诉用户需要触发什么操作（如"请点击登录按钮"）
4. 用户确认后 → `get_messages()` 获取结果

### 4. 分析与迭代
- 将动态结果与 IDA/JADX 的静态分析交叉对比
- 验证参数和返回值是否符合预期
- 如果是加密函数，展示输入输出的 hex dump
- 如果是网络请求，展示 URL 和 body
- 如有差异，调整脚本，重复注入验证
- 遇到崩溃 → `logcat` 查看原因 → 修改脚本 → 重试

## 注意事项
- Native 层使用相对偏移（`Module.findBaseAddress().add(offset)`），不要用绝对地址
- Java 层优先用类名+方法名，更稳定
- Native 层注意 thumb/arm 指令集差异（thumb 地址需要 +1）
- 对于频繁调用的函数，在脚本中加计数器避免消息爆炸
- Java 层 hook 需要 App 已经加载目标类
- Native 层注意 so 库是否已加载（可用 `Module.ensureInitialized()`）
