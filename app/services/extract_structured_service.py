from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models.fallback import FallbackModel

from app.schemas.extract_structured import (
    StructuredData,
)


class ExtractStructuredService:
    SYSTEM_PROMPT = """
    You extract structured data from a medical note.
    Use the healthcare-mcp server to get ICD 10-codes.
    Use the web search to search the internet to get RxNorm codes.
    """

    def __init__(self):
        self._agent = Agent(
            FallbackModel("gateway/openai:gpt-5.1"),
            instructions=self.SYSTEM_PROMPT,
            output_type=StructuredData,
            toolsets=[MCPServerStdio("npx", args=["healthcare-mcp"])],
        )

    async def extract_structured(self, data: str) -> StructuredData:
        result = await self._agent.run(user_prompt=data)
        return result.output


def get_extract_structured_service() -> ExtractStructuredService:
    return ExtractStructuredService()
