
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.agents.definitions import get_all_agents, get_agent
from backend.agents.runner import agent_runner
from backend.agents.reputation import reputation
from backend.coordinator.manager import coordinator
from backend.memory.store import team_memory
from backend.meetings.room import meeting_room
from backend.config import APP_NAME, APP_ENV, AI_MODEL, AI_API_KEY


app = FastAPI(
    title=APP_NAME,
    description="AI Developers Teams — виртуальная команда ИИ-разработчиков",
    version="0.1.0",
)


class RunAgentRequest(BaseModel):
    task: str = Field(min_length=1, max_length=10000)


class PlanRequest(BaseModel):
    description: str = Field(min_length=1, max_length=10000)


class MemoryRequest(BaseModel):
    agent_id: str
    content: str = Field(min_length=1, max_length=10000)
    category: str = "note"


class MeetingRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    topic: str = Field(min_length=1, max_length=10000)


class MessageRequest(BaseModel):
    agent_id: str
    content: str = Field(min_length=1, max_length=10000)


class VoteRequest(BaseModel):
    agent_id: str
    choice: str


class ReputationRequest(BaseModel):
    agent_id: str
    score: float = Field(ge=-10, le=10)
    reason: str = Field(min_length=1, max_length=1000)


@app.get("/")
def root():
    return {
        "name": APP_NAME,
        "status": "running",
        "environment": APP_ENV,
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ai/status")
def ai_status():
    return {
        "provider": "OpenAI-compatible",
        "model": AI_MODEL or None,
        "api_key_configured": bool(AI_API_KEY),
    }


@app.get("/agents")
def agents():
    return get_all_agents()


@app.get("/agents/{agent_id}")
def agent_details(agent_id: str):
    agent = get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Агент не найден")
    return agent


@app.post("/agents/{agent_id}/run")
async def run_agent(agent_id: str, request: RunAgentRequest):
    if get_agent(agent_id) is None:
        raise HTTPException(status_code=404, detail="Агент не найден")
    try:
        return await agent_runner.run(agent_id, request.task)
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))


@app.post("/tasks/plan")
def create_task_plan(request: PlanRequest):
    try:
        return coordinator.create_plan(request.description)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/memory")
def save_memory(request: MemoryRequest):
    if get_agent(request.agent_id) is None:
        raise HTTPException(status_code=404, detail="Агент не найден")
    team_memory.save(
        agent_id=request.agent_id,
        content=request.content,
        category=request.category,
    )
    return {"status": "saved"}


@app.get("/memory/{agent_id}")
def get_memory(agent_id: str):
    if get_agent(agent_id) is None:
        raise HTTPException(status_code=404, detail="Агент не найден")
    return team_memory.get_recent(agent_id)


@app.post("/meetings")
def create_meeting(request: MeetingRequest):
    meeting_id = meeting_room.create_meeting(
        title=request.title,
        topic=request.topic,
    )
    return {"meeting_id": meeting_id}


@app.post("/meetings/{meeting_id}/messages")
def add_meeting_message(meeting_id: str, request: MessageRequest):
    if get_agent(request.agent_id) is None:
        raise HTTPException(status_code=404, detail="Агент не найден")
    try:
        meeting_room.add_message(
            meeting_id=meeting_id,
            agent_id=request.agent_id,
            content=request.content,
        )
        return {"status": "message_added"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.post("/meetings/{meeting_id}/vote")
def vote_in_meeting(meeting_id: str, request: VoteRequest):
    if get_agent(request.agent_id) is None:
        raise HTTPException(status_code=404, detail="Агент не найден")
    try:
        meeting_room.vote(
            meeting_id=meeting_id,
            agent_id=request.agent_id,
            choice=request.choice,
        )
        return {"status": "vote_recorded"}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/meetings/{meeting_id}")
def get_meeting(meeting_id: str):
    try:
        return meeting_room.get_meeting(meeting_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.post("/reputation")
def add_reputation(request: ReputationRequest):
    if get_agent(request.agent_id) is None:
        raise HTTPException(status_code=404, detail="Агент не найден")
    reputation.add_score(
        agent_id=request.agent_id,
        score=request.score,
        reason=request.reason,
    )
    return {"status": "score_added"}


@app.get("/reputation")
def get_all_reputation():
    return reputation.get_all()


@app.get("/reputation/{agent_id}")
def get_agent_reputation(agent_id: str):
    if get_agent(agent_id) is None:
        raise HTTPException(status_code=404, detail="Агент не найден")
    return reputation.get_reputation(agent_id)
