from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./app.db"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_minutes: int = 60 * 24 * 7

    s3_endpoint_url: str = "http://localhost:3900"
    s3_region: str = "garage"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_bucket: str = "doc-images"
    s3_presigned_url_expire_seconds: int = 3600

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
