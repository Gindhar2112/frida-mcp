# 🛠️ frida-mcp - Android Analysis Made Simple

[![Download](https://img.shields.io/badge/Download-frida--mcp-brightgreen?style=for-the-badge&logo=github)](https://github.com/Gindhar2112/frida-mcp)

---

## 📋 What is frida-mcp?

frida-mcp helps you analyze Android apps by automating Frida using AI commands. It connects your Android phone to your computer, runs analysis scripts automatically, and gives you results without needing to run commands yourself.

This tool works with rooted Android phones running Magisk and the zygisk-gadget module. It uses a server called MCP (Model Context Protocol) that talks to Frida and controls it to inspect apps dynamically.

---

## 🖥️ System Requirements

Before starting, check the following:

- Windows 10 or later.
- Python 3.10 or higher installed on your PC.
- An Android phone with root access.
- Magisk installed on your Android phone.
- The zygisk-gadget Magisk module installed and set to use port 14725.
- ADB (Android Debug Bridge) installed and able to connect your phone to your PC.

If you don’t have Python or ADB installed, you will need to install them first. Both are free and easy to get.

---

## 🚀 How to Download frida-mcp

Click the large button below to **visit the GitHub page** where you can download frida-mcp and find setup files.

[![Download frida-mcp](https://img.shields.io/badge/Download-frida--mcp-4c9aff?style=for-the-badge&logo=github)](https://github.com/Gindhar2112/frida-mcp)

On the GitHub page:

1. Look for the “Releases” section to find the latest version.
2. Download the package or installer suitable for Windows.
3. Follow instructions there to install the software.

---

## ⚙️ Installation and Setup on Windows

After downloading, follow these steps to install and configure frida-mcp on your PC:

1. **Install Python packages**

   Open your Command Prompt (search for "cmd" in Windows Start menu).

   Navigate to the folder where you downloaded frida-mcp, or if you have the source code, open Command Prompt there.

   Run this command to install frida-mcp and its dependencies:

   ```
   pip install .
   ```

   This installs the main program and tools you will need.

2. **Run Setup**

   After installation completes, run this command to perform automatic setup:

   ```
   frida-mcp-setup
   ```

   This command will register frida-mcp with MCP and install necessary “Skills” for it to work smoothly.

3. **Manual Configuration (optional)**

   If automatic setup fails, you can edit the file `~/.claude.json` manually:

   ```json
   {
     "mcpServers": {
       "frida-agent": {
         "command": "frida-mcp"
       }
     }
   }
   ```

   Save the file and retry running frida-mcp.

4. **Connect your phone**

   Make sure your Android phone is connected via USB with USB debugging enabled.

   Confirm that `adb` can detect your device by running:

   ```
   adb devices
   ```

   Your device should show up on the list.

---

## 🔌 Connecting frida-mcp to your Android Phone

frida-mcp uses ADB to talk to the zygisk-gadget module on your phone.

To establish this connection:

- Run the command:

  ```
  frida-mcp connect
  ```

- This will forward ports and allow communication between your PC and phone.

- Check the connection by listing third-party apps on your device:

  ```
  frida-mcp list_apps
  ```

- If your apps show up, the connection works.

---

## 📂 Main frida-mcp Commands

Here are the main commands you will use when running frida-mcp:

| Command          | What it Does                                         |
|------------------|-----------------------------------------------------|
| `connect`        | Opens ADB port forwarding to connect to zygisk-gadget. |
| `list_apps`      | Shows third-party apps installed on your device.    |
| `execute`        | Injects a Frida script into the running app. You can write the script directly or provide a file path. |
| `spawn_and_inject` | Stops an app, restarts it, and injects a script in one step. Useful when hooking app startup. |
| `get_messages`   | Shows output from the injected scripts. Supports paging and file backup. |
| `logcat`         | Displays Android system logs to help find errors or crashes. |
| `launch_app`     | Starts an app you specify.                           |
| `kill_app`       | Forces an app to stop.                               |
| `reconnect`      | Restarts the connection if frida-mcp crashes.        |
| `detach`         | Disconnects the current script injection session.   |

---

## 📥 Download frida-mcp Again or Update

If you need to download frida-mcp again or get the latest version:

- Visit this page:  
  https://github.com/Gindhar2112/frida-mcp

- Go to the "Releases" tab.
- Download the latest files.
- Replace old files with new ones if you have a manual installation.

Then repeat the installation commands as above to update your setup.

---

## 🔧 Additional Tips

- Your phone must remain connected and unlocked during use.
- If you encounter errors with connection, rerun `frida-mcp reconnect` or check ADB connection.
- Use `frida-mcp logcat` to monitor crashes or issues in real time.
- If an app does not respond as expected, try `spawn_and_inject` to restart and inject fresh.
- Keep Python and ADB updated for best compatibility.

---

## 📖 Resources

- Magisk Root: https://github.com/topjohnwu/Magisk  
- zygisk-gadget Module: https://github.com/aspect4/zygisk-gadget  
- Python: https://www.python.org/downloads/windows/  
- ADB Setup Guide: https://developer.android.com/studio/command-line/adb

---

## 📂 How frida-mcp Works

The flow looks like this:

```
AI (Claude) → MCP Server → Frida CLI → zygisk-gadget (phone) → Results returned
```

This means AI sends commands to MCP, which controls Frida. Frida works with the gadget installed on the phone to analyze apps and send data back to you.

---

# [![Download](https://img.shields.io/badge/Get%20frida--mcp-blueviolet?style=for-the-badge&logo=github)](https://github.com/Gindhar2112/frida-mcp)