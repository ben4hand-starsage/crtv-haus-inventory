#!/usr/bin/env python3
"""
Build 1200x630 Open Graph share cards for the site.

Every asset we have is portrait, and social platforms centre-crop to 1.91:1,
which decapitates a book cover or a portrait. So rather than hand them the raw
image, each card is composed: the artwork sits intact on the left at its own
aspect ratio, the headline and wordmark sit on the right, on brand cream.

Output: DELAY/site/assets/img/og/<name>.jpg
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SITE = "/Users/benjaminforehand/Desktop/CLAUDE/DELAY/site"
IMG = os.path.join(SITE, "assets", "img")
OUT = os.path.join(IMG, "og")

W, H = 1200, 630

# Brand palette, lifted from assets/css/brand.css
INK      = (38, 32, 25)
INK_2    = (87, 76, 64)
BG       = (247, 242, 234)
SAND     = (231, 222, 207)
CLAY     = (180, 105, 78)
STONE    = (162, 147, 126)
LINE     = (222, 213, 199)

SERIF      = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SERIF_IT   = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
SANS_BOLD  = "/System/Library/Fonts/Supplemental/Futura.ttc"


def font(path, size, index=None):
    try:
        return (ImageFont.truetype(path, size, index=index)
                if index is not None else ImageFont.truetype(path, size))
    except Exception:
        return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(art_path, eyebrow, title, out_name, art_scale=0.80):
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)

    # Left panel in sand, so the artwork has something to sit against.
    panel_w = 470
    d.rectangle([0, 0, panel_w, H], fill=SAND)

    if art_path and os.path.exists(art_path):
        art = Image.open(art_path).convert("RGB")
        target_h = int(H * art_scale)
        scale = target_h / art.height
        target_w = int(art.width * scale)
        if target_w > panel_w - 80:
            target_w = panel_w - 80
            target_h = int(art.height * (target_w / art.width))
        art = art.resize((target_w, target_h), Image.LANCZOS)

        x = (panel_w - target_w) // 2
        y = (H - target_h) // 2

        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rectangle(
            [x + 5, y + 10, x + target_w + 5, y + target_h + 10],
            fill=(60, 48, 38, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(16))
        canvas = Image.alpha_composite(canvas.convert("RGBA"), shadow).convert("RGB")
        d = ImageDraw.Draw(canvas)

        canvas.paste(art, (x, y))
        d.rectangle([x, y, x + target_w - 1, y + target_h - 1], outline=LINE, width=1)

    # Right column: eyebrow, headline, wordmark.
    tx = panel_w + 70
    tw = W - tx - 70

    f_eye = font(SANS_BOLD, 20, index=0)
    f_h1 = font(SERIF, 60)
    f_mark = font(SERIF, 25)

    y = 150
    if eyebrow:
        d.text((tx, y), eyebrow.upper(), font=f_eye, fill=CLAY)
        y += 46

    for line in wrap(d, title, f_h1, tw):
        d.text((tx, y), line, font=f_h1, fill=INK)
        y += 70

    # Rule + wordmark, anchored to the bottom.
    d.line([(tx, H - 118), (tx + 74, H - 118)], fill=CLAY, width=3)
    d.text((tx, H - 96), "Aaron Delay Counseling", font=f_mark, fill=INK_2)

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, out_name)
    canvas.save(path, "JPEG", quality=88, optimize=True, progressive=True)
    return path, os.path.getsize(path)


CARDS = [
    (f"{IMG}/aaron-and-wife.jpg", "Marriage, plainly",
     "Written for anyone with a marriage.", "home.jpg"),
    (f"{IMG}/reset-mockup.jpg", "Free · 3 pages",
     "The 5-Minute Marriage Argument Reset", "reset.jpg"),
    (f"{IMG}/playbook-mockup.jpg", "$19 · 19 pages",
     "You Didn't Marry the Wrong Person", "playbooks.jpg"),
    (f"{IMG}/book-cover.jpg", "Forthcoming",
     "Saying “I Do” Everyday", "book.jpg"),
    (f"{IMG}/aaron-family.jpg", "For churches",
     "A marriage night for your church.", "speaking.jpg"),
    (f"{IMG}/aaron-and-wife.jpg", "Counseling & coaching",
     "Work with Aaron directly.", "counseling.jpg"),
]

if __name__ == "__main__":
    for art, eye, title, name in CARDS:
        p, size = card(art, eye, title, name)
        print(f"  {name:18} {size/1024:6.0f} KB")
    print(f"\nwrote {len(CARDS)} cards to {OUT}")
