"""Medical document summarization service using Pydantic AI."""

from pydantic_ai import Agent
from pydantic_ai.models.fallback import FallbackModel

SYSTEM_PROMPT = """You are a medical document summarization assistant.
Your task is to create concise, accurate summaries of medical notes and documents.

Guidelines:
- Focus on key medical information: diagnoses, treatments, medications, and patient status
- Maintain medical terminology accuracy
- Be concise but comprehensive (3-5 sentences typically)
- Highlight any critical or urgent information
- Preserve important numerical values (dosages, test results, etc.)
- Do not add information that is not present in the original document
"""


class SummarizationService:
    def __init__(self):
        fallback_model = FallbackModel("gateway/openai:gpt-5.1", "gateway/gemini:gemini-3.0-flash")
        self._agent = Agent(fallback_model, instructions=SYSTEM_PROMPT)

    async def summarize(self, content: str) -> str:
        user_prompt = f"Please summarize the following medical note:\n\n{content}"
        result = await self._agent.run(user_prompt=user_prompt)
        return result.output


def get_summarization_service() -> SummarizationService:
    return SummarizationService()
