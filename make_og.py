#!/usr/bin/env python3
"""Generate a 1200x630 Open Graph preview card for the bridesmaid site."""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
SS = 2  # supersample for crisp text
img = Image.new("RGB", (W * SS, H * SS), (33, 16, 8))
d = ImageDraw.Draw(img, "RGBA")

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

# --- warm vertical gradient (coffee -> deep wine -> coffee) ---
top = (42, 21, 9)
mid = (58, 14, 26)
bot = (33, 16, 8)
for y in range(H * SS):
    t = y / (H * SS)
    c = lerp(top, mid, t * 2) if t < 0.5 else lerp(mid, bot, (t - 0.5) * 2)
    d.line([(0, y), (W * SS, y)], fill=c)

# --- soft orange radial glow, top center ---
glow = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
cx, cy = int(W * SS * 0.5), int(H * SS * 0.08)
maxr = int(W * SS * 0.55)
for r in range(maxr, 0, -6):
    a = int(60 * (1 - r / maxr) ** 2)
    gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(210, 118, 47, a))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
d = ImageDraw.Draw(img, "RGBA")

# --- scattered petals ---
PETALS = [(210, 118, 47), (237, 160, 97), (231, 196, 140), (154, 50, 71), (231, 183, 166)]
def petal(cx, cy, size, ang, color, alpha):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    s = size * SS
    pts = []
    for i in range(0, 361, 12):
        th = math.radians(i)
        # teardrop-ish petal
        rr = s * (0.5 + 0.5 * math.sin(th)) * (1 - 0.35 * math.cos(2 * th))
        pts.append((cx * SS + rr * math.cos(th + ang), cy * SS + rr * math.sin(th + ang)))
    ld.polygon(pts, fill=color + (alpha,))
    return layer

import random
random.seed(7)
for _ in range(26):
    px = random.randint(20, W - 20)
    py = random.randint(10, H - 10)
    sz = random.randint(7, 16)
    col = random.choice(PETALS)
    al = random.randint(45, 115)
    img = Image.alpha_composite(img.convert("RGBA"), petal(px, py, sz, random.uniform(0, 6.28), col, al)).convert("RGB")
d = ImageDraw.Draw(img, "RGBA")

# --- fonts ---
def F(path, size, index=0):
    return ImageFont.truetype(path, size * SS, index=index)

DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
SNELL = "/System/Library/Fonts/Supplemental/SnellRoundhand.ttc"
FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"

f_eyebrow = F(FUTURA, 26)
f_q = F(DIDOT, 96)

GOLD = (231, 196, 140)
ORANGE = (237, 160, 97)
BLUSH = (231, 183, 166)
CREAM = (245, 231, 210)

def center_text(y, text, font, fill, tracking=0):
    # measure with tracking
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * SS * (len(text) - 1)
    x = (W * SS - total) / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill)
        x += w + tracking * SS
    return total

# --- sealed envelope illustration (reveals nothing) ---
cx = W * SS // 2
ecy = int(0.40 * H * SS)
EW, EH = 470 * SS, 300 * SS
ex0, ey0 = cx - EW // 2, ecy - EH // 2
ex1, ey1 = cx + EW // 2, ecy + EH // 2

# body
d.rounded_rectangle([ex0, ey0, ex1, ey1], radius=18 * SS, fill=(74, 18, 34), outline=GOLD, width=2 * SS)
# pocket V lines from bottom corners toward centre
tip = ecy + 20 * SS
d.line([(ex0 + 3 * SS, ey1 - 3 * SS), (cx, tip)], fill=(201, 168, 118, 150), width=2 * SS)
d.line([(ex1 - 3 * SS, ey1 - 3 * SS), (cx, tip)], fill=(201, 168, 118, 150), width=2 * SS)
# closed flap (triangle pointing down to centre)
flap_tip = ecy + 6 * SS
d.polygon([(ex0, ey0), (ex1, ey0), (cx, flap_tip)], fill=(110, 29, 46))
d.line([(ex0, ey0), (cx, flap_tip), (ex1, ey0)], fill=GOLD, width=2 * SS)

# heart wax seal at the flap tip
sr = 42 * SS
scy = flap_tip
d.ellipse([cx - sr, scy - sr, cx + sr, scy + sr], fill=(110, 29, 46))
d.ellipse([cx - sr, scy - sr, cx + sr, scy + sr], outline=GOLD, width=2 * SS)
scale = 1.3 * SS
hpts = []
for i in range(0, 361, 4):
    t = math.radians(i)
    hx = cx + scale * 16 * (math.sin(t) ** 3)
    hy = scy - scale * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) + 3 * SS
    hpts.append((hx, hy))
d.polygon(hpts, fill=GOLD)

# --- caption ---
center_text(int(0.82 * H * SS), "TAP TO OPEN", f_eyebrow, ORANGE, tracking=12)

# --- downsample ---
final = img.resize((W, H), Image.LANCZOS)
final.save("/Users/pawuku/Documents/briidesmaid/og-image.png", "PNG")
print("saved og-image.png", final.size)
