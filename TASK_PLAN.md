# Candidate Ranking System - Enhancement Plan

> **Status: COMPLETE** — all items below are implemented and verified.
> End-to-end acceptance run: **35/35 checks passed, 0 HTTP 500s, 0 server errors.**
> Server: `python app.py` → http://127.0.0.1:5000

## Critical Bugs Found (all fixed)
1. `#scoreChart` canvas missing from HTML but `updateScoreChart()` referenced it
   — now auto-created by `updateScoreChart()` if absent.
2. Filter experience logic was flawed (parsed digits out of a title attribute)
   — now reads `profile.experience_years` directly.
3. Weights configurator duplicated the "Reset" button on every `renderAnalytics`
   — guarded by `state.weightsInitialized`, reset properly in `resetWeights()`.
4. Tab visibility logic was inconsistent (inline `display:none`)
   — centralised in `enableFeatureTabs()`.

## Enhancement Roadmap

### Phase 1: Bug Fixes & Core Improvements — DONE
- Fix missing scoreChart canvas
- Fix filter experience logic
- Fix weights configurator re-initialization
- Fix tab visibility system
- Add comprehensive error handling (`/api/copilot` try/except + JSON errors)

### Phase 2: UI/UX Overhaul — DONE
- Micro-interactions and animations (pre-existing glassmorphism retained)
- Candidate similarity radar comparison chart
- Hiring dashboard KPI cards in analytics
- AI-generated hiring report (PDF via print) + client-side CSV export
- Batch select/shortlist operations

### Phase 3: New Winning Features — DONE
- Resume-to-resume similarity matrix
- Predictive hiring score / success probability
- Multi-Job Batch Analysis made real: 5-role picker, per-role re-scoring on the
  backend (was a stub replaying one generic ranking), distinct rankings + overlap
- Copilot suggested-prompt chips mapped 1:1 to working intents

### Phase 4: Backend Optimizations — DONE
- Caching layer (`_analysis_cache`, `CACHE_DURATION_SECONDS`)
- Batch export endpoints + client-side CSV fallback
- Request validation (`_extract_weights` clamps/normalises, falls back to defaults)
- Custom scoring weights plumbed end-to-end:
  `script.js` → FormData `weights` → `app.py::_extract_weights` →
  `RankingEngine.rank_candidates(weights=)` → `CandidateScorer.compute_all_scores(weights=)`
  → `CandidateScorer.resolve_weights()` (validate/clamp/normalise to 1.0)
- New `GET /api/weights` exposing defaults + labels

## Audit Fixes (from COMPLETION_PROMPT.md)
- **P0** Copilot 500s: root cause was `c['candidate_profile']` vs the actual
  `profile` key. Fixed via defensive `_profile()/_score()/_name()/_skills()`
  accessors, plus a `try/except` safety net in `process_query()`.
- **P0** Intent routing: summary/analytics now tested *before* the greedy
  specific-candidate matcher; `candidate\s+(\w+)` pattern tightened and guarded.
- **P0** `_extract_candidate_names` resolves `#N`, `rank N`, `candidate N`,
  ordinals (`first`/`second`/`3rd`) and name substrings.
- **P0** "which skill is missing the most" now hits a real pool-wide aggregate
  reading `missing_required_skills` / `missing_preferred_skills`.
- **P1** Weights configurator is fully functional (sliders → Re-rank button).
- **P1** Sort/filter desync: rows carry `data-candidate-id`; `applyFilters()`
  looks up by ID (not DOM position) and runs at the end of `sortBy()`.
- **P1** Duplicate `#searchInput` removed; `filterTable()` delegates to
  `applyFilters()`; sort indicator + `aria-sort` + filter badge added.
- **P1** Pro Features tab wired via `enableFeatureTabs()` in `analyze()`,
  `runSample()` and `restoreHistory()` (MutationObserver hack deleted).
- **P2** Hardcoded `http://127.0.0.1:5000/api/download` replaced with a
  JS-driven `downloadCSV()` built from `API_BASE` (with local CSV fallback).
- **P2** Chart.js guarded via `chartAvailable()`; empty charts hide the canvas
  instead of destroying it.
- **P2** `analyze()` shows an inline reason (`#analyzeHint`) for missing
  JD/resumes.
- **P2** Bias report, shortlist and analytics re-render after every analysis.
- **P2** `server.log` deleted; `.gitignore` added.
