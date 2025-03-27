from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    CHAT_API: SecretStr
    DB_KEY: SecretStr
    YANDEX_API_KEY: SecretStr
    FOLDER_ID: SecretStr
    OPENAI_API_KEY: SecretStr

    class Config:
        env_file = ".env"


config = Settings()
