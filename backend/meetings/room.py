
import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from backend.config import DATABASE_PATH
from backend.agents.definitions import AGENTS


class MeetingRoom:

    def __init__(self):
        self.db_path = DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS meeting_messages (
                    id TEXT PRIMARY KEY,
                    meeting_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS meeting_votes (
                    id TEXT PRIMARY KEY,
                    meeting_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    choice TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(meeting_id, agent_id),
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id)
                )
            """)

    def create_meeting(self, title):
        if not title or not title.strip():
            raise ValueError("Название совещания обязательно")

        meeting_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        with self._connect() as connection:
            connection.execute("""
                INSERT INTO meetings (id, title, status, created_at)
                VALUES (?, ?, ?, ?)
            """, (meeting_id, title.strip(), "active", created_at))

        return {
            "meeting_id": meeting_id,
            "title": title.strip(),
            "status": "active",
            "created_at": created_at,
        }

    def _check_meeting(self, meeting_id):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM meetings WHERE id = ?",
                (meeting_id,),
            ).fetchone()

        if row is None:
            raise ValueError("Совещание не найдено")

        return dict(row)

    def add_message(self, meeting_id, agent_id, message):
        self._check_meeting(meeting_id)

        if agent_id not in AGENTS:
            raise ValueError("Неизвестный агент")

        if not message or not message.strip():
            raise ValueError("Сообщение не может быть пустым")

        message_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        with self._connect() as connection:
            connection.execute("""
                INSERT INTO meeting_messages
                (id, meeting_id, agent_id, message, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                message_id,
                meeting_id,
                agent_id,
                message.strip(),
                created_at,
            ))

        return {
            "message_id": message_id,
            "meeting_id": meeting_id,
            "agent_id": agent_id,
            "agent_name": AGENTS[agent_id].name,
            "message": message.strip(),
            "created_at": created_at,
        }

    def vote(self, meeting_id, agent_id, choice, reason=""):
        self._check_meeting(meeting_id)

        if agent_id not in AGENTS:
            raise ValueError("Неизвестный агент")

        if choice not in ("approve", "reject", "abstain"):
            raise ValueError("Недопустимый вариант голосования")

        vote_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        try:
            with self._connect() as connection:
                connection.execute("""
                    INSERT INTO meeting_votes
                    (id, meeting_id, agent_id, choice, reason, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    vote_id,
                    meeting_id,
                    agent_id,
                    choice,
                    reason.strip(),
                    created_at,
                ))
        except sqlite3.IntegrityError as error:
            raise ValueError(
                "Этот агент уже проголосовал на данном совещании"
            ) from error

        return {
            "vote_id": vote_id,
            "meeting_id": meeting_id,
            "agent_id": agent_id,
            "choice": choice,
            "reason": reason.strip(),
        }

    def get_meeting(self, meeting_id):
        meeting = self._check_meeting(meeting_id)

        with self._connect() as connection:
            messages = connection.execute("""
                SELECT * FROM meeting_messages
                WHERE meeting_id = ?
                ORDER BY created_at
            """, (meeting_id,)).fetchall()

            votes = connection.execute("""
                SELECT * FROM meeting_votes
                WHERE meeting_id = ?
                ORDER BY created_at
            """, (meeting_id,)).fetchall()

        return {
            **meeting,
            "messages": [dict(row) for row in messages],
            "votes": [dict(row) for row in votes],
            "vote_summary": {
                choice: sum(
                    1 for vote in votes
                    if vote["choice"] == choice
                )
                for choice in ("approve", "reject", "abstain")
            },
        }


meeting_room = MeetingRoom()
