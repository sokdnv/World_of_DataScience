from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    CHAT_API: SecretStr

    class Config:
        env_file = ".env"


config = Settings()
