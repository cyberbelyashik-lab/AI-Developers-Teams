
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.agents.definitions import AGENTS, get_all_agents, get_agent
from backend.agents.runner import agent_runner
from backend.agents.reputation import reputation_system
from backend.coordinator.manager import coordinator
from backend.memory.store import team_memory
from backend.meetings.room import meeting_room
from backend.config import APP_NAME, APP_ENV, AI_MODEL, AI_API_KEY


app = FastAPI(
    title=APP_NAME,
    description="AI Developers Teams — виртуальная команда ИИ-разработчиков",
    version="0.2.0",
)


# -------------------------
# Модели запросов
# -------------------------

class RunAgentRequest(BaseModel):
    task: str = Field(min_length=1, max_length=10000)


class PlanRequest(BaseModel):
    description: str = Field(min_length=1, max_length=10000)


class MemoryRequest(BaseModel):
    agent_id: str
    content: str = Field(min_length=1, max_length=10000)
    category: str = Field(default="note", min_length=1, max_length=100)


class MeetingRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)


class MessageRequest(BaseModel):
    agent_id: str
    content: str = Field(min_length=1, max_length=10000)


class VoteRequest(BaseModel):
    agent_id: str
    choice: str
    reason: str = Field(default="", max_length=1000)


class ReputationRequest(BaseModel):
    agent_id: str
    evaluator_id: str
    scores: dict[str, int]
    evidence: str = Field(min_length=1, max_length=1000)


# -------------------------
# Главная страница
# -------------------------

@app.get("/")
def root():
    return {
        "name": APP_NAME,
        "status": "running",
        "environment": APP_ENV,
        "version": "0.2.0",
    }


# -------------------------
# Проверка сервера
# -------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": APP_NAME,
    }


@app.get("/ai/status")
def ai_status():
    return {
        "provider": "OpenAI-compatible",
        "model": AI_MODEL or None,
        "api_key_configured": bool(AI_API_KEY),
    }


# -------------------------
# ИИ-агенты
# -------------------------

@app.get("/agents")
def agents():
    return get_all_agents()


@app.get("/agents/{agent_id}")
def agent_details(agent_id: str):
    agent = get_agent(agent_id)

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Агент не найден",
        )

    return agent.to_dict()


@app.post("/agents/{agent_id}/run")
async def run_agent(agent_id: str, request: RunAgentRequest):
    if get_agent(agent_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Агент не найден",
        )

    try:
        return await agent_runner.run(
            agent_id,
            request.task.strip(),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Не удалось выполнить задачу агента",
        )


# -------------------------
# Планирование задач
# -------------------------

@app.post("/tasks/plan")
def create_task_plan(request: PlanRequest):
    try:
        return coordinator.create_plan(
            request.description.strip()
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# -------------------------
# Память команды
# -------------------------

@app.post("/memory")
def save_memory(request: MemoryRequest):
    if get_agent(request.agent_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Агент не найден",
        )

    try:
        memory_id = team_memory.save(
            agent_id=request.agent_id,
            content=request.content.strip(),
            category=request.category.strip(),
        )

        return {
            "status": "saved",
            "memory_id": memory_id,
        }
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.get("/memory/{agent_id}")
def get_memory(agent_id: str):
    if get_agent(agent_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Агент не найден",
        )

    return team_memory.get_by_agent(agent_id)


# -------------------------
# Совещания агентов
# -------------------------

@app.post("/meetings")
def create_meeting(request: MeetingRequest):
    try:
        return meeting_room.create_meeting(
            title=request.title.strip()
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.post("/meetings/{meeting_id}/messages")
def add_meeting_message(
    meeting_id: str,
    request: MessageRequest,
):
    if get_agent(request.agent_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Агент не найден",
        )

    try:
        return meeting_room.add_message(
            meeting_id=meeting_id,
            agent_id=request.agent_id,
            message=request.content.strip(),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.post("/meetings/{meeting_id}/vote")
def vote_in_meeting(
    meeting_id: str,
    request: VoteRequest,
):
    if get_agent(request.agent_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Агент не найден",
        )

    try:
        return meeting_room.vote(
            meeting_id=meeting_id,
            agent_id=request.agent_id,
            choice=request.choice,
            reason=request.reason,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.get("/meetings/{meeting_id}")
def get_meeting(meeting_id: str):
    try:
        return meeting_room.get_meeting(meeting_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


# -------------------------
# Репутация агентов
# -------------------------

@app.post("/reputation")
def add_reputation(request: ReputationRequest):
    try:
        return reputation_system.rate_agent(
            agent_id=request.agent_id,
            evaluator_id=request.evaluator_id,
            scores=request.scores,
            evidence=request.evidence.strip(),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.get("/reputation")
def get_all_reputation():
    return {
        agent_id: reputation_system.get_reputation(agent_id)
        for agent_id in AGENTS
    }


@app.get("/reputation/{agent_id}")
def get_agent_reputation(agent_id: str):
    try:
        return reputation_system.get_reputation(agent_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )
