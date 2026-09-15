# LinkedIn post

Attach `architecture-flow.gif`. Replace the bracketed names before posting.

---

Spent the weekend at the **Claude Hackathon at Volta**.

Our team took on a real problem from Halifax Urban Forestry: ~290 tree reports
sitting open, one crew, a handful of site visits a week — worked roughly in the
order they arrive. So a tree that fell on a house last night queues behind a
nine-month-old request to trim a hedge.

We didn't stop at a prototype. What we walked out with is an app they could put
in front of a crew the next morning.

Two things it does:

→ **Ranking.** It reads the description and the photo together, scores the
hazard, and orders the backlog by what actually needs inspecting first — not by
when it arrived.

→ **Clustering.** Once a crew is on a street, it works out which other open
requests are close enough to clear on the same trip. That's how you burn down a
290-request backlog with one crew: not by working faster, but by making every
trip count for more.

Huge thanks to **Volta** and the **Claude team** for the experience — a great
room, real problems from real organisations, and the kind of weekend that
sharpens how you think about a product.

Built with [@teammate] [@teammate] [@teammate].

Next.js · Supabase · Claude

---

## Notes

- Lead with the GIF; LinkedIn autoplays it in-feed and it carries the story
  without anyone needing to click through.
- Tag Volta and Anthropic properly so the thanks actually reaches them.
- Put the repo link in the FIRST COMMENT, not the post body — LinkedIn suppresses
  reach on posts carrying outbound links.
- "Ready the next morning" is a real claim, so be ready to back it: the app runs
  on Supabase with auth, intake, scoring, clustering and the printable field
  sheet all working. Enable RLS before anyone outside the team touches it.
