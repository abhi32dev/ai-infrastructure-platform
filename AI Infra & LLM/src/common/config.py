import os
import json
from pathlib import Path
from typing import Any, Dict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    serving_engine: str = "ollama"
    serving_host: str = "localhost"
    serving_port: int = 11434
    serving_fallback_port: int = 8000
    serving_model: str = "candidate-brain:latest"
    serving_fallback_model: str = "qwen2.5:3b"
    serving_temperature: float = 0.2
    serving_max_tokens: int = 750
    serving_top_p: float = 0.9
    serving_stream: bool = True
    serving_num_ctx: int = 8192

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "candidate_resumes"
    embedding_model: str = "nomic-embed-text:latest"
    reranker_model: str = "BAAI/bge-reranker-base"
    chunk_size: int = 250
    chunk_overlap: int = 30
    top_k_retrieve: int = 15
    top_k_rerank: int = 3

    enable_langfuse: bool = True
    langfuse_public_key: str = "pk-lf-mock"
    langfuse_secret_key: str = "sk-lf-mock"
    langfuse_host: str = "http://localhost:3000"

    class Config:
        env_prefix = "NEXUS_"

def load_settings() -> Settings:
    # Load config from json first
    config_path = Path(__file__).parent.parent.parent / "config" / "app_config.json"
    data: Dict[str, Any] = {}
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                raw = json.load(f)
                data.update({f"serving_{k}": v for k, v in raw.get("serving", {}).items()})
                data.update(raw.get("retrieval", {}))
                data.update(raw.get("observability", {}))
        except Exception:
            pass
    return Settings(**data)

settings = load_settings()
