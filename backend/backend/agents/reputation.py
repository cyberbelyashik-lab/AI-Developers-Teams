import sqlite3
from datetime import datetime, timezone

from backend.config import DATABASE_PATH


class Reputation:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self._initialize()

    def _connect(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.db_path)

    def _initialize(self):
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS agent_reputation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    score REAL NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

    def add_score(self, agent_id: str, score: float, reason: str):
        if not -10 <= score <= 10:
            raise ValueError("Оценка должна быть от -10 до 10")

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO agent_reputation
                (agent_id, score, reason, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    agent_id,
                    score,
                    reason,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def get_reputation(self, agent_id: str):
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    COALESCE(SUM(score), 0),
                    COUNT(*),
                    COALESCE(AVG(score), 0)
                FROM agent_reputation
                WHERE agent_id = ?
                """,
                (agent_id,),
            ).fetchone()

        return {
            "agent_id": agent_id,
            "total_score": row[0],
            "reviews_count": row[1],
            "average_score": round(row[2], 2),
        }

    def get_all(self):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    agent_id,
                    COALESCE(SUM(score), 0),
                    COUNT(*),
                    COALESCE(AVG(score), 0)
                FROM agent_reputation
                GROUP BY agent_id
                ORDER BY SUM(score) DESC
                """
            ).fetchall()

        return [
            {
                "agent_id": row[0],
                "total_score": row[1],
                "reviews_count": row[2],
                "average_score": round(row[3], 2),
            }
            for row in rows
        ]


reputation = Reputation()