from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Blockchain settings
    WEB3_PROVIDER_URI: str = "http://localhost:8545"
    CONTRACT_ADDRESS: str
    CHAIN_ID: int = 1
    
    # IPFS settings
    IPFS_HOST: str = "localhost"
    IPFS_PORT: int = 5001
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings() 