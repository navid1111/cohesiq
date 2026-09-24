# Docs Index

> Navigation map for agents and contributors. One-line description of every file and directory in `docs/`.
> When docs disagree, resolve by the hierarchy below — do not guess.

## Documentation Hierarchy (highest → lowest authority)

```
docs/requirements.md   ← BuildFest rubric (immutable)
    └─ docs/srs.md     ← Cohesiq product spec (authoritative vision)
        └─ docs/plan.md ← Unified implementation plan (reconciles SRS with real code; lists all divergences)
            └─ docs/schema.md ← Code-true relational schema
                └─ docs/tasks/tasks-*.md ← Per-developer backlogs
```

Never silently edit `srs.md` to match a shortcut. Record divergences in `plan.md` §3 Divergence Ledger.

---

## Source of Truth Chain

| File | What it contains |
|---|---|
| [`requirements.md`](requirements.md) | BuildFest 2026 MarTech Track competition rubric — immutable baseline |
| [`srs.md`](srs.md) | IEEE-style product spec: Intro/Scope, Overall Description, Functional & Non-Functional Requirements. References (no longer embeds) user stories, personas, and diagrams |
| [`user-stories.md`](user-stories.md) | INVEST-compliant user stories with acceptance criteria + FR/rubric cross-refs (extracted from the SRS) |
| [`personas.md`](personas.md) | Persona cards by segment — demand (brands/SMEs), supply (creators), internal (operators) |
| [`plan.md`](plan.md) | Unified implementation plan: phase status, as-built vs SRS divergence ledger (§3), migration list, service inventory |
| [`schema.md`](schema.md) | Full DDL for the live PostgreSQL schema — authoritative relational model (migration head `0022`) |
| [`srs-revisions.md`](srs-revisions.md) | Index of all approved SRS change requests → redirects to `revisions/` |

---

## Task Backlogs

| File | Owner | Scope |
|---|---|---|
| [`tasks/tasks-sakib.md`](tasks/tasks-sakib.md) | Sakib | Campaign UI, marketplace, contract entity, analytics, AI features |
| [`tasks/tasks-navid.md`](tasks/tasks-navid.md) | Navid | YouTube enrichment, matching engine, seeding pipeline, semantic/LLM services |
| [`tasks/tasks-labib.md`](tasks/tasks-labib.md) | Labib | Campaign creation UX (modal popup, 3-step wizard), invitation lifecycle (Invited→Negotiation→Accepted Kanban, shortlist-as-bookmark) |
| [`tasks/n01-persist-youtube-enrichment.md`](tasks/n01-persist-youtube-enrichment.md) | Navid | Detailed spec for N01 — persisting YouTube API data to creator profiles |
| [`tasks/admin-panel.md`](tasks/admin-panel.md) | Sakib | **TOP PRIORITY** step-by-step runbook (F00–F13) — role-gated admin panel: Clerk-metadata auth, `/admin` route group, read-only `/admin/*` endpoints |

---

## Design & UI

| File | What it contains |
|---|---|
| [`design-system.md`](design-system.md) | Full token reference: brand colors, neutral scale, typography, spacing, radius, shadows, Tailwind v4 integration, shadcn/ui bridge, agent rules |
| [`pages/frontend-page-reference.md`](pages/frontend-page-reference.md) | All Next.js routes, page components, and their UI responsibilities |

---

## Diagrams

| File | What it contains |
|---|---|
| [`diagrams/architecture.md`](diagrams/architecture.md) | As-built system architecture: Docker containers, ports, external services (Groq, Gemini, YouTube, Tavily, Clerk), request paths, env vars |
| [`diagrams/dfd.md`](diagrams/dfd.md) | Logical data flow diagram (L0 context + L1 major processes) — technology-agnostic |
| [`diagrams/erd.md`](diagrams/erd.md) | Entity relationship diagram — mirrors the live PostgreSQL schema |
| [`diagrams/use-case.md`](diagrams/use-case.md) | UML use case diagram covering all actor/system interactions |
| [`diagrams/html/index.html`](diagrams/html/index.html) | Editorial HTML diagram set (code-checked): architecture, backend layers, journey swimlane, matching pipeline + weights, run-matching sequence, application/contract state machines, two ER diagrams. Rebuild with `python3 docs/diagrams/html/build.py` |
| [`diagrams/html/technical-document.html`](diagrams/html/technical-document.html) | **Technical design document** — whole system in 12 sections with all 10 figures embedded: architecture, backend API surface, frontend routes, auth, workflow, matching, deal lifecycle + endpoint map, data model, configuration, operations/tests, known gaps (G1–G9). Built by the same `build.py` run; PDF copy [`technical-document.pdf`](diagrams/html/technical-document.pdf) via `export_pdf.py` (needs Playwright + Chromium) |

---

## Components (self-contained, code-true references)

| File | What it contains |
|---|---|
| [`matching-engine.md`](matching-engine.md) | Authoritative matching reference — 5-stage pipeline, 6-factor weights (niche 0.45 / budget 0.20 / …), budget gating, capped semantic rescue, LLM rationale. Validated against `matching_config.py` + `matching.py` |
| [`youtube-integration.md`](youtube-integration.md) | YouTube Data API v3 enrichment — endpoints, field mappings, `data_source` provenance, persistence into `creator_social_profiles` |

## Concepts

| File | What it contains |
|---|---|
| [`concepts/campaign.md`](concepts/campaign.md) | What a Campaign is — job posting analogy, visibility model, lifecycle |
| [`concepts/contract.md`](concepts/contract.md) | What a Contract is — engagement types, clause structure, state machine, fee table |

---

## Revision Records

All dated revision records live in `revisions/`. Named `<subject>-YY-MM-DD.md`.

| File | Date | Author | Subject |
|---|---|---|---|
| [`revisions/srs-revisions-26-06-06.md`](revisions/srs-revisions-26-06-06.md) | 2026-06-06 | Sakib | Contract entity change request (E-phase) |
| [`revisions/srs-revisions-26-06-07.md`](revisions/srs-revisions-26-06-07.md) | 2026-06-07 | Navid | Matching weight rebalance + YouTube enrichment persistence |
| [`revisions/matching-engine-plan-26-06-07.md`](revisions/matching-engine-plan-26-06-07.md) | 2026-06-07 | Navid | Full matching engine architecture reference (stages, weights, semantic rescue) |
| [`revisions/youtube-implementation-26-06-07.md`](revisions/youtube-implementation-26-06-07.md) | 2026-06-07 | Navid | YouTube API integration reference (endpoints, field mappings, enrichment flow) |
| [`revisions/youtube-task-26-06-07.md`](revisions/youtube-task-26-06-07.md) | 2026-06-07 | Navid | YouTube integration unit task tracker |
| [`revisions/srs-revisions-26-06-10.md`](revisions/srs-revisions-26-06-10.md) | 2026-06-10 | Team | Documentation overhaul — IEEE SRS restructure, stories/personas extraction, diagram single-sourcing, weight-drift fix (0.45/0.20), migration head 0022, component-doc relocation |

---

## Research & Analysis

These files are background research — informational, not prescriptive.

| File | What it contains |
|---|---|
| [`analysis-reports/data-availability-analysis-report.md`](analysis-reports/data-availability-analysis-report.md) | API constraints, available metrics, and data availability for YouTube/Instagram/Facebook |
| [`analysis-reports/feasibility-analysis-report.md`](analysis-reports/feasibility-analysis-report.md) | Technical feasibility and competitive landscape |
| [`analysis-reports/growth-analysis-report.md`](analysis-reports/growth-analysis-report.md) | 8-section strategic development plan with 5-phase roadmap |
| [`deep-research-reports/data-source-research-report.md`](deep-research-reports/data-source-research-report.md) | Technical architecture and compliance blueprint for multi-platform integration |
| [`deep-research-reports/market-research-report.md`](deep-research-reports/market-research-report.md) | Strategic market intelligence for the Bangladesh influencer marketplace |
| [`ideation/brand-creator-collaboration.md`](ideation/brand-creator-collaboration.md) | Mental model of influencer marketing workflow — early ideation artifact |

---

## Operations & Delivery

| File | What it contains |
|---|---|
| [`api-testing.md`](api-testing.md) | Backend route catalog with access rules, query parameters, and copy-ready API-testing bodies |
| [`seeding.md`](seeding.md) | **Seeding reference** — use `seed.sql` (real creator data); reset procedure; what survives a DB reset; legacy scripts status |
| [`deployment-guide.md`](deployment-guide.md) | Deployment instructions, Docker Compose configuration, environment setup |
| [`openapi.json`](openapi.json) | OpenAPI 3.x specification for all backend API endpoints |
| [`submittable.md`](submittable.md) | BuildFest submission answer sheet — mirrors `requirements.md` section-for-section (copy-paste form answers) |
| [`executive-summary.md`](executive-summary.md) | High-level project overview for non-technical stakeholders |

---

## AI Prompt Templates

Pre-written prompts used during research and development. For reference only — not active system prompts.

| File | Purpose |
|---|---|
| [`base-prompts/build-frontend-prompt.md`](base-prompts/build-frontend-prompt.md) | Full UI generation prompt for Cohesiq |
| [`base-prompts/data-source-research-prompt.md`](base-prompts/data-source-research-prompt.md) | API specialist prompt for data source and compliance analysis |
| [`base-prompts/landing-page-design-prompt.md`](base-prompts/landing-page-design-prompt.md) | Landing page redesign and design system generation |
| [`base-prompts/market-research-prompt.md`](base-prompts/market-research-prompt.md) | Market analysis prompt for Bangladesh influencer ecosystem |
