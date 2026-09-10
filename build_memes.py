#!/usr/bin/env python3
"""Build sir's meme-movie GIF variants (icon-m1..m5) for XLOVESCHARLIE.

Each GIF is a ~4-6s mini-movie: slow cinematic open -> fast slideshow of
viral KirkSlop memes -> credit frames ("@handle loves u") -> "we love u".
Sources: meme-src/ pulled from X (see meme-src/MAPPING below in MAPPING).
"""
import os
from PIL import Image, ImageDraw, ImageFilter

from build_icons import (SIZE, FB, FR, font, cover, watermark, draw_candle,
                         text_frame, darken, NIGHT)

HERE = os.path.dirname(os.path.abspath(__file__))
M = lambda n: os.path.join(HERE, "meme-src", n)
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# image file -> (tweet id, author handle)
MAPPING = {
    "t01-quassssssss-1.jpg": ("2097811700531544281", "@quassssssss"),
    "t01-quassssssss-2.jpg": ("2097811700531544281", "@quassssssss"),
    "t01-quassssssss-3.jpg": ("2097811700531544281", "@quassssssss"),
    "t01-quassssssss-4.jpg": ("2097811700531544281", "@quassssssss"),
    "t02-kayrem333-1.jpg": ("2097868722061119793", "@kayrem333"),
    "t03-Ivyr1ver-1.jpg": ("2097823097420165484", "@Ivyr1ver"),
    "t04-B1TuckerCarlson-1.jpg": ("2097677690778063208", "@B1TuckerCarlson"),
    "t05-Webardos-1.jpg": ("2097663938544406919", "@__Webardos__"),
    "t06-Itskirkslop-1.jpg": ("2097671370771763255", "@Itskirkslop"),
    "t07-B1TuckerCarlson-1.jpg": ("2097484210407641229", "@B1TuckerCarlson"),
    "t08-Erikabot1939-f1.jpg": ("2094776836966531311", "@Erikabot1939"),
    "t11-Itskirkslop-bigk-1.jpg": ("2097890309812220378", "@Itskirkslop"),
    "t12-Itskirkslop-insane-1.jpg": ("2097595384126165214", "@Itskirkslop"),
}

MEME_CREDITS = ["@quassssssss", "@kayrem333", "@Ivyr1ver", "@B1TuckerCarlson",
                "@__Webardos__", "@Itskirkslop", "@Erikabot1939"]
CT_CREDITS = ["@elonmusk", "@cz_binance", "@VitalikButerin"]

GOLD = (232, 179, 75)
WHITE = (235, 238, 248)


def mc(name, focus_y=0.35):
    return cover(M(name), size=SIZE, focus_y=focus_y)


def save_mgif(frames, name, durations, colors=128):
    frames = [watermark(f.convert("RGB")) for f in frames]
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=colors) for f in frames]
    out = os.path.join(HERE, name)
    pal[0].save(out, save_all=True, append_images=pal[1:], loop=0,
                duration=durations, optimize=True, disposal=2)
    kb = os.path.getsize(out) / 1024
    total = sum(durations) / 1000
    print(f"{name}: {len(pal)} frames, {total:.1f}s, {kb:.0f} KB")
    assert kb < 3 * 1024, f"{name} exceeds 3MB"


def credit_frame(handles, title="made with love by"):
    im = Image.new("RGB", (SIZE, SIZE), (8, 10, 22))
    d = ImageDraw.Draw(im)
    ft = font(FR, 20)
    fh = font(FB, 27)
    bb = d.textbbox((0, 0), title, font=ft)
    d.text(((SIZE - bb[2]) / 2, 92), title, font=ft, fill=(150, 158, 180))
    y = 150
    for h in handles:
        txt = f"{h} loves u"
        bb = d.textbbox((0, 0), txt, font=fh)
        d.text(((SIZE - bb[2]) / 2, y), txt, font=fh, fill=GOLD)
        y += 46
    return im


def close_frame(big="we love u", small="X remembers"):
    im = Image.new("RGB", (SIZE, SIZE), (8, 10, 22))
    im = draw_candle(im.convert("RGBA"), SIZE * 0.5, SIZE * 0.78, scale=1.1,
                     flicker=0.2).convert("RGB")
    d = ImageDraw.Draw(im)
    f1 = font(FB, 72)
    bb = d.textbbox((0, 0), big, font=f1)
    d.text(((SIZE - bb[2]) / 2, 120), big, font=f1, fill=WHITE)
    f2 = font(FR, 26)
    bb = d.textbbox((0, 0), small, font=f2)
    d.text(((SIZE - bb[2]) / 2, 215), small, font=f2, fill=GOLD)
    return im


def grid4(imgs):
    canvas = Image.new("RGB", (SIZE, SIZE), (5, 6, 14))
    cells = [im.resize((236, 236), Image.LANCZOS) for im in imgs]
    pos = [(2, 2), (242, 2), (2, 242), (242, 242)]
    for c, p in zip(cells, pos):
        canvas.paste(c, p)
    return canvas


def kenburns(im, scale, cx=0.5, cy=0.4):
    w, h = im.size
    side = int(w / scale)
    x0 = int(max(0, min(w - side, w * cx - side / 2)))
    y0 = int(max(0, min(h - side, h * cy - side / 2)))
    return im.crop((x0, y0, x0 + side, y0 + side)).resize((SIZE, SIZE), Image.LANCZOS)


def filmify(content, sprocket=GOLD):
    """Wrap a 480x400-ish content image in a film-strip frame."""
    im = Image.new("RGB", (SIZE, SIZE), (12, 12, 16))
    content = content.resize((SIZE, 400), Image.LANCZOS)
    im.paste(content, (0, 40))
    d = ImageDraw.Draw(im)
    for x in range(14, SIZE, 44):
        d.rounded_rectangle((x, 10, x + 22, 28), radius=4, outline=sprocket, width=2)
        d.rounded_rectangle((x, 452, x + 22, 470), radius=4, outline=sprocket, width=2)
    return im


# ------------------------------------------------------- m1: classic fade open
def m1():
    emoji = mc("t01-quassssssss-1.jpg")
    black = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
    slides = [mc(n) for n in ["t03-Ivyr1ver-1.jpg", "t06-Itskirkslop-1.jpg",
                              "t02-kayrem333-1.jpg", "t07-B1TuckerCarlson-1.jpg",
                              "t01-quassssssss-2.jpg", "t05-Webardos-1.jpg"]]
    frames = ([Image.blend(black, emoji, 0.55), emoji] + slides +
              [credit_frame(MEME_CREDITS[:4]),
               credit_frame(MEME_CREDITS[4:] + CT_CREDITS[:2]),
               close_frame()])
    save_mgif(frames, "icon-m1-classic.gif",
              [880, 800] + [300] * 6 + [600, 600, 1300])


# ------------------------------------------------------- m2: towers Ken Burns
def m2():
    towers = Image.open(M("t05-Webardos-1.jpg")).convert("RGB")
    # eased push-in: wide on the full meme -> tight on the face on the tower
    s0, s1 = 1.0, 1.85
    c0, c1 = (0.50, 0.50), (0.54, 0.615)
    opens = []
    for t in (0.0, 0.33, 0.67, 1.0):
        e = t * t * (3 - 2 * t)
        opens.append(kenburns(towers, s0 + (s1 - s0) * e,
                              c0[0] + (c1[0] - c0[0]) * e,
                              c0[1] + (c1[1] - c0[1]) * e))
    g1 = grid4([mc("t01-quassssssss-1.jpg"), mc("t03-Ivyr1ver-1.jpg"),
                mc("t06-Itskirkslop-1.jpg"), mc("t02-kayrem333-1.jpg")])
    g2 = grid4([mc("t01-quassssssss-2.jpg"), mc("t01-quassssssss-3.jpg"),
                mc("t01-quassssssss-4.jpg"), mc("t07-B1TuckerCarlson-1.jpg")])
    g3 = grid4([mc("t04-B1TuckerCarlson-1.jpg"), mc("t12-Itskirkslop-insane-1.jpg"),
                mc("t11-Itskirkslop-bigk-1.jpg"), mc("t08-Erikabot1939-f1.jpg")])
    frames = (opens + [g1, g2, g3] +
              [credit_frame(MEME_CREDITS[:4]),
               credit_frame(MEME_CREDITS[4:] + CT_CREDITS[:2]),
               close_frame()])
    save_mgif(frames, "icon-m2-towers-zoom.gif",
              [650, 600, 600, 1000] + [380] * 3 + [550, 550, 1250])


# ------------------------------------------------------- m3: typewriter open
def m3():
    full = "dear charlie,"
    opens = []
    for n in (5, 10, len(full)):
        im = Image.new("RGB", (SIZE, SIZE), (8, 10, 22))
        d = ImageDraw.Draw(im)
        f = font(FM, 46)
        txt = full[:n] + ("_" if n < len(full) else "")
        bb = d.textbbox((0, 0), txt, font=f)
        d.text(((SIZE - bb[2]) / 2, SIZE / 2 - 30), txt, font=f, fill=GOLD)
        opens.append(im)
    cuts = [mc(n) for n in ["t01-quassssssss-1.jpg", "t06-Itskirkslop-1.jpg",
                            "t03-Ivyr1ver-1.jpg", "t05-Webardos-1.jpg",
                            "t02-kayrem333-1.jpg"]]
    # credits ticker: same lines rising
    lines = [f"{h} loves u" for h in MEME_CREDITS + CT_CREDITS[:2]]
    ticker = []
    for k in range(3):
        im = Image.new("RGB", (SIZE, SIZE), (8, 10, 22))
        d = ImageDraw.Draw(im)
        f = font(FB, 30)
        y = SIZE - k * 160 - 40
        for j, ln in enumerate(lines):
            yy = y + j * 64
            if -40 < yy < SIZE:
                bb = d.textbbox((0, 0), ln, font=f)
                d.text(((SIZE - bb[2]) / 2, yy), ln, font=f, fill=GOLD)
        ticker.append(im)
    frames = opens + cuts + ticker + [close_frame()]
    save_mgif(frames, "icon-m3-dear-charlie.gif",
              [650, 650, 800] + [280] * 5 + [430, 430, 430, 1250])


# ------------------------------------------------------- m4: candle + strobe
def m4():
    dark1 = draw_candle(Image.new("RGBA", (SIZE, SIZE), (5, 6, 12, 255)),
                        SIZE * 0.5, SIZE * 0.55, scale=1.4, flicker=0.0)
    dark2 = draw_candle(Image.new("RGBA", (SIZE, SIZE), (5, 6, 12, 255)),
                        SIZE * 0.5, SIZE * 0.55, scale=1.4, flicker=0.6)
    blank = Image.new("RGB", (SIZE, SIZE), (5, 6, 12))
    memes = [mc(n) for n in ["t05-Webardos-1.jpg", "t03-Ivyr1ver-1.jpg",
                             "t06-Itskirkslop-1.jpg", "t01-quassssssss-1.jpg"]]
    strobe = []
    for im in memes:
        strobe += [blank, im]
    frames = ([dark1.convert("RGB"), dark2.convert("RGB")] + strobe +
              [credit_frame(MEME_CREDITS[:4]),
               credit_frame(MEME_CREDITS[4:] + CT_CREDITS[:2]),
               close_frame()])
    save_mgif(frames, "icon-m4-candle-strobe.gif",
              [850, 800] + [230, 290] * 4 + [550, 550, 1250])


# ------------------------------------------------------- m5: film reel
def m5():
    title = Image.new("RGB", (SIZE, 400), (8, 10, 22))
    d = ImageDraw.Draw(title)
    f1 = font(FB, 44)
    bb = d.textbbox((0, 0), "XLOVESCHARLIE", font=f1)
    d.text(((SIZE - bb[2]) / 2, 150), "XLOVESCHARLIE", font=f1, fill=GOLD)
    f2 = font(FR, 24)
    bb = d.textbbox((0, 0), "the meme movie", font=f2)
    d.text(((SIZE - bb[2]) / 2, 215), "the meme movie", font=f2, fill=(150, 158, 180))
    reel = [mc(n) for n in ["t01-quassssssss-1.jpg", "t03-Ivyr1ver-1.jpg",
                            "t06-Itskirkslop-1.jpg", "t05-Webardos-1.jpg",
                            "t02-kayrem333-1.jpg"]]
    cred = Image.new("RGB", (SIZE, 400), (8, 10, 22))
    d = ImageDraw.Draw(cred)
    f3 = font(FB, 26)
    y = 96
    for h in MEME_CREDITS:
        txt = f"{h} loves u"
        bb = d.textbbox((0, 0), txt, font=f3)
        d.text(((SIZE - bb[2]) / 2, y), txt, font=f3, fill=GOLD)
        y += 42
    cred2 = Image.new("RGB", (SIZE, 400), (8, 10, 22))
    d = ImageDraw.Draw(cred2)
    y = 140
    for h in CT_CREDITS:
        txt = f"{h} loves u"
        bb = d.textbbox((0, 0), txt, font=f3)
        d.text(((SIZE - bb[2]) / 2, y), txt, font=f3, fill=GOLD)
        y += 46
    frames = ([filmify(title), filmify(title)] +
              [filmify(r) for r in reel] +
              [filmify(cred), filmify(cred2),
               filmify(close_frame().resize((SIZE, 400), Image.LANCZOS))])
    save_mgif(frames, "icon-m5-film-reel.gif",
              [850, 850] + [330] * 5 + [600, 600, 1500])


if __name__ == "__main__":
    m1(); m2(); m3(); m4(); m5()
    print("done")
