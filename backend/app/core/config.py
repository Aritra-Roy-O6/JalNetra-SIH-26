from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "JalNetra Backend API"
    VERSION: str = "1.0.0"
    
    # PostgreSQL with psycopg2 driver
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/jalnetra"
    
    # Redis & Celery Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # External APIs
    OPENAI_API_KEY: str = ""
    BHASHINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()