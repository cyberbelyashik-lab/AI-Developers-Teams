
from dataclasses import dataclass, field
from uuid import uuid4

from backend.agents.definitions import AGENTS


@dataclass
class Task:
    id: str
    title: str
    description: str
    assigned_to: str
    status: str = "pending"


@dataclass
class TaskPlan:
    id: str
    user_request: str
    status: str
    tasks: list[Task] = field(default_factory=list)


class Coordinator:

    def get_team(self):
        return [
            agent.to_dict()
            for agent in AGENTS.values()
        ]

    def create_plan(self, description: str) -> TaskPlan:
        description = description.strip()

        if not description:
            raise ValueError("Описание задачи не может быть пустым")

        workflow = [
            (
                "Архитектурное планирование",
                "Проанализировать задачу и подготовить архитектуру.",
                "architect",
            ),
            (
                "Разработка",
                "Реализовать решение на основе архитектурного плана.",
                "developer",
            ),
            (
                "Проверка кода",
                "Проверить качество и корректность реализации.",
                "reviewer",
            ),
            (
                "Тестирование",
                "Подготовить и выполнить необходимые тесты.",
                "tester",
            ),
            (
                "Аудит",
                "Проверить безопасность и итоговый результат.",
                "auditor",
            ),
        ]

        tasks = [
            Task(
                id=str(uuid4()),
                title=title,
                description=details,
                assigned_to=agent_id,
            )
            for title, details, agent_id in workflow
        ]

        return TaskPlan(
            id=str(uuid4()),
            user_request=description,
            status="planned",
            tasks=tasks,
        )


coordinator = Coordinator()
