from pydantic_settings import BaseSettings, SettingsConfigDict # Thêm SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/oldshop"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "oldshop"

    # Mail - Khai báo ở đây để Pydantic cho phép nhập từ .env
    SMTP_USER: str = "renekton2311@gmail.com"
    SMTP_PASSWORD: str = "dkfdyumrphhrmjuo"
    MAIL_USERNAME: str = "renekton2311@gmail.com"
    MAIL_PASSWORD: str = "dkfdyumrphhrmjuo"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production-min-32-characters"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Server
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OldShop API"
    PROJECT_VERSION: str = "1.0.0"

    PAYPAL_CLIENT_ID: str = "ATo4XV367A3Jf1KG2BxskbucxSOyb_rIKqc9rNgxCDcwRhAYosZVhohADyFGUwkoAgCC3IhLpj2AAV0x"
    PAYPAL_SECRET: str = "EMe93wpK5-GjzDxZH0y7H_O14Wy9vjluFLJIlh6gPgT1uCzDCai2nxvLPRILDZjFiq40lCqIUegDdEeC"
    PAYPAL_MODE: str = "sandbox"
    PAYPAL_API_URL: str = "https://api-m.sandbox.paypal.com"

    # Cấu hình Pydantic V2 để đọc file .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"  # Quan trọng: Nếu có biến thừa trong .env nó sẽ lờ đi thay vì báo lỗi crash app
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()