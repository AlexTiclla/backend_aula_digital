from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./aula_digital.db"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Aula Digital"

settings = Settings()