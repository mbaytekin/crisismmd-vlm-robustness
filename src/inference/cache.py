from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path


class InferenceCache:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS responses (cache_key TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        self.db.commit()

    @staticmethod
    def key(request: dict) -> str:
        return hashlib.sha256(json.dumps(request, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def get(self, request: dict):
        row = self.db.execute("SELECT payload FROM responses WHERE cache_key=?", (self.key(request),)).fetchone()
        return json.loads(row[0]) if row else None

    def put(self, request: dict, payload: dict):
        self.db.execute("INSERT OR REPLACE INTO responses(cache_key,payload) VALUES(?,?)", (self.key(request), json.dumps(payload, ensure_ascii=False)))
        self.db.commit()

