import time
from typing import Dict, Any, Optional
from langfuse import Langfuse
from src.common.config import settings
from src.common.logger import get_logger

logger = get_logger("gateway_tracer")

class PerformanceTracer:
    def __init__(self):
        self.enabled = settings.enable_langfuse
        self.langfuse = None
        self._init_langfuse()

    def _init_langfuse(self):
        if not self.enabled:
            return
        try:
            self.langfuse = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host
            )
            logger.info(f"Langfuse tracer initialized pointing to {settings.langfuse_host}")
        except Exception as e:
            logger.warn(f"Langfuse failed to initialize: {e}. Running in headless logging trace mode.")
            self.langfuse = None

    def trace_span(
        self,
        name: str,
        input_data: Any,
        output_data: Any,
        latency_ms: float,
        token_count: int = 0,
        model: str = ""
    ):
        trace_id = f"span-{hash(time.time()) & 0xfffffff}"
        
        # Log structured traces as JSON to standard output (OpenTelemetry stdout style)
        logger.info(
            f"Trace Span [{name}] - Latency: {latency_ms:.2f}ms | Tokens: {token_count} | Model: {model} | ID: {trace_id}"
        )

        if self.langfuse:
            try:
                # Log metrics to self-hosted Langfuse server asynchronously
                self.langfuse.trace(
                    id=trace_id,
                    name=name,
                    input=input_data,
                    output=output_data,
                    metadata={
                        "latency_ms": latency_ms,
                        "token_count": token_count,
                        "model": model,
                        "cost": token_count * 0.000002  # Mock cost computation logic
                    }
                )
            except Exception as e:
                logger.debug(f"Langfuse trace ingestion failed: {e}")
performance_tracer = PerformanceTracer()
