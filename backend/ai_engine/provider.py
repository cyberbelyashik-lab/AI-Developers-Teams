import httpx

from backend.config import AI_API_KEY, AI_BASE_URL, AI_MODEL


class AIProviderError(Exception):
    pass


class AIProvider:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or AI_API_KEY
        self.base_url = AI_BASE_URL
        self.model = AI_MODEL

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            raise AIProviderError("Не настроен API-ключ для этого агента")

        if not self.model:
            raise AIProviderError("Не указана AI_MODEL")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=90) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                if not isinstance(content, str):
                    raise TypeError("Ответ модели не является текстом")
                return content
        except httpx.HTTPStatusError as error:
            raise AIProviderError(
                f"Ошибка AI API: HTTP {error.response.status_code}"
            ) from error
        except httpx.RequestError as error:
            raise AIProviderError("Ошибка соединения с AI API") from error
        except (KeyError, IndexError, TypeError) as error:
            raise AIProviderError(
                "ИИ-провайдер вернул ответ неизвестного формата"
            ) from error


# Совместимость с частями проекта, использующими общий провайдер.
ai_provider = AIProvider()