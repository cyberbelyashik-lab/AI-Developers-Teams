
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "AI Developers Teams")
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")
AI_BASE_URL = os.getenv(
    "AI_BASE_URL",
    "https://api.openai.com/v1",
).rstrip("/")
AI_MODEL = os.getenv("AI_MODEL", "")
AI_API_KEY = os.getenv("AI_API_KEY", "")

DATABASE_PATH = Path(
    os.getenv("DATABASE_PATH", "data/ai_developers.db")
)

if not DATABASE_PATH.is_absolute():
    DATABASE_PATH = ROOT_DIR / DATABASE_PATH

MAX_PARALLEL_AGENTS = int(
    os.getenv("MAX_PARALLEL_AGENTS", "3")
)

AGENT_MEMORY_ENABLED = (
    os.getenv("AGENT_MEMORY_ENABLED", "true").lower() == "true"
)

REQUIRE_APPROVAL_FOR_CODE_CHANGES = (
    os.getenv("REQUIRE_APPROVAL_FOR_CODE_CHANGES", "true").lower() == "true"
)

REQUIRE_APPROVAL_FOR_AGENT_MODIFICATIONS = (
    os.getenv("REQUIRE_APPROVAL_FOR_AGENT_MODIFICATIONS", "true").lower() == "true"
)

AUTO_ROLLBACK_ON_CRITICAL_ERROR = (
    os.getenv("AUTO_ROLLBACK_ON_CRITICAL_ERROR", "true").lower() == "true"
)
