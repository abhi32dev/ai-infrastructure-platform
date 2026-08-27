import subprocess
import httpx
import time
from src.common.config import settings
from src.common.logger import get_logger

logger = get_logger("server_manager")

class ServerManager:
    def __init__(self):
        self.host = settings.serving_host
        self.port = settings.serving_port
        self.base_url = f"http://{self.host}:{self.port}"

    def is_server_running(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False

    def start_server(self) -> bool:
        if self.is_server_running():
            logger.info("Serving engine is already running.")
            return True

        logger.info("Attempting to start Ollama background process...")
        try:
            # Try running command line 'ollama serve' as background subprocess
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Poll for startup
            for _ in range(10):
                time.sleep(1.0)
                if self.is_server_running():
                    logger.info("Ollama successfully started.")
                    return True
        except Exception as e:
            logger.error(f"Failed to start Ollama subprocess: {e}")
        
        # Second fallback: check mac application
        try:
            subprocess.Popen(["open", "-a", "Ollama"])
            for _ in range(10):
                time.sleep(1.0)
                if self.is_server_running():
                    logger.info("Ollama started via open command.")
                    return True
        except Exception as e:
            logger.error(f"Failed to open Ollama app: {e}")

        return False

    def ensure_model_pulled(self, model_name: str) -> bool:
        if not self.is_server_running():
            if not self.start_server():
                logger.error("Serving engine offline. Cannot verify model.")
                return False

        try:
            # Check local tags
            res = httpx.get(f"{self.base_url}/api/tags")
            models = [m["name"] for m in res.json().get("models", [])]
            if model_name in models or f"{model_name}:latest" in models:
                logger.info(f"Model {model_name} is already available.")
                return True

            logger.info(f"Model {model_name} missing. Pulling model...")
            # Fire-and-forget pull or synchronous pull
            # For simplicity and test stability, pull synchronously with a timeout
            with httpx.stream("POST", f"{self.base_url}/api/pull", json={"name": model_name}, timeout=120.0) as r:
                for chunk in r.iter_bytes():
                    pass
            logger.info(f"Successfully pulled model {model_name}.")
            return True
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
