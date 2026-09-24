"""Build the Cohesiq diagram set: `python3 docs/diagrams/html/build.py`.

Each function returns (slug, html). Facts are validated against code, not only
docs — see the `sources=` line on each page for the files that were checked.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib import (  # noqa: E402
    ACCENT, INK, LINK, MONO, MUTED, PAPER, SANS, SOFT, WHITE, accent, arrow, callout, ceil4, end_dot,
    esc, ink, label_above, label_below, label_left, label_right, legend, line, muted, node, orth, page,
    start_dot, svg, text, zone,
)

OUT = Path(__file__).resolve().parent


# ── 1. Runtime architecture ─────────────────────────────────────────────────
def architecture():
    b = []
    b.append(zone(368, 64, 848, 128, "AI + DATA APIS"))
    b.append(zone(296, 288, 960, 152, "DOCKER COMPOSE"))
    # arrows
    b.append(arrow([(216, 360), (320, 360)], "link"))
    b.append(arrow([(520, 360), (640, 360)], "accent"))
    b.append(arrow([(840, 360), (1032, 360)]))
    b.append(arrow([(440, 320), (440, 168)], "link"))
    b.append(arrow([(672, 320), (672, 232), (520, 232), (520, 168)], "link"))
    b.append(arrow([(736, 320), (736, 168)], "link"))
    b.append(arrow([(800, 320), (800, 256), (896, 256), (896, 168)], "link"))
    b.append(arrow([(824, 320), (824, 280), (1104, 280), (1104, 168)], "link"))
    b.append(arrow([(104, 400), (104, 564), (640, 564)], "link"))
    b.append(arrow([(152, 400), (152, 480), (704, 480), (704, 400)], "link"))
    b.append(arrow([(784, 528), (784, 400)], dashed=True))
    # labels
    b.append(label_above(268, 360, "HTTPS", LINK))
    b.append(label_above(580, 360, "SSR · ACTIONS", ACCENT))
    b.append(label_above(936, 360, "ASYNC SQL"))
    b.append(label_right(440, 280, "STT · BRIEF", LINK))
    b.append(label_above(596, 232, "RATIONALE", LINK))
    b.append(label_right(736, 200, "EMBEDDINGS", LINK))
    b.append(label_above(848, 256, "YT STATS", LINK))
    b.append(label_above(1000, 280, "IG · TIKTOK", LINK))
    b.append(label_above(372, 564, "SIGN-IN", LINK))
    b.append(label_above(428, 480, "CLIENT FETCH", LINK))
    b.append(label_right(784, 464, "WEBHOOK"))
    # nodes
    b.append(node(40, 320, 176, 80, "input", "USER", "Browser", ["brand · creator · admin"]))
    b.append(node(320, 320, 200, 80, "backend", "WEB", "Next.js 16 frontend", [":3000 · App Router", "Server Actions · /api"]))
    b.append(node(640, 320, 200, 80, "focal", "API", "FastAPI backend", [":8000 · Python 3.12", "DDD domains + services"]))
    b.append(node(1032, 320, 200, 80, "store", "DB", "PostgreSQL 16", [":5432 · relational only", "Alembic head 0022"]))
    b.append(node(392, 96, 176, 72, "external", "LLM", "Groq API", ["llama-3.1-8b · 3.3-70b", "whisper-large-v3-turbo"]))
    b.append(node(600, 96, 176, 72, "external", "LLM", "Gemini API", ["text-embedding-004", "1.5 / 2.0 flash fallback"]))
    b.append(node(808, 96, 176, 72, "external", "EXT", "YouTube Data API", ["v3 · channels · videos"]))
    b.append(node(1016, 96, 176, 72, "external", "EXT", "Apify actors", ["Instagram · TikTok", "public profile scrape"]))
    b.append(node(640, 528, 200, 72, "external", "AUTH", "Clerk", ["RS256 JWT · webhooks"]))
    b.append(callout(904, 548, ["Embeddings are computed live", "and never persisted."]))
    b.append(legend(648, 1280, [
        ("box", "focal", "Core service"), ("box", "backend", "App container"), ("box", "store", "Data store"),
        ("box", "external", "External service"), ("box", "input", "User"),
        ("line", "accent", False, "Primary path"), ("line", "link", False, "HTTP / external API"),
        ("line", "default", True, "Async webhook"),
    ]))
    s = svg("architecture", "Cohesiq runtime architecture",
            "Architecture diagram: the browser reaches a Next.js frontend and a FastAPI backend inside Docker Compose; "
            "FastAPI owns PostgreSQL and calls Groq, Gemini, the YouTube Data API and Apify, while Clerk handles sign-in and "
            "sends user webhooks to FastAPI.", 1280, 720, "".join(b))
    return "architecture", page(
        "architecture", "Architecture · Runtime topology", "Cohesiq runtime architecture",
        "Three containers in Docker Compose (ngrok is an opt-in tunnel profile and omitted). Server Components and "
        "Server Actions reach FastAPI on the internal network; client components call it directly from the browser. "
        "All business data lives in one relational PostgreSQL database.",
        s,
        cards=[
            {"eyebrow": "Contract", "title": "Two API URLs, never mixed", "dot": "accent", "body": [
                "<code>BACKEND_API_URL</code> → <code>http://backend:8000</code> for Server Components &amp; Actions",
                "<code>NEXT_PUBLIC_API_URL</code> → <code>http://localhost:8000</code> for client components",
                "Both go through <code>fetchApi()</code> in <code>lib/api/client.ts</code>"]},
            {"eyebrow": "AI boundary", "title": "Where the models run", "dot": "link", "body": [
                "Next.js: Whisper STT (<code>/api/transcribe</code>), brief analysis (Groq → Gemini 2.0 fallback)",
                "FastAPI: match rationale (Groq), semantic rescue embeddings (Gemini)",
                "PDF briefs are parsed in the browser with pdfjs-dist"]},
            {"eyebrow": "Deferred", "title": "Not in the stack yet", "dot": "muted",
             "body": "pgvector, Neo4j, Redis and TimescaleDB are Phase-E layers (plan §3 D1–D5). "
                     "Nothing in this diagram depends on them."},
        ],
        sources="Sources: docs/diagrams/architecture.md §1 · docker-compose.yml · backend/app/main.py · "
                "backend/app/services/semantic_match.py")


# ── 2. Backend layers ───────────────────────────────────────────────────────
def layers():
    rows = [
        ("L1", "HTTP routers", "backend/app/*/router.py", "parse request → return Pydantic model · no logic"),
        ("L2", "Dependencies & auth", "common/dependencies.py", "get_db · get_current_user · require_admin"),
        ("L3", "Domain services", "backend/app/*/service.py", "auth · brands · creators · campaigns · admin · youtube"),
        ("L4", "Cross-domain services", "backend/app/services/", "matching · matching_config · semantic_match"),
        ("L5", "ORM models & migrations", "*/models.py · alembic/", "SQLAlchemy 2.0 async · head 0022"),
        ("L6", "PostgreSQL 16", "postgres:5432", "relational only · no pgvector / Neo4j / Redis"),
    ]
    x, w, y0, h = 176, 1064, 72, 72
    b = []
    for i, (idx, name, path, note) in enumerate(rows):
        y = y0 + i * h
        focal = idx == "L4"
        fill = accent(0.08) if focal else (PAPER if i % 2 == 0 else "#F3EFE9")
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>')
        if i:
            b.append(line(x, y, x + w, y, ink(0.12), 1))
        b.append(text(x + 24, y + 40, idx, size=9, color=ACCENT if focal else SOFT, weight=500, track="0.14em"))
        b.append(text(x + 96, y + 34, name, size=15, color=INK, family=SANS, weight=600))
        b.append(text(x + 96, y + 52, path, size=9, color=MUTED))
        b.append(text(x + w - 24, y + 40, note, size=10, color=MUTED, anchor="end"))
    b.append(f'<rect x="{x}" y="{y0}" width="{w}" height="{h * len(rows)}" fill="none" stroke="{MUTED}" stroke-width="1"/>')
    fy = y0 + 3 * h
    b.append(f'<rect x="{x}" y="{fy}" width="{w}" height="{h}" fill="none" stroke="{ACCENT}" stroke-width="1.2"/>')
    # direction indicator
    b.append(arrow([(104, 96), (104, 480)]))
    b.append(text(88, 288, "REQUEST", size=8, color=SOFT, anchor="end", track="0.14em"))
    b.append(text(88, 300, "FLOWS DOWN", size=8, color=SOFT, anchor="end", track="0.14em"))
    b.append(legend(560, 1280, [("box", "focal", "Focal layer — scoring lives here"), ("box", "backend", "Layer"),
                                ("line", "default", False, "Request direction")]))
    s = svg("layers", "FastAPI backend layers",
            "Layer stack of the FastAPI backend from HTTP routers through dependencies, domain services, cross-domain "
            "matching services and ORM models down to PostgreSQL, with the matching services layer highlighted.",
            1280, 620, "".join(b))
    return "layers", page(
        "layers", "Layer stack · backend/app", "FastAPI backend layers",
        "Domain-driven layout: every domain folder carries <code>router.py</code>, <code>service.py</code>, "
        "<code>schemas.py</code> and <code>models.py</code>. Routers only parse and respond; all logic sits in the "
        "service layer. Scoring lives in <code>services/</code>, which is called from <code>campaigns/service.py</code>.",
        s,
        cards=[
            {"eyebrow": "Rule", "title": "No cross-domain imports in routers", "dot": "accent",
             "body": "A router talks only to its own domain service. Cross-domain work (matching, semantic, LLM) goes "
                     "through <code>services/</code>, reached from the campaigns service."},
            {"eyebrow": "Single source", "title": "matching_config.py", "dot": "",
             "body": "<code>SCORE_WEIGHTS</code>, budget buffer (1.3×), semantic threshold (0.28) and cap (0.40), "
                     "<code>TOP_MATCH_LIMIT</code> = 10, <code>LLM_RATIONALE_TOP_N</code> = 5."},
            {"eyebrow": "Also mounted", "title": "webhooks/ · youtube/", "dot": "muted",
             "body": "<code>webhooks/</code> syncs Clerk users; <code>youtube/</code> is a stateless public-API "
                     "wrapper whose enrichment is persisted by <code>creators/</code>."},
        ],
        sources="Sources: docs/diagrams/architecture.md §2b · backend/app/*/router.py · backend/app/common/dependencies.py · "
                "backend/app/services/matching_config.py")


# ── 3. Matching pipeline ────────────────────────────────────────────────────
def matching():
    b = []
    # arrows
    b.append(arrow([(54, 148), (80, 148)]))
    b.append(arrow([(240, 148), (288, 148)]))
    b.append(arrow([(448, 148), (496, 148)]))
    b.append(arrow([(640, 148), (720, 148)], "accent"))
    b.append(arrow([(896, 148), (944, 148)], "accent"))
    b.append(arrow([(1152, 148), (1192, 148)]))
    b.append(arrow([(160, 200), (160, 288)], dashed=True))
    b.append(arrow([(368, 200), (368, 288)], dashed=True))
    b.append(arrow([(568, 196), (568, 268)]))
    b.append(arrow([(648, 300), (784, 300), (784, 200)]))
    b.append(arrow([(568, 356), (568, 416)], dashed=True))
    b.append(arrow([(648, 452), (848, 452), (848, 200)], dashed=True))
    # labels
    b.append(label_above(680, 148, "YES", ACCENT))
    b.append(label_right(160, 244, "FAIL"))
    b.append(label_right(368, 244, "CONFLICT"))
    b.append(label_right(568, 232, "NO · NICHE = 0"))
    b.append(label_above(716, 300, "SIM ≥ 0.28"))
    b.append(label_right(568, 386, "SIM < 0.28"))
    b.append(label_above(748, 452, "IF 0 MATCHES"))
    # nodes
    b.append(start_dot(48, 148))
    b.append(node(80, 96, 160, 104, "backend", "STAGE 1", "Hard gates",
                  ["available · platform", "followers min / max", "budget ≤ 1.3 × max"], num="1"))
    b.append(node(288, 96, 160, 104, "backend", "STAGE 2", "Conflict gate",
                  ["same brand_category", "collab ≤ 90 days", "→ hard exclude"], num="2"))
    b.append(f'<polygon points="568,100 640,148 568,196 496,148" fill="{PAPER}"/>'
             f'<polygon points="568,100 640,148 568,196 496,148" fill="{WHITE}" stroke="{INK}" stroke-width="1"/>')
    b.append(text(568, 138, "STAGE 3", size=7, color=SOFT, anchor="middle", track="0.08em"))
    b.append(text(568, 154, "Exact niche", size=11, color=INK, family=SANS, anchor="middle", weight=600))
    b.append(text(568, 168, "match?", size=11, color=INK, family=SANS, anchor="middle", weight=600))
    b.append(node(488, 268, 160, 88, "backend", "STAGE 3b", "Semantic rescue",
                  ["Gemini embeddings", "niche capped at 0.40"]))
    b.append(node(488, 416, 160, 72, "optional", "HOLD", "Fallback pool", ["held back, not dropped"]))
    b.append(node(720, 96, 176, 104, "focal", "STAGE 4", "Weighted score",
                  ["niche .45 · budget .20", "platform .15 · eng .10", "language .08 · recency .02"], num="4"))
    b.append(node(944, 96, 208, 104, "backend", "STAGE 5", "Rank & explain",
                  ["sort score → followers → id", "top 10 → ai_match_scores", "Groq rationale for top 5"], num="5"))
    b.append(end_dot(1200, 148))
    b.append(node(112, 288, 320, 64, "external", "OUT", "Excluded", ["never rescued by semantic scoring"]))
    b.append(callout(944, 252, ["The LLM only phrases the rationale", "for the top 5 — it never changes", "the numeric score."]))
    b.append(legend(536, 1280, [
        ("dot", "Run matching"), ("ring", "Ranked matches"), ("box", "focal", "Scoring stage"),
        ("box", "backend", "Stage"), ("box", "external", "Excluded"), ("box", "optional", "Conditional pool"),
        ("line", "accent", False, "Happy path"), ("line", "default", True, "Exit / fallback"),
    ]))
    s = svg("matching", "Matching engine: five-stage pipeline",
            "Flowchart of run_campaign_matching: creators pass hard gates and a competitor-conflict gate, then an exact "
            "niche check with a capped semantic rescue, then a six-signal weighted score, and finally ranking, "
            "persistence of the top 10 and LLM rationale for the top 5.", 1280, 608, "".join(b))
    return "matching-pipeline", page(
        "matching", "Flowchart · POST /campaigns/{id}/run-matching", "Matching engine: five-stage pipeline",
        "Hard filters run first and are never rescued. Only creators whose exact niche score is zero get a "
        "semantic second chance, and that path can add at most 0.40 to the niche signal. Creators that fail the "
        "semantic threshold are held back and used only if strict matching returns nothing.",
        s,
        cards=[
            {"eyebrow": "Stage 1", "title": "Budget gate", "dot": "",
             "body": "Exact rate-card totals per <code>deliverable_code</code> × quantity when available; cheapest active "
                     "platform card next; follower-tier estimate last. Hard ceiling is max budget × 1.3 "
                     "(<code>BUDGET_RATE_HARD_CAP</code>)."},
            {"eyebrow": "Stage 2", "title": "Competitor conflict", "dot": "",
             "body": "Same <code>brand_category</code>, different brand, collaboration within "
                     "<code>CONFLICT_LOOKBACK_DAYS</code> = 90 → excluded before scoring. Unregistered past brands "
                     "with no category pass through."},
            {"eyebrow": "Stage 5", "title": "Deterministic ranking", "dot": "accent",
             "body": "Ties break on follower count, then creator id, so reruns give identical order. Previous scores "
                     "for the campaign are deleted before the new top 10 are inserted."},
        ],
        sources="Sources: docs/matching-engine.md · backend/app/campaigns/service.py::run_campaign_matching · "
                "backend/app/services/matching_config.py · backend/app/services/semantic_match.py")


# ── 4. Score weights ────────────────────────────────────────────────────────
def weights():
    rows = [("Niche", "exact niche, or capped semantic", 0.45), ("Budget", "rate cards vs campaign budget", 0.20),
            ("Platform", "required platform coverage", 0.15), ("Engagement", "engagement rate vs tier", 0.10),
            ("Language", "creator vs target language", 0.08), ("Recency", "days since latest post", 0.02)]
    x0, x1, top, pitch = 256, 976, 72, 64
    scale = (x1 - x0) / 0.5
    b = []
    for i in range(6):
        gx = x0 + i * 0.1 * scale
        b.append(line(round(gx), top - 16, round(gx), top + pitch * 6 - 16,
                      ink(0.25) if i == 0 else ink(0.08), 1 if i == 0 else 0.8))
        b.append(text(round(gx), top + pitch * 6 + 4, f"{i / 10:.1f}", size=8, color=MUTED, anchor="middle"))
    b.append(text((x0 + x1) // 2, top + pitch * 6 + 24, "WEIGHT IN SCORE_TOTAL", size=7, color=MUTED,
                  anchor="middle", track="0.14em"))
    for i, (name, sub, v) in enumerate(rows):
        cy = top + i * pitch + 16
        bw = round(v * scale)
        focal = i == 0
        fill, stroke = (accent(0.12), ACCENT) if focal else (muted(0.15), MUTED)
        b.append(f'<rect x="{x0}" y="{cy - 14}" width="{bw}" height="28" fill="{PAPER}"/>'
                 f'<rect x="{x0}" y="{cy - 14}" width="{bw}" height="28" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
        b.append(text(x0 + bw + 12, cy + 4, f"{v:.2f}", size=10, color=ACCENT if focal else MUTED, weight=500))
        b.append(text(x0 - 16, cy, name, size=12, color=INK, family=SANS, anchor="end", weight=600))
        b.append(text(x0 - 16, cy + 14, sub, size=8, color=SOFT, anchor="end"))
    # bracket for commercial fit (first three rows)
    bx = 1000
    y_a, y_b = top + 16 - 14, top + 2 * pitch + 16 + 14
    b.append(f'<path d="M {bx - 8},{y_a} H {bx} V {y_b} H {bx - 8}" fill="none" stroke="{SOFT}" stroke-width="1"/>')
    b.append(callout(bx + 16, (y_a + y_b) // 2 - 4, ["Niche + budget + platform = 0.80.",
                                                     "Commercial fit outranks raw reach."]))
    s = svg("weights", "Matching score weights",
            "Horizontal bar chart of the six matching weights: niche 0.45, budget 0.20, platform 0.15, engagement "
            "0.10, language 0.08 and recency 0.02, summing to 1.0.", 1280, 520, "".join(b))
    return "matching-weights", page(
        "weights", "Bar chart · SCORE_WEIGHTS", "Matching score weights",
        "The single source of truth is <code>SCORE_WEIGHTS</code> in <code>backend/app/services/matching_config.py</code>. "
        "Each sub-score is normalised to 0–1 and stored on <code>ai_match_scores</code> alongside "
        "<code>score_semantic</code> and <code>score_total</code>. Older docs that say 0.35 / 0.30 are superseded.",
        s,
        cards=[
            {"eyebrow": "Why", "title": "A big creator can't outrank a fitting one", "dot": "accent",
             "body": "Engagement and reach together are worth 0.10. A correctly priced niche creator beats a massive "
                     "off-niche one."},
            {"eyebrow": "Caps", "title": "Semantic rescue is bounded", "dot": "",
             "body": "When the exact niche score is 0, semantic similarity (≥ 0.28) can stand in, capped at 0.40, so "
                     "the most it adds to <code>score_total</code> is 0.18."},
            {"eyebrow": "Unknowns", "title": "Missing data isn't free", "dot": "muted",
             "body": "Unknown budget scores 0.5; unknown recency scores 0.2. A missing signal ranks below a verified one."},
        ],
        sources="Sources: backend/app/services/matching_config.py · backend/app/services/matching.py · docs/matching-engine.md")


# ── 5. Application lifecycle ────────────────────────────────────────────────
def application_lifecycle():
    b = []
    # arrows
    b.append(arrow([(62, 196), (120, 196)]))
    b.append(arrow([(56, 190), (56, 80), (680, 80), (680, 160)]))
    b.append(arrow([(632, 160), (632, 112), (240, 112), (240, 160)]))
    b.append(arrow([(280, 196), (360, 196)]))
    b.append(arrow([(520, 196), (600, 196)]))
    b.append(arrow([(776, 196), (856, 196)]))
    b.append(arrow([(736, 160), (736, 128), (1136, 128), (1136, 160)]))
    b.append(arrow([(1032, 196), (1096, 196)], "accent"))
    b.append(arrow([(1168, 232), (1168, 384)]))
    b.append(arrow([(1168, 456), (1168, 496)]))
    b.append(arrow([(696, 232), (696, 384)]))
    b.append(arrow([(560, 424), (440, 424), (440, 232)], dashed=True))
    # labels
    b.append(label_above(91, 196, "APPLY"))
    b.append(label_above(368, 80, "BRAND INVITES"))
    b.append(label_above(436, 112, "CREATOR ACCEPTS INVITE"))
    b.append(label_above(320, 196, "SHORTLIST"))
    b.append(label_above(560, 196, "SEND OFFER"))
    b.append(label_above(816, 196, "COUNTER"))
    b.append(label_above(944, 128, "ACCEPT OFFER"))
    b.append(label_above(1064, 196, "ACCEPT", ACCENT))
    b.append(label_right(1168, 308, "CLOSE CONTRACT"))
    b.append(label_right(696, 308, "DECLINE"))
    b.append(label_left(440, 328, "RE-SHORTLIST"))
    # nodes
    b.append(start_dot(56, 196))
    b.append(node(120, 160, 160, 72, "backend", "PENDING", "Applied", ["awaiting brand review"]))
    b.append(node(360, 160, 160, 72, "backend", "SHORTLISTED", "Shortlisted", ["brand-curated"]))
    b.append(node(600, 160, 176, 72, "backend", "INVITED", "Invite / offer out", ["contract drafted", "creator to respond"]))
    b.append(node(856, 160, 176, 72, "backend", "PENDING_AGREEMENT", "Negotiating", ["counters repeat", "either side declines"]))
    b.append(node(1096, 160, 144, 72, "focal", "ACCEPTED", "Accepted", ["contract active"]))
    b.append(node(1096, 384, 144, 72, "backend", "COMPLETED", "Completed", ["reviews unlocked"]))
    b.append(node(560, 384, 240, 80, "external", "TERMINAL", "Closed out",
                  ["rejected · declined · withdrawn", "revivable by re-shortlist"]))
    b.append(end_dot(1168, 504))
    b.append(callout(120, 400, ["invited is reused: it means", "“invite pending” and “offer out”."]))
    b.append(legend(600, 1280, [
        ("dot", "Start"), ("ring", "End"), ("box", "focal", "Deal won"), ("box", "backend", "Status"),
        ("box", "external", "Terminal statuses"), ("line", "accent", False, "Acceptance"),
        ("line", "default", False, "Transition"), ("line", "default", True, "Revival"),
    ]))
    s = svg("applifecycle", "Campaign application lifecycle",
            "State machine for campaign_applications.status: creators apply into pending or brands invite; brands "
            "shortlist and send offers, which move the application to invited; counters move it to pending_agreement; "
            "acceptance moves it to accepted and closing the contract to completed. Declines lead to terminal "
            "statuses that a re-shortlist can revive.", 1280, 672, "".join(b))
    return "application-lifecycle", page(
        "applifecycle", "State machine · campaign_applications.status", "Campaign application lifecycle",
        "The offer-driven deal flow lives on the application, not the campaign. Every offer or counter writes a "
        "<code>negotiation_turns</code> row; only the other party's latest turn can be accepted. The contract is "
        "drafted on the first offer and activated on acceptance.",
        s,
        cards=[
            {"eyebrow": "Offers", "title": "send_offer guards", "dot": "",
             "body": "Campaign must be <code>active</code>; application must be <code>shortlisted</code> or "
                     "<code>pending</code> (a direct offer skips the shortlist). Counters require <code>invited</code> "
                     "or <code>pending_agreement</code>."},
            {"eyebrow": "Declines", "title": "Who declined is recorded", "dot": "muted",
             "body": "<code>decline_offer</code> writes <code>rejected</code> when the brand declines and "
                     "<code>declined</code> when the creator does. <code>withdrawn</code> is set only through the "
                     "brand's generic status update."},
            {"eyebrow": "Capacity", "title": "Auto-reject on fill", "dot": "accent",
             "body": "When accepted applications reach <code>number_of_creators</code>, remaining "
                     "<code>shortlisted</code> applications are rejected with “Campaign capacity has been filled”."},
        ],
        sources="Sources: backend/app/campaigns/service.py (respond_invite, shortlist_creator, send_offer, counter_offer, "
                "accept_offer, decline_offer, close_contract) · backend/app/campaigns/models.py")


# ── 6. Contract lifecycle ───────────────────────────────────────────────────
def contract_lifecycle():
    b = []
    # arrows
    b.append(arrow([(62, 172), (112, 172)]))
    b.append(arrow([(288, 172), (432, 172)]))
    b.append(arrow([(608, 172), (752, 172)]))
    b.append(arrow([(944, 160), (1072, 160)]))
    b.append(arrow([(1072, 184), (944, 184)]))
    b.append(arrow([(848, 208), (848, 392)], "accent"))
    b.append(arrow([(920, 208), (920, 300), (1152, 300), (1152, 392)], dashed=True))
    b.append(arrow([(752, 428), (608, 428)]))
    b.append(arrow([(432, 428), (288, 428)]))
    b.append(arrow([(112, 428), (72, 428)]))
    # labels
    b.append(label_above(360, 172, "ACCEPT OFFER"))
    b.append(label_above(680, 172, "SUBMIT DRAFT URL"))
    b.append(label_above(1008, 160, "REQUEST REVISION"))
    b.append(label_below(1008, 184, "RESUBMIT"))
    b.append(label_left(848, 300, "APPROVE", ACCENT))
    b.append(label_above(1036, 300, "REVISION CAP HIT"))
    b.append(label_above(680, 428, "PUBLISH LIVE URL"))
    b.append(label_above(360, 428, "CLOSE"))
    # nodes
    b.append(start_dot(56, 172))
    b.append(node(112, 136, 176, 72, "backend", "DRAFTED", "Offer drafted", ["send_offer", "terms + deliverables"]))
    b.append(node(432, 136, 176, 72, "backend", "ACTIVE", "Active", ["creator in production"]))
    b.append(node(752, 136, 192, 72, "focal", "CONTENT_SUBMITTED", "Draft under review", ["draft_content_url"]))
    b.append(node(1072, 136, 168, 72, "backend", "IN_PRODUCTION", "Revising", ["revisions_used += 1"]))
    b.append(node(1072, 392, 168, 72, "optional", "DISPUTED", "Disputed", ["enum only · no endpoint"]))
    b.append(node(752, 392, 192, 72, "backend", "CONTENT_APPROVED", "Approved", ["creator may go live"]))
    b.append(node(432, 392, 176, 72, "backend", "PUBLISHED", "Published", ["live_post_url", "metric snapshots"]))
    b.append(node(112, 392, 176, 72, "backend", "CLOSED", "Closed", ["application → completed"]))
    b.append(end_dot(64, 428))
    b.append(callout(112, 280, ["Revisions stop at max_revision_rounds;", "after that the brand must approve."]))
    b.append(legend(528, 1280, [
        ("dot", "Start"), ("ring", "End"), ("box", "focal", "Review gate"), ("box", "backend", "Status"),
        ("box", "optional", "Reserved, not wired"), ("line", "accent", False, "Approval"),
        ("line", "default", False, "Transition"), ("line", "default", True, "Not implemented"),
    ]))
    s = svg("contractlifecycle", "Contract lifecycle",
            "State machine for contracts.status: drafted on offer, active on acceptance, content_submitted when the "
            "creator submits a draft, with a capped revision loop through in_production, then content_approved, "
            "published and closed. Disputed exists in the enum but no endpoint sets it.", 1280, 600, "".join(b))
    return "contract-lifecycle", page(
        "contractlifecycle", "State machine · contracts.status", "Contract lifecycle",
        "One contract per application (<code>contracts.application_id</code> is unique). The brand reviews each "
        "draft URL and can request a revision or approve it. Once approved, the creator publishes a live URL and "
        "the brand closes the contract, which completes the application and unlocks reviews.",
        s,
        cards=[
            {"eyebrow": "Revision cap", "title": "Bounded review loop", "dot": "accent",
             "body": "<code>request_revision</code> is rejected with 409 once <code>revisions_used</code> reaches "
                     "<code>max_revision_rounds</code>. The error says to approve or raise a dispute, but no dispute "
                     "endpoint exists yet."},
            {"eyebrow": "Shortcut", "title": "create_contract", "dot": "",
             "body": "For an already <code>accepted</code> application with no contract, "
                     "<code>create_contract</code> inserts one directly as <code>active</code>, skipping "
                     "<code>drafted</code>."},
            {"eyebrow": "Analytics", "title": "Live metrics", "dot": "muted",
             "body": "Metric sync is allowed only in <code>published</code> or <code>closed</code>. Each sync writes a "
                     "<code>live_content_metric_snapshots</code> row."},
        ],
        sources="Sources: backend/app/campaigns/service.py (send_offer, accept_offer, submit_content_draft, approve_content, "
                "request_revision, publish_content, close_contract, sync_contract_live_metrics) · campaigns/models.py")


# ── 7. Run-matching sequence ────────────────────────────────────────────────
def run_matching_sequence():
    lanes = [("UI", "Brand dashboard", "Next.js", 128), ("API", "FastAPI", "campaigns/service.py", 432),
             ("DB", "PostgreSQL", "async SQLAlchemy", 736), ("LLM", "Gemini", "text-embedding-004", 960),
             ("LLM", "Groq", "llama-3.1-8b-instant", 1168)]
    X = {name: cx for _, name, _, cx in lanes}
    ui, api, db, gem, groq = X["Brand dashboard"], X["FastAPI"], X["PostgreSQL"], X["Gemini"], X["Groq"]
    end_y = 700
    b = []
    # lifelines
    for _, _, _, cx in lanes:
        b.append(line(cx, 104, cx, end_y, ink(0.25), 1, "4,4"))
    # loop fragment
    fx, fy, fw, fh = 240, 324, 792, 176
    b.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="4" fill="none" stroke="{ink(0.22)}" stroke-width="1"/>'
             f'<rect x="{fx}" y="{fy}" width="44" height="16" rx="2" fill="{PAPER}" stroke="{ink(0.22)}" stroke-width="1"/>')
    b.append(text(fx + 22, fy + 12, "LOOP", size=8, color=MUTED, anchor="middle", track="0.12em"))
    b.append(text(fx + 56, fy + 12, "[each creator in pool]", size=8, color=MUTED, track="0.04em"))
    # activation bars
    def bar(cx, y1, y2, focal=False):
        return (f'<rect x="{cx - 4}" y="{y1}" width="8" height="{y2 - y1}" fill="{accent(0.12) if focal else WHITE}" '
                f'stroke="{ACCENT if focal else INK}" stroke-width="1"/>')
    # messages (arrows first)
    def call(y, x1, x2, kind="default"):
        return arrow([(x1, y), (x2, y)], kind)

    def self_msg(y, kind="default"):
        return arrow([(api + 4, y), (api + 56, y), (api + 56, y + 20), (api + 4, y + 20)], kind)
    b.append(call(144, ui, api - 4, "link"))
    b.append(call(184, api + 4, db - 4))
    b.append(call(224, api + 4, db - 4))
    b.append(call(264, api + 4, gem - 4, "link"))
    b.append(self_msg(356))
    b.append(call(420, api + 4, gem - 4, "link"))
    b.append(self_msg(460, "accent"))
    b.append(self_msg(548))
    b.append(call(604, api + 4, groq - 4, "link"))
    b.append(call(636, api + 4, db - 4))
    b.append(arrow([(api - 4, 672), (ui, 672)], dashed=True))
    # labels
    b.append(label_above((ui + api) // 2, 144, "POST /campaigns/{id}/run-matching", LINK))
    b.append(label_above((api + db) // 2, 184, "DELETE ai_match_scores · COMMIT"))
    b.append(label_above((api + db) // 2, 224, "SELECT available creators + profiles"))
    b.append(label_above((api + db) // 2, 264, "embed campaign text", LINK))
    b.append(label_right(api + 56, 366, "hard gates · conflict · niche"))
    b.append(label_above((api + db) // 2, 420, "[niche = 0] embed creator text", LINK))
    b.append(label_right(api + 56, 470, "compute_match_score", ACCENT))
    b.append(label_right(api + 56, 558, "sort · keep top 10"))
    b.append(label_above((api + db) // 2, 604, "rationale for top 5", LINK))
    b.append(label_above((api + db) // 2, 636, "INSERT ai_match_scores · COMMIT"))
    b.append(label_above((ui + api) // 2, 672, "200 · ranked AIMatchScoreOut[]"))
    # activation bars on top of lifelines
    b.append(bar(api, 144, 672, focal=False))
    b.append(bar(db, 184, 236))
    b.append(bar(db, 636, 648))
    b.append(bar(gem, 264, 276))
    b.append(bar(gem, 420, 432))
    b.append(bar(groq, 604, 616))
    # headers
    for tg, name, sub, cx in lanes:
        kind = "focal" if name == "FastAPI" else ("store" if name == "PostgreSQL" else
                                                  "external" if tg == "LLM" else "input")
        b.append(node(cx - 88, 48, 176, 56, kind, tg, name, [sub]))
    b.append(legend(740, 1280, [
        ("box", "focal", "Orchestrator"), ("line", "default", False, "Sync call"),
        ("line", "link", False, "HTTP / external API"), ("line", "accent", False, "Scoring step"),
        ("line", "default", True, "Response"), ("frame", "Loop fragment"),
    ]))
    s = svg("runmatching", "Run matching: request sequence",
            "Sequence diagram of POST /campaigns/{id}/run-matching: FastAPI clears old scores, loads creators from "
            "PostgreSQL, embeds the campaign text with Gemini, loops over creators applying gates, optional semantic "
            "embedding and scoring, sorts and keeps the top 10, asks Groq for rationale on the top 5, inserts the "
            "scores and returns the ranked list.", 1280, 800, "".join(b))
    return "run-matching-sequence", page(
        "runmatching", "Sequence · POST /campaigns/{id}/run-matching", "Run matching: request sequence",
        "A single synchronous request. The router delegates to <code>run_campaign_matching</code>, which owns every "
        "call below. Returns are omitted except the final response; Gemini and Groq failures fall back to token "
        "Jaccard similarity and a heuristic rationale respectively, so the request still completes.",
        s,
        cards=[
            {"eyebrow": "Idempotent", "title": "Rerun replaces, never appends", "dot": "",
             "body": "Old <code>ai_match_scores</code> rows are deleted and committed before scoring, so a rerun "
                     "always reflects the current creator pool."},
            {"eyebrow": "Cost control", "title": "Embeddings only when needed", "dot": "link",
             "body": "The campaign is embedded once. Creator text is embedded only when the exact niche score is 0 "
                     "and the campaign niche is specific. Vectors are never stored."},
            {"eyebrow": "Scoring", "title": "LLM after ranking", "dot": "accent",
             "body": "Groq is called only after the deterministic sort, for <code>LLM_RATIONALE_TOP_N</code> = 5 "
                     "matches. It rewrites the explanation and cannot move a creator's rank."},
        ],
        sources="Sources: backend/app/campaigns/router.py · backend/app/campaigns/service.py::run_campaign_matching · "
                "backend/app/services/semantic_match.py")


# ── 8–9. ER diagrams ────────────────────────────────────────────────────────
def entity(x, y, w, name, fields, focal=False):
    h = 36 + 8 + 14 * len(fields) + 6
    stroke = ACCENT if focal else INK
    fill = accent(0.06) if focal else WHITE
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{PAPER}"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1"/>',
           f'<rect x="{x + 8}" y="{y + 6}" width="44" height="12" rx="2" fill="transparent" '
           f'stroke="{ACCENT if focal else ink(0.3)}" stroke-width="0.8"/>',
           text(x + 30, y + 15, "ENTITY", size=7, color=ACCENT if focal else SOFT, anchor="middle", track="0.08em"),
           text(x + 10, y + 31, name, size=12, color=INK, family=SANS, weight=600),
           line(x, y + 36, x + w, y + 36, accent(0.4) if focal else ink(0.15), 1)]
    for i, f in enumerate(fields):
        color = INK if f.startswith(("#", "→")) else MUTED
        out.append(text(x + 10, y + 36 + 18 + 14 * i, f, size=9, color=color))
    return "".join(out)


def rel(points):
    return f'<path d="{orth(points)}" fill="none" stroke="{MUTED}" stroke-width="1"/>'


def card_label(x, y, s):
    w = ceil4(len(s) * 5.4 + 6)
    return (f'<rect x="{x - w / 2:g}" y="{y - 9}" width="{w}" height="12" rx="2" fill="{PAPER}"/>'
            + text(x, y, s, size=8, color=MUTED, anchor="middle"))


def er_campaign():
    b = []
    # relationships
    b.append(rel([(264, 128), (376, 128)]))
    b.append(rel([(600, 128), (712, 128)]))
    b.append(rel([(936, 128), (1016, 128)]))
    b.append(rel([(488, 216), (488, 344)]))
    b.append(rel([(376, 416), (264, 416)]))
    b.append(rel([(600, 416), (712, 416)]))
    b.append(rel([(880, 344), (880, 276), (1128, 276), (1128, 170)]))
    b.append(rel([(936, 416), (1016, 416)]))
    # cardinalities (10–12px from entity edges, above the line)
    for x, y, s in [(276, 120, "N"), (364, 120, "1"), (612, 120, "1"), (700, 120, "N"), (948, 120, "1"),
                    (1004, 120, "N"), (500, 232, "1"), (500, 332, "N"), (364, 408, "1"), (276, 408, "N"),
                    (612, 408, "1"), (696, 408, "0..1"), (892, 336, "1"), (1140, 186, "N"), (948, 408, "1"),
                    (1004, 408, "N")]:
        b.append(card_label(x, y, s))
    # entities
    b.append(entity(40, 64, 224, "ai_match_scores",
                    ["# id", "→ campaign_id", "→ creator_id", "score_niche … score_recency", "score_semantic",
                     "score_total", "rationale"]))
    b.append(entity(376, 64, 224, "campaigns",
                    ["# id", "→ brand_id", "→ primary_niche_id", "brand_category", "required_platforms",
                     "budget_per_creator_min/max", "status · visibility"], focal=True))
    b.append(entity(712, 64, 224, "campaign_deliverable_req…",
                    ["# id", "→ campaign_id", "platform", "deliverable_code", "quantity"]))
    b.append(entity(1016, 64, 224, "contract_deliverables",
                    ["# id", "→ contract_id", "→ requirement_id", "quantity"]))
    b.append(entity(40, 344, 224, "negotiation_turns",
                    ["# id", "→ application_id", "author_role", "status", "proposed_rate", "proposed_terms"]))
    b.append(entity(376, 344, 224, "campaign_applications",
                    ["# id", "→ campaign_id", "→ creator_id", "initiated_by", "status", "proposed_rate · agreed_rate"]))
    b.append(entity(712, 344, 224, "contracts",
                    ["# id", "→ application_id  (unique)", "→ brand_id · → creator_id", "status",
                     "payment_amount_bdt", "max_revision_rounds", "revisions_used", "draft / live URLs"]))
    b.append(entity(1016, 344, 224, "live_content_metric_snap…",
                    ["# id", "→ contract_id", "platform · captured_at", "views · likes · comments", "engagement_rate"]))
    b.append(legend(632, 1280, [("box", "focal", "Aggregate root"), ("box", "backend", "Entity"),
                                ("line", "default", False, "Relationship — cardinality at each end")]))
    s = svg("ercampaign", "Data model: campaigns and deals",
            "Entity-relationship diagram of the campaign side: campaigns own deliverable requirements, applications "
            "and AI match scores; applications have negotiation turns and at most one contract; contracts have "
            "deliverables mapped to requirements and live metric snapshots.", 1280, 680, "".join(b))
    return "er-campaign", page(
        "ercampaign", "ER · campaign & deal pipeline", "Data model: campaigns and deals",
        "Eight of the campaign-side tables, cut to the columns that drive matching and the deal lifecycle. "
        "<code>→ brand_id</code> and <code>→ creator_id</code> point into the identity model on the "
        "<a href=\"er-creator.html\">creator ER diagram</a>. <code>#</code> marks a primary key and "
        "<code>→</code> a foreign key.",
        s,
        cards=[
            {"eyebrow": "Not shown", "title": "Omitted tables", "dot": "muted",
             "body": "<code>campaign_niche_targets</code>, <code>campaign_language_targets</code>, application "
                     "questions / acknowledgments, and <code>reviews</code> (keyed on <code>application_id</code>)."},
            {"eyebrow": "Deliverables", "title": "Demand meets contract", "dot": "",
             "body": "<code>contract_deliverables</code> copies quantities from "
                     "<code>campaign_deliverable_requirements</code> at offer time, so a counter can change the "
                     "quantity without editing the campaign."},
            {"eyebrow": "Derived", "title": "Scores are replaceable", "dot": "accent",
             "body": "<code>ai_match_scores</code> holds six sub-scores plus <code>score_semantic</code> and "
                     "<code>score_total</code>. Each matching run deletes and rewrites the campaign's rows."},
        ],
        sources="Sources: backend/app/campaigns/models.py · docs/schema.md · Alembic head 0022")


def er_creator():
    b = []
    b.append(rel([(376, 100), (264, 100)]))
    b.append(rel([(488, 154), (488, 300)]))
    b.append(rel([(600, 340), (712, 340)]))
    b.append(rel([(1128, 140), (1128, 346), (936, 346)]))
    b.append(rel([(376, 368), (264, 368)]))
    b.append(rel([(152, 168), (152, 300)]))
    b.append(rel([(424, 448), (424, 484), (272, 484), (272, 520)]))
    b.append(rel([(552, 448), (552, 484), (656, 484), (656, 520)]))
    for x, y, s in [(364, 92, "1"), (280, 92, "0..1"), (500, 170, "1"), (504, 288, "0..1"), (612, 332, "1"),
                    (700, 338, "N"), (1140, 156, "1"), (948, 338, "N"), (364, 360, "1"), (276, 360, "N"),
                    (168, 184, "0..1"), (164, 288, "N"), (436, 464, "1"), (284, 508, "N"), (564, 464, "1"),
                    (668, 508, "N")]:
        b.append(card_label(x, y, s))
    b.append(entity(376, 48, 224, "users", ["# id", "email  (unique)", "clerk_id  (unique)", "role"]))
    b.append(entity(40, 48, 224, "brand_profiles",
                    ["# id", "→ user_id", "brand_name", "→ niche_id", "brand_category"]))
    b.append(entity(1016, 48, 224, "niches", ["# id", "name · slug", "→ parent_id"]))
    b.append(entity(40, 300, 224, "creator_collaboration_hist…",
                    ["# id", "→ creator_id", "→ brand_id  (nullable)", "brand_name", "collaborated_on"]))
    b.append(entity(376, 300, 224, "creator_profiles",
                    ["# id", "→ user_id", "display_name · city", "is_available", "min_budget", "average_rating",
                     "deleted_at"], focal=True))
    b.append(entity(712, 300, 224, "creator_niches", ["# → creator_id", "# → niche_id", "is_primary"]))
    b.append(entity(160, 520, 224, "creator_social_profiles",
                    ["# id", "→ creator_id", "platform · handle", "follower_count", "engagement_rate",
                     "is_api_verified", "data_source"]))
    b.append(entity(544, 520, 224, "creator_rate_cards",
                    ["# id", "→ creator_id", "platform", "deliverable_code", "price_bdt", "is_active"]))
    b.append(callout(832, 560, ["Rate cards feed the budget gate;", "collaboration history feeds the",
                                "competitor-conflict gate."]))
    b.append(legend(720, 1280, [("box", "focal", "Aggregate root"), ("box", "backend", "Entity"),
                                ("line", "default", False, "Relationship — cardinality at each end")]))
    s = svg("ercreator", "Data model: identity and creator supply",
            "Entity-relationship diagram: users own at most one brand profile or creator profile; creator profiles "
            "have social profiles, rate cards, niches and collaboration history, which may reference a registered "
            "brand.", 1280, 768, "".join(b))
    return "er-creator", page(
        "ercreator", "ER · identity & creator supply", "Data model: identity and creator supply",
        "Clerk owns authentication; <code>users</code> mirrors it by <code>clerk_id</code> and carries the role. "
        "The creator side stores everything the matching engine reads: platform stats, prices, niches and past "
        "brand work. See the <a href=\"er-campaign.html\">campaign ER diagram</a> for the demand side.",
        s,
        cards=[
            {"eyebrow": "Provenance", "title": "data_source on social profiles", "dot": "link",
             "body": "YouTube enrichment writes into <code>creator_social_profiles</code> and labels the row with "
                     "<code>data_source</code> and <code>is_api_verified</code>, so API-verified stats are "
                     "distinguishable from self-reported ones."},
            {"eyebrow": "Not shown", "title": "Omitted tables", "dot": "muted",
             "body": "<code>creator_languages</code>, <code>creator_portfolio_items</code>, and the brand-side "
                     "campaign tables."},
            {"eyebrow": "Soft delete", "title": "deleted_at", "dot": "",
             "body": "Profiles and users are soft-deleted. Matching skips any creator with <code>deleted_at</code> "
                     "set or <code>is_available</code> false."},
        ],
        sources="Sources: backend/app/auth/models.py · backend/app/brands/models.py · backend/app/creators/models.py · "
                "backend/app/common/models.py · docs/schema.md")


# ── 10. Journeys swimlane ───────────────────────────────────────────────────
def journeys():
    lanes = [("BRAND", 64), ("PLATFORM · AI", 224), ("CREATOR", 384)]
    lh = 160
    xs = [152 + 124 * i for i in range(9)]
    cy = {"B": 144, "P": 304, "C": 464}
    b = []
    for i, (name, y) in enumerate(lanes):
        if i % 2:
            b.append(f'<rect x="40" y="{y}" width="1224" height="{lh}" fill="{ink(0.025)}"/>')
        b.append(line(40, y, 1264, y, ink(0.12), 1))
        b.append(text(48, y + lh // 2 + 3, name, size=8, color=MUTED, track="0.14em"))
    b.append(line(40, 544, 1264, 544, ink(0.12), 1))
    b.append(line(136, 64, 136, 544, ink(0.12), 1))

    def c(i):
        return xs[i] + 56
    # arrows (forward handoffs)
    b.append(arrow([(c(0), 176), (c(0), 304), (xs[1], 304)]))
    b.append(arrow([(c(1), 272), (c(1), 144), (xs[2], 144)]))
    b.append(arrow([(c(2), 176), (c(2), 464), (xs[3], 464)], "accent"))
    b.append(arrow([(c(3) + 4, 432), (c(3) + 4, 144), (xs[2] + 112, 144)], dashed=True))
    b.append(arrow([(c(3) + 24, 432), (c(3) + 24, 304), (xs[4], 304)]))
    b.append(arrow([(c(4), 336), (c(4), 464), (xs[5], 464)]))
    b.append(arrow([(c(5), 432), (c(5), 144), (xs[6], 144)]))
    b.append(arrow([(c(6) - 32, 176), (c(6) - 32, 480), (xs[5] + 112, 480)], dashed=True))
    b.append(arrow([(c(6) + 8, 176), (c(6) + 8, 464), (xs[7], 464)]))
    b.append(arrow([(c(7), 432), (c(7), 144), (xs[8], 144)]))
    # labels
    b.append(label_right(c(0), 240, "RUN MATCHING"))
    b.append(label_right(c(1), 208, "TOP 10"))
    b.append(label_right(c(2), 320, "SEND OFFER", ACCENT))
    b.append(label_right(c(3) + 4, 248, "COUNTER"))
    b.append(label_right(c(3) + 24, 368, "ACCEPT"))
    b.append(label_right(c(5), 320, "DRAFT URL"))
    b.append(label_left(c(6) - 32, 256, "REVISE"))
    b.append(label_right(c(6) + 8, 400, "APPROVED"))
    b.append(label_right(c(7), 240, "LIVE URL"))
    # nodes
    steps = [(0, "B", "input", "Brief campaign", ["voice · PDF · AI"]),
             (1, "P", "focal", "Rank & explain", ["top 10 · why ×5"]),
             (2, "B", "backend", "Shortlist", ["pick creators"]),
             (3, "C", "backend", "Negotiate", ["counter · accept"]),
             (4, "P", "backend", "Contract live", ["drafted → active"]),
             (5, "C", "backend", "Submit draft", ["draft URL"]),
             (6, "B", "backend", "Review draft", ["approve · revise"]),
             (7, "C", "backend", "Publish", ["live post URL"]),
             (8, "B", "backend", "Close & review", ["reviews unlock"])]
    for i, lane, kind, name, subs in steps:
        b.append(node(xs[i], cy[lane] - 32, 112, 64, kind, None, name, subs, num=str(i + 1)))
    b.append(legend(592, 1280, [("box", "focal", "AI step"), ("box", "backend", "Step"), ("box", "input", "Entry"),
                                ("line", "accent", False, "Key handoff"), ("line", "default", False, "Handoff"),
                                ("line", "default", True, "Loop back")]))
    s = svg("journeys", "End-to-end campaign journey",
            "Swimlane across brand, platform and creator lanes: the brand briefs a campaign, the platform ranks and "
            "explains creators, the brand shortlists and sends an offer, the creator negotiates, the platform "
            "activates the contract, the creator submits a draft that the brand approves or sends back, the creator "
            "publishes and the brand closes and reviews.", 1280, 640, "".join(b))
    return "journeys-swimlane", page(
        "journeys", "Swimlane · brand ⇄ platform ⇄ creator", "End-to-end campaign journey",
        "The happy path from brief to review, with the two loops that matter: counter-offers during negotiation "
        "and revisions during content review. Creators can also enter at step 3 by applying to a public campaign "
        "or accepting an invite.",
        s,
        cards=[
            {"eyebrow": "Step 1", "title": "Three ways to brief", "dot": "",
             "body": "Voice (Groq Whisper STT), PDF (parsed in the browser), or free text. All three go through "
                     "brief analysis (Groq, Gemini fallback) to pre-fill the campaign form."},
            {"eyebrow": "Step 4", "title": "Turn-based negotiation", "dot": "accent",
             "body": "Each offer or counter is a <code>negotiation_turns</code> row; the drawer polls every 4 s. "
                     "Either party can accept the other's latest turn."},
            {"eyebrow": "Admin", "title": "Off the main path", "dot": "muted",
             "body": "Admins see platform stats, manage users, moderate campaigns and delete reviews. "
                     "They never enter the deal flow."},
        ],
        sources="Sources: docs/diagrams/use-case.md · docs/user-stories.md · backend/app/campaigns/service.py")


# ── Index ───────────────────────────────────────────────────────────────────
INDEX = [
    ("architecture.html", "Architecture", "Runtime topology",
     "Browser, Next.js, FastAPI, PostgreSQL, Clerk and the AI and data APIs."),
    ("layers.html", "Layer stack", "FastAPI backend layers", "Routers → services → matching → ORM → Postgres."),
    ("journeys-swimlane.html", "Swimlane", "End-to-end campaign journey",
     "Brief to review across brand, platform and creator."),
    ("matching-pipeline.html", "Flowchart", "Matching engine pipeline",
     "Hard gates, conflict gate, semantic rescue, weighted score, ranking."),
    ("matching-weights.html", "Bar chart", "Matching score weights", "The six weights in matching_config.py."),
    ("run-matching-sequence.html", "Sequence", "Run matching: request sequence",
     "FastAPI ⇄ PostgreSQL ⇄ Gemini ⇄ Groq for one matching run."),
    ("application-lifecycle.html", "State machine", "Application lifecycle",
     "Apply, invite, shortlist, offer, counter, accept, complete."),
    ("contract-lifecycle.html", "State machine", "Contract lifecycle",
     "Drafted to closed, with the capped revision loop."),
    ("er-creator.html", "ER", "Identity & creator supply", "Users, brand and creator profiles, stats, prices."),
    ("er-campaign.html", "ER", "Campaigns & deals", "Campaigns, applications, negotiation, contracts, scores."),
]


def index():
    cards = "".join(
        f'<a class="tile" href="{href}"><p class="eyebrow">{esc(kind)}</p><h3>{esc(title)}</h3><p>{esc(desc)}</p></a>'
        for href, kind, title, desc in INDEX)
    extra = """
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.tile { display: block; background: #ffffff; border: 1px solid var(--color-rule); border-radius: 6px;
  padding: 1.25rem; text-decoration: none; color: inherit; }
.tile:hover { border-color: var(--color-accent); }
.tile h3 { font-size: 1rem; font-weight: 600; margin-bottom: 0.4rem; }
.tile p:last-child { color: var(--color-muted); font-size: 0.85rem; line-height: 1.5; }
.tile.feature { margin-bottom: 1.5rem; border-left: 3px solid var(--color-accent); }
"""
    from _lib import CSS, FONT_LINK
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cohesiq diagrams</title>
  <link href="{FONT_LINK}" rel="stylesheet">
  <style>{CSS}{extra}</style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">Cohesiq · docs/diagrams/html</p>
    <h1>Cohesiq diagrams</h1>
    <p class="lede">Editorial diagrams of the running system, checked against the code as of Alembic head 0022.
    The Mermaid sources in <code>docs/diagrams/*.md</code> remain the editable text versions.</p>
    <a class="tile feature" href="technical-document.html"><p class="eyebrow">Document</p><h3>Technical design document</h3><p>The whole system in twelve sections, with all ten figures: architecture, backend, frontend, auth, matching, deal lifecycle, data model, configuration, operations and known gaps.</p></a>
    <div class="grid">{cards}</div>
    <footer>Rebuild (diagrams + document) with <code>python3 docs/diagrams/html/build.py</code> · diagram-design skill · cohesiq profile</footer>
  </div>
</body>
</html>
"""


DIAGRAMS = [architecture, layers, matching, weights, application_lifecycle, contract_lifecycle,
            run_matching_sequence, er_campaign, er_creator, journeys]


def main():
    for fn in DIAGRAMS:
        slug, html_doc = fn()
        (OUT / f"{slug}.html").write_text(html_doc)
        print("wrote", slug)
    (OUT / "index.html").write_text(index())
    print("wrote index")
    import techdoc  # imports this module, so load it only after the figures are defined
    techdoc.main()


if __name__ == "__main__":
    main()
