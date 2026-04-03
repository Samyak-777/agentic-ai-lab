"""
Day 3 — Interaction Logger
===========================
Logs every agent interaction (input, selected tool, output) to both
a JSON Lines file and the terminal with rich formatting.
"""

import json
import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "agent_logs.jsonl"


def log_interaction(user_input: str, tool_name: str, tool_input: str, output: str):
    """Append a structured log entry to the log file."""
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user_input": user_input,
        "tool_selected": tool_name,
        "tool_input": tool_input,
        "agent_output": output,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def load_logs(last_n: int = 10):
    """Read the last N log entries."""
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    entries = [json.loads(line) for line in lines if line.strip()]
    return entries[-last_n:]
