"""Latency & throughput benchmark for the served LLM (Phase 7).

The numbers this produces (TTFT, p50/p95/p99, throughput) are what you'll put in
the README and talk about in interviews. Concurrency sweep + percentile math are
provided as glue; the single request call is a small TODO so you point it at
your endpoint.

Run:  python -m serving.benchmarks.load_test
"""
from __future__ import annotations

import asyncio
import statistics
import time
from dataclasses import dataclass

import httpx

from config.settings import settings

CONCURRENCY_LEVELS = [1, 5, 10, 25, 50, 100]
PROMPT = "Summarize the key considerations when deploying a RAG system in production."


@dataclass
class Sample:
    ttft: float      # time to first token (s)
    total: float     # total completion time (s)
    tokens: int


async def _one_request(client: httpx.AsyncClient) -> Sample:
    """Fire a single streaming completion and time it.

    TODO(you): call your vLLM OpenAI-compatible endpoint (settings.llm_base_url)
    with stream=True, record the timestamp of the FIRST token (TTFT) and the
    last (total), and count tokens. TTFT vs. total is the distinction that makes
    a serving benchmark meaningful — measure both, not just wall-clock.
    """
    raise NotImplementedError("Implement a single streaming request against vLLM.")


async def _run_level(concurrency: int) -> list[Sample]:
    async with httpx.AsyncClient(base_url=settings.llm_base_url, timeout=120) as client:
        return await asyncio.gather(*[_one_request(client) for _ in range(concurrency)])


def _percentiles(values: list[float]) -> dict[str, float]:
    """p50/p95/p99 helper. (Glue.)"""
    s = sorted(values)
    def pct(p: float) -> float:
        return s[min(len(s) - 1, int(round(p / 100 * (len(s) - 1))))]
    return {"p50": pct(50), "p95": pct(95), "p99": pct(99), "mean": statistics.mean(s)}


async def main() -> None:
    print(f"{'conc':>5} {'ttft_p50':>9} {'lat_p95':>9} {'lat_p99':>9} {'req/s':>8}")
    for level in CONCURRENCY_LEVELS:
        start = time.perf_counter()
        samples = await _run_level(level)
        wall = time.perf_counter() - start
        ttft = _percentiles([s.ttft for s in samples])
        lat = _percentiles([s.total for s in samples])
        print(f"{level:>5} {ttft['p50']:>9.3f} {lat['p95']:>9.3f} {lat['p99']:>9.3f} {level / wall:>8.2f}")


if __name__ == "__main__":
    asyncio.run(main())
