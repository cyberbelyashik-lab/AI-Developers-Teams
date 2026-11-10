
import pytest

from backend.memory.store import TeamMemory


@pytest.fixture
def memory(tmp_path):
    return TeamMemory(tmp_path / "test_memory.db")


def test_save_memory(memory):
    memory_id = memory.save(
        "developer",
        "note",
        "Исправлена ошибка",
    )

    assert memory_id


def test_get_memory_by_agent(memory):
    memory.save("developer", "note", "Тестовая запись")

    result = memory.get_by_agent("developer")

    assert len(result) == 1
    assert result[0]["content"] == "Тестовая запись"


def test_memory_metadata(memory):
    memory.save(
        "architect",
        "design",
        "Архитектура готова",
        {"version": 1},
    )

    result = memory.get_by_agent("architect")

    assert result[0]["metadata"]["version"] == 1


def test_reject_empty_memory(memory):
    with pytest.raises(ValueError):
        memory.save("developer", "note", "")
