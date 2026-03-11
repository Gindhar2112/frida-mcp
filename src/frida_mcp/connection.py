"""Frida gadget connection management via zygisk-gadget.
Uses frida CLI with -o flag to capture console.log output to file."""

import subprocess
import tempfile
import os
import json
import time


GADGET_PORT = 14725
GADGET_HOST = "127.0.0.1"


class GadgetConnection:
    def __init__(self):
        self._forwarded = False
        self._frida_proc = None
        self._messages: list[dict] = []
        self._script_file: str | None = None
        self._output_file: str | None = None
        self._last_read_pos: int = 0

    @property
    def messages(self) -> list[dict]:
        return self._messages

    def connect(self) -> str:
        """Setup adb port forwarding (only once)."""
        if not self._forwarded:
            result = subprocess.run(
                ["adb", "forward", f"tcp:{GADGET_PORT}", f"tcp:{GADGET_PORT}"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                return f"adb forward failed: {result.stderr.strip()}"
            self._forwarded = True
            return f"Port forwarding established (tcp:{GADGET_PORT})"
        return f"Port forwarding already active (tcp:{GADGET_PORT})"

    def execute_script(self, js_code: str) -> str:
        """Inject script using frida CLI: frida -H host:port -F -l script.js -o output.txt"""
        if not self._forwarded:
            fwd = self.connect()
            if "failed" in fwd.lower():
                return fwd

        self._stop_frida()
        self._messages.clear()
        self._last_read_pos = 0

        # Write script to temp file
        self._script_file = tempfile.mktemp(suffix=".js", prefix="frida_")
        with open(self._script_file, "w") as f:
            f.write(js_code)

        # Create output file
        self._output_file = tempfile.mktemp(suffix=".txt", prefix="frida_out_")

        # Launch: frida -H 127.0.0.1:14725 -F -l script.js -o output.txt
        try:
            self._frida_proc = subprocess.Popen(
                [
                    "frida", "-H", f"{GADGET_HOST}:{GADGET_PORT}",
                    "-F", "-l", self._script_file,
                    "-o", self._output_file,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )

            # Wait briefly to check if frida started OK
            time.sleep(2)
            if self._frida_proc.poll() is not None:
                _, stderr = self._frida_proc.communicate()
                err = stderr.decode().strip()
                return self._diagnose_error(err)

            return "Script injected successfully. Use get_messages to retrieve results after triggering the target."
        except FileNotFoundError:
            return "frida command not found. Make sure frida-tools is installed."
        except Exception as e:
            return f"Script injection failed: {e}"

    def get_collected_messages(self) -> list[dict]:
        """Stop frida to flush output, then read messages from file."""
        # frida -o only writes file on exit, so we must stop it first
        # Use _stop_frida_proc_only to avoid deleting the output file before reading
        self._stop_frida_proc_only()

        if not self._output_file or not os.path.exists(self._output_file):
            return self._messages

        try:
            with open(self._output_file, "r", encoding="utf-8", errors="replace") as f:
                f.seek(self._last_read_pos)
                new_content = f.read()
                self._last_read_pos = f.tell()

            if new_content.strip():
                for line in new_content.strip().splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        self._messages.append(msg)
                    except json.JSONDecodeError:
                        self._messages.append({"type": "log", "content": line})
        except Exception:
            pass
        return self._messages

    def detach(self) -> str:
        """Stop the frida process."""
        self._stop_frida()
        return "Detached."

    def reconnect(self) -> str:
        """Stop frida, re-establish forwarding."""
        self._stop_frida()
        self._forwarded = False
        return self.connect()

    def spawn_and_inject(self, package: str, js_code: str) -> str:
        """Kill app, relaunch, inject script - one step."""
        self._stop_frida()

        subprocess.run(
            ["adb", "shell", "am", "force-stop", package],
            capture_output=True, text=True
        )
        time.sleep(1)

        launch = subprocess.run(
            ["adb", "shell", "monkey", "-p", package, "-c",
             "android.intent.category.LAUNCHER", "1"],
            capture_output=True, text=True
        )
        if launch.returncode != 0:
            return f"Launch failed: {launch.stderr.strip()}"

        if not self._forwarded:
            fwd = self.connect()
            if "failed" in fwd.lower():
                return fwd

        time.sleep(3)
        return self.execute_script(js_code)

    def launch_app(self, package: str) -> str:
        """Launch an app by package name via adb."""
        result = subprocess.run(
            ["adb", "shell", "monkey", "-p", package, "-c",
             "android.intent.category.LAUNCHER", "1"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return f"Launch failed: {result.stderr.strip()}"
        return f"Launched {package}"

    def kill_app(self, package: str) -> str:
        """Force stop an app by package name via adb."""
        self._stop_frida()
        result = subprocess.run(
            ["adb", "shell", "am", "force-stop", package],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return f"Kill failed: {result.stderr.strip()}"
        return f"Killed {package}"

    def list_applications(self) -> list[dict]:
        """List third-party apps via adb."""
        result = subprocess.run(
            ["adb", "shell", "pm", "list", "packages", "-3"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return [{"error": result.stderr.strip()}]
        packages = []
        for line in result.stdout.strip().splitlines():
            pkg = line.replace("package:", "").strip()
            if pkg:
                packages.append({"package": pkg})
        return packages

    def _diagnose_error(self, err: str) -> str:
        """Analyze frida error and return actionable diagnosis."""
        diagnosis = f"Frida failed.\nRaw error: {err}\n\nDiagnosis: "

        if "connection closed" in err.lower() or "connection refused" in err.lower():
            # Check if app is running
            app_check = subprocess.run(
                ["adb", "shell", "pidof", "com.taobao.taobao"],
                capture_output=True, text=True
            )
            if not app_check.stdout.strip():
                diagnosis += "Target app is NOT running. Use launch_app to start it first, then retry."
            else:
                diagnosis += (
                    f"App is running (PID: {app_check.stdout.strip()}) but gadget connection failed. "
                    "Possible causes: (1) Gadget not yet initialized - wait and retry. "
                    "(2) Gadget crashed - use kill_app then launch_app to restart."
                )
        elif "unable to connect" in err.lower() or "timed out" in err.lower():
            # Check adb connection
            adb_check = subprocess.run(
                ["adb", "devices"], capture_output=True, text=True
            )
            if "device" not in adb_check.stdout:
                diagnosis += "No Android device connected via USB. Check USB connection."
            else:
                diagnosis += (
                    "Device connected but gadget unreachable. "
                    "Check: (1) Is the Zygisk module enabled in Magisk? "
                    "(2) Try: adb forward tcp:14725 tcp:14725"
                )
        elif "failed to attach" in err.lower():
            diagnosis += (
                "Could not attach to process. "
                "The app may have crashed or the gadget is not loaded. "
                "Use kill_app + launch_app to restart, then retry."
            )
        elif "script" in err.lower() and ("error" in err.lower() or "exception" in err.lower()):
            diagnosis += (
                "Script execution error. The JavaScript code has a runtime error. "
                "Check the script logic and try again."
            )
        else:
            diagnosis += (
                "Unknown error. Try: (1) kill_app + launch_app to restart the app. "
                "(2) reconnect to re-establish forwarding. "
                "(3) Check logcat for crash details."
            )

        return diagnosis

    def _stop_frida_proc_only(self):
        """Terminate frida process only, keep temp files for reading."""
        if self._frida_proc:
            try:
                self._frida_proc.terminate()
                self._frida_proc.wait(timeout=5)
            except Exception:
                try:
                    self._frida_proc.kill()
                except Exception:
                    pass
            self._frida_proc = None

    def _stop_frida(self):
        """Terminate the running frida process and clean up all temp files."""
        was_running = self._frida_proc is not None
        self._stop_frida_proc_only()
        if self._script_file and os.path.exists(self._script_file):
            try:
                os.unlink(self._script_file)
            except Exception:
                pass
            self._script_file = None
        if self._output_file and os.path.exists(self._output_file):
            try:
                os.unlink(self._output_file)
            except Exception:
                pass
            self._output_file = None
        # Allow gadget to fully release previous session
        if was_running:
            time.sleep(1)
