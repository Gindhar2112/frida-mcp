"""Message collection with pagination and file fallback."""

import json
import os
from datetime import datetime


DEFAULT_LIMIT = 50
SIZE_THRESHOLD = 64 * 1024  # 64KB


def get_messages(
    messages: list[dict],
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
    save_to_file: bool = False,
) -> dict:
    """Get collected messages with pagination or file fallback."""
    total = len(messages)

    if total == 0:
        return {"total": 0, "messages": [], "hint": "No messages yet. Has the target been triggered?"}

    if save_to_file:
        return _save_to_file(messages)

    # Check total size
    content = json.dumps(messages)
    if len(content) > SIZE_THRESHOLD:
        # Auto file fallback
        result = _save_to_file(messages)
        result["hint"] = f"Messages too large ({len(content)} bytes), saved to file."
        return result

    # Pagination
    page = messages[offset : offset + limit]
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": offset + limit < total,
        "messages": page,
    }


def _save_to_file(messages: list[dict]) -> dict:
    """Save messages to a file and return the path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"frida_messages_{timestamp}.json"
    filepath = os.path.join(os.getcwd(), filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    return {
        "total": len(messages),
        "saved_to": filepath,
        "size_bytes": os.path.getsize(filepath),
    }
