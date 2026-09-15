# Which Tree Falls First — 3-minute hackathon story

**Total time:** ~3:00 · **Slides:** `Which-Tree-Falls-First-Hackathon.pptx` (speaker notes mirror this script)

**Cast:** One presenter narrates; a second drives the laptop (form → admin → detail). Swap roles in Q&A.

---

## The one-line pitch (memorize this)

> **We tell Halifax Urban Forestry which tree to visit first — not whether it is dangerous.**

---

## Slide 1 — Title (0:00–0:15)

**Say:**

"Good afternoon. We're **[Team]**. Urban Forestry has roughly **290 open tree requests** and enough crew time for **a handful of site visits per week**. Every resident thinks their tree is an emergency. The city cannot inspect them all tomorrow — but it *can* avoid inspecting them in the wrong order. Our app is called **Which Tree Falls First**."

**Do:** Stand still; title slide only.

---

## Slide 2 — Problem (0:15–0:40)

**Say:**

"This is a **queue problem**, not a chatbot that declares trees safe or unsafe. If you sort by **oldest first**, a **new** report — tree on power lines, reported this morning — loses to a cosmetic prune from last year. If you sort by **severity only**, you send a truck across the peninsula while **three workable jobs** sit **200 metres apart** on Quinpool. Staff need **urgency**, **geography**, and **auditability** in one place."

**Do:** Optional hand count: "How many of you have ever reprioritized a backlog manually in a spreadsheet?"

---

## Slide 3 — Story anchor: Jean-Luc / Quinpool (0:40–1:10)

**Say:**

"Meet **6410 Quinpool Road** — our seeded demo, queue **#1**. A resident describes a **dead tree**, **sparking**, roots lifting — **96 days** waiting. The engine tags hazards, scores danger in the **90s**, and applies an **escalation floor** so a live hazard cannot sit at Medium just because it is new. The **resident** gets a reference number — **no score** — because 'Low priority' must never sound like 'safe tree'."

**Do:** Switch to live app → **`/admin/login`** → queue.

---

## Slide 4 — Scoring + bundling (1:10–1:45)

**Say:**

"Staff see a **transparent breakdown**: danger, wait, location, review — weights on screen. **Unsure** means missing information, not 'low risk'. On the detail page, **Same-Day Work Plan** asks: given an **8-hour shift**, what else is worth doing near the anchor? We rank by **severity per hour**, not 'five nearest pins'. The **queue map** shows priority colours; click a pin — you're on the case."

**Do:** Open **6410 Quinpool** → scroll **scoring → map → bundle list** → mention **print poster**.

---

## Slide 5 — What we built (1:45–2:10)

**Say:**

"**Public form** at `/`, **staff console** behind login, **Supabase** backlog, **Google geocoding** and maps on the detail view, **OpenStreetMap** on the dashboard map. Photo and LLM paths are **optional** — if keys are missing, we fall back to **text-only triage** and still accept the report. Duplicates, status history, and a **one-page field poster** are in scope for real crews."

**Do:** Quick flash of **`/`** form if time allows.

---

## Slide 6 — Demo checklist (2:10–2:45)

**Say:**

"In **30 seconds**: resident submits. In **30 seconds**: admin queue and map. In **one minute**: detail, bundle, poster. We close with the rule again: **order of inspection**, arborist on site decides safety."

**Do:** Run only what you haven't shown; skip if ahead of time.

---

## Slide 7 — Thank you (2:45–3:00)

**Say:**

"**Which tree falls first?** With this tool, crews know **where to drive first**. Thank you — we're happy to take questions."

**Do:** Leave detail page or queue map on screen for judges.

---

## Backup lines (if something breaks)

| Issue | Line |
|--------|------|
| DB down | "Scores are deterministic — we can walk through the seeded Quinpool fixture from the deck." |
| Map tiles slow | "Pins are live from coordinates; tiles are OSM — the ranking table is the source of truth." |
| No vision key | "Vision is optional; danger from complaint text still drives the queue." |
| Login forgot | "Default demo login is admin / admin — gate is middleware on `/admin` only." |

---

## Judge questions (short answers)

- **Is this replacing arborists?** No — it prioritizes **site visits**; every UI says so.
- **Why not just use 311 order?** Age alone starves **new** imminent hazards; we combine danger, wait, location, review.
- **Privacy?** Admin is gated; public form needs no account; resident email stays off the confirmation page score.
- **What's next?** Email on completion, duplicate confirm UI, rate limiting on public POST.

---

## Timing cheat sheet

| Block | Target |
|--------|--------|
| Hook + problem | 0:40 |
| Quinpool story + open admin | 1:10 |
| Detail / map / bundle | 1:45 |
| Built + demo | 2:45 |
| Close | 3:00 |
