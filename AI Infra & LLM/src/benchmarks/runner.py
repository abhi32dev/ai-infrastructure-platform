import asyncio
import argparse
from src.benchmarks.engine import BenchmarkEngine
from src.benchmarks.metrics import MetricsCalculator
from src.common.config import settings
from src.common.logger import get_logger

logger = get_logger("benchmark_runner")

# Example prompts for RAG evaluation profiles of varying lengths
DEFAULT_PROMPTS = [
    "Evaluate candidate Abhishek Singh for Staff AI Infrastructure role. Check distributed training design patterns.",
    "Verify resume profile match against senior backend engineer role. Check FastAPI experience.",
    "Does this candidate demonstrate production Triton CUDA scheduler optimization skills?",
    "Assess cost router RAG compression pipeline efficiency for high throughput metrics."
]

async def run_sweeps(model: str, max_concurrency: int = 32):
    prompts = DEFAULT_PROMPTS * 8  # 32 total queries to ensure load
    concurrency_levels = [1, 2, 4, 8, 16, 32]
    # Filter list up to max_concurrency
    concurrency_levels = [c for c in concurrency_levels if c <= max_concurrency]

    print(f"\n### Benchmark Run for model: `{model}`\n")
    print("| Concurrency | Total Req | Successful | Failed | Mean TTFT (ms) | P95 TTFT (ms) | Mean TPOT (ms) | Throughput (tok/s) | Mem Delta (MB) |")
    print("|-------------|-----------|------------|--------|----------------|---------------|----------------|--------------------|----------------|")

    for c in concurrency_levels:
        start_mem = MetricsCalculator.get_system_memory_mb()
        engine = BenchmarkEngine(concurrency=c, model_name=model)
        results = await engine.execute_sweep(prompts[:c * 2])  # scales workload with concurrency
        end_mem = MetricsCalculator.get_system_memory_mb()

        stats = MetricsCalculator.calculate(results, start_mem, end_mem)
        print(f"| {c:<11} | {stats['total_requests']:<9} | {stats['successful_requests']:<10} | {stats['failed_requests']:<6} | {stats['mean_ttft_ms']:<14} | {stats['p95_ttft_ms']:<13} | {stats['mean_tpot_ms']:<14} | {stats['tokens_per_sec']:<18} | {stats['memory_delta_mb']:<14} |")

def main():
    parser = argparse.ArgumentParser(description="Nexus local LLM benchmark runner.")
    parser.add_argument("--model", type=str, default=settings.serving_model, help="Ollama or vLLM model to test.")
    parser.add_argument("--concurrency", type=int, default=32, help="Max concurrency limit.")
    args = parser.parse_args()

    asyncio.run(run_sweeps(args.model, args.concurrency))

if __name__ == "__main__":
    main()
