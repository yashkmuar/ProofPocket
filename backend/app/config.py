"""
Central place where every environment variable is loaded and validated once.

Nothing else in the app should read os.environ directly. Import `settings`
from here instead, so a missing/typo'd variable fails loudly at startup
rather than deep inside a request.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- App ----
    APP_NAME: str = "ProofPocket API"
    ENV: str = "local"
    DEBUG: bool = True

    # Comma-separated list of origins allowed to call this API from a browser.
    CORS_ORIGINS: str = "http://localhost:3000"

    # ---- Database ----
    # Format: postgresql+psycopg://user:password@host:port/dbname
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://proofpocket:proofpocket@localhost:5432/proofpocket"
    )

    # ---- Azure OpenAI / Microsoft Foundry ----
    AZURE_OPENAI_ENDPOINT: str = ""          # https://<resource>.openai.azure.com/
    AZURE_OPENAI_API_KEY: str = ""           # leave blank if using Entra ID
    AZURE_OPENAI_API_VERSION: str = "2024-10-21"

    # These are DEPLOYMENT names from Foundry, not model names.
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = "gpt-4o-mini"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-small"

    # Must match the embedding model's output size.
    # text-embedding-3-small -> 1536, text-embedding-3-large -> 3072
    EMBEDDING_DIM: int = 1536

    # Set true to authenticate with Entra ID (managed identity / az login)
    # instead of an API key. Recommended once you deploy to Azure.
    USE_ENTRA_ID_AUTH: bool = False

    # ---- RAG tuning ----
    CHUNK_SIZE: int = 1000        # characters per chunk
    CHUNK_OVERLAP: int = 150      # characters repeated between chunks
    TOP_K: int = 5                # chunks retrieved per question

    @property
    def cors_origin_list(self) -> listreturn [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached so the .env file is parsed only once per process."""
    return Settings()


settings = get_settings()