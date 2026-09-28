# Decision points reference

Read the relevant section before presenting options for that stage of the project. These are starting points, not scripts — adapt the framing to the user's actual data and constraints, and mention considerations here that don't apply, if relevant, so the explanation doesn't feel canned.

## RAG projects

### Chunking strategy
- **Fixed-size chunks (e.g. 300-800 tokens, with overlap)**: simplest to implement, predictable cost/latency. Works fine when documents are fairly uniform prose. Weak on documents with meaningful structure (tables, code, nested sections) since it can cut mid-thought.
- **Semantic/structure-aware chunking (split on headings, paragraphs, sections)**: preserves meaning better, usually improves retrieval precision. Costs more engineering effort and requires the source documents to have exploitable structure.
- **Recursive/hierarchical chunking**: chunk at multiple granularities (e.g. section + paragraph) and retrieve at the level that fits the query. More complex to build and reason about, but handles mixed long/short queries better.
- **Chunk size tradeoff**: smaller chunks → better precision (less irrelevant text per chunk) but less context per chunk, and more chunks to retrieve/rerank. Larger chunks → more context, worse precision, higher token cost per retrieval.

### Embedding model choice
- **Hosted API embeddings (OpenAI, Cohere, Voyage, etc.)**: no infra to manage, generally strong quality, ongoing per-call cost, sends data to a third party (matters for sensitive documents).
- **Open-source local embeddings (e.g. BGE, GTE, E5 family)**: free after setup, data stays local, requires GPU/CPU capacity and some setup; quality is competitive with hosted for many use cases but worth checking a leaderboard (e.g. MTEB) for the specific task type.
- **Domain-specific / fine-tuned embeddings**: best quality for narrow domains (legal, medical, code), but requires training data and effort — usually not the starting point.

### Vector store
- **Local/embedded (Chroma, FAISS, sqlite-vec, in-memory)**: zero infra, great for prototyting and small corpora, doesn't scale to many concurrent users or huge corpora, no built-in multi-tenancy.
- **Managed vector DB (Pinecone, Qdrant Cloud, Weaviate Cloud, etc.)**: scales, has real ops features (filtering, multi-tenancy, backups), costs money, adds a network hop.
- **Self-hosted vector DB (Qdrant, Weaviate, Milvus)**: more control and no per-call cost at scale, but the user now operates a database.
- Bigger factor than the specific product: expected corpus size and query volume. Small personal projects rarely need more than a local/embedded store.

### Retrieval strategy
- **Pure vector (dense) search**: good for semantic/paraphrase matches, can miss exact keyword/number/name matches.
- **Hybrid (dense + sparse/BM25)**: catches keyword matches dense search misses (IDs, names, exact terms) — usually worth the modest extra complexity for real-world document sets.
- **Reranking (cross-encoder or LLM-based) after initial retrieval**: improves precision of the final context sent to the LLM, at the cost of extra latency and (often) an extra model call. Worth it once initial retrieval quality is a bottleneck, not before.

### Evaluation
- **Vibes-based (read a few outputs and judge)**: fast, fine for the first prototype, doesn't scale and is easy to fool yourself with.
- **Golden set + retrieval metrics (recall@k, MRR)**: tells you if retrieval itself is the problem, requires the user to build a small labeled set of query→relevant-doc pairs.
- **End-to-end answer quality (LLM-as-judge or human rating on generated answers)**: closer to what the user actually cares about, more expensive to run and noisier as a signal.
- Recommend starting with a small (10-20 example) golden set as soon as the user wants to compare two design choices — it's the only way "which chunking strategy is better" stops being a guess.

## Fine-tuning projects

### Base model choice
- Smaller open models (1B-8B class) are cheap to iterate on, can run locally, but have a lower ceiling on complex tasks.
- Larger open models need more compute (often needing LoRA/quantization to be feasible on consumer hardware).
- Match the model family to the deployment target — if the user's endgame is running locally or on a specific inference stack, that constrains the choice more than raw benchmark quality does.

### Full fine-tune vs. LoRA/QLoRA vs. prompt-based (no fine-tune)
- **Full fine-tune**: updates all weights, highest ceiling for shifting model behavior, requires the most compute/memory and full checkpoints, highest risk of catastrophic forgetting if the dataset is narrow.
- **LoRA**: trains small adapter matrices, dramatically less memory, fast to iterate, easy to swap/merge adapters, slightly lower ceiling than full fine-tune but sufficient for most task-adaptation use cases.
- **QLoRA**: LoRA on a quantized base model — makes fine-tuning large models feasible on a single consumer GPU, small quality tradeoff from quantization.
- **No fine-tune (prompting/few-shot/RAG instead)**: zero training cost, worth ruling out first — ask what's failing with prompting before assuming fine-tuning is necessary. Fine-tuning is for teaching style/format/domain behavior consistently, not for injecting facts (that's what RAG is for).

### Dataset format and size
- Instruction/chat fine-tunes need consistent prompt-response formatting matching the base model's chat template — mismatches here are a very common silent bug.
- Quality and consistency of examples matters more than raw count for small fine-tunes; a clean set of a few hundred to a few thousand well-formed examples often beats a noisy 10x larger set.
- Held-out validation examples (not used in training) are necessary to tell overfitting from real improvement — don't let the user skip this to save data.

### Hyperparameters
- Learning rate is the highest-leverage knob and the most common source of a "didn't learn anything" vs. "forgot everything" failure; when in doubt, start from the base model/framework's recommended default rather than guessing.
- Epoch count: small datasets overfit fast (sometimes in 1-3 epochs) — watch validation loss, not just training loss.
- LoRA rank/alpha: higher rank = more capacity to learn (and more memory), but small fine-tunes often don't need high rank; this is a good one to treat as a tunable experiment rather than a single right answer.

### Evaluation
- Task-specific automatic metrics (exact match, BLEU/ROUGE, classification accuracy) where applicable — fast and repeatable.
- Held-out human or LLM-judge review for anything subjective (tone, style, helpfulness) — automatic metrics alone are misleading for these.
- Always compare against the un-fine-tuned base model on the same eval set — "better than base" is the actual bar, not "looks good in isolation."

## Agents

### Framework vs. hand-rolled
- A framework (LangGraph, CrewAI, etc.) gives structure and common patterns fast, at the cost of an abstraction layer to learn and occasional fights with it when the use case doesn't fit its assumptions.
- Hand-rolled (a loop you write yourself calling the model and tools directly) is more transparent and easier to debug, especially good for learning what an agent loop actually does under the hood — often the better choice for a first learning project.

### Tool design
- Fewer, higher-level tools are easier for the model to use correctly; many low-level tools give more flexibility but raise the chance of the model picking a bad sequence.
- Tool descriptions function like prompts — vague descriptions are a common source of the model calling the wrong tool or misusing arguments.

### Memory/state
- Stateless (full context replay each turn) is simplest and most predictable, but expensive/slow as conversations grow.
- Summarization or retrieval-based memory scales better but introduces its own failure mode (losing or misremembering details) — worth introducing only once context length is an actual, observed problem.
