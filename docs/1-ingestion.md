# Design doc: Phase 1 ingestion

## Problem

Build a reproducible ingestion path for developer documentation that produces
clean text, structured metadata, and retrievable chunks for dense search. The
corpus must support conceptual questions from prose, exact endpoint and
parameter lookups, and later relational questions about API versions and
changes.

## Requirements & constraints

- Use a real, openly available developer-documentation corpus.
- Include conceptual guides, exact API reference data, and version/change data.
- Keep the first phase small enough to inspect and evaluate locally.
- Pin two source snapshots so ingestion and evaluation are reproducible.
- Limit the initial corpus to one representative REST domain.
- Preserve source and version provenance so later answers can cite evidence and
  distinguish current behavior from historical behavior.
- Do not optimize parsing, chunking, or indexing before those decisions are
  explicitly evaluated and recorded.

## Options considered

### Kubernetes

Use the `kubernetes/website` documentation, release OpenAPI specifications, and
per-version changelogs. This provides rich conceptual material and strong,
machine-readable version artifacts, but creates a large and noisy first corpus.
Generated pages, numerous releases, and Kubernetes-specific concepts would add
substantial ingestion and normalization work.

### GitHub REST API

Use GitHub's open documentation and REST API descriptions, supplemented by
GitHub changelog or version metadata. The domain is recognizable, the OpenAPI
descriptions support exact endpoint and parameter questions, and the prose docs
support conceptual questions. The corpus is broad enough to demonstrate hybrid
retrieval without making the first ingestion iteration unmanageably large.
Date-based API versions and changelog entries are less directly packaged for
relational comparison than Kubernetes releases, so later version-diff data will
require deliberate curation.

### FastAPI

Use FastAPI's documentation, source-derived API reference, and release notes.
This is compact and easy to inspect, but its smaller corpus and weaker
version-relational story would make hybrid retrieval and production-scale
evaluation less convincing.

### Snapshot policies

- **Current pinned snapshot:** smallest reproducible baseline, but it cannot
  support meaningful version comparisons without a later schema expansion.
- **Bounded two-snapshot corpus:** pin current and older docs/OpenAPI commits and
  ingest the changelog interval between them. This adds curation work but
  supports conceptual, exact, and relational questions while keeping the corpus
  bounded.
- **Rolling latest corpus:** demonstrates freshness, but makes retrieval
  experiments non-repeatable and introduces synchronization and deletion
  behavior before the baseline works.

## Decision

Use the **GitHub REST API** as the corpus. It offers the preferred balance of
scope and recognizability: conceptual guides exercise semantic retrieval, the
machine-readable REST API description supplies exact endpoint and parameter
facts, and version/changelog data can support the later SQL route. Compared with
Kubernetes it reduces domain and ingestion complexity; compared with FastAPI it
provides a stronger hybrid-retrieval and portfolio story.

Use a **bounded two-snapshot policy**: pin current and older documentation and
OpenAPI commits, include changelog entries between them, and initially ingest
only one representative REST domain. This preserves repeatable evaluation while
providing real version-difference data for the later SQL route. It costs more
normalization effort than a single snapshot, but avoids the unstable golden sets
and synchronization complexity of a rolling corpus.

Align the snapshots by **official API version**. Use the named GitHub REST
OpenAPI versions `2022-11-28` and `2026-03-10`. Pair each specification with the
latest `github/docs` commit at or before that API version's publication date,
and include the intervening entries from
`github/rest-api-description/descriptions/api.github.com/CHANGELOG.md`.
Official version labels give comparisons stable, explainable identities and
make the later SQL branch easier to defend than arbitrary repository cutoffs.

Every normalized record must preserve the API version, source repository,
source commit SHA, source commit or publication date, source path, and relevant
OpenAPI operation identity. Documentation and specification publication are not
guaranteed to be atomic: the nearest prior docs commit may lag the corresponding
OpenAPI publication. That lag must remain visible in provenance and must not be
silently interpreted as an API change.

Use **GitHub Actions** as that initial domain. The bounded source set includes
three feature slices only:

- workflow runs and workflows:
  `github/docs/content/rest/actions/workflow-runs.md`,
  `github/docs/content/rest/actions/workflows.md`, their matching OpenAPI
  operations, and explicitly selected supporting pages under
  `github/docs/content/actions/`;
- artifacts: `github/docs/content/rest/actions/artifacts.md`, its matching
  OpenAPI operations, and explicitly selected supporting artifact pages under
  `github/docs/content/actions/`;
- Actions secrets: `github/docs/content/rest/actions/secrets.md`, its matching
  OpenAPI operations, and explicitly selected supporting secrets pages under
  `github/docs/content/actions/`.

These paths and operations form a strict source manifest. Directory membership
or an `actions` OpenAPI tag alone does not admit content: every Markdown page
and operation must appear in the allowlist. Other Actions features remain out of
Milestone 1.

Use a **curated core prose** policy alongside the four REST reference files.
The initial supporting-page allowlist is:

- workflows/runs:
  `content/actions/concepts/workflows-and-actions/workflows.md`,
  `content/actions/how-tos/manage-workflow-runs/manually-run-a-workflow.md`,
  `content/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs.md`,
  and
  `content/actions/how-tos/manage-workflow-runs/cancel-a-workflow-run.md`;
- artifacts:
  `content/actions/concepts/workflows-and-actions/workflow-artifacts.md`,
  `content/actions/how-tos/manage-workflow-runs/download-workflow-artifacts.md`,
  and
  `content/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts.md`;
- Actions secrets:
  `content/actions/concepts/security/secrets.md` and
  `content/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets.md`.

The source manifest records every page, REST reference, and matching OpenAPI
operation against its pinned snapshot. It also records the transitive
`data/reusables` and `data/variables` dependencies resolved from the same docs
commit. Dependencies are included because they contribute source text, not
because their containing directories are in scope.

Links to adjacent pages that are not allowlisted remain unresolved-link
diagnostics and citation targets; they never trigger recursive page or subtree
ingestion. This keeps scope auditable while giving each selected feature slice
at least one semantic question from prose and one exact API-reference question
from its REST/OpenAPI material.

Including all three slices creates a richer portfolio demo and a more useful
mix of conceptual, exact-endpoint, status/filter, permission, and lifecycle
questions than any one slice alone. The cost is more resolver/parser coverage,
more retrieval failure modes, and a larger golden-set workload. The strict
allowlist contains that cost and prevents the selection from becoming an
all-Actions ingestion project.

The `github/rest-api-description` repository does not publish a separate
Actions specification: each dated OpenAPI description contains the complete
GitHub REST API. Ingestion must therefore read the pinned monolithic description
and retain only operations belonging to the Actions domain, using the
specification's operation tags rather than treating the whole file as corpus
content. The selected operation and source snapshot must remain in provenance
metadata so version comparisons are auditable.

Use GitHub's official **dereferenced YAML** artifact for each selected OpenAPI
version. After filtering the monolithic specification to Actions-tagged
operations, each canonical operation payload is self-contained rather than
depending on a custom `$ref` resolver. The bounded domain limits the duplication
introduced by expanded component schemas, while the official artifacts avoid
resolver bugs around transitive, cyclic, or polymorphic references.

Expanded request and response schemas remain canonical structured data, not
ready-made embedding input. Concise retrieval text will be derived later from
selected operation fields instead of serializing and embedding each full
expanded schema. Preserve the operation identity, API version, source artifact,
source commit/date, and any original component or operation provenance exposed
by the artifact.

Normalize sources as **source-aware typed records with a shared envelope**.
Every record shares provenance, title, and document-type fields, including the
source repository and path, source commit and date, API version, and any stable
source identity. The payload remains specific to its source:

- a Markdown-section payload preserves its heading hierarchy and section body;
- an OpenAPI-operation payload preserves the HTTP method, path, operation
  identity, parameters, request/response facts, and relevant schema references;
- a changelog-event payload preserves the event date/version, affected
  operation or area when available, and structured change description.

Retrieval text is derived downstream from these typed payloads rather than
becoming the canonical stored representation. This costs more schema and parser
work than flattening every source into `ParsedDoc.text`, but avoids discarding
the exact structure needed for filtering, citations, version comparison, and
source-specific chunking. It also avoids the historical build fragility and
loss of machine-readable API semantics that would come from normalizing
everything through rendered HTML.

Normalize GitHub Docs Markdown with a **targeted source resolver**. Resolve
`{% data reusables... %}` and `{% data variables... %}` dependencies from the
same pinned `github/docs` commit as the referring page, and evaluate supported
product/version conditionals against an explicit GitHub.com target profile.
This produces usable, snapshot-consistent prose without depending on the full
historical GitHub Docs build pipeline.

Each normalized section retains pointers to its source page and resolved
reusable/variable dependencies so included text remains auditable. Unsupported
directives, missing dependencies, recursive includes, and conditionals that
cannot be evaluated must produce explicit diagnostics or ingestion errors;
they must never be silently removed or treated as successfully resolved text.
The constrained resolver costs more implementation and testing effort than
preserving raw Markdown, but avoids embedding template syntax, omitted prose,
or mutually exclusive product variants.

Evaluate supported docs conditionals for the **GitHub Free/Pro/Team (`fpt`)**
product profile only in Phase 1. This keeps the initial corpus bounded, matches
the broadly recognizable public GitHub.com developer experience, and avoids
duplicating near-identical sections before the API-version retrieval baseline
is measured. GitHub Enterprise Cloud (`ghec`) content is deferred; if added, it
will be materialized as separately tagged records rather than merged into
`fpt` prose.

API version and docs product profile are independent provenance dimensions.
Each normalized docs record therefore carries `product_profile=fpt` separately
from its aligned API version (`2022-11-28` or `2026-03-10`). This prevents a
product-tier difference from being misreported as a change between API
versions.

Use **dual logical and revision identity** for normalized records. Each record
type defines a stable `logical_id` for the cross-version concept: for example,
an OpenAPI operation can use its stable method-and-path or operation identity,
while a Markdown section can use its canonical page and heading coordinate.
This identity supports explicit joins and comparisons between the two
snapshots.

Each immutable snapshot instance also receives a `revision_id` derived from its
logical identity, API version, product profile, source commit, and canonical
payload digest. Reprocessing the same source revision is therefore idempotent,
while changed content produces a distinct revision with exact provenance.
Chunks will eventually retain both their logical parent and exact record
revision, but their own identity remains a later decision.

Renames and source-coordinate moves are not silently treated as continuity.
When cross-version continuity matters, it must be represented through an
explicit alias mapping or a later reviewed matching heuristic. This avoids
inventing equivalence between records merely because their content looks
similar.

Persist normalized records with a **hybrid relational envelope and
typed/versioned JSONB payload**. Promote identity and frequently filtered
provenance into typed columns: `logical_id`, `revision_id`, document type, API
version, product profile, source repository, source commit/date, and source
path. Keep source-specific canonical Markdown-section, OpenAPI-operation, and
changelog-event data in a payload whose type and schema version are explicit.

This preserves database constraints and efficient cross-version/provenance
filters without prematurely normalizing expanded OpenAPI schemas into a large
relational model. The promoted columns are the source of truth for shared
envelope fields; JSONB must not carry conflicting copies. Nested facts needed
by later SQL use cases can be exposed through reviewed derived tables or views
once their query requirements are known.

Use **source-aware bounded recursive chunking** for the dense baseline:

- Markdown chunks retain heading ancestry and keep a section whole while it
  fits the shared token cap. Oversized sections split recursively on semantic
  boundaries such as paragraphs, lists, and fenced code blocks, with limited
  overlap between adjacent chunks.
- OpenAPI chunks repeat the operation identity needed to interpret an isolated
  result and group overview/authentication, parameters, request, and response
  facts into bounded field-aware chunks. They do not serialize or duplicate
  entire dereferenced schemas as embedding text.
- Changelog events remain atomic unless an event exceeds the shared cap, in
  which case it uses the same bounded semantic splitting rule.

All source types use a **384-token cap with 48-token overlap**, measured with
the selected embedding model's tokenizer. The cap applies to the final text sent
to the embedding model, including repeated heading ancestry or OpenAPI operation
identity, not only the source payload body. A chunk that exceeds the cap must be
split again or fail validation; silent tokenizer truncation is not allowed.

This is the Milestone 1 baseline, not an assumed optimum. Milestone 2 evaluation
must justify any change to chunk size or overlap against the fixed golden set.
Hierarchical parent-child retrieval is deferred until evaluation shows that fine
chunks need automatic parent expansion. Milestone 1 establishes a simpler dense
baseline rather than introducing multi-granularity ranking before it can be
measured.

Use local **`BAAI/bge-small-en-v1.5`** embeddings pinned to Hugging Face
revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`. The model produces
384-dimensional vectors, and `vector(384)` is a fixed PostgreSQL/pgvector schema
contract for Milestone 1. The pinned model tokenizer measures the final 384-token
chunk limit.

Normalize both document and query embeddings consistently to unit length for
cosine distance. Preserve the model-specific asymmetric retrieval formatting:
document chunks are embedded as passages, while user queries use the BGE
retrieval instruction `Represent this sentence for searching relevant
passages: ` before tokenization and encoding. Store the model ID, revision,
normalization setting, and formatting contract with the index configuration so
queries cannot silently use a different embedding space.

Larger local or hosted embedding models are deferred. Milestone 2 may compare
them only if retrieval metrics identify semantic embedding quality, rather than
chunking or sparse exact-match behavior, as the bottleneck.

Use an **HNSW index with cosine operator classes** for the operational
Milestone 1 dense path. Keep HNSW construction parameters (`m` and
`ef_construction`) and query-time `ef_search` in explicit index/query
configuration rather than relying on invisible defaults. Initial values are
baselines, not conclusions; tuning is deferred until measured retrieval quality
and latency justify a change.

Validate the approximate path against exact pgvector cosine scans on the bounded
corpus and report ANN recall for representative queries. Exact search is the
validation oracle, not the production access path. IVFFlat is deferred because
the small, incrementally ingested corpus does not provide a compelling training
or list-sizing case.

## Failure modes

- Documentation and OpenAPI descriptions may disagree or update on different
  schedules, producing apparently conflicting facts.
- A docs commit selected immediately before an API publication date may still
  describe an earlier state; provenance must expose this publication lag.
- API-version history may be incomplete unless the ingestion snapshot records
  commit and version provenance.
- Generated reference material may dominate retrieval unless document type is
  represented in metadata and evaluated separately.
- An overly broad initial snapshot may slow iteration and make retrieval errors
  difficult to diagnose.

## How I'll measure it

- Every ingested item retains enough provenance to trace it to its source
  repository artifact and version or commit.
- A small inspection set covers all three target query types: conceptual,
  exact lookup, and version/change.
- Milestone 1 includes at least one traceable retrieval and citation example
  for workflow runs/workflows, artifacts, and Actions secrets.
- Phase 1 retrieval will be evaluated on a small golden set before expanding the
  corpus; recall@k will be the primary retrieval metric.

## Open questions / TODO

The design is ready for a first small Phase 0 implementation increment. The
remaining work below either applies already selected policies or can be
introduced as a measured implementation baseline; it does not require another
architecture decision before starting:

- Resolve and record the exact `github/docs` commit SHAs selected by the
  at-or-before publication-date rule.
- Finalize the matching OpenAPI-operation IDs and same-commit reusable/variable
  dependency closure in the pinned source manifest.
- Materialize the selected shared-envelope and versioned typed-payload contract
  as schemas and migrations.
- Derive deterministic chunk revisions from the parent record revision, chunk
  ordinal, and canonical final chunk text while inheriting source provenance.
- Record initial HNSW parameters in configuration and add exact-scan ANN recall
  validation.

PostgreSQL/pgvector is the Milestone 1 dense source of truth. OpenSearch dense
storage remains outside the vertical slice and may be reconsidered with the
Milestone 2 hybrid design.
