from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    """
    Application settings. 
    Các giá trị mặc định ở đây chỉ phục vụ mục đích dự phòng hoặc demo.
    Thông tin bảo mật thực tế nằm hoàn toàn trong file .env.
    """
    
    # Database
    DATABASE_URL: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Mail
    SMTP_USER: str
    SMTP_PASSWORD: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str

    # JWT
    # Lưu ý: Không để mặc định secret key trong code thực tế
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Server
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OldShop API"
    PROJECT_VERSION: str = "1.0.0"

    # PayPal
    PAYPAL_CLIENT_ID: str
    PAYPAL_SECRET: str
    PAYPAL_MODE: str = "sandbox"
    PAYPAL_API_URL: str = "https://api-m.sandbox.paypal.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# Do you understand? 