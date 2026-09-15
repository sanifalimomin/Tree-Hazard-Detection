"""
Builds presentation/architecture-flow.gif — an animated walkthrough of how a
resident report becomes a dispatch decision.

Run with the Windows Python (the one that has Pillow):
  C:/Users/Sanif/AppData/Local/Programs/Python/Python314/python.exe presentation/build_flow_gif.py

Design matches the app: white ground, slate text, one red accent reserved for
genuine hazard. Flat colours keep the GIF small.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1000, 600
FPS_MS = 70

INK = (15, 23, 42)
BODY = (51, 65, 85)
MUTED = (100, 116, 139)
HAIR = (226, 232, 240)
PANEL = (248, 250, 252)
WHITE = (255, 255, 255)
RED = (220, 38, 38)
AMBER = (251, 191, 36)
GREEN = (5, 150, 105)

FONTS = "C:/Windows/Fonts/"


def font(name, size):
    try:
        return ImageFont.truetype(FONTS + name, size)
    except OSError:
        return ImageFont.load_default()


F_TITLE = font("segoeuib.ttf", 30)
F_SUB = font("segoeui.ttf", 16)
F_STAGE = font("segoeuib.ttf", 15)
F_BODY = font("segoeui.ttf", 15)
F_SMALL = font("segoeui.ttf", 13)
F_MONO = font("consola.ttf", 15)
F_MONO_S = font("consola.ttf", 13)
F_CAPS = font("segoeuib.ttf", 11)

# --- the pipeline ----------------------------------------------------------
STAGES = [
    {
        "key": "REPORT",
        "title": "Resident reports",
        "detail": [
            "Photo, address and a description —",
            "typed by someone who is not an arborist.",
        ],
        "mono": '"Massive oak leaning 45° toward the house"',
        "accent": MUTED,
    },
    {
        "key": "LOCATE",
        "title": "Pin it, and de-duplicate",
        "detail": [
            "GPS from the photo beats a typed address.",
            "Nine neighbours reporting one tree is one job.",
        ],
        "mono": "EXIF GPS  ->  Google  ->  gazetteer",
        "accent": MUTED,
    },
    {
        "key": "READ",
        "title": "Read the words AND the picture",
        "detail": [
            "Both score 0–100 on the same hazard vocabulary,",
            "so fusing them is arithmetic, not translation.",
        ],
        "mono": "text 80   photo 90   ->   fused 90",
        "accent": AMBER,
    },
    {
        "key": "RANK",
        "title": "Rank the backlog",
        "detail": [
            "danger x.50 + wait x.25 + location x.15 + review x.10",
            "A falling tree reported today scores 56 — 'Medium'.",
        ],
        "mono": "weighted 46   ->   FLOORED to 80",
        "accent": RED,
    },
    {
        "key": "DISPATCH",
        "title": "Plan the day",
        "detail": [
            "The crew is already on that street.",
            "What else is worth clearing before they leave?",
        ],
        "mono": "5 jobs within 500 m  —  not the next 5 in the queue",
        "accent": GREEN,
    },
]

BOX_Y = 168
BOX_H = 62
GAP = 14
MARGIN = 54
BOX_W = (W - 2 * MARGIN - GAP * (len(STAGES) - 1)) // len(STAGES)


def rounded(d, xy, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def draw_frame(active, reveal):
    """active: index of highlighted stage. reveal: how many stages are drawn."""
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # masthead
    d.rectangle([0, 0, W, 5], fill=RED)
    d.text((MARGIN, 40), "WHICH TREE FALLS FIRST", font=F_CAPS, fill=MUTED)
    d.text((MARGIN, 60), "From a resident's photo to a crew's route",
           font=F_TITLE, fill=INK)
    d.text((MARGIN, 104),
           "290 open reports. One crew. The order is the whole problem.",
           font=F_SUB, fill=MUTED)

    # pipeline boxes
    for i, stage in enumerate(STAGES):
        if i >= reveal:
            break
        x = MARGIN + i * (BOX_W + GAP)
        is_active = i == active
        fill = INK if is_active else PANEL
        outline = INK if is_active else HAIR
        rounded(d, [x, BOX_Y, x + BOX_W, BOX_Y + BOX_H], 4,
                fill=fill, outline=outline, width=1)

        label = stage["key"]
        tw = d.textlength(label, font=F_STAGE)
        d.text((x + (BOX_W - tw) / 2, BOX_Y + 14), label,
               font=F_STAGE, fill=WHITE if is_active else BODY)

        num = f"0{i + 1}"
        nw = d.textlength(num, font=F_MONO_S)
        d.text((x + (BOX_W - nw) / 2, BOX_Y + 36), num,
               font=F_MONO_S, fill=(148, 163, 184) if is_active else MUTED)

        # connector
        if i < len(STAGES) - 1 and i + 1 < reveal:
            cx = x + BOX_W
            cy = BOX_Y + BOX_H // 2
            d.line([cx + 2, cy, cx + GAP - 2, cy], fill=HAIR, width=2)

    # active-stage accent bar
    if active < reveal:
        ax = MARGIN + active * (BOX_W + GAP)
        d.rectangle([ax, BOX_Y + BOX_H + 6, ax + BOX_W, BOX_Y + BOX_H + 9],
                    fill=STAGES[active]["accent"])

    # detail panel
    stage = STAGES[active]
    py = 280
    d.line([MARGIN, py, W - MARGIN, py], fill=HAIR, width=1)

    d.text((MARGIN, py + 22), stage["title"], font=F_TITLE, fill=INK)
    for j, line in enumerate(stage["detail"]):
        d.text((MARGIN, py + 70 + j * 26), line, font=F_BODY, fill=BODY)

    # mono callout
    my = py + 136
    rounded(d, [MARGIN, my, W - MARGIN, my + 46], 3,
            fill=PANEL, outline=HAIR, width=1)
    d.rectangle([MARGIN, my, MARGIN + 3, my + 46], fill=stage["accent"])
    d.text((MARGIN + 20, my + 14), stage["mono"], font=F_MONO, fill=INK)

    # footer
    d.text((MARGIN, H - 42),
           "It decides inspection ORDER — never whether a tree is dangerous.",
           font=F_SMALL, fill=MUTED)
    d.text((W - MARGIN - 190, H - 42),
           "Next.js · Supabase · Claude",
           font=F_SMALL, fill=MUTED)
    return img


frames = []

# Build the pipeline up, one box at a time.
for i in range(len(STAGES)):
    for _ in range(3):
        frames.append(draw_frame(active=i, reveal=i + 1))

# Then walk through each stage with the whole pipeline visible.
for i in range(len(STAGES)):
    hold = 26 if i in (2, 3, 4) else 20   # linger on the interesting ones
    for _ in range(hold):
        frames.append(draw_frame(active=i, reveal=len(STAGES)))

out = "presentation/architecture-flow.gif"
frames[0].save(
    out,
    save_all=True,
    append_images=frames[1:],
    duration=FPS_MS,
    loop=0,
    optimize=True,
)
print(f"wrote {out}  ({len(frames)} frames, {len(frames) * FPS_MS / 1000:.1f}s)")
