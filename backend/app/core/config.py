from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Warband HQ"
    environment: str = "development"
    database_url: str

    # Identifie notre application auprès de Blizzard
    blizzard_client_id: str

    # Permet au backend de s'authentifier auprès de Blizzard
    blizzard_client_secret: str

    # Région Blizzard utilisée par l'application
    blizzard_region: str

    # URL vers laquelle Blizzard redirige l'utilisateur après son authentification
    blizzard_redirect_uri: str

    # Clé secrète utilisée pour sécuriser les sessions d'authentification
    session_secret_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
