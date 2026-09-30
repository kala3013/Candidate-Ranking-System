# COMPLETION PROMPT — TalentRank AI (Candidate Ranking System)

Audit date: 2026-09-26 · Scope: `frontend/index.html`, `frontend/script.js`, `app.py`, `models/*`
Method: static read + live API verification against a running server (Flask, `127.0.0.1:5000`).

---

## PART 1 — VERIFIED GAP LIST

### P0 — Demo-breaking (confirmed by live API test)

**1. Recruiter Copilot returns HTTP 500 on its headline questions.**
Root cause: `app.py:259` serialises each candidate as `'profile'`, but `models/copilot.py`
reads `c['candidate_profile']` in 8 places — lines **227, 251, 281, 301, 418, 458, 532, 533**.
`/api/copilot` (`app.py:504-525`) has no `try/except`, so the `KeyError` becomes a 500 and
`sendCopilotQuery()` (script.js:2063-2096) shows a red error bubble in the chat.

Live test results (after `/api/analyze-sample` → 6 candidates):
```
[500] show top 3 candidates                <<< FAILS
[500] who has python skills                <<< FAILS
[500] compare candidate 1 and candidate 2  <<< FAILS
[OK ] who should we hire
```

**2. Copilot intent routing is wrong for natural demo phrasings.**
- `"summarize the candidate pool"` → routed to `_handle_specific_candidate`
  (`_is_specific_candidate_query`, copilot.py:147-155, matches `candidate\s+(\w+)`) →
  answers *"I couldn't find that candidate"*.
- `"tell me about candidate 1"` → same dead end. `_extract_candidate_names`
  (copilot.py:506-528) only resolves `#N` ranks and name substrings — **not** `candidate 1`
  or ordinals ("the second candidate").
- `"which skill is missing the most"` → falls through to the generic fallback because
  `_is_missing_skills_query` (copilot.py:115-123) has no pattern for `missing the most`.

### P1 — Feature is visible but non-functional

**3. "⚙️ Custom Scoring Weights" sliders are cosmetic.**
`state.customWeights` (script.js:30) only updates the `weightTotal` label
(script.js:1676-1689). It is **never sent to the server** — `analyze()` posts only
`job_file`/`job_description` + `resumes` (script.js:646-651), `app.py` has no `weights`
handling, and `CandidateScorer.compute_all_scores` (scorer.py:241-323) hardcodes weights.
Dragging a slider changes nothing. `showCandidateDetail` even hardcodes "35%/20%/15%…"
labels in the modal. Side effect: `state.weightsInitialized` (script.js:31, 1640, 1671) is
never reset, so `resetWeights()` cannot re-render the sliders from state.

**4. Sort and filter desynchronise (wrong rows filtered).**
`sortBy()` re-orders DOM rows via `tbody.appendChild(row)` (script.js:1052), but
`applyFilters()` pairs **DOM position** with data via `candidatesData[idx]`
(script.js:962-963). After any column sort, filters evaluate the wrong candidate, and
`filterTable()` (`#searchInput`) sets `row.style.display = ''`, silently **undoing** the
other filter bar's work. Two competing search boxes sit in the same header
(`#searchInput` + `#filterName`).

**5. "Multi-Job Batch Analysis" is a stub — always 1 role.**
`runMultiJobAnalysis()` (script.js:2746-2753) hardcodes a single `primary_role` job with
only `{role}`. `app.py:939-965` reuses the *same* ranked candidate list for every job, so
"Roles = 1", talent overlap = all candidates, and hiring priorities are meaningless.
The backend (`multi_job_analyzer.py`) is fully built and unused.

**6. Pro Features tab is enabled once, by a MutationObserver hack.**
script.js:2776-2797 monkey-patches around `tabRankings.disabled`, calls
`populateFeatureSelects()` once, then `obs.disconnect()`. On a **second** analysis the
candidate dropdowns keep the previous run's names/indices, and `restoreHistory()`
(script.js:2716-2727) never enables or repopulates them at all.

**7. Backend features with zero UI wiring.**
Endpoints implemented in `app.py` but never called by any frontend file:
`/api/executive-summary` (970), `/api/demo-config` (981), `/api/features-list` (988),
`/api/analytics` (535), `/api/export` (606), `/api/salary-compare` (738),
`/api/team-fit/compare` (880), `/api/skill-gaps/<i>` (431), `/api/interview-questions/<i>`
(445), `/api/potential/<i>` (459), `/api/bias-report/<i>` (473), `/api/candidate-summary/<i>` (487).
`DemoModeController` and `ExecutiveDashboardGenerator` (industry benchmarks) are imported at
`app.py:32` and never used from the UI. The Pro Features tab has only 8 cards (ATS, Salary,
Career, Email, Diversity, Team Fit, History, Multi-Job) — no Executive Dashboard, no Demo Mode.

**8. Hardcoded origin.** `#downloadBtn` points at `http://127.0.0.1:5000/api/download`
(index.html:275) while everything else uses `API_BASE`; breaks on any other host/port
(`app.py` honours the `PORT` env var).

### P2 — Polish / risk

- Chart.js loads from `cdn.jsdelivr.net` (index.html:12) — analytics + score chart break offline.
- `renderScoreDistribution` / `renderSkillCoverage` replace the chart card's innerHTML with
  "no data" text (script.js:1802-1806, 1840-1856), permanently destroying the `<canvas>`.
- No client-side guard before `analyze()`; an empty JD surfaces the server's
  "Empty job description" as a generic error toast.
- `renderBiasReport` only runs on tab switch (script.js:443-445), so Bias-Free is stale after
  a re-analysis until the user leaves and returns to the tab.
- `server.log` (24 KB) is committed at the repo root; `TASK_PLAN.md` Phase 4 items
  (PDF endpoint, batch export, rate limiting, caching) are still open.

---

## PART 2 — READY-TO-PASTE COMPLETION PROMPT

> You are completing the **TalentRank AI** candidate-ranking system at
> `c:\Users\ELCOT\Desktop\Hospital-website\candidate-ranking-system`.
> It is a Flask + vanilla-JS app (`app.py`, `models/`, `frontend/index.html`,
> `frontend/script.js`, `frontend/style.css`). Vanilla ES6 only — **no frameworks, no
> build step, no new npm packages**. Keep the existing glassmorphism UI, emoji, and
> code style (`// ==== SECTION ====` comments, camelCase, `showToast()`, `escapeHtml()`).
> Do not add a database or auth.
>
> **Contract to respect:** each candidate in `_current_results['ranked_candidates']`
> has keys `rank, candidate_id, candidate_name, final_score, scores, reason, profile,
> skill_gaps, potential, interview_questions, bias_free, candidate_summary`
> (see `app.py:252-265`). **`profile` is the only key — never `candidate_profile`.**
>
> ### 1. Fix the Copilot (highest priority)
> - Replace every `c['candidate_profile']` in `models/copilot.py` (lines 227, 251, 281, 301,
>   418, 458, 532, 533) with the correct `c['profile']` key, or normalise once at the top of
>   `process_query()`. Use `.get()` with sane defaults everywhere.
> - Wrap `/api/copilot` (`app.py:504`) in `try/except` returning `jsonify({'error': ...}), 500`
>   so a failure never returns an HTML 500 page.
> - Fix intent ordering in `_classify_and_respond`: run `_is_summary_query` **before**
>   `_is_specific_candidate_query`, and tighten the `candidate\s+(\w+)` pattern.
> - Extend `_extract_candidate_names` (copilot.py:506) to resolve `candidate 1`,
>   `candidate #2`, `rank 3`, and ordinals ("first", "second", "top candidate").
> - Add a pattern so "which skill is missing the most" hits `_handle_missing_skills_query`.
> - Add 4 suggested-prompt chips to the Copilot tab that map 1:1 to working intents.
>
> ### 2. Make the Weights Configurator real
> - Send `state.customWeights` with the `/api/analyze` request (FormData key `weights`, JSON).
> - In `app.py::_handle_file_upload` / `_handle_json_input`, parse `weights`, validate all
>   seven keys (`skill_match, experience_match, project_relevance, semantic_similarity,
>   education, certifications, behavioral_score`), clamp to `[0,1]`, normalise to sum 1.0,
>   and fall back to `scorer.py` defaults when absent/invalid.
> - Give `CandidateScorer.compute_all_scores` an optional `weights=None` parameter that
>   overrides the hardcoded constants (scorer.py:300-323) without changing defaults.
> - Add a **"⚡ Re-rank with these weights"** button next to "🔄 Reset to Default"
>   (index.html:527-529) that re-posts the last JD + resumes, shows progress, and refreshes
>   rankings + analytics. Disable it while running.
> - Replace the hardcoded `'35%'`, `'20%'`, … labels in `showCandidateDetail` with live values
>   from `state.customWeights || DEFAULT_WEIGHTS`.
> - Reset `state.weightsInitialized = false` in `resetWeights()`.

>
> ### 3. Make sort + filter correct
> - Add `data-candidate-id` to every `<tr>` at render time and rewrite `applyFilters()` to look
>   candidates up by `row.dataset.candidateId` instead of DOM position.
> - Call `applyFilters()` at the end of `sortBy()` so sorting and filtering compose.
> - Delete the duplicate `#searchInput` / `filterTable()` path; bind the header search box to
>   `applyFilters()`. Keep exactly one search input.
> - Add a "Sort: Rank ↑" indicator plus `aria-sort` on the active `<th>`.
> - Keep `#resultsMeta` in sync ("Showing X of Y") whenever rows are hidden.
>
> ### 4. Wire the Pro Features tab properly
> - Remove the MutationObserver/monkey-patch block (script.js:2776-2797). Enable `tabFeatures`
>   inside `analyze()`, `runSample()`, and `restoreHistory()`, and call `populateFeatureSelects()`
>   after **every** one of them.
> - Make **Multi-Job Batch Analysis** real: add a role multi-select (Data Scientist / ML Engineer /
>   Full Stack / Product / Analytics) posting `{jobs: {role_key: {job_profile: {...}}}}` with
>   distinct `required_skills`, `experience_required`, and `domain` per role; update
>   `app.py:939-965` to re-score candidates per role instead of reusing one ranked list, and
>   render the per-role cards, hiring priorities, and talent overlap the backend already returns.
> - Add three new cards: **Executive Dashboard** (`GET /api/executive-summary` — pool score,
>   industry benchmark bars, insights), **Demo Mode** (`GET /api/demo-config` +
>   `DemoModeController`) with a guided auto-play button, and **Offer vs Market**
>   (`POST /api/salary-compare`).
>
> ### 5. Robustness / polish
> - Replace the hardcoded `http://127.0.0.1:5000/api/download` (index.html:275) with a
>   JS-driven download built from `API_BASE`.
> - Guard `analyze()`: require a JD **and** ≥1 resume before POSTing, and show the reason
>   inline next to the button.
> - When a chart has no data, hide the canvas instead of replacing the card's innerHTML.
> - Re-render the Bias-Free report and shortlist after a new analysis, not only on tab switch.
> - Guard Chart.js usage behind `typeof Chart !== 'undefined'` with a fallback notice so the
>   rest of the app still works offline.
> - Delete the committed `server.log` and add it to `.gitignore`.
>
> ### Acceptance criteria (verify before reporting done)
> 1. `POST /api/analyze-sample`, then these Copilot queries all return **200 with a useful
>    answer**: "show top 3 candidates", "who has python skills", "compare candidate 1 and
>    candidate 2", "tell me about candidate 1", "summarize the candidate pool",
>    "which skill is missing the most", "who should we hire".
> 2. Move a weight slider → click Re-rank → the order, scores, and Analytics tab change, and the
>    total badge shows 100%.
> 3. Sort by "AI Match" descending, then apply the "Excellent (80%+)" filter → the correct rows
>    hide and the visible count matches.
> 4. Run a second analysis → the Pro Features dropdowns list the new candidates.
> 5. Multi-Job with 3 roles selected → 3 role cards, non-zero overlap, ranked priorities.
> 6. No console errors when switching across all 7 tabs; no 500s in the server log.
>
> Work through the sections in order, run `python app.py` to smoke-test, and report what
> changed with before/after evidence for each acceptance criterion.

