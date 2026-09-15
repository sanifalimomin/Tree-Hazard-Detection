"""
Build the 3-minute hackathon deck for Which Tree Falls First.
Run: py presentation/build_deck.py
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parent / "Which-Tree-Falls-First-Hackathon.pptx"

# Municipal / product palette (matches admin UI)
SLATE_900 = RGBColor(0x0F, 0x17, 0x2A)
SLATE_600 = RGBColor(0x47, 0x55, 0x69)
SLATE_200 = RGBColor(0xE2, 0xE8, 0xF0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RED = RGBColor(0xDC, 0x26, 0x26)
AMBER = RGBColor(0xF5, 0x9E, 0x0B)


def set_notes(slide, text: str) -> None:
    notes = slide.notes_slide.notes_text_frame
    notes.text = text


def add_title_slide(prs: Presentation, title: str, subtitle: str, notes: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    bar = slide.shapes.add_shape(
        1, Inches(0), Inches(0), prs.slide_width, Inches(1.35)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = SLATE_900
    bar.line.fill.background()

    box = slide.shapes.add_textbox(Inches(0.6), Inches(1.7), Inches(8.8), Inches(2.2))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = SLATE_900

    p2 = tf.add_paragraph()
    p2.text = subtitle
    p2.font.size = Pt(20)
    p2.font.color.rgb = SLATE_600
    p2.space_before = Pt(12)

    footer = slide.shapes.add_textbox(Inches(0.6), Inches(6.8), Inches(8), Inches(0.4))
    fp = footer.text_frame.paragraphs[0]
    fp.text = "Halifax Regional Municipality · Urban Forestry · Hackathon 2026"
    fp.font.size = Pt(11)
    fp.font.color.rgb = SLATE_600

    set_notes(slide, notes)


def add_content_slide(
    prs: Presentation,
    heading: str,
    bullets: list[str],
    notes: str,
    accent: RGBColor | None = None,
) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    accent = accent or RED

    stripe = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.12), prs.slide_height)
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = accent
    stripe.line.fill.background()

    title = slide.shapes.add_textbox(Inches(0.55), Inches(0.35), Inches(9), Inches(0.8))
    tp = title.text_frame.paragraphs[0]
    tp.text = heading
    tp.font.size = Pt(28)
    tp.font.bold = True
    tp.font.color.rgb = SLATE_900

    body = slide.shapes.add_textbox(Inches(0.55), Inches(1.25), Inches(9), Inches(5.5))
    tf = body.text_frame
    tf.word_wrap = True
    for i, line in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.level = 0
        p.font.size = Pt(20 if line.startswith("•") else 18)
        p.font.color.rgb = SLATE_900 if line.startswith("•") else SLATE_600
        p.space_after = Pt(10)
        if not line.startswith("•") and line:
            p.font.italic = True

    set_notes(slide, notes)


def add_two_column_slide(
    prs: Presentation,
    heading: str,
    left_title: str,
    left_items: list[str],
    right_title: str,
    right_items: list[str],
    notes: str,
) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title = slide.shapes.add_textbox(Inches(0.55), Inches(0.35), Inches(9), Inches(0.7))
    title.text_frame.paragraphs[0].text = heading
    title.text_frame.paragraphs[0].font.size = Pt(28)
    title.text_frame.paragraphs[0].font.bold = True

    def column(x, col_title, items):
        box = slide.shapes.add_textbox(x, Inches(1.15), Inches(4.2), Inches(5.5))
        tf = box.text_frame
        tf.word_wrap = True
        h = tf.paragraphs[0]
        h.text = col_title
        h.font.size = Pt(16)
        h.font.bold = True
        h.font.color.rgb = SLATE_600
        for item in items:
            p = tf.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(17)
            p.space_after = Pt(6)

    column(Inches(0.55), left_title, left_items)
    column(Inches(5.1), right_title, right_items)
    set_notes(slide, notes)


def main() -> None:
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    add_title_slide(
        prs,
        "Which Tree Falls First?",
        "Inspection triage for HRM Urban Forestry",
        "OPEN (15 sec): Good afternoon. We are [team names]. Imagine you are Urban Forestry "
        "on Monday morning: 290 tree reports open, one crew can visit a handful this week. "
        "Every resident believes their tree is urgent. Your job is not to declare trees safe "
        "or dangerous from a desk—you need to decide what order to drive to them in. "
        "That is the product we built.",
    )

    add_content_slide(
        prs,
        "The problem is a queue, not a verdict",
        [
            "• ~290 open requests; crews reach only a handful per week",
            "• Residents submit text + photo through a public form—no account",
            "• Waiting time alone would starve a brand-new imminent hazard",
            "• Same tree gets reported multiple times; duplicate trips waste shifts",
            "",
            "Product rule: the tool ranks inspection ORDER. It never certifies danger.",
        ],
        "PROBLEM (25 sec): Backlog age is real—some requests have waited months. But if we "
        "sorted purely by oldest-first, a tree actively leaning on power lines reported "
        "today would sit behind cosmetic pruning from last year. And if we sorted purely "
        "by severity, we would send a crew across town while three Medium jobs sit 200 "
        "meters apart on the same street. We needed both urgency and geography.",
        RED,
    )

    add_content_slide(
        prs,
        "Meet Jean-Luc’s report (our demo anchor)",
        [
            "• 6410 Quinpool Road — dead tree, sparking near lines, 96 days waiting",
            "• Text + photo in → hazard tags, danger score, priority band",
            "• Escalation floor: imminent hazard cannot sit at “Medium” because it is new",
            "• Staff see queue rank #1, map pin, and a printable field poster",
            "",
            "Live path: / → submit · /admin → triage · detail → same-day bundle map",
        ],
        "STORY (30 sec): Walk the judges through Jean-Luc on Quinpool—Critical, queue #1. "
        "Say explicitly: the system read the complaint, tagged hazards like powerline and "
        "leaning, fused photo when available, and applied the escalation floor so danger "
        "in the 90s cannot lose to wait time. The resident confirmation page shows a "
        "reference number only—no score—because a Low label is not a safety clearance.",
        AMBER,
    )

    add_two_column_slide(
        prs,
        "Transparent scoring (staff can argue with it)",
        "Four components",
        [
            "Danger 50% — rules + optional vision/LLM",
            "Wait 25% — backlog age",
            "Location 15% — arterial / foot traffic",
            "Review 10% — “Unsure” ≠ safe or unsafe",
        ],
        "Same-day bundling",
        [
            "Rank by severity earned per hour of shift",
            "Discount by proximity (400 m half-life)",
            "Map: priority pins + OSM streets",
            "Plan: anchor job + numbered add-ons",
        ],
        "HOW (35 sec): Show the formula on the detail page if you can. Emphasize escalation: "
        "weighted score might be 72 but floor bumps Critical to 80 when danger ≥ 70. "
        "Then scroll to Same-Day Work Plan—this is not ‘five nearest’; it is best value "
        "for the remaining hours on the truck. Quinpool cluster demo is seeded on purpose.",
    )

    add_content_slide(
        prs,
        "What we shipped in the hackathon",
        [
            "• Public intake at / with geocoding (Google + offline gazetteer fallback)",
            "• Staff queue: filters, live map, ranked table, gated /admin login",
            "• Request detail: Google static maps, bundle overlay, status workflow",
            "• Supabase Postgres + optional GLM/vision pipeline (degrades without keys)",
            "• Duplicate detection, feedback capture, one-page print poster for crews",
        ],
        "TECH (25 sec): Next.js, strict backend/frontend split, scores recomputed on "
        "every read so wait time stays honest. Maps: Google server-side for detail; "
        "OpenStreetMap tiles on the dashboard—no key required for the queue map. "
        "Missing API keys never block a resident submission.",
    )

    add_content_slide(
        prs,
        "3-minute demo script",
        [
            "1. Resident form → submit Quinpool-style hazard (30 sec)",
            "2. Admin login → queue map + #1 row (30 sec)",
            "3. Open detail → poster, map, bundle plan (60 sec)",
            "4. One sentence: order of inspection, not safety verdict (15 sec)",
        ],
        "DEMO (45 sec): If live DB fails, use seeded 6410 Quinpool. Click map pin. "
        "Point at numbered bundle on map. Print preview poster. Close with: arborist "
        "on site still makes the call—we only stop the wrong tree waiting 96 days "
        "while a worse one sits three blocks away.",
        RED,
    )

    add_title_slide(
        prs,
        "Thank you",
        "Which tree falls first? → Now we know where to drive first.",
        "CLOSE (15 sec): We give Urban Forestry a defensible queue, a map that matches "
        "the plan, and a field sheet crews can print. Next: resident email on close, "
        "duplicate confirm UI, rate limits. Questions?",
    )

    prs.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
