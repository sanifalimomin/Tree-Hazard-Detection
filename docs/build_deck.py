"""
Builds the demo deck: docs/which-tree-falls-first.pptx

Run with the Windows Python (the one that has python-pptx installed):
  C:/Users/Sanif/AppData/Local/Programs/Python/Python314/python.exe docs/build_deck.py

Design follows the app: white ground, slate text, restrained colour, one red
accent reserved for genuine hazard. No gradients, no clip art - it should look
like the tool it is presenting.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# --- palette ---------------------------------------------------------------
INK = RGBColor(0x0F, 0x17, 0x2A)      # slate-900
BODY = RGBColor(0x33, 0x41, 0x55)     # slate-700
MUTED = RGBColor(0x64, 0x74, 0x8B)    # slate-500
HAIR = RGBColor(0xE2, 0xE8, 0xF0)     # slate-200
PANEL = RGBColor(0xF8, 0xFA, 0xFC)    # slate-50
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

RED = RGBColor(0xDC, 0x26, 0x26)
ORANGE = RGBColor(0xF9, 0x73, 0x16)
AMBER = RGBColor(0xFB, 0xBF, 0x24)
GREY = RGBColor(0x94, 0xA3, 0xB8)
GREEN = RGBColor(0x05, 0x96, 0x69)

SANS = "Segoe UI"
MONO = "Consolas"

W, H = Inches(13.333), Inches(7.5)
M = Inches(0.72)          # side margin
CONTENT_W = W - 2 * M

prs = Presentation()
prs.slide_width = W
prs.slide_height = H
BLANK = prs.slide_layouts[6]


# --- primitives ------------------------------------------------------------
def slide():
    s = prs.slides.add_slide(BLANK)
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = WHITE
    return s


def box(s, x, y, w, h, text, size=18, color=BODY, bold=False, font=SANS,
        align=PP_ALIGN.LEFT, spacing=1.25, anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = font
    return tb


def rect(s, x, y, w, h, fill=None, line=None, line_w=1.0):
    from pptx.enum.shapes import MSO_SHAPE
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    sh.shadow.inherit = False
    return sh


def eyebrow(s, text):
    box(s, M, Inches(0.52), CONTENT_W, Inches(0.3), text.upper(),
        size=11, color=MUTED, bold=True)


def title(s, text, sub=None):
    box(s, M, Inches(0.88), CONTENT_W, Inches(0.75), text,
        size=34, color=INK, bold=True, spacing=1.0)
    rect(s, M, Inches(1.72), Inches(1.1), Emu(28000), fill=INK)
    if sub:
        box(s, M, Inches(1.95), CONTENT_W, Inches(0.5), sub,
            size=16, color=MUTED, spacing=1.2)


def footer(s, n):
    box(s, M, H - Inches(0.52), Inches(6), Inches(0.3),
        "Which Tree Falls First  ·  Halifax Urban Forestry",
        size=9, color=MUTED)
    box(s, W - M - Inches(1), H - Inches(0.52), Inches(1), Inches(0.3),
        str(n), size=9, color=MUTED, align=PP_ALIGN.RIGHT, font=MONO)


def stat(s, x, y, w, value, label, hint="", color=INK):
    rect(s, x, y, w, Inches(1.62), fill=PANEL, line=HAIR)
    box(s, x + Inches(0.24), y + Inches(0.2), w - Inches(0.48), Inches(0.28),
        label.upper(), size=10, color=MUTED, bold=True)
    box(s, x + Inches(0.24), y + Inches(0.52), w - Inches(0.48), Inches(0.62),
        value, size=38, color=color, bold=True, font=MONO, spacing=1.0)
    if hint:
        box(s, x + Inches(0.24), y + Inches(1.16), w - Inches(0.48), Inches(0.34),
            hint, size=10, color=MUTED, spacing=1.15)


def bullets(s, x, y, w, items, size=16, gap=0.52):
    for i, (head, rest) in enumerate(items):
        yy = y + Inches(gap * i)
        rect(s, x, yy + Inches(0.08), Emu(30000), Inches(0.2), fill=INK)
        tb = s.shapes.add_textbox(x + Inches(0.2), yy, w - Inches(0.2), Inches(0.46))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.line_spacing = 1.2
        r1 = p.add_run(); r1.text = head
        r1.font.size = Pt(size); r1.font.bold = True; r1.font.color.rgb = INK
        r1.font.name = SANS
        if rest:
            r2 = p.add_run(); r2.text = "  " + rest
            r2.font.size = Pt(size); r2.font.color.rgb = BODY; r2.font.name = SANS


n = 0


# =========================================================================
# 1. Title
# =========================================================================
n += 1
s = slide()
rect(s, Inches(0), Inches(0), W, Inches(0.14), fill=RED)
box(s, M, Inches(2.0), CONTENT_W, Inches(0.34),
    "HALIFAX REGIONAL MUNICIPALITY  ·  URBAN FORESTRY",
    size=13, color=MUTED, bold=True)
box(s, M, Inches(2.5), CONTENT_W, Inches(1.3), "Which Tree Falls First",
    size=60, color=INK, bold=True, spacing=1.0)
box(s, M, Inches(3.85), Inches(9.4), Inches(0.9),
    "Reading 290 backlogged tree reports and deciding what a crew "
    "should inspect today.",
    size=20, color=BODY, spacing=1.3)
rect(s, M, Inches(5.0), Inches(1.1), Emu(28000), fill=INK)
box(s, M, Inches(5.3), Inches(11), Inches(0.5),
    "A prioritisation tool — not a safety determination.",
    size=13, color=MUTED)
footer(s, n)

# =========================================================================
# 2. Problem
# =========================================================================
n += 1
s = slide()
eyebrow(s, "The problem")
title(s, "290 open requests. Every one needs a site visit.")
gap = Inches(0.28)
cw = (CONTENT_W - 2 * gap) / 3
stat(s, M, Inches(2.6), cw, "290", "Open requests", "Sitting in the 311 backlog")
stat(s, M + cw + gap, Inches(2.6), cw, "~6", "Inspected per week",
     "One crew, whole municipality", color=BODY)
stat(s, M + 2 * (cw + gap), Inches(2.6), cw, "290d", "Longest wait",
     "And it is still not the worst tree", color=RED)
box(s, M, Inches(4.7), CONTENT_W, Inches(1.4),
    "Requests are worked roughly in the order they arrive. That means a tree "
    "that fell on a house last night\nqueues behind a nine-month-old request "
    "to prune a hedge — and nobody can see that has happened.",
    size=17, color=BODY, spacing=1.4)
footer(s, n)

# =========================================================================
# 3. What we built
# =========================================================================
n += 1
s = slide()
eyebrow(s, "What we built")
title(s, "Two surfaces, one ranked queue.")
half = (CONTENT_W - Inches(0.4)) / 2

rect(s, M, Inches(2.5), half, Inches(3.0), fill=PANEL, line=HAIR)
box(s, M + Inches(0.3), Inches(2.75), half - Inches(0.6), Inches(0.3),
    "RESIDENT  /report", size=11, color=MUTED, bold=True, font=MONO)
box(s, M + Inches(0.3), Inches(3.12), half - Inches(0.6), Inches(2.2),
    "Name, email, location, description\nand a photo.\n\n"
    "Scored the moment it is submitted.\n\n"
    "Gets a reference number — and no\nrisk score, because the ranking is\n"
    "an internal dispatch decision.",
    size=15, color=BODY, spacing=1.35)

rect(s, M + half + Inches(0.4), Inches(2.5), half, Inches(3.0), fill=PANEL, line=HAIR)
box(s, M + half + Inches(0.7), Inches(2.75), half - Inches(0.6), Inches(0.3),
    "URBAN FORESTRY  /admin", size=11, color=MUTED, bold=True, font=MONO)
box(s, M + half + Inches(0.7), Inches(3.12), half - Inches(0.6), Inches(2.2),
    "Queue ranked by hazard, not by date.\n\n"
    "Full reasoning for every score.\n\n"
    "Same-day work plan, completion\nsign-off, and a printable one-page\n"
    "field assessment sheet.",
    size=15, color=BODY, spacing=1.35)
footer(s, n)

# =========================================================================
# 4. Scoring
# =========================================================================
n += 1
s = slide()
eyebrow(s, "How it ranks")
title(s, "Four factors, every one explainable.",
      "No black box: each score shows the phrase that produced it.")

rect(s, M, Inches(2.75), CONTENT_W, Inches(0.66), fill=INK)
box(s, M, Inches(2.92), CONTENT_W, Inches(0.4),
    "finalScore  =  danger x 0.50   +   wait x 0.25   +   location x 0.15   +   review x 0.10",
    size=17, color=WHITE, bold=True, font=MONO, align=PP_ALIGN.CENTER)

items = [
    ("Danger 50%", "keyword + phrase rules over the text, fused with the photo"),
    ("Wait time 25%", "backlog pressure, saturating at 180 days"),
    ("Location 15%", "a hazard on Barrington exposes more people than one on a cul-de-sac"),
    ("Human review 10%", "the description was too vague to score at all"),
]
bullets(s, M, Inches(3.85), CONTENT_W, items, size=16, gap=0.5)

bw = (CONTENT_W - Inches(0.36)) / 4
for i, (lab, col) in enumerate(
        [("CRITICAL 80+", RED), ("HIGH 60-79", ORANGE),
         ("MEDIUM 35-59", AMBER), ("LOW 0-34", GREY)]):
    x = M + i * (bw + Inches(0.12))
    rect(s, x, Inches(6.05), bw, Inches(0.46), fill=col)
    box(s, x, Inches(6.17), bw, Inches(0.3), lab, size=12,
        color=WHITE if col != AMBER else INK, bold=True, align=PP_ALIGN.CENTER)
footer(s, n)

# =========================================================================
# 5. Escalation floor  (the insight)
# =========================================================================
n += 1
s = slide()
eyebrow(s, "The insight")
title(s, "Weighted averages bury emergencies.")

box(s, M, Inches(2.35), CONTENT_W, Inches(0.5),
    "A tree actively falling onto a house, reported today on a residential street:",
    size=16, color=BODY)

rect(s, M, Inches(2.9), CONTENT_W, Inches(0.62), fill=PANEL, line=HAIR)
box(s, M, Inches(3.06), CONTENT_W, Inches(0.4),
    "danger 100 x 0.50   +   wait 0 x 0.25   +   location 40 x 0.15   =   56   ->   MEDIUM",
    size=16, color=INK, bold=True, font=MONO, align=PP_ALIGN.CENTER)

box(s, M, Inches(3.78), CONTENT_W, Inches(0.5),
    "Backlog age would outrank an active hazard. That is the wrong answer to "
    "the only question this tool exists to answer.",
    size=16, color=BODY, spacing=1.3)

rect(s, M, Inches(4.5), CONTENT_W, Inches(1.55), fill=WHITE, line=RED, line_w=1.5)
rect(s, M, Inches(4.5), Emu(48000), Inches(1.55), fill=RED)
box(s, M + Inches(0.34), Inches(4.72), CONTENT_W - Inches(0.7), Inches(0.32),
    "IMMINENT-HAZARD ESCALATION FLOOR", size=12, color=RED, bold=True)
box(s, M + Inches(0.34), Inches(5.08), CONTENT_W - Inches(0.7), Inches(0.9),
    "Severity sets a floor, the way severity rows work in a municipal risk matrix.\n"
    "danger >= 70 floors at 80 (Critical).   danger >= 50 floors at 60 (High).\n"
    "It never lowers a score, never alters the four components — and the UI says when it binds.",
    size=14, color=BODY, spacing=1.3)

box(s, M, Inches(6.25), CONTENT_W, Inches(0.4),
    "Agricola Street:  weighted 46  ->  floored to 80  ->  CRITICAL, ranked #2 of 24.",
    size=14, color=INK, bold=True, font=MONO)
footer(s, n)

# =========================================================================
# 6. Photo + text fusion
# =========================================================================
n += 1
s = slide()
eyebrow(s, "Reading the photo")
title(s, "The picture and the words disagree more than you would think.",
      "Both produce a 0-100 severity on the same hazard vocabulary, so fusing them is arithmetic.")

rows = [
    ("Photo and text agree", "higher of the two", "", BODY),
    ("Photo shows MORE than described", "use the photo", "", ORANGE),
    ("Text claims MORE than the photo supports", "keep higher score", "FLAGGED", RED),
    ("Photo resolves a vague description", "use the photo", "CLEARED", GREEN),
    ("Photo unusable - not a tree, too dark", "use the text", "FLAGGED", MUTED),
]
y0 = Inches(2.9)
cw1, cw2, cw3 = Inches(6.2), Inches(3.3), Inches(2.3)
box(s, M, y0 - Inches(0.34), cw1, Inches(0.3), "SITUATION", size=10, color=MUTED, bold=True)
box(s, M + cw1, y0 - Inches(0.34), cw2, Inches(0.3), "SCORE USED", size=10, color=MUTED, bold=True)
box(s, M + cw1 + cw2, y0 - Inches(0.34), cw3, Inches(0.3), "REVIEW FLAG", size=10, color=MUTED, bold=True)
rect(s, M, y0 - Inches(0.06), CONTENT_W, Emu(20000), fill=INK)

for i, (a, b, c, col) in enumerate(rows):
    yy = y0 + Inches(0.12) + Inches(0.62 * i)
    box(s, M, yy, cw1 - Inches(0.2), Inches(0.4), a, size=14, color=BODY)
    box(s, M + cw1, yy, cw2 - Inches(0.2), Inches(0.4), b, size=14, color=INK, bold=True)
    if c:
        box(s, M + cw1 + cw2, yy, cw3, Inches(0.4), c, size=12, color=col, bold=True)
    rect(s, M, yy + Inches(0.46), CONTENT_W, Emu(9000), fill=HAIR)

box(s, M, Inches(6.35), CONTENT_W, Inches(0.4),
    "The fused score is never LOWER than the text score — under-ranking a hazard someone "
    "described is the expensive mistake.",
    size=13, color=MUTED, spacing=1.25)
footer(s, n)

# =========================================================================
# 7. Bundling  (the differentiator)
# =========================================================================
n += 1
s = slide()
eyebrow(s, "The differentiator")
title(s, "Once the truck is there, what else gets cleared?",
      "Mobilisation costs the same whether the crew does one job or four.")

rect(s, M, Inches(2.5), CONTENT_W, Inches(0.95), fill=PANEL, line=HAIR)
box(s, M + Inches(0.3), Inches(2.68), CONTENT_W - Inches(0.6), Inches(0.62),
    "\"The five nearest\" is the obvious answer, and it is wrong. It returns five cosmetic prunings "
    "on one block\nwhile a High-priority tree sits 400 m away.",
    size=15, color=BODY, spacing=1.3)

box(s, M, Inches(3.7), CONTENT_W, Inches(0.35),
    "Ranked by severity earned per hour of shift consumed, discounted for distance:",
    size=15, color=BODY)

hdr = ["ANCHOR", "IN RANGE", "RECOMMENDED", "THEIR QUEUE RANKS"]
data = [
    ("Quinpool Rd  (#1, Critical)", "6", "5 @ 235-805 m", "#6, #9, #13, #14, #23"),
    ("Agricola St  (#2, Critical)", "9", "5 @ 205-336 m", "#5, #11, #15, #19, #20"),
    ("Dutch Village Rd  (#3)", "1", "none fit", "isolated — cannot bundle"),
]
cws = [Inches(4.1), Inches(1.5), Inches(2.9), Inches(3.4)]
y0 = Inches(4.35)
x = M
for i, h in enumerate(hdr):
    box(s, x, y0 - Inches(0.32), cws[i], Inches(0.3), h, size=10, color=MUTED, bold=True)
    x += cws[i]
rect(s, M, y0 - Inches(0.04), CONTENT_W, Emu(20000), fill=INK)

for r, row in enumerate(data):
    yy = y0 + Inches(0.14) + Inches(0.56 * r)
    x = M
    for i, cell in enumerate(row):
        box(s, x, yy, cws[i] - Inches(0.15), Inches(0.4), cell, size=13,
            color=INK if i == 0 else BODY,
            bold=(i == 0), font=MONO if i in (1, 3) else SANS)
        x += cws[i]
    rect(s, M, yy + Inches(0.42), CONTENT_W, Emu(9000), fill=HAIR)

box(s, M, Inches(6.28), CONTENT_W, Inches(0.45),
    "Note the ranks: the suggestions are deliberately NOT the next entries in the queue. "
    "And #2 is 1.5 km from #1 — so it cannot be bundled, and the tool says so.",
    size=13, color=MUTED, spacing=1.25)
footer(s, n)

# =========================================================================
# 8. Honest edges
# =========================================================================
n += 1
s = slide()
eyebrow(s, "Where it is careful")
title(s, "The parts that stop it being dangerous.")
bullets(s, M, Inches(2.6), CONTENT_W, [
    ("\"Unsure\" is not \"dangerous\".",
     "A vague report means the system lacks information, not that the tree is safe. Priority and review flag are shown side by side, never substituted."),
    ("Duplicates are detected, not stacked.",
     "Nine neighbours reporting one fallen tree would otherwise fill the top nine slots — and make bundling recommend one job five times."),
    ("Every score is auditable.",
     "Each hazard tag carries the exact phrase that triggered it and the points it added."),
    ("It never certifies a tree as safe.",
     "The printed sheet says so explicitly. It sets inspection order; an arborist makes the call."),
], size=15, gap=0.92)
footer(s, n)

# =========================================================================
# 9. Demo flow
# =========================================================================
n += 1
s = slide()
eyebrow(s, "Live demo")
title(s, "Ninety seconds, six clicks.")
steps = [
    ("1", "Submit a report", "/report — photo, address, description"),
    ("2", "It is already ranked", "/admin — scored on submission, queue re-sorted"),
    ("3", "Open the top tree", "full reasoning, hazard tags, photo assessment"),
    ("4", "See the escalation", "weighted 46 -> floored to 80, and why"),
    ("5", "Read the day plan", "5 nearby jobs, what fits the shift, what follows"),
    ("6", "Print the field sheet", "one Letter page, only the poster"),
]
for i, (num, head, sub) in enumerate(steps):
    col, row = i % 3, i // 3
    x = M + col * (CONTENT_W / 3)
    y = Inches(2.65) + Inches(1.75) * row
    rect(s, x, y, Inches(0.44), Inches(0.44), fill=INK)
    box(s, x, y + Inches(0.07), Inches(0.44), Inches(0.3), num,
        size=14, color=WHITE, bold=True, align=PP_ALIGN.CENTER, font=MONO)
    box(s, x, y + Inches(0.6), CONTENT_W / 3 - Inches(0.5), Inches(0.35),
        head, size=17, color=INK, bold=True)
    box(s, x, y + Inches(1.0), CONTENT_W / 3 - Inches(0.5), Inches(0.5),
        sub, size=13, color=MUTED, spacing=1.2)
footer(s, n)

# =========================================================================
# 10. Stack + status
# =========================================================================
n += 1
s = slide()
eyebrow(s, "Built with")
title(s, "Next.js · TypeScript · Supabase Postgres · Claude vision")

half = (CONTENT_W - Inches(0.4)) / 2
rect(s, M, Inches(2.55), half, Inches(3.3), fill=PANEL, line=HAIR)
box(s, M + Inches(0.3), Inches(2.78), half - Inches(0.6), Inches(0.3),
    "WORKING TODAY", size=11, color=GREEN, bold=True)
box(s, M + Inches(0.3), Inches(3.16), half - Inches(0.6), Inches(2.5),
    "Public intake with photo upload\n"
    "Text + image hazard scoring\n"
    "Ranked queue, filters, sorting\n"
    "Same-day work planning + map\n"
    "Completion sign-off with audit trail\n"
    "Printable field assessment sheet\n"
    "Live on Supabase Postgres 17.6",
    size=14, color=BODY, spacing=1.55)

rect(s, M + half + Inches(0.4), Inches(2.55), half, Inches(3.3), fill=PANEL, line=HAIR)
box(s, M + half + Inches(0.7), Inches(2.78), half - Inches(0.6), Inches(0.3),
    "NEXT", size=11, color=MUTED, bold=True)
box(s, M + half + Inches(0.7), Inches(3.16), half - Inches(0.6), Inches(2.5),
    "Completion email + feedback capture\n"
    "Admin UI to confirm suggested duplicates\n"
    "Authentication on the admin console\n"
    "Photo storage moved to Supabase\n"
    "Real crew durations replacing estimates",
    size=14, color=BODY, spacing=1.55)

box(s, M, Inches(6.15), CONTENT_W, Inches(0.5),
    "The scoring engine is pure and isolated — swapping the classifier for a different model "
    "does not touch the weighting, thresholds, reasoning or UI.",
    size=13, color=MUTED, spacing=1.25)
footer(s, n)

# =========================================================================
out = "docs/which-tree-falls-first.pptx"
prs.save(out)
print(f"wrote {out}  ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
