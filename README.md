# Cohesiq

> AI-powered B2B influencer-matching platform for the Bangladesh creator economy.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Next.js 16](https://img.shields.io/badge/Next.js-16-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)

## What is Cohesiq

Cohesiq is a B2B SaaS marketplace that connects brands with the right content creators using an explainable AI matching engine. Brands describe a campaign — by typing, talking, or uploading a brief — and Cohesiq ranks creators by niche, budget, platform, engagement, language, and recency, then drives the relationship through an offer, negotiation, and contract lifecycle. It is built for the Bangladesh influencer market and seeded with real, verified creator data.

## The problem

Bangladesh's influencer marketing is fragmented and largely manual. Brands discover creators through word of mouth and spreadsheets, have no reliable way to gauge fit or fair pricing, and negotiate over scattered DMs with no contract trail. Creators, in turn, lack a single place to surface their reach and rates to serious buyers. Cohesiq replaces that guesswork with data-driven, explainable matching and a structured deal pipeline.

## Key features

- **Explainable AI matching engine** — a 6-factor weighted score (niche 0.45, budget 0.20, platform 0.15, engagement 0.10, language 0.08, recency 0.02) with a per-factor breakdown so brands understand *why* a creator ranks where they do.
- **Voice + PDF campaign creation** — describe a campaign out loud (transcribed via Groq Whisper) or upload a brief PDF; an LLM extracts structured campaign fields automatically.
- **Offer & negotiation flow** — brands send offers, creators counter, and both sides negotiate within the platform until terms are accepted.
- **Contract lifecycle** — accepted offers convert into trackable contracts with engagement types, clauses, and a defined state machine.
- **Creator discovery** — filterable, URL-driven marketplace of verified creators with profiles, rate cards, and portfolios.
- **Admin panel** — role-gated `/admin` area (Clerk-metadata auth) for read-only oversight of users, campaigns, and platform activity.
- **YouTube enrichment** — pulls live channel metrics from the YouTube Data API to keep creator profiles current.

## Architecture

Cohesiq is a decoupled full-stack application: a **Next.js 16** App Router frontend talks to a **FastAPI** backend over HTTP, and the backend persists everything to **PostgreSQL 16** (relational-only). The backend follows Domain-Driven Design (`auth`, `brands`, `creators`, `campaigns`, plus cross-domain `services`), where routers only parse requests and all logic lives in the service layer. Authentication is handled by Clerk using RS256 JWTs validated against Clerk's JWKS on the backend. The entire stack is orchestrated with Docker Compose (`postgres`, `backend`, `frontend`, `ngrok`).

See **[`docs/diagrams/architecture.md`](docs/diagrams/architecture.md)** for the full as-built diagram (containers, ports, external services, request paths, and env vars).

For the whole system in one place, read the **[technical design document (PDF)](docs/diagrams/html/technical-document.pdf)**. It has 12 sections and 10 diagrams covering architecture, API surface, auth, the matching engine, the deal lifecycle, the data model, configuration, operations and known gaps. An HTML version is at [`docs/diagrams/html/technical-document.html`](docs/diagrams/html/technical-document.html) (open it locally in a browser).

## Tech stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, shadcn/ui, Clerk auth |
| **Backend** | FastAPI, Python 3.12, SQLAlchemy 2.0 (async), Alembic, Pydantic v2 |
| **Data** | PostgreSQL 16 (relational-only); 67 verified Bangladesh YouTube channels seeded |
| **AI** | Groq `llama-3.1-8b-instant` (extraction/matching), Groq Whisper `large-v3-turbo` (voice), Gemini `1.5-flash` + `text-embedding-004` (semantic) |
| **Infra** | Docker Compose (`postgres`, `backend`, `frontend`, `ngrok`), Clerk, YouTube Data API |

## Quick start

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop) and Docker Compose
- A [Clerk](https://clerk.com/) account (publishable + secret keys)
- API keys: [Groq](https://console.groq.com/) and [Google Gemini](https://aistudio.google.com/); a [YouTube Data API](https://console.cloud.google.com/) key for enrichment

### 1. Clone

```bash
git clone https://github.com/sakibhossain323/cohesiq.git
cd cohesiq
```

### 2. Configure environment variables

Copy the example files and fill in your keys. Never commit `.env` files.

```bash
# Backend — set CLERK_SECRET_KEY, DATABASE_URL, GROQ_API_KEY, GEMINI_API_KEY, YouTube key
cp backend/.env.example backend/.env

# Frontend — set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY
cp frontend/cohesiq-v0/.env.example frontend/cohesiq-v0/.env
```

> The frontend uses a two-variable API contract: `BACKEND_API_URL` (`http://backend:8000`, server-side only) and `NEXT_PUBLIC_API_URL` (`http://localhost:8000`, browser only). Do not mix them up.

### 3. Run the stack

```bash
docker compose up --build
```

- Frontend → http://localhost:3000
- Backend → http://localhost:8000
- Interactive API docs (Swagger) → http://localhost:8000/docs

### 4. Seed the database

Load the canonical seed (real Bangladesh creator data) once the containers are up:

```bash
docker compose exec -T postgres psql -U cohesiq -d cohesiq < db/seed.sql
```

`db/seed.sql` is a symlink to the latest snapshot in `db/snapshots/`. To wipe and re-seed, see [`docs/seeding.md`](docs/seeding.md).

## Project structure

```
cohesiq/
├── frontend/cohesiq-v0/      # Next.js 16 App Router frontend
│   └── app/                  # routes; _actions/ + _components/ colocated per feature
├── backend/                  # FastAPI service
│   ├── app/
│   │   ├── auth/             # Clerk JWT validation, user sync
│   │   ├── brands/           # brand profiles
│   │   ├── creators/         # creator profiles, social profiles, rate cards, portfolio
│   │   ├── campaigns/        # campaigns, applications, collaborations, reviews
│   │   ├── admin/            # role-gated admin endpoints
│   │   ├── services/         # cross-domain: matching, semantic_match, llm_matching
│   │   ├── youtube/          # stateless YouTube Data API read wrapper
│   │   └── common/           # shared deps (get_db, get_current_user)
│   └── scripts/              # reset_db, sync_clerk_users, seeding utilities
├── db/                       # seed.sql + dated snapshots
└── docs/                     # source-of-truth documentation (start at docs/index.md)
```

## Documentation

Start at **[`docs/index.md`](docs/index.md)** — the full navigation map for every doc file and the source-of-truth hierarchy.

| Doc | What it covers |
|---|---|
| [`docs/index.md`](docs/index.md) | Master navigation map for all documentation |
| [Technical design document](docs/diagrams/html/technical-document.pdf) ([HTML](docs/diagrams/html/technical-document.html)) | The whole system with diagrams: architecture, API, auth, matching, deal lifecycle, data model, config, ops, known gaps |
| [`docs/diagrams/html/`](docs/diagrams/html/index.html) | The 10 standalone diagrams (rebuild with `python3 docs/diagrams/html/build.py`) |
| [`docs/srs.md`](docs/srs.md) | Product spec — functional/non-functional requirements, user stories, ERD |
| [`docs/plan.md`](docs/plan.md) | Implementation plan, phase status, and the divergence ledger (§3) |
| [`docs/schema.md`](docs/schema.md) | Code-true relational schema (read before changing any model) |
| [`docs/matching-engine.md`](docs/matching-engine.md) | Matching engine architecture — stages, weights, semantic rescue |
| [`docs/youtube-integration.md`](docs/youtube-integration.md) | YouTube Data API integration and enrichment flow |
| [`docs/executive-summary.md`](docs/executive-summary.md) | High-level overview for non-technical stakeholders |

## Contributing

1. **Branch from `main`** — create a feature branch; never commit directly to `main`. Open a PR for review.
2. **Graphify-first** — this repo ships a live AST knowledge graph at `graphify-out/`. Before grepping source, run `graphify query "<question>"`, `graphify explain "<concept>"`, or `graphify path "<A>" "<B>"` to locate relevant code. Run `graphify update .` after meaningful changes.
3. **Track your work** — confirm the task exists in the relevant `docs/tasks/tasks-*.md` backlog before implementing, and mark it done/partial/broken afterward.
4. **Respect the layering** — backend routers parse requests only; all logic lives in the service layer with no cross-domain imports. Frontend follows the Server Component → Client Island pattern and always uses `fetchApi()` from `lib/api/client.ts`.
5. **Use design tokens** — never hardcode colors, font sizes, spacing, or shadows. See [`docs/design-system.md`](docs/design-system.md).

Detailed conventions live in **[`AGENTS.md`](AGENTS.md)** (all AI agents and contributors) and **[`CLAUDE.md`](CLAUDE.md)** (Claude Code specifics).

## License

Released under the [MIT License](LICENSE).

## Team

Built by the Cohesiq Team for **BuildFest 2026** (MarTech Track).
