# PathReview — Module 3 Journal

Working branch: `docs/36-hybrid-retrieval-scoring`  
Claimed issue: [#36 — Architecture doc doesn't explain the hybrid retrieval scoring formula](https://github.com/Nick-Aurel/pathreview/issues/36) (tier-1 / docs)

---

## Week 7

### What I did
- Forked and cloned PathReview; confirmed local `main` tracks my fork (`Nick-Aurel/pathreview`).
- Reviewed `docs/SETUP.md` and `docs/CONTRIBUTING.md` (branch naming + conventional commits).
- Claimed tier-1 issue **#36** (hybrid retrieval scoring formula missing from `docs/ARCHITECTURE.md`).
- Created working branch `docs/36-hybrid-retrieval-scoring` and drafted a solution plan for the docs change.
- Skimmed `HybridRetriever` in `rag/retriever/hybrid.py` to confirm default weights (`vector_weight=0.7`, `keyword_weight=0.3`) before documenting.

### What I learned
- Branch names must use the **GitHub issue number**, not the manifest id (`B-16` → `#36`).
- Submit the **branch URL** (not bare repo/`main`) so graders can see this week’s work.
- The scoring behavior already exists in code; #36 is documentation-only — keep scope to `docs/ARCHITECTURE.md`.

### Challenges / blockers
- Issue numbers on the fork can differ from manifest labels until issues are seeded/linked — resolved by using #36 from the tracker.
- Nested accidental clone / local draft files cluttered `git status`; kept them out of this setup commit.

### Next up
- Implement #36: add a hybrid retrieval scoring section + worked example to `docs/ARCHITECTURE.md`.
- Open a PR once the docs change is ready.

---

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/Nick-Aurel/pathreview/commit/0a1c88d8f0942c569fe6ad6ea414dd45088b3b1d

**Reproduction summary:**
Confirmed locally that `docs/ARCHITECTURE.md` only mentions hybrid retrieval in one sentence and omits the scoring formula, default weights, and example. Cross-checked `HybridRetriever` in `rag/retriever/hybrid.py` (`vector_weight=0.7`, `keyword_weight=0.3`) as the source of truth for the docs gap.

**PLAN.md link:** https://github.com/Nick-Aurel/pathreview/blob/docs/36-hybrid-retrieval-scoring/PLAN.md

**Walkthrough video (recommended):** _Not recorded (optional / not graded)._

**Blockers or open questions:**
None going into Week 9 — next step is implementing the hybrid scoring subsection + worked example in `docs/ARCHITECTURE.md`.

---

## Week 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
Implemented the hybrid retrieval scoring subsection in `docs/ARCHITECTURE.md` (formula, default weights, normalization, filter/rank steps, and worked example aligned with `HybridRetriever`). Added `tests/unit/test_hybrid_retriever.py` to lock in the documented blend behavior, `min_score` filtering, and single-channel edge cases.

**Next steps:**
Run `make check` and `make test-unit`, open the PR with a filled template, and complete Check-in 2 with the PR link.

**Blockers:**

---

### Check-in 2 (end of week)

**PR link:** https://github.com/Nick-Aurel/pathreview/compare/main...docs/36-hybrid-retrieval-scoring?expand=1 (open and submit as ready for review — `Closes #36`)

**Branch:** `docs/36-hybrid-retrieval-scoring`

**What you built:**
Documented how `HybridRetriever` normalizes vector and BM25 scores, blends them with default weights (`0.7` / `0.3`), filters by `min_score`, and ranks results — including a numeric example in `docs/ARCHITECTURE.md`. Added unit tests so the architecture description stays aligned with runtime behavior.

**Tests added or updated:**
`tests/unit/test_hybrid_retriever.py` — default weights, blend formula, `min_score` filtering, single-channel chunks, `max_chunks` cap, and empty-result handling (6 tests, all passing).

**Self-review confirmation:** [x] make check passes (changed files only; pre-existing ruff issues elsewhere) [x] make test-unit passes (new hybrid tests pass; pre-existing collection errors on Python 3.9 `str | None` syntax in unrelated modules — not introduced by this PR)

**Draft PR feedback received from:** none

---

## Week 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes [x] No — still awaiting review

**Summary of feedback:**
No reviewer or maintainer comments arrived on the PR. Per the Summer 2026 course note, reviewer feedback is not a provided feature this term, so there was nothing to action beyond documenting that the review is still pending.

**How you responded:**
N/A — no feedback received.

---

### Reflection

**What was harder than you expected?**
Keeping a “docs-only” change honest against live behavior. `docs/ARCHITECTURE.md` only mentioned hybrid retrieval in one sentence, but writing the scoring section meant carefully reading `HybridRetriever` in `rag/retriever/hybrid.py` so the formula, default weights (`vector_weight=0.7`, `keyword_weight=0.3`), normalization, `min_score` filtering, and ranking matched what the code actually does — not a simplified story. Local `make check` / `make test-unit` also surfaced pre-existing ruff issues and Python 3.9 `str | None` collection errors in unrelated modules; figuring out what was in scope versus noise took more judgment than I expected for a documentation PR.

**What did you learn about working in a large codebase?**
Contributing to someone else’s production-shaped repo is different from greenfield work: you navigate an existing RAG layout (ingestion → retriever → generator → agent), follow `docs/CONTRIBUTING.md` conventions, and stay scoped so you don’t “fix” adjacent stubs. I also learned process details that don’t show up in a personal project — branch names use the GitHub issue number (`#36`), not the manifest id (`B-16`), and graders need the `/tree/<branch>` URL so they see `JOURNAL.md` on the working branch instead of `main`.

**How did AI tools help — and where did they fall short?**
AI helped me locate `HybridRetriever`, draft the architecture subsection and worked example, and scaffold unit tests around blend behavior and edge cases. It fell short when defaults or edge cases had to be verified against the real implementation — I still had to read `hybrid.py` myself and write `tests/unit/test_hybrid_retriever.py` so the docs couldn’t drift from runtime behavior. AI also couldn’t decide scope for me when the repo had pre-existing lint/test failures outside my files.

**What would you do differently if you started over?**
I’d open a formal pull request earlier in Week 9 instead of relying mainly on a compare link, and I’d keep the reproduction commit and `PLAN.md` even tighter so Week 8 → Week 9 handoff was one clear path. I might also record the optional walkthrough — not for points, but to force a clearer explanation of the scoring formula before writing the docs.

**What are you most proud of from this module?**
Shipping an architecture subsection that documents the real hybrid blend (normalize → weighted sum → filter → rank) and backing it with unit tests so the documentation stays tied to `HybridRetriever` instead of becoming aspirational prose.
