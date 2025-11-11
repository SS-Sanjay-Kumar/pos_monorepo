from pydantic import BaseSettings
from datetime import timedelta


class Settings(BaseSettings):
    PROJECT_NAME: str = "HotelBillingAPI"
    DATABASE_URL: str = "mysql+asyncmy://myuser:mypassword@127.0.0.1:3306/hotel_db"
    SECRET_KEY: str = "change_this_to_a_random_secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
ACCESS_TOKEN_EXPIRE = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


