# -*- coding: utf-8 -*-
"""FotoSecim ikon paketi ureteci. Calistir: python assets/make_icons.py"""
from pathlib import Path
from PIL import Image, ImageDraw

GOLD = (211, 180, 140, 255)
S = 128
C = S // 2

def _img():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))

def d_folder(d):
    d.rounded_rectangle([22, 48, 106, 96], radius=8, outline=GOLD, width=9)
    d.polygon([(22, 52), (22, 36), (52, 36), (60, 48)], outline=GOLD, width=9)

def d_image(d):
    d.rounded_rectangle([22, 32, 106, 96], radius=8, outline=GOLD, width=9)
    d.ellipse([40, 48, 56, 64], fill=GOLD)
    d.line([(30, 88), (58, 60), (76, 78), (88, 66), (100, 78)], fill=GOLD, width=9, joint="curve")

def d_gear(d):
    import math
    for a in range(0, 360, 30):
        r = math.radians(a)
        x1, y1 = C + 26 * math.cos(r), C + 26 * math.sin(r)
        x2, y2 = C + 40 * math.cos(r), C + 40 * math.sin(r)
        d.line([(x1, y1), (x2, y2)], fill=GOLD, width=12)
    d.ellipse([C - 28, C - 28, C + 28, C + 28], outline=GOLD, width=10)
    d.ellipse([C - 11, C - 11, C + 11, C + 11], outline=GOLD, width=9)

def d_heart(d):
    d.ellipse([32, 44, 66, 78], fill=GOLD)
    d.ellipse([62, 44, 96, 78], fill=GOLD)
    d.polygon([(36, 62), (92, 62), (64, 100)], fill=GOLD)

def d_check(d):
    d.line([(36, 66), (58, 88), (94, 42)], fill=GOLD, width=15, joint="curve")

def d_x(d):
    d.line([(42, 42), (86, 86)], fill=GOLD, width=15)
    d.line([(86, 42), (42, 86)], fill=GOLD, width=15)

def d_info(d):
    d.ellipse([26, 26, 102, 102], outline=GOLD, width=10)
    d.line([(64, 56), (64, 88)], fill=GOLD, width=12)
    d.ellipse([58, 36, 70, 48], fill=GOLD)

def d_warn(d):
    d.line([(64, 24), (104, 94), (24, 94), (64, 24)], fill=GOLD, width=10, joint="curve")
    d.line([(64, 52), (64, 74)], fill=GOLD, width=11)
    d.ellipse([58, 80, 70, 92], fill=GOLD)

def d_success(d):
    d.ellipse([26, 26, 102, 102], outline=GOLD, width=10)
    d.line([(46, 66), (60, 80), (84, 50)], fill=GOLD, width=12, joint="curve")

def d_error(d):
    d.ellipse([26, 26, 102, 102], outline=GOLD, width=10)
    d.line([(50, 50), (78, 78)], fill=GOLD, width=12)
    d.line([(78, 50), (50, 78)], fill=GOLD, width=12)

def d_chev_l(d):
    d.line([(76, 32), (46, 64), (76, 96)], fill=GOLD, width=15, joint="curve")

def d_chev_r(d):
    d.line([(52, 32), (82, 64), (52, 96)], fill=GOLD, width=15, joint="curve")

def d_zoom(d):
    d.ellipse([28, 28, 84, 84], outline=GOLD, width=11)
    d.line([(74, 74), (100, 100)], fill=GOLD, width=13)

def d_grid(d):
    for x0, y0 in ((28, 28), (70, 28), (28, 70), (70, 70)):
        d.rounded_rectangle([x0, y0, x0 + 30, y0 + 30], radius=6, fill=GOLD)

def d_plus(d):
    d.line([(64, 34), (64, 94)], fill=GOLD, width=16)
    d.line([(34, 64), (94, 64)], fill=GOLD, width=16)

def d_minus(d):
    d.line([(34, 64), (94, 64)], fill=GOLD, width=16)


def d_refresh(d):
    d.arc([30, 30, 98, 98], start=40, end=320, fill=GOLD, width=13)
    import math
    r = math.radians(40)
    x, y = C + 34 * math.cos(r), C + 34 * math.sin(r)
    d.polygon([(x - 14, y - 6), (x + 12, y - 2), (x - 2, y + 14)], fill=GOLD)


def d_play(d):
    d.polygon([(46, 34), (46, 94), (88, 64)], fill=GOLD)

ICONS = {"folder": d_folder, "image": d_image, "gear": d_gear, "heart": d_heart,
         "check": d_check, "x": d_x, "info": d_info, "warn": d_warn,
         "success": d_success, "error": d_error, "chev-l": d_chev_l,
         "chev-r": d_chev_r, "zoom": d_zoom, "grid": d_grid,
         "plus": d_plus, "minus": d_minus, "refresh": d_refresh, "play": d_play}

DARK = (20, 26, 32, 255)
DARK_VARIANTS = ("folder", "heart", "play", "check")

def main():
    out = Path(__file__).resolve().parent / "icons"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in ICONS.items():
        im = _img()
        fn(ImageDraw.Draw(im))
        im.save(out / f"{name}.png")
        print("wrote", name)
    for name in DARK_VARIANTS:
        im = Image.open(out / f"{name}.png").convert("RGBA")
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if a > 10:
                    px[x, y] = DARK[:3] + (a,)
        im.save(out / f"{name}_dark.png")
        print("wrote", name + "_dark")

if __name__ == "__main__":
    main()
