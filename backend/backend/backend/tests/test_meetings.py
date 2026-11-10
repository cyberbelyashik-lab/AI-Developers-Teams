
import pytest

from backend.meetings.room import MeetingRoom


@pytest.fixture
def room(tmp_path):
    test_room = MeetingRoom.__new__(MeetingRoom)
    test_room.db_path = tmp_path / "test_meetings.db"
    test_room.db_path.parent.mkdir(parents=True, exist_ok=True)
    test_room._initialize()
    return test_room


def test_create_meeting(room):
    meeting = room.create_meeting("Планирование проекта")

    assert meeting["title"] == "Планирование проекта"
    assert meeting["status"] == "active"


def test_reject_empty_meeting_title(room):
    with pytest.raises(ValueError):
        room.create_meeting("   ")


def test_add_message(room):
    meeting = room.create_meeting("Обсуждение")

    message = room.add_message(
        meeting["meeting_id"],
        "manager",
        "Начинаем работу",
    )

    assert message["agent_id"] == "manager"
    assert message["message"] == "Начинаем работу"


def test_vote_in_meeting(room):
    meeting = room.create_meeting("Голосование")

    vote = room.vote(
        meeting["meeting_id"],
        "architect",
        "approve",
        "План хороший",
    )

    assert vote["choice"] == "approve"


def test_reject_duplicate_vote(room):
    meeting = room.create_meeting("Голосование")

    room.vote(meeting["meeting_id"], "manager", "approve")

    with pytest.raises(ValueError):
        room.vote(meeting["meeting_id"], "manager", "reject")


def test_get_meeting_summary(room):
    meeting = room.create_meeting("Проверка")

    room.vote(meeting["meeting_id"], "manager", "approve")
    room.vote(meeting["meeting_id"], "architect", "reject")

    result = room.get_meeting(meeting["meeting_id"])

    assert result["vote_summary"]["approve"] == 1
    assert result["vote_summary"]["reject"] == 1
