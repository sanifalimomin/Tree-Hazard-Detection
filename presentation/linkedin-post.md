# LinkedIn post

Attach `architecture-flow.gif`.

---

Weekend hackathon at Volta, building for Halifax Urban Forestry.

The problem: ~290 tree reports sitting open, one crew, a handful of site visits a
week. They get worked roughly in the order they arrive — so a tree that fell on a
house last night queues behind a nine-month-old request to trim a hedge.

We built a triage tool that reads the description *and* the photo, scores the
hazard, and ranks the backlog.

Two things surprised me:

→ A weighted average buries emergencies. A tree actively falling onto a house,
reported today, scored 56 — "Medium". Severity now sets a floor on the score, the
way a real risk matrix does.

→ "The five nearest jobs" is the wrong answer to "what else can the crew clear
while they're on that street." It hands back five cosmetic prunings while a
serious tree sits 400 m away. Ranking by severity per hour of shift actually
works.

Next.js · Supabase · Claude

It decides inspection *order*. It never decides whether a tree is dangerous —
that call stays with the arborist on site.

---

## Notes

- Lead with the GIF; LinkedIn autoplays it in-feed and it carries the whole story
  without anyone clicking through.
- The two "surprised me" lines are the post. They are specific and falsifiable,
  which is what makes a build post worth reading rather than another
  "excited to share".
- Tag teammates and Volta. If the repo is public by then, put the link in the
  first comment rather than the post body — LinkedIn suppresses reach on posts
  with outbound links.
