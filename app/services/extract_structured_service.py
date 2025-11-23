from pydantic_ai import Agent, WebSearchTool
from pydantic_ai.mcp import load_mcp_servers
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIResponsesModelSettings

from app.schemas.extract_structured import (
    StructuredData,
)


class ExtractStructuredService:
    SYSTEM_PROMPT = """
    You extract structured data from a medical note.
    Use the healthcare-mcp server to get ICD 10-codes.
    Use the WebSearchTool to search the internet to get RxNorm codes.
    """

    def __init__(self):
        fallback_model = FallbackModel(
            "gateway/openai-responses:gpt-5.1", "gateway/gemini:gemini-3.0-flash"
        )
        # TODO: Switch to higher reasoning effort for production
        openai_model_settings = OpenAIResponsesModelSettings(openai_reasoning_effort="none")
        mcp_servers = load_mcp_servers("mcp_config_with_env.json")
        self._agent = Agent(
            fallback_model,
            instructions=self.SYSTEM_PROMPT,
            output_type=StructuredData,
            model_settings=openai_model_settings,
            builtin_tools=[WebSearchTool()],
            toolsets=mcp_servers,
        )

    def extract_structured(self, data: str) -> StructuredData:
        result = self._agent.run_sync(user_prompt=data)
        return result.output


def get_extract_structured_service() -> ExtractStructuredService:
    return ExtractStructuredService()
