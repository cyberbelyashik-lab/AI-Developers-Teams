
import pytest

from backend.agents.definitions import get_all_agents, get_agent
from backend.agents.reputation import ReputationSystem
from backend.coordinator.manager import coordinator


def test_team_has_six_agents():
    assert len(get_all_agents()) == 6


def test_all_six_agents_exist():
    agent_ids = [
        "manager",
        "architect",
        "developer",
        "reviewer",
        "tester",
        "auditor",
    ]

    for agent_id in agent_ids:
        assert get_agent(agent_id) is not None


def test_unknown_agent_does_not_exist():
    assert get_agent("unknown_agent") is None


def test_coordinator_creates_task_plan():
    plan = coordinator.create_plan("Создать простой веб-сайт")

    assert plan.status == "planned"
    assert plan.user_request == "Создать простой веб-сайт"
    assert len(plan.tasks) == 5


def test_coordinator_rejects_empty_description():
    with pytest.raises(ValueError):
        coordinator.create_plan("   ")


def test_reputation_records_agent_rating():
    system = ReputationSystem()

    result = system.rate_agent(
        agent_id="developer",
        evaluator_id="reviewer",
        scores={
            "quality": 9,
            "speed": 8,
            "teamwork": 10,
            "error_recovery": 7,
        },
        evidence="Агент успешно выполнил задачу и исправил ошибки.",
    )

    assert result["status"] == "recorded"
    assert system.get_reputation("developer")["ratings_count"] == 1


def test_reputation_rejects_self_rating():
    system = ReputationSystem()

    with pytest.raises(ValueError):
        system.rate_agent(
            agent_id="developer",
            evaluator_id="developer",
            scores={
                "quality": 9,
                "speed": 8,
                "teamwork": 10,
                "error_recovery": 7,
            },
            evidence="Самооценка",
        )


def test_reputation_rejects_invalid_score():
    system = ReputationSystem()

    with pytest.raises(ValueError):
        system.rate_agent(
            agent_id="developer",
            evaluator_id="reviewer",
            scores={
                "quality": 11,
                "speed": 8,
                "teamwork": 10,
                "error_recovery": 7,
            },
            evidence="Проверка оценки",
        )
