"""
Central place where every environment variable is loaded and validated once.

NOthing else in the app should read os.environ directly. Import settings from here isntead,
so a missing/typo'd variable fails loudly at startup rathern than deep inside a request.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    #---App---

    APP_Name:str = "ProofPocket API"
    ENV:str = "local"
    DEBUG: bool = True

    #Comma-separated list of origins allowed to call this API from a browser.
    CORS_ORIGINS: str = "http://localhost:3000"

    #--- Database ----
    #Format: postgresql+psycopg:
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://proofpocket:proofpocket@localhost:5432/proofpocket"
    )

    #Azure OpenAI/Microsoft Foundry
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-10-21"

    #These are DEPLOYMENT names from Foundry, not model names.
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = "gpt-4o-mini"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-small"

    # Must match the embedding model's output size.
    EMBEDDING_DIM: int = 1536

    USE_ENTRA_ID_AUTH: bool = False

    # -- RAG Tuning ---
    CHUNK_SIZE : int = 1000  #characters per chunk
    CHUNK_OVERLAP: int = 150 #characters repeated between chunks
    TOP_K: int = 5  #chunks retrieved per question

    @property
    def cors_origin_list(self) -> listreturn [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

@lru_cache
def get_settings() -> Settings:
        """Cache so the .env file is parsed only once per process."""
        return Settings()

settings = get_settings()

