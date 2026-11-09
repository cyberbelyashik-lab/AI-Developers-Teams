
from collections import defaultdict

from backend.agents.definitions import AGENTS


CATEGORIES = (
    "quality",
    "speed",
    "teamwork",
    "error_recovery",
)


class ReputationSystem:

    def __init__(self):
        self.ratings = defaultdict(list)

    def rate_agent(
        self,
        agent_id: str,
        evaluator_id: str,
        scores: dict,
        evidence: str,
    ):
        if agent_id not in AGENTS:
            raise ValueError("Неизвестный оцениваемый агент")

        if evaluator_id not in AGENTS:
            raise ValueError("Неизвестный оценивающий агент")

        if agent_id == evaluator_id:
            raise ValueError("Нельзя оценивать самого себя")

        if not evidence.strip():
            raise ValueError("Необходимо указать доказательства")

        if set(scores.keys()) != set(CATEGORIES):
            raise ValueError("Необходимо указать все четыре категории")

        validated_scores = {}

        for category in CATEGORIES:
            score = scores[category]

            if type(score) is not int or not 1 <= score <= 10:
                raise ValueError(
                    f"Оценка {category} должна быть целым числом от 1 до 10"
                )

            validated_scores[category] = score

        rating = {
            "agent_id": agent_id,
            "evaluator_id": evaluator_id,
            "scores": validated_scores,
            "evidence": evidence.strip(),
        }

        self.ratings[agent_id].append(rating)

        return {
            "status": "recorded",
            "rating": rating,
        }

    def get_reputation(self, agent_id: str):
        if agent_id not in AGENTS:
            raise ValueError("Неизвестный агент")

        ratings = self.ratings[agent_id]

        averages = {}

        for category in CATEGORIES:
            values = [
                item["scores"][category]
                for item in ratings
            ]

            averages[category] = (
                round(sum(values) / len(values), 2)
                if values else None
            )

        return {
            "agent_id": agent_id,
            "ratings_count": len(ratings),
            "scores": averages,
        }


reputation_system = ReputationSystem()
