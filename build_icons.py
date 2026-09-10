#!/usr/bin/env python3
"""Build 5 animated-GIF icon samples for the XLOVESCHARLIE tribute token.

Memorial tone only: portraits, candlelight, Tribute-in-Light beams, skyline.
Sources (Wikimedia Commons):
  kirk.jpg    - Charlie Kirk headshot, CC BY-SA 2.0
  elon.jpg    - Elon Musk portrait, CC BY-SA 4.0
  beams.jpg   - Tribute in Light, public domain
  skyline.jpg - Lower Manhattan w/ beams, CC BY-SA 4.0
Drawn with PIL: candle flames, supplemental beams, X motif, text frames.
Every frame carries a discreet "Litagatoro MK" watermark (review samples).
"""
import math
import os
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda n: os.path.join(HERE, "assets", n)
SIZE = 480
DUR = 700  # ms per frame

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def cover(path, size=SIZE, focus_y=0.35):
    """Load image and center-crop to square, biased toward the top (faces)."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    side = min(w, h)
    x0 = (w - side) // 2
    y0 = int(max(0, min(h - side, (h * focus_y) - side // 2)))
    im = im.crop((x0, y0, x0 + side, y0 + side))
    return im.resize((size, size), Image.LANCZOS)

def darken(im, factor):
    return ImageEnhance.Brightness(im).enhance(factor)

def watermark(im):
    """Small discreet Litagatoro MK mark, bottom-right."""
    im = im.copy()
    d = ImageDraw.Draw(im, "RGBA")
    f = font(FR, 13)
    txt = "Litagatoro MK"
    bb = d.textbbox((0, 0), txt, font=f)
    x, y = SIZE - (bb[2] - bb[0]) - 8, SIZE - (bb[3] - bb[1]) - 6
    d.text((x + 1, y + 1), txt, font=f, fill=(0, 0, 0, 140))
    d.text((x, y), txt, font=f, fill=(255, 255, 255, 150))
    return im

def vignette(im, strength=0.55):
    """Soft dark vignette so small-icon legibility improves."""
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((-w * 0.25, -h * 0.25, w * 1.25, h * 1.25), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(60))
    black = Image.new("RGB", (w, h), (5, 5, 15))
    return Image.composite(im, black, mask.point(lambda p: int(255 - (255 - p) * strength)))

def radial_glow(size, color, radius, cx, cy):
    """RGBA glow sprite."""
    s = int(radius * 2)
    spr = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(spr)
    steps = 24
    for i in range(steps, 0, -1):
        r = radius * i / steps
        alpha = int(color[3] * (1 - i / steps) ** 1.6)
        d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), fill=color[:3] + (alpha,))
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(spr, (int(cx - s / 2), int(cy - s / 2)), spr)
    return out

def draw_candle(base, cx, cy, scale=1.0, flicker=0.0, lit=True):
    """Candle with animated flame. flicker in [-1,1] shifts the flame."""
    im = base.convert("RGBA")
    w_body = 26 * scale
    h_body = 70 * scale
    d = ImageDraw.Draw(im, "RGBA")
    # candle body
    d.rounded_rectangle((cx - w_body / 2, cy, cx + w_body / 2, cy + h_body),
                        radius=6 * scale, fill=(232, 222, 200, 255))
    d.rounded_rectangle((cx - w_body / 2, cy, cx + w_body / 2, cy + h_body),
                        radius=6 * scale, outline=(180, 168, 140, 255), width=2)
    # wick
    d.line((cx, cy - 2, cx, cy - 8 * scale), fill=(40, 30, 20, 255), width=max(2, int(2 * scale)))
    if lit:
        fx = cx + flicker * 5 * scale
        fh = 34 * scale * (1 + 0.12 * flicker)
        fw = 15 * scale
        fy = cy - 8 * scale
        # warm glow behind flame
        im = Image.alpha_composite(im, radial_glow(im.size, (255, 190, 90, 120), 90 * scale, fx, fy - fh * 0.4))
        d = ImageDraw.Draw(im, "RGBA")
        # outer flame (teardrop via polygon + ellipse)
        d.polygon([(fx - fw * 0.5, fy), (fx + fw * 0.5, fy),
                   (fx + flicker * 4 * scale, fy - fh)], fill=(255, 150, 40, 220))
        d.ellipse((fx - fw * 0.5, fy - fw * 0.5, fx + fw * 0.5, fy + fw * 0.55),
                  fill=(255, 150, 40, 220))
        # inner flame
        iw = fw * 0.45
        ih = fh * 0.55
        d.polygon([(fx - iw * 0.5, fy), (fx + iw * 0.5, fy),
                   (fx + flicker * 2 * scale, fy - ih)], fill=(255, 225, 140, 235))
        d.ellipse((fx - iw * 0.5, fy - iw * 0.4, fx + iw * 0.5, fy + iw * 0.45),
                  fill=(255, 225, 140, 235))
        # core
        cw = fw * 0.16
        d.ellipse((fx - cw, fy - cw * 1.6, fx + cw, fy + cw * 0.6), fill=(255, 250, 225, 245))
    return im

def draw_beams(base, x1, x2, alpha=90, width=16, lean=0.06, y_top=-40):
    """Twin tribute light beams rising into the sky."""
    im = base.convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    W, H = im.size
    for x in (x1, x2):
        dx = W * lean
        d.polygon([(x - width, H), (x + width, H),
                   (x + dx + width * 0.35, y_top), (x + dx - width * 0.35, y_top)],
                  fill=(150, 190, 255, alpha))
        d.polygon([(x - width * 0.35, H), (x + width * 0.35, H),
                   (x + dx + width * 0.12, y_top), (x + dx - width * 0.12, y_top)],
                  fill=(215, 230, 255, min(255, alpha + 60)))
    for x in (x1, x2):
        g = radial_glow(im.size, (170, 200, 255, alpha + 40), width * 3.2, x, H - 8)
        ov = Image.alpha_composite(ov, g)
    ov = ov.filter(ImageFilter.GaussianBlur(1.2))
    return Image.alpha_composite(im, ov)

def draw_x_motif(base, cx, cy, r=46, alpha=110, color=(235, 240, 255), weight=10):
    """Subtle X logo motif: two diagonal strokes."""
    im = base.convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ov = Image.alpha_composite(ov, radial_glow(im.size, (200, 215, 255, alpha // 2), r * 1.7, cx, cy))
    d = ImageDraw.Draw(ov)
    d.line((cx - r, cy - r, cx + r, cy + r), fill=color + (alpha,), width=weight)
    d.line((cx - r, cy + r, cx + r, cy - r), fill=color + (alpha,), width=weight)
    return Image.alpha_composite(im, ov)

def text_frame(bg, lines, sub=None):
    """Memorial text frame: 'X remembers' style."""
    im = bg.convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    W, H = im.size
    total_h = 0
    fonts = []
    for txt, sz in lines:
        f = font(FB, sz)
        bb = d.textbbox((0, 0), txt, font=f)
        tw = bb[2] - bb[0]
        while tw > W * 0.88 and sz > 20:
            sz -= 4
            f = font(FB, sz)
            bb = d.textbbox((0, 0), txt, font=f)
            tw = bb[2] - bb[0]
        fonts.append((txt, f, tw, bb[3] - bb[1]))
        total_h += bb[3] - bb[1] + 14
    y = H * 0.42 - total_h / 2
    for txt, f, tw, th in fonts:
        d.text(((W - tw) / 2 + 2, y + 2), txt, font=f, fill=(0, 0, 0, 170))
        d.text(((W - tw) / 2, y), txt, font=f, fill=(240, 244, 255, 255))
        y += th + 14
    if sub:
        f2 = font(FR, 20)
        bb = d.textbbox((0, 0), sub, font=f2)
        d.text(((W - (bb[2] - bb[0])) / 2, y + 10), sub, font=f2, fill=(190, 200, 225, 220))
    return im

def blend(a, b, t):
    return Image.blend(a.convert("RGBA"), b.convert("RGBA"), t)

def save_gif(frames, name, durations=None):
    frames = [watermark(f.convert("RGB")) for f in frames]
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=256) for f in frames]
    out = os.path.join(HERE, name)
    pal[0].save(out, save_all=True, append_images=pal[1:], loop=0,
                duration=durations or [DUR] * len(pal), optimize=True, disposal=2)
    kb = os.path.getsize(out) / 1024
    print(f"{name}: {len(pal)} frames, {kb:.0f} KB")
    assert kb < 3 * 1024, f"{name} exceeds 3MB"

KIRK = cover(A("kirk.jpg"), focus_y=0.30)
ELON = cover(A("elon.jpg"), focus_y=0.32)
BEAMS = cover(A("beams.jpg"))
SKY = cover(A("skyline.jpg")).resize((SIZE, SIZE), Image.LANCZOS)
NIGHT = Image.new("RGB", (SIZE, SIZE), (8, 10, 24))

# Shared memorial text backdrop: dim beams photo + drawn twin beams + candle
def memorial_bg():
    bg = darken(BEAMS, 0.55)
    bg = draw_beams(bg, SIZE * 0.40, SIZE * 0.60, alpha=70, width=13)
    bg = draw_candle(bg, SIZE * 0.5, SIZE * 0.82, scale=0.9, flicker=0.2)
    return bg

def x_remembers_frame():
    return text_frame(memorial_bg(), [("X remembers", 64)],
                      sub="XLOVESCHARLIE - a tribute")

# ---------------------------------------------------------------- 1. Candle Vigil
def v1():
    base = vignette(darken(KIRK, 0.92))
    f1 = draw_candle(base, SIZE * 0.5, SIZE * 0.86, scale=1.25, flicker=0.0)
    f2 = draw_candle(base, SIZE * 0.5, SIZE * 0.86, scale=1.25, flicker=0.7)
    f3 = draw_candle(draw_beams(darken(BEAMS, 0.9), SIZE * 0.42, SIZE * 0.58, alpha=95),
                     SIZE * 0.5, SIZE * 0.86, scale=1.1, flicker=-0.5)
    f4 = vignette(darken(ELON, 0.95))
    f5 = x_remembers_frame()
    save_gif([f1, f2, f3, f4, f5], "icon-v1-candle-vigil.gif",
             durations=[700, 700, 750, 700, 900])

# ---------------------------------------------------------------- 2. Twin Beams
def v2():
    bg = draw_beams(darken(NIGHT, 1.0), SIZE * 0.38, SIZE * 0.62, alpha=110, width=18)
    bg = Image.alpha_composite(bg.convert("RGBA"),
                               radial_glow((SIZE, SIZE), (120, 150, 220, 60), 200, SIZE / 2, SIZE))
    kirk = blend(bg, vignette(KIRK), 0.82)
    candle = draw_candle(bg, SIZE * 0.5, SIZE * 0.82, scale=1.3, flicker=0.3)
    elon = blend(bg, vignette(ELON), 0.82)
    txt = text_frame(draw_candle(bg, SIZE * 0.5, SIZE * 0.86, scale=0.9, flicker=0.0),
                     [("X remembers", 64)], sub="XLOVESCHARLIE - a tribute")
    frames = [kirk,
              blend(kirk, candle, 0.5),
              candle,
              blend(candle, elon, 0.5),
              elon,
              blend(elon, txt, 0.5),
              txt]
    save_gif(frames, "icon-v2-twin-beams.gif", durations=[700] * 6 + [900])

# ---------------------------------------------------------------- 3. Skyline Memorial
def v3():
    sky0 = darken(SKY, 0.75)
    f1 = sky0  # strongest: dusk skyline
    f2 = draw_beams(sky0, SIZE * 0.68, SIZE * 0.80, alpha=60, width=12)
    f3 = draw_beams(sky0, SIZE * 0.68, SIZE * 0.80, alpha=130, width=14)
    kirk_over = blend(f3, vignette(KIRK, 0.4), 0.0)
    kirk_circle = vignette(KIRK)
    f4 = blend(f3, kirk_circle, 0.45)
    f5 = blend(f3, kirk_circle, 0.8)
    f6 = text_frame(draw_beams(darken(sky0, 0.7), SIZE * 0.68, SIZE * 0.80, alpha=100, width=13),
                    [("X remembers", 60)], sub="XLOVESCHARLIE - a tribute")
    save_gif([f1, f2, f3, f4, f5, f6], "icon-v3-skyline-memorial.gif",
             durations=[650, 650, 700, 650, 750, 950])

# ---------------------------------------------------------------- 4. Triptych
def panel(img, glow=False):
    p = img.resize((148, 420), Image.LANCZOS).convert("RGBA")
    if glow:
        p = Image.alpha_composite(Image.new("RGBA", p.size, (30, 40, 70, 255)), p)
    return p

def triptych_image(order_kirk=True, beams_mid_glow=1.0):
    canvas = Image.new("RGBA", (SIZE, SIZE), (10, 12, 26, 255))
    kirk_p = cover(A("kirk.jpg"), size=420, focus_y=0.30).crop((136, 0, 284, 420))
    mid_src = draw_candle(draw_beams(darken(NIGHT, 1.0).resize((420, 420)),
                                     170, 250, alpha=int(100 * beams_mid_glow), width=14),
                          210, 290, scale=1.2, flicker=0.2).crop((136, 0, 284, 420))
    elon_p = cover(A("elon.jpg"), size=420, focus_y=0.32).crop((136, 0, 284, 420))
    canvas.paste(kirk_p, (26, 30))
    canvas.paste(mid_src.convert("RGBA"), (166, 30))
    canvas.paste(elon_p, (306, 30))
    d = ImageDraw.Draw(canvas, "RGBA")
    for x in (24, 164, 304):
        d.rectangle((x, 28, x + 152, 452), outline=(120, 140, 190, 160), width=2)
    return canvas

def v4():
    full = triptych_image()
    kirk_only = Image.new("RGBA", (SIZE, SIZE), (10, 12, 26, 255))
    kirk_p = cover(A("kirk.jpg"), size=420, focus_y=0.30).crop((136, 0, 284, 420))
    kirk_only.paste(kirk_p, (166, 30))
    d = ImageDraw.Draw(kirk_only, "RGBA")
    d.rectangle((164, 28, 316, 452), outline=(120, 140, 190, 160), width=2)
    kirk_mid = triptych_image()
    # build "two panels" state: kirk + candle/beams panel, empty right slot
    two = Image.new("RGBA", (SIZE, SIZE), (10, 12, 26, 255))
    mid_src = draw_candle(draw_beams(darken(NIGHT, 1.0).resize((420, 420)),
                                     170, 250, alpha=100, width=14),
                          210, 290, scale=1.2, flicker=0.2).crop((136, 0, 284, 420))
    two.paste(kirk_p, (86, 30))
    two.paste(mid_src.convert("RGBA"), (246, 30))
    d2 = ImageDraw.Draw(two, "RGBA")
    for x in (84, 244):
        d2.rectangle((x, 28, x + 152, 452), outline=(120, 140, 190, 160), width=2)
    txt = text_frame(memorial_bg(), [("X remembers", 64)], sub="XLOVESCHARLIE - a tribute")
    frames = [full, kirk_only, two, full,
              triptych_image(beams_mid_glow=1.5), txt]
    save_gif(frames, "icon-v4-triptych.gif", durations=[750, 600, 600, 650, 700, 950])

# ---------------------------------------------------------------- 5. Minimal Heart
def v5():
    base = vignette(darken(KIRK, 0.97), strength=0.45)
    base = draw_x_motif(base, SIZE * 0.82, SIZE * 0.16, r=34, alpha=95)
    # small discreet heart of light above the candle
    def with_heart(im, beat=1.0):
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        cx, cy, s = SIZE * 0.18, SIZE * 0.16, 15 * beat
        d.polygon([(cx, cy + s * 0.9),
                   (cx - s, cy - s * 0.15), (cx - s * 0.55, cy - s * 0.8),
                   (cx, cy - s * 0.25),
                   (cx + s * 0.55, cy - s * 0.8), (cx + s, cy - s * 0.15)],
                  fill=(255, 120, 140, 120))
        ov = ov.filter(ImageFilter.GaussianBlur(1.5))
        return Image.alpha_composite(im.convert("RGBA"), ov)
    f1 = draw_candle(with_heart(base), SIZE * 0.5, SIZE * 0.90, scale=0.95, flicker=0.0)
    f2 = draw_candle(with_heart(base, 1.06), SIZE * 0.5, SIZE * 0.90, scale=0.95, flicker=0.6)
    f3 = draw_candle(with_heart(base, 0.97), SIZE * 0.5, SIZE * 0.90, scale=0.95, flicker=-0.5)
    flash = draw_beams(base, SIZE * 0.36, SIZE * 0.64, alpha=150, width=20)
    f4 = draw_candle(with_heart(flash, 1.1), SIZE * 0.5, SIZE * 0.90, scale=0.95, flicker=0.2)
    f5 = f1.copy()
    save_gif([f1, f2, f3, f4, f5], "icon-v5-minimal-heart.gif",
             durations=[800, 650, 650, 550, 800])

if __name__ == "__main__":
    v1(); v2(); v3(); v4(); v5()
    print("done")
