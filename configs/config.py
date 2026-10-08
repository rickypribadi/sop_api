from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="_prod.env", extra="ignore")

    DB_CONFIG: str

    # JWT auth
    SECRET_KEY: str = "CHANGE_ME_IN_ENV_super_secret_key_for_jwt_signing"
    ALGORITHM: str = "HS256"
    # Masa berlaku token default (jam). Default 4 jam.
    ACCESS_TOKEN_EXPIRE_HOURS: int = 4
    # Batas maksimal masa berlaku token (jam) - dari env.
    MAX_TOKEN_EXPIRE_HOURS: int = 8


settings = Settings()
