from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    async_database_url: str
    sync_database_url: str

    openai_api_key: str
    pydantic_ai_gateway_api_key: str
    fda_api_key: str


settings = Settings()  # type: ignore[call-arg]
