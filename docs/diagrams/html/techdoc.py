"""Build the Cohesiq technical design document (also run by build.py).

Embeds the SVG from each diagram in build.py, so the document and the standalone
diagram pages always show the same figure. Rerun after editing either file.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build  # noqa: E402
from _lib import CSS, FONT_LINK  # noqa: E402

OUT = Path(__file__).resolve().parent / "technical-document.html"
DATE = "2026-09-24"


def figure(fn, num, caption):
    slug, html_doc = fn()
    svg_markup = re.search(r'<svg class="diagram".*?</svg>', html_doc, re.S).group(0)
    # Every figure carries identical arrow markers; keep one copy so ids stay unique.
    if num > 1:
        svg_markup = re.sub(r"<defs>.*?</defs>", "", svg_markup, count=1, flags=re.S)
    return (f'<figure id="fig-{num}"><div class="figure">{svg_markup}</div>'
            f'<figcaption><b>Figure {num}.</b> {caption} '
            f'<a href="{slug}.html">Open standalone ↗</a></figcaption></figure>')


def table(head, rows, cls=""):
    # Cells are plain strings passed through f-string sections; undo any {{ }} escaping.
    rows = [[c.replace("{{", "{").replace("}}", "}") for c in r] for r in rows]
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


SECTIONS = []


def section(num, title):
    def deco(fn):
        SECTIONS.append((num, title, fn))
        return fn
    return deco


# ── 1 ──────────────────────────────────────────────────────────────────────
@section("1", "Introduction")
def s_intro():
    return f"""
<h3 id="s1-1">1.1 Purpose</h3>
<p>This document describes how Cohesiq is built: its runtime topology, code structure, authentication,
matching engine, deal lifecycle, data model, configuration and operations. It is written for engineers who
will change the system and for reviewers who need to check that it does what the product specification says.</p>
<p>It describes the system <em>as built</em>. Every statement was checked against the source code on {DATE}
(Alembic migration head <code>0022</code>). Where the code and the product spec
(<code>docs/srs.md</code>) differ, the code wins here and the difference is either listed in
<a href="#s12">§12</a> or already recorded in <code>docs/plan.md</code> §3.</p>

<h3 id="s1-2">1.2 The system in one paragraph</h3>
<p>Cohesiq is a B2B influencer-matching marketplace for the Bangladesh market. A <b>brand</b> briefs a
campaign by voice, PDF or text. A deterministic <b>matching engine</b> filters and scores every available
<b>creator</b> and stores the top 10, with an LLM-written explanation for the top 5. The brand shortlists and
sends offers; brand and creator negotiate turn by turn; acceptance activates a <b>contract</b> that tracks the
draft, review, revision and publication of the content, then live metrics and mutual reviews. An <b>admin</b>
role moderates users, campaigns and reviews.</p>

<h3 id="s1-3">1.3 Glossary</h3>
{table(["Term", "Meaning"], [
    ["Campaign", "A brand's demand: niche, platforms, budget per creator, deliverables, audience targets. Status: <code>draft · active · in_progress · completed · cancelled · archived</code>."],
    ["Application", "One creator's participation in one campaign (<code>campaign_applications</code>). Carries the deal status from apply/invite to completion."],
    ["Negotiation turn", "One offer or counter-offer with a rate and terms (<code>negotiation_turns</code>). Only the other party's latest turn can be accepted."],
    ["Contract", "The agreed deal for one application: payment, deliverables, revision cap, content URLs."],
    ["Rate card", "A creator's price for one deliverable on one platform, in BDT (<code>creator_rate_cards</code>)."],
    ["Match score", "Weighted 0–1 fit between a campaign and a creator, stored with its six sub-scores in <code>ai_match_scores</code>."],
    ["Semantic rescue", "Using embedding similarity to give a creator a capped niche score when the exact niche does not match."],
    ["BDT", "Bangladeshi taka; all prices and payments are stored in BDT."],
])}

<h3 id="s1-4">1.4 Document map</h3>
{table(["If you need…", "Read"], [
    ["The product requirements", "<code>docs/srs.md</code>, <code>docs/user-stories.md</code>"],
    ["Why the build differs from the spec", "<code>docs/plan.md</code> §3 Divergence Ledger"],
    ["Every column of every table", "<code>docs/schema.md</code>"],
    ["Request bodies for each endpoint", "<code>docs/api-testing.md</code>, <code>docs/openapi.json</code>"],
    ["Matching engine internals", "<code>docs/matching-engine.md</code>"],
    ["Seeding and resets", "<code>docs/seeding.md</code>"],
])}
"""


# ── 2 ──────────────────────────────────────────────────────────────────────
@section("2", "System architecture")
def s_arch():
    return f"""
<p>Cohesiq runs as three containers under Docker Compose: a Next.js frontend, a FastAPI backend and PostgreSQL.
An optional fourth container, ngrok, exposes the frontend publicly when started with
<code>--profile tunnel</code>. Everything else is an external managed service.</p>
{figure(build.architecture, 1, "Runtime topology. Red arrows are HTTP calls to services outside the Compose network.")}

<h3 id="s2-1">2.1 Containers</h3>
{table(["Container", "Image / stack", "Port", "Responsibility"], [
    ["<code>frontend</code>", "Next.js 16 App Router, React 19, Tailwind v4, shadcn/ui, Clerk", "3000", "All UI; Server Components fetch data; route handlers for speech-to-text, AI suggestions, OAuth and image proxying"],
    ["<code>backend</code>", "FastAPI, Python 3.12, SQLAlchemy 2.0 async (asyncpg)", "8000", "All business rules, matching, persistence, external data enrichment"],
    ["<code>postgres</code>", "postgres:16", "5432", "Single relational store. Health-checked with <code>pg_isready</code>; the backend waits for it"],
    ["<code>ngrok</code> (optional)", "ngrok/ngrok", "4040", "Public tunnel to <code>frontend:3000</code>"],
])}

<h3 id="s2-2">2.2 Request paths</h3>
<p>The frontend reaches the backend two ways, and the two base URLs must never be swapped:</p>
{table(["Caller", "Variable", "Local value", "Why"], [
    ["Server Components, Server Actions, route handlers", "<code>BACKEND_API_URL</code>", "<code>http://backend:8000</code>", "Docker-internal hostname; never reaches the browser"],
    ["Client Components (browser)", "<code>NEXT_PUBLIC_API_URL</code>", "<code>http://localhost:8000</code>", "Must be publicly reachable from the user's machine"],
])}
<p>Both paths go through <code>fetchApi()</code> in <code>lib/api/client.ts</code>, which attaches the Clerk
session token as a bearer token. There are no websockets: the negotiation drawer polls every 4 seconds while open, and
application and contract lists poll every 30–90 seconds (<code>hooks/use-polling</code>).</p>

<h3 id="s2-3">2.3 External services</h3>
{table(["Service", "Called from", "Used for", "If unavailable"], [
    ["Clerk", "Browser, Next.js, FastAPI", "Sign-in, session JWTs, user webhooks, role metadata", "No sign-in; gated routes redirect"],
    ["Groq <code>whisper-large-v3-turbo</code>", "Next.js <code>/api/transcribe</code>", "Voice brief → text", "Voice briefing fails; text and PDF still work"],
    ["Groq <code>llama-3.3-70b</code>", "Next.js <code>/api/campaign-suggestion</code>", "Campaign field suggestions", "No suggestions"],
    ["Groq <code>llama-3.1-8b-instant</code>", "Next.js brief analysis; FastAPI matching", "Brief → form fields; match rationale for the top 5", "Brief: Gemini 2.0 Flash fallback. Rationale: heuristic text"],
    ["Gemini <code>text-embedding-004</code>", "FastAPI matching", "Semantic rescue similarity", "Token Jaccard similarity"],
    ["YouTube Data API v3", "FastAPI <code>youtube/</code>, <code>creators/</code>", "Channel stats, recent videos → social profile + portfolio", "Enrichment returns an error; stored data unchanged"],
    ["Apify actors", "FastAPI <code>social_ingestion/</code>", "Public Instagram and TikTok profile stats", "Enrichment returns an error"],
    ["YouTube / TikTok OAuth", "Next.js <code>/api/oauth/*</code>", "Creator proves account ownership, then triggers enrichment", "Creator can still add the platform manually"],
])}
<p>PDF briefs are parsed in the browser with <code>pdfjs-dist</code>; the file never reaches the server.
Embeddings are computed per request and never stored. pgvector, Neo4j, Redis and TimescaleDB are
deliberately not part of the stack yet (plan §3 D1–D5).</p>
"""


# ── 3 ──────────────────────────────────────────────────────────────────────
@section("3", "Backend design")
def s_backend():
    return f"""
<p>The backend is organised by domain. Each domain folder under <code>backend/app/</code> holds
<code>router.py</code>, <code>service.py</code>, <code>schemas.py</code> and <code>models.py</code>. Routers
only parse input and return Pydantic models; all rules live in services. Scoring code shared across domains
lives in <code>services/</code>.</p>
{figure(build.layers, 2, "Backend layers. A request flows down; cross-domain scoring (L4) is called from the campaigns service.")}

<h3 id="s3-1">3.1 Domains and API surface</h3>
{table(["Prefix", "Domain", "Main endpoints", "Access"], [
    ["<code>/auth</code>", "auth", "<code>GET /me</code>, <code>POST /onboarding</code> (local <code>/register</code>, <code>/login</code> for HS256 dev tokens)", "Signed-in"],
    ["<code>/brands</code>", "brands", "List, get, <code>/me</code>, update; a brand's campaigns and applications", "Mixed; writes are owner-only"],
    ["<code>/creators</code>", "creators", "Profile CRUD; platforms (manual + <code>/platforms/{{youtube,instagram,tiktok}}/enrich</code>); rate cards; portfolio; collaboration history", "Public reads; owner writes"],
    ["<code>/campaigns</code>", "campaigns", "Campaign CRUD and status; apply, invite, respond-invite, shortlist; offer, negotiate, accept, decline; <code>run-matching</code>, <code>matches</code>; contract actions; analytics; reviews", "Role-checked per action"],
    ["<code>/youtube</code>", "youtube", "<code>/search</code>, <code>/videos/{{id}}</code>, <code>/channels</code>, <code>/channels/enrichment</code> — stateless read wrapper", "Signed-in"],
    ["<code>/admin</code>", "admin", "Stats; list/deactivate/delete users; moderate campaign status; list/delete reviews", "<code>require_admin</code>"],
    ["<code>/webhooks</code>", "webhooks", "<code>POST /clerk</code>", "Svix signature"],
    ["<code>/health</code>", "—", "Liveness", "Public"],
])}
<p>Three cross-domain reads are mounted directly in <code>main.py</code>: a creator's own applications and the
public review lists for a creator and a brand. <code>docs/api-testing.md</code> has request bodies for every
route.</p>

<h3 id="s3-2">3.2 Persistence</h3>
<p>SQLAlchemy 2.0 in async mode over <code>asyncpg</code>. <code>get_db</code> yields one
<code>AsyncSession</code> per request. Schema changes go through Alembic; the chain is numbered
<code>0001 → 0022</code> plus a few hash-named revisions. Users and profiles are soft-deleted with
<code>deleted_at</code>.</p>
"""


# ── 4 ──────────────────────────────────────────────────────────────────────
@section("4", "Frontend design")
def s_frontend():
    return f"""
<h3 id="s4-1">4.1 Route groups</h3>
{table(["Group", "Routes", "Who"], [
    ["<code>(public)</code>", "<code>/</code> landing, <code>/design-system</code>", "Anyone"],
    ["<code>(auth)</code>", "<code>/onboarding</code>, brand profile, creator personal info → niches → platforms", "Signed in, onboarding incomplete"],
    ["<code>(dashboards)/brand</code>", "Dashboard; campaigns (new, detail, edit, <code>matches</code>, rate benchmark, ROI calculator); creators (browse, detail, compare); collaborations; messages; profile", "Brand"],
    ["<code>(dashboards)/creator</code>", "Dashboard; campaigns (browse, detail); collaborations; contracts; messages; profile; connect YouTube / TikTok", "Creator"],
    ["<code>(admin)</code>", "<code>/admin</code>, users, campaigns, reviews", "Admin"],
    ["<code>api/</code>", "<code>transcribe</code>, <code>campaign-suggestion</code>, <code>image-proxy</code>, <code>oauth/{{youtube,tiktok}}/{{authorize,callback}}</code>", "Route handlers"],
])}

<h3 id="s4-2">4.2 Rendering pattern</h3>
<p>Each <code>page.tsx</code> is an async Server Component that only fetches data. Interactive UI lives in a
colocated <code>_components/*Client.tsx</code> marked <code>"use client"</code>. Filters are driven by the URL:
the client island calls <code>router.push('?filter=…')</code> and the server page re-reads
<code>searchParams</code>. Server Actions sit in colocated <code>_actions/</code> folders, never in a shared
top-level folder.</p>

<h3 id="s4-3">4.3 Design system</h3>
<p>All colours, type sizes, spacing and shadows come from CSS custom properties in
<code>frontend/design/cohesiq.css</code>, exposed to Tailwind through the <code>@theme inline</code> block in
<code>app/globals.css</code>. Headings use Plus Jakarta Sans, UI text uses DM Sans. The diagrams in this
document use the same palette (brand violet <code>#5B2BD9</code>, warm neutrals).</p>
"""


# ── 5 ──────────────────────────────────────────────────────────────────────
@section("5", "Authentication and access control")
def s_auth():
    return f"""
<h3 id="s5-1">5.1 Identity flow</h3>
<ol>
<li><b>Sign-in.</b> Clerk hosts sign-in. Its session JWT carries <code>metadata.role</code>
(<code>brand · creator · admin</code>) and <code>metadata.onboardingComplete</code>.</li>
<li><b>Route gating (frontend).</b> <code>proxy.ts</code> runs Clerk middleware. Public routes skip auth.
Unauthenticated users on gated routes go to sign-in; users who haven't finished onboarding go to
<code>/onboarding</code>; brands are kept out of creator dashboards and vice versa; <code>/admin</code> requires
<code>role = admin</code>.</li>
<li><b>Token check (backend).</b> <code>get_current_user</code> verifies the RS256 JWT against Clerk's JWKS
(fetched once and cached) and the configured issuer, then loads the <code>users</code> row by
<code>clerk_id</code>.</li>
<li><b>Lazy provisioning.</b> If no row exists yet (for example after a dev database reset), the backend fetches
the user from the Clerk API with <code>CLERK_SECRET_KEY</code> and creates it with the real email and role.</li>
<li><b>Webhooks.</b> <code>POST /webhooks/clerk</code> verifies the Svix signature with
<code>CLERK_WEBHOOK_SECRET</code>, rejects timestamps older than 5 minutes, and handles
<code>user.created</code>, <code>user.updated</code> and <code>user.deleted</code>.</li>
</ol>
<p>When <code>CLERK_ISSUER_URL</code> is unset, the backend accepts local HS256 tokens signed with
<code>SECRET_KEY</code> instead. That mode exists for development and tests only.</p>

<h3 id="s5-2">5.2 Authorisation</h3>
<p>Role checks happen in dependencies and services, not in the UI alone. Brand actions resolve the caller's
<code>brand_profiles</code> row and compare it with <code>campaign.brand_id</code> or <code>contract.brand_id</code>;
creator actions do the same with <code>creator_id</code>. Admin endpoints use <code>require_admin</code>, which
reads the role from the JWT claims.</p>
"""


# ── 6 ──────────────────────────────────────────────────────────────────────
@section("6", "End-to-end workflow")
def s_flow():
    return f"""
<p>A campaign moves across three actors. The two loops, counter-offers and content revisions, are where most
of the elapsed time goes.</p>
{figure(build.journeys, 3, "Brief to review. Numbers give the order of steps; dashed arrows loop back.")}
<p>Creators can also enter at step 3: they browse public campaigns and apply, which creates a
<code>pending</code> application, or they accept a brand's invite. Campaign visibility controls whether a
campaign appears in the public browse list.</p>
"""


# ── 7 ──────────────────────────────────────────────────────────────────────
@section("7", "Matching engine")
def s_matching():
    return f"""
<p><code>POST /campaigns/{{id}}/run-matching</code> ranks every available creator for one campaign. The engine
is deterministic: the same data always gives the same ranking. The LLM only writes the explanation text.</p>
{figure(build.matching, 4, "The five stages. Hard filters are never undone; semantic rescue can only raise a zero niche score, and only up to 0.40.")}

<h3 id="s7-1">7.1 Scoring</h3>
<p>Each creator that passes stages 1–3 gets six sub-scores between 0 and 1, combined with fixed weights:</p>
<p class="formula">score_total = 0.45·niche + 0.20·budget + 0.15·platform + 0.10·engagement + 0.08·language + 0.02·recency</p>
{figure(build.weights, 5, "Weights from <code>SCORE_WEIGHTS</code>. Niche, budget and platform together make up 0.80 of the score.")}

<h3 id="s7-2">7.2 Configuration constants</h3>
<p>All in <code>backend/app/services/matching_config.py</code>; nothing else defines them.</p>
{table(["Constant", "Value", "Effect"], [
    ["<code>SCORE_WEIGHTS</code>", ".45 / .20 / .15 / .10 / .08 / .02", "Weights in the formula above"],
    ["<code>BUDGET_SOFT_BUFFER_RATIO</code>", "0.30", "Creators up to 1.3 × the campaign's max budget per creator still pass the budget gate"],
    ["<code>BUDGET_UNKNOWN_SCORE</code>", "0.5", "Budget score when no rate card or tier estimate exists"],
    ["<code>SEMANTIC_SIMILARITY_THRESHOLD</code>", "0.28", "Minimum similarity for a semantic rescue"],
    ["<code>SEMANTIC_RESCUE_NICHE_CAP</code>", "0.40", "Highest niche score a rescue can give"],
    ["<code>UNKNOWN_RECENCY_SCORE</code>", "0.20", "Recency score with no post dates"],
    ["<code>CONFLICT_LOOKBACK_DAYS</code>", "90", "Window for the competitor-conflict gate"],
    ["<code>TOP_MATCH_LIMIT</code>", "10", "Matches stored per campaign"],
    ["<code>LLM_RATIONALE_TOP_N</code>", "5", "Matches that get an LLM-written rationale"],
])}

<h3 id="s7-3">7.3 One matching run</h3>
{figure(build.run_matching_sequence, 6, "Calls made during one request. Returns are omitted except the final response.")}
<p>Rerunning replaces the previous result: the campaign's old <code>ai_match_scores</code> rows are deleted
first. Ties are broken by follower count, then creator id. If strict matching finds nobody, the creators that were
excluded <em>only</em> by the niche filter are scored instead, so a brand never sees an empty list just because of
how the niche was worded.</p>
"""


# ── 8 ──────────────────────────────────────────────────────────────────────
@section("8", "Deal lifecycle")
def s_lifecycle():
    return f"""
<p>The deal is tracked on two records with separate status fields. The <b>application</b> covers everything up
to agreement; the <b>contract</b> covers delivery. Campaign status is not part of the deal flow; the one link is
that offers can only be sent while the campaign is <code>active</code>.</p>
{figure(build.application_lifecycle, 7, "<code>campaign_applications.status</code>.")}
{figure(build.contract_lifecycle, 8, "<code>contracts.status</code>.")}

<h3 id="s8-1">8.1 Endpoint to transition map</h3>
{table(["Endpoint (under <code>/campaigns</code>)", "Actor", "Application", "Contract"], [
    ["<code>POST /{{id}}/apply</code>", "Creator", "→ pending", "—"],
    ["<code>POST /{{id}}/invite</code>", "Brand", "→ invited", "—"],
    ["<code>POST /{{id}}/applications/{{a}}/respond-invite</code>", "Creator", "invited → pending | declined", "—"],
    ["<code>POST /{{id}}/shortlist</code>", "Brand", "pending | terminal → shortlisted", "—"],
    ["<code>POST /{{id}}/applications/{{a}}/offer</code>", "Brand", "shortlisted | pending → invited", "→ drafted"],
    ["<code>POST /{{id}}/applications/{{a}}/negotiate</code>", "Either", "invited | pending_agreement → pending_agreement", "terms updated"],
    ["<code>POST …/offer/accept</code>", "Either", "→ accepted", "drafted → active"],
    ["<code>POST …/offer/decline</code>", "Either", "→ rejected (brand) | declined (creator)", "—"],
    ["<code>PATCH /contracts/{{c}}/submit-draft</code>", "Creator", "—", "active | in_production → content_submitted"],
    ["<code>PATCH /contracts/{{c}}/request-revision</code>", "Brand", "—", "content_submitted → in_production (if under cap)"],
    ["<code>PATCH /contracts/{{c}}/approve</code>", "Brand", "—", "content_submitted → content_approved"],
    ["<code>PATCH /contracts/{{c}}/publish</code>", "Creator", "—", "content_approved → published"],
    ["<code>PATCH /contracts/{{c}}/close</code>", "Brand", "→ completed", "published → closed"],
], cls="compact")}
<p>After closing, both sides can post a review (<code>POST /campaigns/reviews/</code>). Live metrics can be synced
while a contract is <code>published</code> or <code>closed</code>; each sync stores a
<code>live_content_metric_snapshots</code> row.</p>
"""


# ── 9 ──────────────────────────────────────────────────────────────────────
@section("9", "Data model")
def s_data():
    return f"""
<p>PostgreSQL 16, relational only. The two diagrams below split the model into supply (who creators are and
what they charge) and demand (campaigns and the deals they produce). They show the columns that drive behaviour;
<code>docs/schema.md</code> lists every column.</p>
{figure(build.er_creator, 9, "Identity and creator supply. <code>#</code> = primary key, <code>→</code> = foreign key.")}
{figure(build.er_campaign, 10, "Campaigns and deals.")}
<h3 id="s9-1">9.1 Integrity rules worth knowing</h3>
<ul>
<li>One contract per application: <code>contracts.application_id</code> is unique.</li>
<li><code>ai_match_scores</code> is derived data. It is safe to delete; the next matching run rebuilds it.</li>
<li><code>creator_collaboration_history.brand_id</code> is nullable, so past work with brands that are not on the
platform can be recorded. Those rows have no <code>brand_category</code> and cannot trigger a competitor
conflict.</li>
<li><code>creator_social_profiles.data_source</code> and <code>is_api_verified</code> record where each set of
stats came from (API, scrape or self-reported).</li>
<li><code>campaigns.campaign_type</code> (what the brand wants) and a creator's collaboration types (what the
creator offers) are separate lists on purpose. Do not merge them (plan §3.1).</li>
</ul>
"""


# ── 10 ─────────────────────────────────────────────────────────────────────
@section("10", "Configuration")
def s_config():
    return f"""
<p>Every variable is listed in the matching <code>.env.example</code>. New variables must be added there in
both <code>frontend/</code> and <code>backend/</code> where they apply.</p>
<h3 id="s10-1">10.1 Backend (<code>backend/.env</code>)</h3>
{table(["Variable", "Purpose"], [
    ["<code>DATABASE_URL</code>", "asyncpg DSN; Compose sets it to the <code>postgres</code> service"],
    ["<code>SECRET_KEY</code>", "HS256 signing for local dev tokens"],
    ["<code>CLERK_ISSUER_URL</code>", "Enables RS256 Clerk verification; set in Compose"],
    ["<code>CLERK_SECRET_KEY</code>", "Lazy user provisioning from the Clerk API"],
    ["<code>CLERK_WEBHOOK_SECRET</code>", "Svix signature check on <code>/webhooks/clerk</code> (not yet in <code>.env.example</code>, see G9)"],
    ["<code>GROQ_API_KEY</code>", "Match rationale"],
    ["<code>GEMINI_API_KEY</code>", "Embeddings for semantic rescue"],
    ["<code>YOUTUBE_API_KEY</code>", "YouTube Data API v3"],
    ["<code>APIFY_API_TOKEN</code>, <code>APIFY_*_ACTOR_ID</code>", "Instagram / TikTok enrichment"],
    ["<code>NGROK_AUTHTOKEN</code>", "Optional tunnel"],
])}
<h3 id="s10-2">10.2 Frontend (<code>frontend/cohesiq-v0/.env</code>)</h3>
{table(["Variable", "Purpose"], [
    ["<code>NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY</code>, <code>CLERK_SECRET_KEY</code>", "Clerk SDK"],
    ["<code>BACKEND_API_URL</code>", "Server-side base URL (<code>http://backend:8000</code>)"],
    ["<code>NEXT_PUBLIC_API_URL</code>", "Browser base URL; must be publicly reachable in each environment"],
    ["<code>GROQ_API_KEY</code>, <code>GEMINI_API_KEY</code>", "Speech-to-text, brief analysis, suggestions"],
    ["<code>YOUTUBE_CLIENT_ID/SECRET/REDIRECT_URI</code>", "YouTube OAuth connect"],
    ["<code>TIKTOK_CLIENT_KEY/SECRET/REDIRECT_URI</code>", "TikTok OAuth connect"],
    ["<code>NEXT_ALLOWED_DEV_ORIGINS</code>", "Extra hosts allowed to use the dev server's hot reload"],
])}
"""


# ── 11 ─────────────────────────────────────────────────────────────────────
@section("11", "Operations and quality")
def s_ops():
    return f"""
<h3 id="s11-1">11.1 Running</h3>
{table(["Task", "Command"], [
    ["Start everything", "<code>docker compose up --build</code>"],
    ["With public tunnel", "<code>docker compose --profile tunnel up</code>"],
    ["Health", "<code>docker compose ps</code>, <code>GET /health</code>"],
    ["Seed real creator data", "<code>docker compose exec -T postgres psql -U cohesiq -d cohesiq &lt; db/seed.sql</code>"],
    ["Wipe data (keeps schema)", "<code>docker compose exec backend python -m scripts.reset_db</code>"],
    ["Assign roles to test users", "<code>docker compose exec backend python -m scripts.sync_clerk_users</code>"],
])}
<p>In Compose, both the frontend and the backend mount the source folder and run in dev mode (<code>pnpm dev</code>,
<code>uvicorn --reload</code>). The backend entrypoint runs <code>alembic upgrade head</code> before starting, so
migrations apply on every container start. <code>db/seed.sql</code> is a symlink to the latest snapshot in <code>db/snapshots/</code>, holding real
YouTube, Instagram and TikTok creator data.</p>

<h3 id="s11-2">11.2 Tests</h3>
{table(["Suite (<code>backend/tests/</code>)", "Tests", "Covers"], [
    ["<code>test_matching_engine.py</code>", "7", "Budget buffer, recency buckets, semantic rescue cap, score normalisation"],
    ["<code>test_campaign_application_gatekeeper.py</code>", "7", "Application status transition guards"],
    ["<code>test_creator_youtube_enrichment.py</code>", "8", "YouTube → social profile + portfolio persistence"],
    ["<code>test_social_ingestion_service.py</code>", "7", "Apify Instagram / TikTok parsing"],
    ["<code>test_creator_public_social_enrichment.py</code>", "3", "Public enrichment endpoints"],
    ["<code>test_youtube_service.py</code>", "3", "YouTube API wrapper"],
])}
<p>Run with <code>docker compose exec backend python -m unittest discover tests -v</code>. The frontend has no
automated tests; <code>pnpm run lint</code> is the only check.</p>
"""


# ── 12 ─────────────────────────────────────────────────────────────────────
@section("12", "Known gaps and risks")
def s_gaps():
    return f"""
<p>Found while checking this document against the code. None of these block the current demo, but each one
should be settled before production.</p>
{table(["#", "Area", "Finding", "Suggested action"], [
    ["G1", "Contracts", "<code>disputed</code> is in the status enum and the revision-limit error tells brands to raise a dispute, but no endpoint sets it.", "Add a dispute endpoint, or remove the status and change the error text."],
    ["G2", "Applications", "<code>invited</code> means both \"invite waiting for the creator\" and \"offer sent\".", "Split into two statuses, or rely on whether a contract exists and document it."],
    ["G3", "Security", "CORS allows every origin together with credentials (<code>main.py</code>).", "Restrict <code>allow_origins</code> per environment."],
    ["G4", "Performance", "The Gemini embedding call, the Clerk JWKS fetch and lazy provisioning are blocking calls inside async handlers.", "Move them to a thread pool or async HTTP clients."],
    ["G5", "Performance", "Matching embeds creator text on every run; nothing is cached.", "Persist embeddings (Phase-E pgvector, plan §3) or cache per profile version."],
    ["G6", "Docs", "The baseline table in <code>docs/tasks/tasks-navid.md</code> still lists niche .35 / budget .30.", "Update to .45 / .20."],
    ["G7", "Quality", "No frontend tests; no end-to-end test of the deal lifecycle.", "Add an API-level lifecycle test from offer to close."],
    ["G8", "Deployment", "Compose runs dev servers with source mounts; there is no production build profile.", "Add a production Compose profile or image targets."],
    ["G9", "Config", "<code>CLERK_WEBHOOK_SECRET</code> is required by the webhook router but missing from both <code>.env.example</code> files; the root file also carries misspelt <code>APPIFY_*</code> duplicates.", "Add the variable; drop the duplicates."],
], cls="compact")}
"""


def toc():
    items = "".join(f'<li><a href="#s{n}">{n}. {t}</a></li>' for n, t, _ in SECTIONS)
    return f'<nav class="toc"><p class="eyebrow">Contents</p><ol>{items}</ol></nav>'


EXTRA_CSS = """
.frame { max-width: 1280px; }
.doc p, .doc li { font-size: 0.95rem; line-height: 1.65; color: var(--color-ink); max-width: 52rem; }
.doc p { margin-bottom: 0.9rem; }
.doc ul, .doc ol { padding-left: 1.4rem; margin-bottom: 1rem; }
.doc li { margin-bottom: 0.35rem; }
.doc code { font-family: var(--font-mono); font-size: 0.82em; background: rgba(33,29,24,0.05);
  padding: 0.05em 0.3em; border-radius: 3px; }
.doc a { color: var(--color-accent); }
h2 { font-family: var(--font-serif); font-weight: 400; font-size: 1.9rem; letter-spacing: -0.01em;
  margin: 3.5rem 0 1rem; padding-top: 1.5rem; border-top: 1px solid var(--color-rule); }
h2 .num { color: var(--color-accent); margin-right: 0.5rem; }
h3 { font-size: 1.05rem; font-weight: 600; margin: 2rem 0 0.75rem; }
.meta { display: flex; gap: 2rem; flex-wrap: wrap; font-family: var(--font-mono); font-size: 0.72rem;
  color: var(--color-muted); margin: 1rem 0 2rem; }
.meta b { color: var(--color-ink); font-weight: 500; }
.toc { background: #fff; border: 1px solid var(--color-rule); border-radius: 6px; padding: 1.25rem 1.5rem;
  margin-bottom: 1rem; }
.toc ol { columns: 2; list-style: none; padding: 0; }
.toc li { font-size: 0.9rem; margin-bottom: 0.35rem; }
.toc a { color: var(--color-ink); text-decoration: none; }
.toc a:hover { color: var(--color-accent); }
table { width: 100%; border-collapse: collapse; margin: 0.5rem 0 1.5rem; font-size: 0.86rem; background: #fff;
  border: 1px solid var(--color-rule); }
th { text-align: left; font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500;
  letter-spacing: 0.1em; text-transform: uppercase; color: var(--color-muted); background: #F3EFE9;
  padding: 0.6rem 0.8rem; border-bottom: 1px solid var(--color-rule); }
td { padding: 0.6rem 0.8rem; border-bottom: 1px solid var(--color-rule); vertical-align: top; line-height: 1.5; }
table.compact td { padding: 0.45rem 0.7rem; }
figure { margin: 1.5rem 0 2rem; }
figure .figure { border: 1px solid var(--color-rule); border-radius: 6px; }
figcaption { font-size: 0.82rem; color: var(--color-muted); margin-top: 0.6rem; line-height: 1.5; }
figcaption a { font-family: var(--font-mono); font-size: 0.72rem; margin-left: 0.4rem; }
.formula { font-family: var(--font-mono); font-size: 0.85rem !important; background: #fff;
  border: 1px solid var(--color-rule); border-left: 3px solid var(--color-accent); padding: 0.9rem 1rem;
  border-radius: 4px; max-width: none !important; }
@page { size: A4; margin: 14mm 12mm; }
@media print {
  html, body { background: #fff; padding: 0; } .frame { max-width: none; padding: 0; } .nav { display: none; }
  h2 { break-before: page; margin-top: 0; } h3 { break-after: avoid; }
  figure, tr { break-inside: avoid; } thead { display: table-header-group; }
  .figure { overflow: visible; } svg.diagram { min-width: 0; }
  figcaption a { display: none; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
"""


def main():
    body = "".join(f'<section id="s{n}"><h2><span class="num">{n}</span>{t}</h2>{fn()}</section>'
                   for n, t, fn in SECTIONS)
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cohesiq technical design document</title>
  <link href="{FONT_LINK}" rel="stylesheet">
  <style>{CSS}{EXTRA_CSS}</style>
</head>
<body>
  <div class="frame doc">
    <p class="nav"><a href="index.html">← Cohesiq diagrams</a></p>
    <p class="eyebrow">Technical design document</p>
    <h1>Cohesiq: system architecture and design</h1>
    <p class="lede">How the influencer-matching platform is built, from containers and code layout to the matching
    engine, deal lifecycle and data model. Checked against the source code.</p>
    <div class="meta"><span>Date <b>{DATE}</b></span><span>Schema <b>Alembic 0022</b></span>
      <span>Status <b>As built</b></span><span>Figures <b>10</b></span></div>
    {toc()}
    {body}
    <footer>Generated by docs/diagrams/html/techdoc.py from the figures in build.py · diagram-design skill ·
    cohesiq profile. Rebuild with build.py, then export_pdf.py for the PDF.</footer>
  </div>
</body>
</html>
"""
    OUT.write_text(doc)
    print("wrote", OUT.name)


if __name__ == "__main__":
    main()
