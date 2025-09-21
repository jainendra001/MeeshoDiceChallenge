from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "asia-southeast1-gcp"
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    INDEX_NAME: str = "meesho-product-index"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
