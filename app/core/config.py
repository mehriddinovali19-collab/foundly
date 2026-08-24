from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    debug: bool = True

    project_name: str = "Campus Lost & Found API"

    db_name: str
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    

    secret_key: str
    algorithm: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()