
from backend.agents.definitions import get_all_agents, get_agent
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

    assert plan is not None
    assert plan.status == "planned"
    assert plan.user_request == "Создать простой веб-сайт"
    assert len(plan.tasks) == 5
    assert {task.assigned_to for task in plan.tasks} == {
        "architect",
        "developer",
        "reviewer",
        "tester",
        "auditor",
    }


def test_coordinator_rejects_empty_description():
    try:
        coordinator.create_plan("   ")
        assert False, "Ожидалась ошибка ValueError"
    except ValueError:
        pass
