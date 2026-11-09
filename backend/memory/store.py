
import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from backend.config import DATABASE_PATH


class TeamMemory:

    def __init__(self):
        self.db_path = Path(DATABASE_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save(self, agent_id, category, content, metadata=None):
        if not agent_id or not category or not content:
            raise ValueError("Все поля памяти обязательны")

        memory_id = str(uuid4())

        with self._connect() as connection:
            connection.execute("""
                INSERT INTO memories
                (id, agent_id, category, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                memory_id,
                agent_id,
                category,
                content,
                json.dumps(metadata or {}, ensure_ascii=False),
            ))

        return memory_id

    def get_recent(self, limit=50):
        with self._connect() as connection:
            rows = connection.execute("""
                SELECT * FROM memories
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()

        return [self._format(row) for row in rows]

    def get_by_agent(self, agent_id, limit=50):
        with self._connect() as connection:
            rows = connection.execute("""
                SELECT * FROM memories
                WHERE agent_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (agent_id, limit)).fetchall()

        return [self._format(row) for row in rows]

    @staticmethod
    def _format(row):
        item = dict(row)
        item["metadata"] = json.loads(item["metadata"])
        return item


team_memory = TeamMemory()
