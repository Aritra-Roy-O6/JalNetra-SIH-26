from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "JalNetra API"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/jalnetra"
    
    # API Keys
    OPENAI_API_KEY: str = ""  # Or Anthropic, depending on your LangGraph LLM setup
    BHASHINI_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()