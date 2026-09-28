# Enterprise AI Research & Intelligence Platform

A hybrid-RAG + agentic retrieval system with its own model serving and
evaluation. Delivered as three standalone milestones so each increment is
usable, measurable, and understood before the next is added.

> **Status:** skeleton. Structure, glue, and interfaces are in place; the core
> logic in each phase is intentionally left as `TODO(you)` — that's where the
> learning is. See [Delivery milestones](#delivery-milestones).

---

## Architecture

```
                                   ┌─────────────┐
        Documents ──► Ingestion ──►│  pgvector   │  (dense)
        (parse→chunk→embed→index)  │  OpenSearch │  (BM25 + dense)
                                   └──────┬──────┘
                                          │
   Query ─► Router ─┬─ vector ─► Hybrid Search ─► Rerank ─► Self-RAG loop ─┐
                    ├─ sql ────► guarded text-to-SQL ─────────────────────►│─► Answer ─► SSE stream
                    └─ web ────► web search ─────────────────────────────► │
                                          ▲                                 │
                                   Semantic cache (Redis) ◄─────────────────┘
```

Full component reasoning lives in `docs/` (write your design docs there before
implementing each phase — that's the habit that builds the system-design muscle).

## Stack

| Layer            | Tech |
|------------------|------|
| API              | FastAPI, async, SSE streaming |
| Dense store      | PostgreSQL + pgvector (HNSW) |
| Hybrid search    | OpenSearch (BM25 + kNN) |
| Cache / state    | Redis (semantic cache, conversation) |
| Embeddings/rerank| sentence-transformers (bge + cross-encoder) |
| Agent            | LangGraph (router + tools) |
| Serving          | vLLM (Llama-3), OpenAI-compatible |
| Evaluation       | RAGAS |

## Repo layout

```
api/         FastAPI app, routes (query/documents/conversation), middleware
agents/      LangGraph graph, router, sql/retrieval/web tool nodes
retrieval/   embeddings, hybrid_search (RRF), reranker, self_rag
ingestion/   parser, chunker, indexer (writes to both stores)
evaluation/  RAGAS harness + gold dataset
serving/     vLLM notes + latency/throughput benchmark
cache/       semantic cache (Redis)
database/    SQLAlchemy models, migrations, pgvector init
tests/       smoke tests (imports) — add unit tests as you build
```

---

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # fill in secrets

docker compose up -d            # postgres(pgvector) + redis + opensearch
# alembic upgrade head          # once migrations are written (Phase 1)

uvicorn api.main:app --reload   # http://localhost:8000/docs
pytest                          # skeleton smoke tests should pass
```

vLLM runs separately (needs a GPU) — see `serving/vllm/README.md`.

---

## Delivery milestones

Each milestone must stand on its own as a narrow, portfolio-ready artifact.
Within a milestone, **write the relevant design decision in `docs/` before
implementing its `TODO`s.** Don't let an assistant pick the design — that's the
skill you're building.

### Milestone 1 — End-to-End Vertical Slice

**Scope:** Phase 0 foundation, three strictly allowlisted GitHub Actions feature
slices from the Phase 1 corpus, and only the basic FastAPI streaming path needed
to demonstrate them.

- **Phase 0 foundation:** reproducible source manifest, configuration, database
  migration baseline, and focused tests for the contracts selected in the
  design log.
- **Bounded Phase 1:** for both pinned snapshots and the `fpt` profile, ingest
  only workflow runs/workflows, artifacts, and Actions secrets through an
  explicit Markdown-page/OpenAPI-operation allowlist. Each slice contains a
  small curated set of concept/how-to prose plus its REST/OpenAPI material;
  same-commit reusable/variable dependencies are tracked, while adjacent links
  remain diagnostics rather than expanding scope. Then run typed parsing →
  chunking → `bge-small-en-v1.5` embeddings → PostgreSQL/pgvector dense
  retrieval.
- **Basic API path:** ask one docs question and stream a simple grounded answer
  with a source citation. Conversation state, semantic caching, hybrid search,
  agent routing, and production hardening are not part of this milestone.

**Acceptance outcome:** from a clean setup, ingest the pinned allowlist and ask
representative questions through FastAPI for workflow runs/workflows, artifacts,
and Actions secrets. Each returns a simple streamed answer grounded in retrieved
content with a traceable citation; each slice includes at least one semantic
question and one exact API-reference question. This broader slice improves demo
and test variety at the cost of more parser coverage and golden-set work; the
allowlist is the scope control.

### Milestone 2 — Quality & Retrieval Depth

**Scope:** Phase 2 hybrid retrieval and Phase 5 evaluation.

- Add OpenSearch BM25 retrieval.
- Implement reciprocal rank fusion and cross-encoder reranking.
- Build a fixed golden set and run retrieval/end-to-end evaluation, including
  RAGAS where appropriate.

**Acceptance outcome:** publish a reproducible quantitative comparison showing
whether hybrid retrieval and reranking improve over the Milestone 1 dense-only
baseline. The results table below is the milestone artifact.

### Milestone 3 — Agentic Intelligence & Infrastructure

**Scope:** Phase 3/4 agent behavior and Phase 7 model-serving evidence.

- Add LangGraph routing between documentation retrieval and guarded SQL.
- Add retrieval grading, bounded reformulation/retry, grounding checks, and
  explicit abstention behavior.
- Serve the model with vLLM and benchmark time to first token plus
  p50/p95/p99 latency under declared load.

**Acceptance outcome:** demonstrate docs/SQL routing, observable correction and
grounding behavior, and a reproducible serving benchmark reporting TTFT and
p50/p95/p99 latency.

### Post-Milestone-3 future scope

These are explicit extensions, not permission to expand the current milestones:

- Add GitHub Enterprise Cloud (`ghec`) as separately tagged profile data; never
  merge it into the Phase 1 `fpt` records.
- Add REST domains beyond GitHub Actions, including Pull Requests and Issues,
  using the established ingestion and retrieval architecture.

## Publication policy

Publish the repository **publicly from the first commit** so the design history,
learning process, and milestone progression are part of the portfolio artifact.
Repository initialization and the first push remain blocked on the remaining
publication choices and a final secret/large-artifact readiness check.

License the project under the **MIT License**. Add the canonical `LICENSE` file
during repository setup only after the authenticated GitHub account owner's
name can be established safely for the copyright notice.

---

## Results (fill these in as you go)

Retrieval quality (RAGAS) — swap in your real numbers per configuration:

| Metric            | Baseline (dense only) | + Hybrid | + Rerank | + Self-RAG |
|-------------------|:---------------------:|:--------:|:--------:|:----------:|
| context_recall    |  —  |  —  |  —  |  —  |
| context_precision |  —  |  —  |  —  |  —  |
| faithfulness      |  —  |  —  |  —  |  —  |
| answer_relevancy  |  —  |  —  |  —  |  —  |

Serving (vLLM, Llama-3-8B) — from `serving/benchmarks/load_test.py`:

| Concurrency | TTFT p50 | Latency p95 | Latency p99 | Throughput (req/s) |
|:-----------:|:--------:|:-----------:|:-----------:|:------------------:|
| 1 / 10 / 50 / 100 | — | — | — | — |

> The story these two tables tell — retrieval quality climbing phase over phase,
> latency holding under load — is the project. Prioritize getting real numbers
> in here over adding more stack.

## Retro (write when done)

Keep a short `docs/RETRO.md`: what you'd change at 10× data, where the design
has hidden scaling limits, what surprised you. Great interview material.
