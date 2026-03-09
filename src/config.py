from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_name: str = "rlt_videos"
    db_password: str = "2293663"
    db_user: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 5432

    openai_api_key: str = ""
    bot_token: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
