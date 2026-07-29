## Solution plan

**Issue:** [#36 — Architecture doc doesn't explain the hybrid retrieval scoring formula](https://github.com/Nick-Aurel/pathreview/issues/36)  
Manifest id: `B-16` in `scripts/issues_manifest.json`

### Reproduction (confirmed locally)

On branch `docs/36-hybrid-retrieval-scoring`, I confirmed the issue exists in this local checkout:

- Opened `docs/ARCHITECTURE.md` → RAG subsection is a one-sentence overview of hybrid retrieval (vector + BM25). It does **not** document the blend formula, default weights, filtering (`min_score`), or a worked example.
- Cross-checked `rag/retriever/hybrid.py` → `HybridRetriever` already implements the scoring behavior (`vector_weight=0.7`, `keyword_weight=0.3`, normalize-by-max, blend, filter, top-k).

**Expected:** Architecture docs explain the hybrid scoring formula, default weights, and include a worked example so contributors understand ranking without diving into code first.

**Actual:** The RAG subsection is a one-sentence overview. The real logic already lives in `HybridRetriever.retrieve()` but is undocumented at the architecture level.

### Understand

**Root cause:** `docs/ARCHITECTURE.md` only mentions that the RAG system uses hybrid retrieval (vector similarity + BM25 keyword). It never documents *how* those scores are combined, what the default weights are, or how results are filtered and ranked. Someone reading the architecture doc cannot reconstruct the scoring behavior without reading the source.

### Map

| Role | Path |
|------|------|
| **Edit (primary)** | `docs/ARCHITECTURE.md` — add a hybrid scoring subsection under RAG |
| **Source of truth (read-only)** | `rag/retriever/hybrid.py` — `HybridRetriever` (`vector_weight=0.7`, `keyword_weight=0.3`, normalize-by-max, blend, `min_score`, top-k) |
| **Supporting context (read-only)** | `rag/retriever/vector_store.py` — distance → similarity `1 / (1 + distance)` |
| **Supporting context (read-only)** | `rag/retriever/keyword_search.py` — BM25 scores via `rank_bm25` |

**Files expected to touch:** `docs/ARCHITECTURE.md` only (per issue scope). No application code changes.

### Plan

1. Confirm the formula and defaults against `HybridRetriever` (normalize each channel by its max score in the candidate set, then `0.7 * vector_norm + 0.3 * keyword_norm`; drop below `min_score`; sort; take `max_chunks`).
2. Add a `#### Hybrid retrieval scoring` (or similarly titled) subsection under `### RAG System (`rag/`)` in `docs/ARCHITECTURE.md`.
3. Document: channels involved, normalization, blend formula with default weights, post-blend filter/rank behavior, and briefly where vector vs BM25 scores come from.
4. Add a short numeric example table showing two chunks with different vector/keyword strengths and the resulting blended scores (so the weight bias is obvious).
5. Proofread against the rest of `ARCHITECTURE.md` for tone/structure; verify the example math matches the documented formula.

### Inputs & outputs

**Inputs:**
- Issue requirements (explain formula + default weights + example)
- Existing scoring behavior in `rag/retriever/hybrid.py` (and related score producers)

**Outputs:**
- Updated `docs/ARCHITECTURE.md` with a clear hybrid retrieval scoring section and example
- No runtime behavior change; no new APIs or config

### Risks & unknowns

- **Doc drift:** If weights or the formula change later in code, the architecture section can go stale — mitigate by stating defaults as implemented in `HybridRetriever` and optionally pointing at `rag/retriever/hybrid.py`.
- **Scope creep:** Tempting to document full RAG pipeline or fix placeholder wiring in `review_service.py` — out of scope for this docs issue.
- **Over-detail:** Too much BM25/Chroma math could overwhelm an architecture overview — keep score-source notes brief.

### Edge cases

Docs should make these code behaviors clear (without needing to “handle” them in code for this issue):

- Chunk appears in only one channel → missing channel contributes `0` after blend.
- Empty result set / max score of `0` → normalization guards avoid divide-by-zero (`default=1.0` / score stays `0`).
- Scores below `min_score` (default `0.3`) are dropped even if they appeared in search results.
- Example should use values that remain valid after normalization (norms in `[0, 1]`) so readers aren’t confused by raw BM25 or distance scales.
