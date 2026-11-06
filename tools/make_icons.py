#!/usr/bin/env python3
"""產生 PWA 圖示：一疊索引卡。用法：python3 tools/make_icons.py"""
import os
from PIL import Image, ImageDraw

BG = (47, 93, 138, 255)
CARD = (250, 247, 241, 255)
ACCENT = (181, 106, 19, 255)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons")
S = 1024


def rounded(size, radius, fill):
    img = Image.new("RGBA", (size[0], size[1]), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=fill)
    return img


def build():
    canvas = rounded((S, S), int(S * 0.235), BG)
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # 三張微微錯開的卡片
    specs = [(300, 250, 0.0), (320, 240, -5.0), (340, 232, 4.0)]
    for i, (w, h, rot) in enumerate(specs):
        card = rounded((w, h), 26, CARD if i == 2 else (232, 228, 219, 255))
        card = card.rotate(rot, expand=True, resample=Image.BICUBIC)
        cx = S // 2
        cy = S // 2 + 20 - i * 18
        layer.alpha_composite(card, (cx - card.width // 2, cy - card.height // 2))

    d = ImageDraw.Draw(layer)
    # 卡片上的線條與連結點
    cx = S // 2
    cy = S // 2 + 2
    for i, w in enumerate((120, 92, 68)):
        d.rounded_rectangle([cx - 60, cy - 18 + i * 34, cx - 60 + w, cy - 8 + i * 34], radius=5,
                            fill=(90, 84, 74, 190) if i else ACCENT)
    for pt in ((cx + 62, cy + 46), (cx + 96, cy + 78)):
        d.ellipse([pt[0] - 9, pt[1] - 9, pt[0] + 9, pt[1] + 9], fill=ACCENT)
        d.ellipse([pt[0] - 15, pt[1] - 15, pt[0] + 15, pt[1] + 15], outline=ACCENT, width=4)

    # 依內容邊界裁切，放大至畫布的 66%，居中
    box = layer.getbbox()
    art = layer.crop(box)
    target = int(S * 0.66)
    ratio = target / max(art.width, art.height)
    art = art.resize((int(art.width * ratio), int(art.height * ratio)), Image.LANCZOS)
    canvas.alpha_composite(art, ((S - art.width) // 2, (S - art.height) // 2))

    os.makedirs(OUT, exist_ok=True)
    for size, name in ((180, "icon-180.png"), (192, "icon-192.png"), (512, "icon-512.png")):
        canvas.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, name))
        print("wrote", name)


if __name__ == "__main__":
    build()
