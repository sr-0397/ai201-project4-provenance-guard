import json
import os
from datetime import datetime, timezone

LOG_FILE = "audit_log.json"

def write_log(entry: dict):
    entries = read_log()
    entries.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(entries, f, indent=2)

def read_log() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def get_recent(n=20) -> list:
    entries = read_log()
    return entries[-n:]

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"