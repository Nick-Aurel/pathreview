# Architecture Overview

PathReview is a multi-service application with five major subsystems. This document describes how they fit together.

## High-Level Data Flow

```
User Input (GitHub username, resume PDF, repo URLs)
    │
    ▼
┌─────────────────────┐
│  API Layer (FastAPI) │ ← Authentication, validation, rate limiting
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Ingestion Pipeline  │ ← Parse documents, chunk, embed, store
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Agent Orchestrator  │ ← Plan analysis, execute tools, manage state
│  ┌───────────────┐  │
│  │ GitHub Tool    │  │
│  │ Skill Extract  │  │
│  │ README Scorer  │  │
│  │ Market Analyze │  │
│  │ Tech Detector  │  │
│  └───────────────┘  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  RAG System          │ ← Retrieve context, generate feedback, evaluate
│  (Hybrid Retrieval   │
│   + LLM Generation)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Safety Layer        │ ← Bias check, content filter, PII scrub
└──────────┬──────────┘
           │
           ▼
      Review Output
```

## Subsystem Details

### API Layer (`api/`)
FastAPI application serving REST endpoints. Handles authentication (JWT), request validation (Pydantic), rate limiting, and CORS. Routes delegate to service layer in `core/services/`.

### Ingestion Pipeline (`ingestion/`)
Processes user-submitted documents into vector embeddings. Parsers implement `BaseParser` and extract structured text. Chunkers split text for embedding. The pipeline orchestrates: parse → chunk → embed → store.

### Agent System (`agent/`)
A plan-execute orchestrator that coordinates multiple analysis tools. Each tool implements `BaseTool` with `name`, `description`, and `execute()`. The orchestrator builds a plan based on available profile data, executes tools with retry and timeout policies, and synthesizes results.

### RAG System (`rag/`)
Hybrid retrieval (vector similarity + BM25 keyword) fetches relevant context from the user's ingested documents. The generator uses prompt templates to produce structured, evidence-based feedback. The evaluator scores retrieval relevance and generation faithfulness.

#### Hybrid retrieval scoring

`HybridRetriever` in `rag/retriever/hybrid.py` combines two retrieval channels for each query:

| Channel | Source | Raw score |
|---------|--------|-----------|
| **Vector** | ChromaDB cosine distance via `VectorStore.query()` | Similarity `1 / (1 + distance)` |
| **Keyword** | BM25 via `KeywordSearcher.search()` | `bm25_score` from `rank_bm25` |

**Default weights:** `vector_weight = 0.7`, `keyword_weight = 0.3` (configurable on `HybridRetriever` construction).

**Blending steps** (per candidate chunk in the union of vector and keyword hits):

1. **Normalize** each channel to `[0, 1]` by dividing raw scores by the max score in that channel's result set (if max is `0`, the normalized score stays `0`; empty sets use `default=1.0` to avoid divide-by-zero).
2. **Blend:** `blended = vector_weight × vector_norm + keyword_weight × keyword_norm`.
3. **Filter:** drop chunks with `blended < min_score` (default `0.3`).
4. **Rank:** sort by blended score descending and return up to `max_chunks` (default `10`).

Chunks that appear in only one channel contribute `0` for the missing channel after normalization. Each returned result includes `score` (blended), plus `vector_score` and `keyword_score` for debugging.

**Worked example** (defaults `0.7` / `0.3`, two chunks in both channels):

| Chunk | Vector raw | Keyword raw | Vector norm | Keyword norm | Blended |
|-------|------------|-------------|-------------|--------------|---------|
| A | 0.80 | 2.0 | 1.00 | 0.33 | **0.80** |
| B | 0.40 | 6.0 | 0.50 | 1.00 | 0.65 |

Max vector = `0.80`, max keyword = `6.0`. Chunk A ranks first because the higher default vector weight favors semantic similarity even when B has the stronger keyword match.

### Safety Layer (`safety/`)
Middleware wrapping the generation pipeline. Components run in sequence: prompt injection defense → content filter → bias detector → PII scrubber. All safety events are logged with structured metadata for monitoring.

## Key Design Decisions

See the Architecture Decision Records in `docs/adr/` for context on major decisions:
- [ADR-001: Chunking Strategy](adr/001-chunking-strategy.md)
- [ADR-002: Embedding Model Selection](adr/002-embedding-model.md)
- [ADR-003: Agent Orchestration Approach](adr/003-agent-orchestration.md)
