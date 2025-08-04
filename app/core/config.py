from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:root@localhost:5432/Shoplist"
    SECRET_KEY: str = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1

    MAIL_USERNAME: str = "harendra263@gmail.com"
    MAIL_PASSWORD: str = "xchl zijm hyzx memi"
    MAIL_FROM: str = "harendra263@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    STATIC_FILES_DIR: str = "app/static"
    MAX_FILE_SIZE: int = 2_097_152  # 2MB
    ALLOWED_FILE_TYPES: list = ["image/jpeg", "image/png"]

    class Config:
        env_file= ".env"


settings = Settings()