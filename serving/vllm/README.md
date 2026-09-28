# Model serving (Phase 7)

vLLM is intentionally kept out of `docker-compose.yml` — it needs a GPU and
usually runs on a separate box (a rented A10/A100 on RunPod, Lambda, etc.).

## Start vLLM (OpenAI-compatible server)

```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Meta-Llama-3-8B-Instruct \
  --port 8001 \
  --max-model-len 8192
```

Then point the app at it: set `LLM_BASE_URL=http://<gpu-host>:8001/v1` in `.env`.

## What to actually learn / measure here

Don't just get it running — understand *why* it's fast, because this is prime
interview territory:

- **PagedAttention** — how vLLM manages the KV cache in pages to cut memory
  waste. This is the headline reason it beats naive HF `generate`.
- **Continuous batching** — new requests join the batch mid-flight instead of
  waiting for the slowest one. Explains the throughput curve you'll benchmark.
- **Quantization tradeoffs** — AWQ/GPTQ vs. fp16: memory & latency down, quality
  down how much? Measure it against your RAGAS set, don't assume.

## Benchmark

`serving/benchmarks/load_test.py` sweeps concurrency 1→100 and reports TTFT and
p50/p95/p99 latency. Fill the results into the README table at the repo root.

TODO(you): also compare vLLM vs. a naive baseline (single-request HF generate)
so you have a concrete "Nx throughput" number.
