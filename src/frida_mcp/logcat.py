"""Android logcat wrapper."""

import subprocess


def get_logcat(
    filter_expr: str | None = None,
    lines: int = 100,
    clear: bool = False,
) -> str:
    """Get Android logcat output."""
    if clear:
        subprocess.run(["adb", "logcat", "-c"], capture_output=True)

    cmd = ["adb", "logcat", "-d", "-t", str(lines)]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    if result.returncode != 0:
        return f"logcat failed: {result.stderr.strip()}"

    output = result.stdout

    if filter_expr:
        filtered_lines = [
            line for line in output.splitlines()
            if filter_expr.lower() in line.lower()
        ]
        return "\n".join(filtered_lines) if filtered_lines else f"No lines matching '{filter_expr}'."

    return output
