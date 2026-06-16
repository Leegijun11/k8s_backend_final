import json
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    DATABASE_URL: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def parse_aws_secret_json(cls, value: str) -> str:

        if isinstance(value, str) and value.strip().startswith("{"):
            try:
                secret_dict = json.loads(value)
                return secret_dict.get("DATABASE_URL", value)
            except (json.JSONDecodeError, KeyError):
                return value
        return value

    class Config:
        env_file = ".env"
        extra = "ignore" 

settings = Settings()