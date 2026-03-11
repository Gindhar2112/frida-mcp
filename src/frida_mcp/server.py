"""Frida MCP Server - AI-driven dynamic analysis tool."""

from mcp.server.fastmcp import FastMCP
from frida_mcp.connection import GadgetConnection
from frida_mcp.executor import wrap_script, validate_script
from frida_mcp.messages import get_messages
from frida_mcp.logcat import get_logcat

mcp = FastMCP("frida-agent")
conn = GadgetConnection()


@mcp.tool()
def connect() -> str:
    """Connect to the Frida gadget on the device.
    Performs adb port forwarding (tcp:14725) and connects to the zygisk-gadget.
    Call this before any other operation."""
    return conn.connect()


@mcp.tool()
def list_apps() -> list[dict]:
    """List running applications on the connected device.
    Returns application identifier, name, and PID."""
    return conn.list_applications()


@mcp.tool()
def execute(script: str = "", script_file: str = "") -> str:
    """Inject a Frida JavaScript script into the frontmost application.
    The script is automatically wrapped with try-catch for safety.
    Returns immediately after injection - use get_messages() to retrieve results
    after the user has triggered the target functionality.

    Args:
        script: Frida JavaScript code to inject. Use send() to return data.
        script_file: Path to a .js file to inject. Use this for large scripts instead of script parameter.
    """
    if script_file:
        import os
        if not os.path.exists(script_file):
            return f"Script file not found: {script_file}"
        with open(script_file, "r", encoding="utf-8") as f:
            script = f.read()

    if not script:
        return "Provide either script or script_file parameter."

    # Validate
    error = validate_script(script)
    if error:
        return f"Script validation failed: {error}"

    # Wrap with try-catch
    wrapped = wrap_script(script)

    # Execute
    return conn.execute_script(wrapped)


@mcp.tool()
def get_messages(
    limit: int = 50,
    offset: int = 0,
    save_to_file: bool = False,
) -> dict:
    """Get messages collected from the injected script's send() calls.
    Call this after the user has triggered the target functionality.

    Args:
        limit: Maximum number of messages to return (default 50).
        offset: Skip first N messages for pagination.
        save_to_file: If True, save all messages to a JSON file and return the path.
    """
    from frida_mcp.messages import get_messages as _get_messages
    # Refresh messages from log file
    conn.get_collected_messages()
    return _get_messages(conn.messages, limit=limit, offset=offset, save_to_file=save_to_file)


@mcp.tool()
def logcat(
    filter: str | None = None,
    lines: int = 100,
    clear: bool = False,
) -> str:
    """Get Android logcat output. Useful for debugging crashes after script injection.

    Args:
        filter: Optional filter string (case-insensitive match on each line).
        lines: Number of recent lines to fetch (default 100).
        clear: If True, clear logcat buffer before fetching.
    """
    return get_logcat(filter_expr=filter, lines=lines, clear=clear)


@mcp.tool()
def spawn_and_inject(package: str, script: str = "", script_file: str = "") -> str:
    """Kill app, relaunch, connect, and inject script in one step.
    Use this when you need to hook early initialization (e.g. onCreate, static initializers).
    Equivalent to: kill_app -> launch_app -> connect -> execute.

    Args:
        package: The app package name (e.g. com.taobao.taobao).
        script: Frida JavaScript code to inject at startup. Use send() to return data.
        script_file: Path to a .js file to inject. Use this for large scripts.
    """
    if script_file:
        import os
        if not os.path.exists(script_file):
            return f"Script file not found: {script_file}"
        with open(script_file, "r", encoding="utf-8") as f:
            script = f.read()

    if not script:
        return "Provide either script or script_file parameter."

    error = validate_script(script)
    if error:
        return f"Script validation failed: {error}"
    wrapped = wrap_script(script)
    return conn.spawn_and_inject(package, wrapped)


@mcp.tool()
def launch_app(package: str) -> str:
    """Launch an Android app by package name.

    Args:
        package: The app package name (e.g. com.example.app).
    """
    return conn.launch_app(package)


@mcp.tool()
def kill_app(package: str) -> str:
    """Force stop an Android app by package name.

    Args:
        package: The app package name (e.g. com.example.app).
    """
    return conn.kill_app(package)


@mcp.tool()
def reconnect() -> str:
    """Reconnect to the gadget after an app crash.
    Detaches current session, re-establishes adb forwarding, and reconnects.
    After reconnect, restart the target app and call execute() again."""
    return conn.reconnect()


@mcp.tool()
def detach() -> str:
    """Detach from the current session and unload any injected scripts."""
    return conn.detach()


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
