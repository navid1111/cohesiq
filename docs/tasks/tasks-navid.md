# Tasks — Navid (Data · YouTube · Matching Engine · Seeding)

Derived from `docs/plan.md` (the unified plan). Source of truth chain:
`requirements.md` → `srs.md` → `plan.md` → this file. Schema reference: `docs/schema.md`.

**Ownership:** the *intelligence + data* half of Cohesiq — YouTube ingestion, the matching
engine, semantic/LLM services, seeding, normalization, authenticity scoring, and the optional
graph/vector layers. Sakib owns the brand/creator marketplace UI & campaign workflow (`tasks-sakib.md`).

## Legend
- `[x]` Done & verified · `[~]` Partial / needs work · `[ ]` Not started · `[!]` Broken · `[P]` Parallelizable

---

## Done — current baseline

| Item | Status | Evidence |
|---|---|---|
| YouTube Tier-0 public read wrapper | `[x]` | `app/youtube/{router,service,schemas}.py`, mounted `/youtube` |
| Channel enrichment (creator-ready metrics) | `[x]` | `GET /youtube/channels/enrichment` → subs, avg views/likes/comments, est. engagement, uploads/month |
| YouTube unit + smoke tests | `[x]` | `tests/test_youtube_service.py`, `scripts/test_youtube_api.py` |
| Pure deterministic scorer | `[x]` | `services/matching.py` + `services/matching_config.py` — current weights: niche .35 / budget .30 / platform .15 / engagement .10 / language .08 / recency .02 |
| `run-matching` + `matches` endpoints | `[~]` | `app/campaigns/` — relational, top-5 Groq rationale when configured, persisted score breakdown; rank column still pending only if UI needs stored rank |
| Semantic similarity (Gemini + token fallback) | `[~]` | `services/semantic_match.py` — computed on the fly, persisted as `score_semantic`; wrong-niche rescue is capped in `score_niche` |
| Seed pipeline (synthetic + real YouTube script) | `[x]` | `scripts/generate_seed_data.py` (Tavily+Groq), `seed_db.py`, `reset_db.py`, `sync_clerk_users.py`, `seed_real_youtube_creators.py` — live run verified: 19 channels succeeded, 0 failed |
| YouTube enrichment persistence + normalization | `[x]` | N01/N02/N03/N12 all verified. `POST /creators/{id}/platforms/youtube/enrich` persists to `creator_social_profiles`; `normalization.py` handles niche/language/city/tier; 19 YouTube `verified` + 38 estimated profiles + 190 portfolio items seeded. See `docs/revisions/srs-revisions-26-06-07.md` §3. |

---

## Phase D — Real data + matching depth (current focus)

**Goal:** turn the stateless YouTube wrapper into persisted, matchable creator data; make the
matching pipeline transparent end-to-end; ship authenticity scoring and ethical-AI data tags.

[x] N01 [P] Persist YouTube enrichment → `creator_social_profiles`
  - Add `POST /creators/{creator_id}/platforms/youtube/enrich` (body: `channel_ref`, `recent_video_limit`)
  - Map enrichment output → social profile columns per `youtube_implementation.md` "Recommended mapping", plus two fields the recommended mapping omits:
    - `posts_per_month = enrichment.uploads_per_month` (schema column exists, mapping doc skips it)
    - `api_channel_id = enrichment.platform_user_id` (the YouTube channel ID)
  - Add `is_api_verified`, `api_verified_at`, `api_channel_id` columns via migration `0016` (schema.md extension point)
  - Keep persistence in `app/creators/` — the YouTube wrapper stays stateless
  - Verified with `docker compose exec backend python -m unittest tests.test_creator_youtube_enrichment tests.test_youtube_service -v`

[x] N02 Seed real BD YouTube channels (SRS US-3)
  - Discover known refs via `GET /youtube/channels?handle=` (1 unit each); use `Search.list` only when explicitly batch-enabled because it costs 100 units per name.
  - Seeder now carries a 100-name BD YouTube creator inventory. Entries with known handles/channel IDs seed directly; unresolved display names are skipped unless `YOUTUBE_SEED_SEARCH_RESOLVE_LIMIT` is set for an explicit, quota-aware search-resolution batch.
  - Add proportional synthetic IG/TikTok companion profiles labelled `"Estimated"` (N09, US-19)
  - Verified with `docker compose exec backend python -m scripts.seed_real_youtube_creators`; latest demo DB has 67 resolved creators from the 100-name inventory.
  - Verified DB counts: 67 YouTube `verified`, 67 Instagram `estimated`, 67 TikTok `estimated`.
  - Remaining unresolved YouTube handles are not needed for the current demo supply pool.
  - Seed bios are generated from public channel descriptions plus the last five recent-video descriptions; city is left unset to avoid confusing creator location with audience/content location.
  - Generated-bio behavior verified with `docker compose exec backend python -m unittest tests.test_creator_youtube_enrichment tests.test_youtube_service -v`.

[x] N03 Normalization at ingestion (SRS US-4, FR-26)
  - Niche: YouTube `topicCategories` Wikipedia URL → internal `niches` table via `YOUTUBE_CATEGORY_MAP` dict
  - Optional Groq classifier: when `GROQ_API_KEY` exists, classify niche from channel description plus last five video titles/descriptions; invalid/missing Groq output falls back to YouTube topic categories, then generic `Lifestyle`.
  - Language: detect Bangla/English/Banglish from video **titles+descriptions**; current implementation uses deterministic script/keyword heuristics and stores on `creator_social_profiles.content_languages`. Note: full captions require a separate `captions.list` API call not in the Tier-0 enrichment endpoint — detection on titles+descriptions is the correct Tier-0 scope.
  - Tier: map follower count → nano/micro/macro/mega; compute engagement vs tier benchmark for N06
  - City: unrecognised city strings → `unknown_location` bucket, never silently dropped (SRS §4.4)
  - Implemented as deterministic Tier-0 normalization in `app/creators/normalization.py`: topic-category niche map, Bangla/English/Banglish heuristic from titles/descriptions, city fallback, and engagement-vs-tier ratio helper.
  - Verified with `docker compose exec backend python -m unittest tests.test_creator_youtube_enrichment tests.test_youtube_service -v`

[ ] N04 Persist full score breakdown to `ai_match_scores` (SRS FR-10, plan Phase C)
  - `score_platform`, `score_recency`, `score_semantic`, and all deterministic sub-scores are already present and written by `run_campaign_matching`
  - Remaining decision: add a stored `rank` column only if the UI/API needs rank persisted instead of derived from sorted response order
  - Update `AIMatchScoreOut` Pydantic schema if any newly exposed score/rank field is missing from API responses
  - Coordinate with Sakib: these columns unlock the six-bar breakdown in `MatchesClient.tsx`

[~] N05 [P] Bounded LLM rationale service (SRS FR-9)
  - Groq rationale call now runs only on the top 5 sorted matches when `GROQ_API_KEY` is configured
  - Prompt is grounded in campaign text, creator bio, and an English-only recent-content evidence brief; ranking still uses deterministic scores only
  - Output is capped to two sentences and post-processed to avoid copied Bangla/non-ASCII text and canned "Based on..." openers
  - Verified with `docker compose exec backend python -m unittest tests.test_matching_engine -v` and `docker compose exec backend python -m scripts.test_matching`
  - Heuristic fallback when `GROQ_API_KEY` absent or generation fails (keeps matching testable without a key)
  - Resolve `services/llm_matching.py` — integrate into the pipeline or delete; no dead experimental paths
  - Coordinate with Sakib D02: the Gemini call structure here will be reused by the AI Brief Analyzer

[ ] N06 Authenticity / Trust Score MVP (SRS US-11, FR-12)
  - Engagement-vs-tier proxy: how far creator's engagement falls below tier benchmark → 0–100 score
  - Flag labels + plain-language reason (e.g. "engagement 2× above micro average — low fraud signal")
  - Store score on `creator_social_profiles` or a new `creator_trust_scores` table (decide before migration)
  - Surface result to Sakib: D01 Authenticity Auditor UI card reads this score
  - Note: follower growth-spike Z-score needs TimescaleDB history (Phase E, N14) — not a blocker for MVP proxy

[ ] N07 Formalize the 5-stage gated funnel (SRS US-12)
  - Label stages explicitly in `services/matching.py`:
    1. Hard filter (SQL — platform, budget, follower range, availability)
    2. Relational conflict check (N08)
    3. Semantic ranking (on-the-fly cosine, `semantic_match.py`)
    4. Deterministic weighted score
    5. LLM rationale on top-N only
  - Document which stages are active vs deferred in `plan.md` §4 Phase D after implementation

[x] N08 [P] Relational conflict-of-interest check (SRS FR-13, lighter-than-Neo4j first cut)
  - Concept doc: `docs/concepts/conflict-of-interest.md`
  - Added `brand_category` to `brand_profiles` and `campaigns` via migration `0018`.
  - Stage-2 gate now excludes creators who collaborated with a different registered brand in the same `brand_category` within 90 days.
  - Uses product category, not creator niche: pen vs edtech is allowed; two pen brands conflict.
  - Debug visibility: `scripts.test_conflict_matching` prints same-category conflict audit rows for baseline creators excluded by the gate.
  - Verified with `docker compose exec backend python -m scripts.test_conflict_matching`.
  - Future extension: persist conflict audit metadata and add category capture for unregistered historical brands if needed.
  - No Neo4j needed for this cut (D2); superseded by N16 if Neo4j is built later

[ ] N09 [P] Ethical-AI data tags at ingestion (SRS US-19, NFR-14/15/16)
  - Mark all synthetic/estimated fields explicitly: `data_source = "estimated"` on `creator_social_profiles`
  - Mark API-verified fields: `data_source = "verified"`, `api_verified_at` timestamp
  - Under-18 audience flag: if `audience_age_range_max < 18` or demographic data shows >20% under-18, set a flag on the profile
  - Staleness: `stats_reported_at` must be populated at ingestion; surface in API response for Sakib to render in UI
  - "Uncategorized %" — for incomplete demographic data never redistribute; pass the remainder explicitly as uncategorized

[ ] N10 [P] Per-campaign engagement snapshots (SRS US-20, plan Phase D)
  - After a collaboration reaches `completed` status, pull creator's public metrics at Day 7, Day 14, Day 30
  - Store snapshots as a simple table (`campaign_engagement_snapshots`) referencing `campaign_applications.id`
  - Expose via a new endpoint (shape to confirm with Sakib for C02 analytics panel)
  - Use cached enrichment data (N01) — no extra API calls if stats were recently fetched

[x] N11 Align `scripts/test_matching.py` to call the live run-matching path correctly
  - Strategy document: `matching_engine_plan.md`
  - Script now exercises the same live service layer via `run_campaign_matching`
  - Added matching-engine unit coverage for budget buffer, recency buckets, semantic rescue cap, and 0–1 score normalization
  - Verified with `docker compose exec backend python -m unittest tests.test_matching_engine -v`
  - Verified against seeded data with `docker compose exec backend python -m scripts.test_matching`

[x] N12 [P] Portfolio import from recent YouTube videos (youtube_task.md Unit 3)
  - After N01 persists the social profile, import `enrichment.recent_videos` → `creator_portfolio_items`
  - Each `YouTubeRecentVideo` maps to one portfolio row: `content_url`, `title`, `thumbnail_url`, `views`, `likes`, `comments`, `published_at`, `platform = "youtube"`, `niche_id` from normalization (N03)
  - Upsert by `content_url` so re-running enrichment doesn't duplicate rows
  - Only import videos missing from the portfolio (compare against existing `creator_portfolio_items`)
  - Implemented in `app/creators/service.py` and wired into `POST /creators/{creator_id}/platforms/youtube/enrich` plus `scripts/seed_real_youtube_creators.py`.
  - Verified with live seeder and `scripts.test_matching`; current demo DB uses the 67 resolved YouTube creators from the 100-name inventory.

[x] N19 Editorial HTML diagram set (diagram-design skill, `cohesiq` profile)
  - `docs/diagrams/html/` — architecture, backend layers, journey swimlane, matching pipeline, score weights, run-matching sequence, application + contract state machines, two ER diagrams; `index.html` links them
  - Generated by `python3 docs/diagrams/html/build.py` (shared primitives in `_lib.py`); facts checked against `campaigns/service.py`, `matching_config.py` and the models, not only the docs
  - Verified with the skill's `self_check.py` and `verify-geometry.py` (0 findings on all 10 files)

[x] N20 Technical design document (`docs/diagrams/html/technical-document.html`)
  - 12 sections embedding all 10 figures; generated by `techdoc.py`, which `build.py` runs after the diagrams, so figures never drift from the standalone pages
  - Claims checked against code (routes, auth, compose/entrypoint, env examples, polling, matching fallback, test counts)
  - PDF export: `export_pdf.py` (Playwright/Chromium, A4) → `technical-document.pdf`; linked from README
  - §12 lists gaps G1–G9 found while checking (unused `disputed`, overloaded `invited`, CORS `*`, blocking calls in async handlers, missing `CLERK_WEBHOOK_SECRET` in `.env.example`, …) — not yet triaged into tasks

---

## Phase E — Optional heavy layers (deferred by design, plan §3 D1–D5)

Do **not** start these until Phases A–D are demo-solid. Each is purely additive (NFR-3/4).

[ ] N13 YouTube quota guard + `Search.list` circuit-breaker (plan D8, NFR-8)
  - Required before any looped or automated channel discovery
  - Add a circuit-breaker guard on `GET /youtube/search` — the endpoint stays for demo use but must not be called in any loop or seeding script (plan.md D8: "allowed for demo, flagged")
  - Quota counter tracks daily unit spend; circuit-breaker disables Search.list automatically at a threshold

[ ] N14 Redis: match-score cache (6 h TTL) + YouTube quota counter (plan D4, NFR-8)
  - Cache `ai_match_scores` keyed by `(campaign_id, hash(creator_pool))`; invalidate on re-run
  - Quota counter guards daily YouTube unit budget; feeds into N13 circuit-breaker

[ ] N15 TimescaleDB / snapshot table → follower history → authenticity growth Z-score (plan D3)
  - Prerequisite for the Z-score signal in N06 (growth-spike detection)
  - Start collecting snapshots as early as possible even before the scoring is ready

[ ] N16 pgvector: persist content + brief embeddings; replace on-the-fly cosine (plan D1)
  - Store Gemini embeddings on `creator_social_profiles` or `creator_profiles`
  - Query via `<->` cosine distance at Stage 3 instead of recomputing each match run

[ ] N17 Neo4j: graph sync + multi-hop matching + graph conflict-of-interest (plan D2)
  - Sync `creator_profiles`, `brand_profiles`, `campaign_applications` into Neo4j as nodes/edges
  - Replace relational conflict check (N08) with Cypher 90-day traversal
  - Unlock multi-hop niche alignment and lookalike expansion (SRS §5.1 Stage 2)

[ ] N18 Polymorphic talent + event-host availability matching (plan D5, SRS US-15, FR-17)
  - Availability-first matching (date/calendar) for hosts — distinct from audience-score matching
  - Requires host extension table (`HOST_PROFILE_EXT` in SRS ER) added as an additive migration

---

## Notes

- The YouTube wrapper (`app/youtube/`) is **stateless by design**. N01 is the first DB-touching unit — persistence belongs in `app/creators/`, not `app/youtube/`. Keep the wrapper pure.
- `Search.list` costs 100 units of the 10,000/day quota — treat as scarce (D8). The `/youtube/search` endpoint stays active for demo use but must never be called in a loop or seeding script. All automated discovery must go through `channels?handle=` (1 unit each). Circuit-breaker guard is N13.
- Conflict-of-interest ships relationally (N08) before Neo4j (N17); do not block FR-13 on a new datastore.
- Matching weights live in `services/matching_config.py`: niche .35 / budget .30 / platform .15 / engagement .10 / language .08 / recency .02. Do not duplicate weights in scripts or docs as a second source of truth.
- After any migration or model change: update `docs/schema.md` to stay code-true, then `graphify update .` (AST-only, no API cost).
