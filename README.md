# Which Tree Falls First

Inspection triage for Halifax Regional Municipality Urban Forestry.

Around 290 tree reports are open. Every one needs a site visit, and one crew
reaches a handful a week, so requests get worked roughly in the order they
arrive — which means a tree that fell on a house last night queues behind a
nine-month-old request to prune a hedge.

This reads each report, scores the hazard from the description **and the
photograph**, ranks the backlog, and then answers the follow-up question:
*given the crew is already on that street, what else should they clear today?*

> It decides **inspection order**. It never decides whether a tree is dangerous.
> Only a qualified arborist on site can make that call, and every screen and the
> printed sheet say so.

---

## Quick start

```bash
npm install
cp .env.example .env.local     # fill in the values below
npm run db:check               # verify the Supabase connection
npm run db:seed                # load the demo dataset
npm run dev                    # http://localhost:5177
```

| Route | Who | What |
|---|---|---|
| `/report` | public | Submit a tree report with a photo |
| `/report/[reference]` | public | Confirmation + reference number |
| `/admin/login` | staff | Sign in |
| `/admin` | staff | Ranked inspection queue |
| `/admin/requests/[id]` | staff | Assessment, work plan, printable sheet |

---

## Environment

Only the Supabase values are required. Everything else degrades to a local
fallback, so the app still runs — and says what it lost — with nothing else set.

```bash
# Database (required) — Supabase project, accessed over the REST API
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_KEY=<publishable or service-role key>

# Admin console (required to reach /admin)
ADMIN_USERNAME=
ADMIN_PASSWORD=
ADMIN_SESSION_SECRET=          # any long random string
ADMIN_SESSION_HOURS=12

# Photo analysis (optional) — without it, text-only triage
ANTHROPIC_API_KEY=
VISION_MODEL=claude-opus-5

# Alternative OpenAI-compatible LLM (optional)
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=

# Geocoding (optional) — falls back to a built-in Halifax street gazetteer
GOOGLE_MAPS_API_KEY=           # server-side only; never prefix NEXT_PUBLIC_
GEOCODER_URL=                  # Nominatim-compatible alternative

# Static map tiles (optional)
MAP_PROXY_SECRET=

# Uploaded photos
UPLOAD_DIR=var/uploads
```

---

## How the ranking works

```
finalScore = danger x 0.50  +  wait x 0.25  +  location x 0.15  +  review x 0.10
```

| Component | Weight | Source |
|---|---|---|
| Danger | 50% | Phrase rules over the description, fused with the photo analysis |
| Wait time | 25% | `min(daysWaiting / 180 x 100, 100)` |
| Location impact | 15% | Per-street table — an arterial exposes more people than a cul-de-sac |
| Human review | 10% | 100 when the report is too vague to score at all |

Bands: **Critical** 80–100 · **High** 60–79 · **Medium** 35–59 · **Low** 0–34.

### The imminent-hazard escalation floor

A weighted average buries emergencies. A tree actively falling onto a house,
reported *today* on a residential street, tops out at:

```
danger 100 x 0.50  +  wait 0 x 0.25  +  location 40 x 0.15  =  56  ->  "Medium"
```

Backlog age would outrank an active hazard, which is the wrong answer to the
only question this tool exists to answer. So severity sets a **floor**, the way
severity rows work in a municipal risk matrix:

- danger ≥ 70 → floored at 80 (Critical)
- danger ≥ 50 → floored at 60 (High)

The floor never lowers a score and never alters the four component scores. When
it binds, the UI and the printed sheet both say so and show the pre-escalation
weighted score.

### Fusing the photo with the description

Both produce a 0–100 severity on the same hazard vocabulary, so combining them
is arithmetic rather than translation.

| Situation | Score used | Review flag |
|---|---|---|
| No photo, or analysis unavailable | text | unchanged |
| Photo and text agree (within 20) | higher of the two | unchanged |
| Photo shows **more** than described | photo | unchanged |
| Text claims **more** than the photo supports | text (the higher) | **flagged** |
| Photo resolves a vague description | photo | **cleared** |
| Photo unusable (not a tree, too dark) | text | **flagged** |

The fused score is never *lower* than the text score — under-ranking a hazard
someone described is the expensive mistake. Both source scores are shown side by
side so a disagreement is visible rather than averaged away.

### "Unsure" is not "dangerous"

The review flag means the system lacks information, not that the tree is safe or
hazardous. Priority is computed independently, and the two are displayed side by
side — never substituted for one another.

---

## Same-day work planning

Mobilising a crew costs the same whether they do one job or four. When a request
is opened, the planner proposes what else is worth clearing on the same trip.

**"The five nearest" is the obvious answer and it is wrong** — it returns five
cosmetic prunings on one block while a High-priority tree sits 400 m away. Three
things are weighed together: severity (final score), time on site, and travel
time. Candidates are ranked by severity earned per hour of shift consumed, then
discounted by a proximity factor so a crew does not leave the area for a
marginally better job.

Because a Critical removal is genuinely 5–6 h of an 8 h shift, often only one
extra job actually *fits*. So the plan reports two groups: **scheduled today**,
and a **follow-up trip** for the rest of the shortlist.

The recommendations are deliberately *not* the next entries in the queue.

---

## Architecture

Three layers, enforced by one rule: **`frontend/` never imports from
`backend/`**. Anything both sides need lives in `shared/`.

```
src/
  backend/                  server-only
    config.ts               environment reading; every value optional
    db/client.ts            Supabase REST (PostgREST) client
    db/repository.ts        every query; snake_case in, camelCase out
    domain/scoring.ts       hazard rules, classification, fusion, escalation
    domain/bundling.ts      same-day work planner
    domain/duplicates.ts    same-tree detection
    services/               intake, vision, geocode, exif, auth, storage, maps
    seed/                   demo dataset + seeder
  shared/                   pure, safe in both bundles
    types.ts                domain types and server -> client prop shapes
    scoring-config.ts       weights and priority bands — the displayed contract
    geo.ts                  distance maths
  frontend/
    components/
    styles/
  app/                      Next.js routing only; pages compose, not compute
```

`WEIGHTS` and the plan types live in `shared` because the UI prints them — one
definition means the number the engine multiplies by is provably the number the
arborist reads on the sheet.

### Classification is stored; scoring is not

```
classifyComplaint(text) -> Classification   expensive, runs once, PERSISTED
scoreRequest(cls, ctx)  -> Assessment       cheap, recomputed EVERY READ
```

Wait time changes daily, so a final score written to the database would be wrong
by the next morning. Only findings derived from the report itself are stored;
the weighting, escalation and priority are always live. Queue ordering happens
in JS for the same reason.

### Swapping the classifier

All text understanding sits behind `classifyComplaint()`, and all image
understanding behind `analyzeImage()`. Replace either with a different model
returning the same shape and the weighting, thresholds, reasoning, UI and
printed sheet keep working untouched.

---

## Other behaviour worth knowing

**Duplicate detection.** When a large tree comes down, a dozen neighbours report
it — which would otherwise fill the top of the queue with one tree and make the
planner recommend the same job five times. Three gated signals (proximity,
recency, description overlap) are required, because a street-centroid geocode
puts every address on a street at the same point and proximity alone would merge
the whole block.

**Location resolution**, in order: EXIF GPS from the photo (the phone was at the
tree) → Google Geocoding → a built-in Halifax street gazetteer → nothing, in
which case the request is stored anyway, flagged for a manual pin, and excluded
from distance maths.

**Printing.** The detail page carries a one-page US Letter field assessment
sheet. Everything else sits inside `.no-print`, so only the sheet reaches the
printer.

---

## Scripts

| Command | Does |
|---|---|
| `npm run dev` | Development server on :5177 |
| `npm run build` | Production build |
| `npm run db:check` | Verify the Supabase connection and tables |
| `npm run db:seed` | Load the demo dataset |
| `npm run db:reset` | Wipe and re-seed |
| `npm run typecheck` | `tsc --noEmit` |
| `npm test` | Scoring engine tests |

---

## Demo data

The seeded dataset is engineered, not random, and `db:seed` prints a
verification report. It deliberately contains five geographic clusters plus one
isolated outlier; the **#1 ranked request inside a tight cluster** with several
same-day candidates that are *not* the next entries in the queue; the **#2
ranked request 1.5 km away** so it visibly cannot be bundled; a linked duplicate
pair and an unlinked one; and completed records, one with resident feedback.

All seeded emails are `@example.com`.

---

## Stack

Next.js 14 (App Router) · TypeScript · Tailwind CSS · Supabase (PostgreSQL via
PostgREST) · Claude vision · Lucide icons
