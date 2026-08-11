# Fabricators.ai

AI engineering platform for materials science. Users describe a materials
engineering problem in conversation (formula, target property, use case);
the platform grounds the conversation in verified scientific data and turns
it into a structured **Knowledge Model** and, on request, a professional
**Engineering Report** (material identification, synthesis pathway, 3D
structure visualization, performance analysis, citations).

Chat is the interface. The Knowledge Model + Report is the product.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript, Vite, Wouter (routing), Tailwind CSS, Shadcn UI / Radix |
| Backend | Express.js + TypeScript |
| Database | PostgreSQL, hosted on **Neon** (owned account, not Replit-provisioned) |
| ORM | Drizzle ORM + Drizzle Kit |
| Sessions | `express-session` + `connect-pg-simple` (Postgres-backed, survives server restarts) |
| AI / LLM | **Anthropic Claude API** (`claude-sonnet-4-5`) — conversation, knowledge extraction, report generation |
| Vector search / RAG | **Pinecone** (`multilingual-e5-large` embeddings), grounded in the RetChemQA dataset |
| State management | TanStack React Query |
| Validation | Zod |
| i18n | Custom EN/AR translation system with RTL support |
| Deployment | **Railway**, auto-deploys on push to `main` |
| Dev assistant | Claude Code (CLI, VS Code extension) |

> Fireworks AI / OpenAI-compatible integration and Replit's provisioned
> Postgres were used early in development and have been **fully replaced**.
> No code should reference either going forward.

---

## Architecture Overview

The platform is conceptually a 6-layer pipeline:

```
1. Input        → Conversation (live), file upload (UI-only, not wired), spectrometer (roadmap)
2. Retrieval    → RAG via Pinecone, grounded in RetChemQA (~84,000 records)
3. Generation   → Claude API (single model handles chat, extraction, and report generation today)
4. Fine-tuning  → Not started — data collection phase
5. Validation   → Citations + source tracking live; schema/scientific validation not yet built
6. Output       → Knowledge Model (JSON) + Engineering Report (3D viz, heatmap, citations, PDF export)
```

Current scope is specialized in **reticular chemistry** (MOFs, COFs) via the
RetChemQA dataset. Expansion to other material classes (alloys, polymers,
ceramics) is planned — see architecture roadmap docs/slides if available,
or ask in-repo for the latest plan.

---

## Project Structure

```
client/               React frontend
  src/pages/           Routed pages (landing, auth, chat, report, etc.)
  src/components/      Shared UI components
  src/components/ui/   Shadcn primitives (many unused — scaffold boilerplate)
  src/contexts/        Auth + language context
  src/i18n/            EN/AR translation strings
  src/lib/             Query client, utils

server/                Express backend
  index.ts              App entry: session/logging middleware, dev/prod bootstrap
  routes.ts              All /api/* route definitions
  storage.ts             Drizzle data-access layer (IStorage interface)
  db.ts                  Postgres/Drizzle client
  llm-service.ts          Claude API calls: chat, knowledge extraction, report generation
  rag-service.ts          Pinecone retrieval + prompt augmentation
  vite.ts                 Dev Vite middleware / prod static serving
  scripts/load-knowledge.ts   Manual CLI script to load RetChemQA into Pinecone
  data/RetChemQA/          RAG source dataset (do not delete — dormant, not dead)

shared/
  schema.ts              Single source of truth for DB tables (Drizzle) + Zod schemas

migrations/             Versioned SQL migrations (see Database section below)
```

---

## Database Schema (6 tables)

`users`, `projects`, `chats`, `messages`, `knowledgeModels`, `reports`

No `attachments` or `bookmarks` tables exist — both were partially built on
the frontend at various points and have since been removed or disabled (see
Known Incomplete Features below).

### ⚠️ Migration rule — read before touching schema.ts

This project now uses **versioned migrations**. As of the schema's baseline:

```bash
# Correct workflow for ANY schema change:
npx drizzle-kit generate   # creates a new migrations/NNNN_*.sql file
npx drizzle-kit migrate    # applies it

# NEVER use:
npx drizzle-kit push       # bypasses migration history — will cause drift
```

`db:push` was used exclusively earlier in development. If you use it again,
the `migrations/` folder and the live database schema will silently diverge.

---

## Setup

```bash
git clone https://github.com/M-Fabricators-ai/fabricators-ai.git
cd fabricators-ai
npm install
```

Create a `.env` file in the project root:

```
SESSION_SECRET=
ANTHROPIC_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX=
DATABASE_URL=
PORT=3000
```

`.env` is gitignored — never commit it. Get real values from whoever
manages the Neon/Pinecone/Anthropic accounts, or from Railway's Variables
tab (values there are the production set).

```bash
npm run dev
```

Runs on `http://localhost:$PORT` (default 3000 locally; Railway assigns its
own `PORT` in production — both are handled by `process.env.PORT || '5000'`
in `server/index.ts`).

### macOS-specific note
`server.listen()` previously used `reusePort: true`, which is Linux-only
(Replit's container OS) and throws `ENOTSUP` on macOS. This has been fixed —
if you see this error again, check that fix hasn't regressed.

---

## Deployment

- **Host:** Railway, connected directly to this GitHub repo
- **Trigger:** any push to `main` auto-deploys
- **Environment variables:** set manually in Railway's Variables tab (not
  synced from `.env` — must be kept in sync by hand if secrets rotate)
- **Build command:** `npm install && npm run build`
- **Start command:** `npm start`

Replit is no longer used for hosting or development. If you find `.replit`,
`replit.md`, or Replit-specific env vars (`REPL_ID`, `REPLIT_DOMAINS`)
referenced anywhere, they are dead — safe to ignore or remove.

---

## Known Incomplete / Disabled Features

Documented explicitly so nobody rebuilds around a false assumption:

| Feature | Status | Notes |
|---|---|---|
| File attachments in chat | **Disabled (UI-only stub)** | Button is disabled with "Coming soon". Previously, selected files were silently discarded and never reached Claude — a real trust risk, now mitigated. No upload endpoint exists. |
| Data Sources page | **UI preview only** | Sidebar shows "Coming Soon" badge, page shows a preview banner. Entries (PubChem, PDB, ChEMBL) are hardcoded, not live. Strong candidate to become the real Materials Project / PubChem integration point (see Phase 2 roadmap). |
| Per-user API key management | **Removed from UI** | `users.apiKey` column still exists in the DB schema (kept for potential future use — programmatic API access for enterprise tiers) but is never read or written. No dialog/UI exists. |
| Bookmarks | **Fully removed** | Was half-built (frontend called a `/api/bookmarks` endpoint that never existed server-side). Deleted entirely, can be rebuilt properly later if needed. |
| `report.tsx` section types | **Type-safety hole, not a runtime bug** | `ReportContent.sections` is typed as optional but indexed as if guaranteed. Code defensively handles this at runtime (`?? []` fallbacks throughout), so nothing crashes today — but TypeScript has stopped checking ~26 call sites in this file. Worth tightening when doing report enhancement work. |
| 25 unused Shadcn UI primitives | **Dead code, zero risk** | Standard unused scaffold components in `components/ui/`. Safe to delete anytime, low priority. |

---

## AI / Generation Layer — Current vs. Planned

| Tier | Model / Deployment |
|---|---|
| Fab+, Fab Pro (current) | Anthropic Claude API — all LLM tasks (chat, extraction, report generation) |
| Fab Advanced (planned) | Option of open-source hosted model (e.g. Llama 3.1 405B) or private VPC deployment |
| Customized (planned) | Fine-tuned proprietary model, deployed on-prem for strategic/enterprise clients |

Fine-tuning has not started — currently in data collection phase (real
conversations + RetChemQA are the base dataset for when this begins).

---

## Contributing / Working in this Repo

- This project is actively developed with **Claude Code** as the primary
  dev assistant — it has full read/write/execute access to this repo.
- Prefer small, single-purpose commits with clear messages (see recent git
  history for the expected style).
- Run `npm run check` before considering a change complete — the current
  baseline is 26 pre-existing errors, all in `report.tsx`, all understood
  and non-critical (see table above). Any *new* errors introduced by a
  change should be treated as a real problem, not ignored as "probably like
  the others."
