
from backend.agents.definitions import get_all_agents, get_agent
from backend.coordinator.manager import Coordinator, Task


def test_team_has_six_agents():
    agents = get_all_agents()
    assert len(agents) == 6


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
    task = Task(description="Создать простой веб-сайт")
    plan = Coordinator.create_plan(task)

    assert plan is not None
