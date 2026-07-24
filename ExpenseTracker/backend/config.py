'''
Script that
'''
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Settings(BaseSettings):
    # model config loads secret key from env file for server to provide signature.
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, '..', '..', '.env'),
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # secret_key maps to case-insensitive secret key field inside env file to fetch value. SecretStr converts the fetched value to something ...
    # ... even if it's leaked somehow cannot be figured out by anyone.
    secret_key: SecretStr
    algorithm: str = "HS256"
    # short-access token that expires within timelimit specified.
    access_token_expire_minutes: int = 30

settings = Settings()