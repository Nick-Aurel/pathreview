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

## Week 8

_TBD_

---

## Week 9

_TBD_

---

## Week 10

_TBD_
