"""Setup script to install skills and MCP config for Claude Code."""

import os
import shutil
import json
from pathlib import Path
from importlib import resources


def main():
    home = Path.home()

    # 1. Install skills to ~/.claude/commands/
    commands_dir = home / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    skills_dir = Path(__file__).parent / "skills"
    if skills_dir.exists():
        for skill_file in skills_dir.glob("*.md"):
            dest = commands_dir / skill_file.name
            shutil.copy2(skill_file, dest)
            print(f"Installed skill: {skill_file.name} -> {dest}")
    else:
        print("Warning: skills directory not found, skipping skill installation.")

    # 2. Add frida-agent to global ~/.claude.json
    claude_json = home / ".claude.json"
    if claude_json.exists():
        with open(claude_json, "r") as f:
            config = json.load(f)
    else:
        config = {}

    if "mcpServers" not in config:
        config["mcpServers"] = {}

    if "frida-agent" not in config["mcpServers"]:
        config["mcpServers"]["frida-agent"] = {"command": "frida-mcp"}
        with open(claude_json, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"Added frida-agent MCP to {claude_json}")
    else:
        print("frida-agent MCP already configured.")

    print("\nSetup complete! Restart Claude Code to use frida-agent tools.")
    print("Skills available: /reverse-analyze, /trace-vm")


if __name__ == "__main__":
    main()
