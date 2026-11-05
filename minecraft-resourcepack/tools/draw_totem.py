"""Zeichnet die Totem-Textur (weißer Audi A3 Sportback S line 2017, Seitenansicht).

Gezeichnet wird in einem 64x64-Koordinatensystem mit Überabtastung, danach verkleinert
und die Kanten hart gemacht, damit es wie saubere Pixel-Art aussieht.

    python3 draw_totem.py <ausgabe.png> [größe]
"""
import math
import sys

from PIL import Image, ImageDraw, ImageFilter

SUPER = 8
Y_SHIFT = -1.5  # Auto vertikal mittig setzen

BODY = (244, 245, 247)
BODY_LOWER = (222, 226, 232)
BODY_SHADE = (196, 201, 210)
SHOULDER = (255, 255, 255)
SEAM = (178, 184, 194)
OUTLINE = (52, 56, 64)
GLASS = (32, 38, 50)
GLASS_HI = (96, 116, 138)
BLACK = (24, 24, 28)
TRIM = (58, 60, 66)
TAIL = (186, 18, 30)
TAIL_HI = (255, 82, 82)
LED = (215, 238, 255)
TIRE = (26, 26, 30)
RIM = (188, 193, 201)
RIM_DARK = (92, 97, 108)
HUB = (60, 62, 68)

REAR_WHEEL = (14.5, 40.5)
FRONT_WHEEL = (49.0, 40.5)


def draw(size):
    scale = size / 64 * SUPER
    canvas = size * SUPER
    img = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def p(x, y):
        return (x * scale, (y + Y_SHIFT) * scale)

    def poly(points, color):
        d.polygon([p(x, y) for x, y in points], fill=color + (255,))

    def rect(x0, y0, x1, y1, color):
        d.rectangle([p(x0, y0), p(x1, y1)], fill=color + (255,))

    def circle(cx, cy, r, color):
        (x, y) = p(cx, cy)
        d.ellipse([x - r * scale, y - r * scale, x + r * scale, y + r * scale], fill=color + (255,))

    def line(points, color, width):
        d.line([p(x, y) for x, y in points], fill=color + (255,), width=max(1, round(width * scale)))

    # Karosserie (Front rechts)
    body = [
        (4.0, 41.0), (3.4, 36.0), (3.8, 31.0), (5.0, 28.6), (7.6, 21.6), (11.5, 20.4),
        (30.0, 19.6), (35.6, 20.4), (45.0, 28.2), (55.0, 30.0), (59.6, 31.6),
        (61.2, 35.0), (60.8, 40.8), (56.0, 41.4), (8.0, 41.4),
    ]
    poly(body, BODY)
    # untere Flanke etwas dunkler, Lichtkante (Tornadolinie) darüber
    poly([(3.4, 34.5), (61.0, 34.5), (60.8, 40.8), (56.0, 41.4), (8.0, 41.4), (4.0, 41.0)], BODY_LOWER)
    line([(5.0, 30.6), (56.0, 31.2)], SHOULDER, 0.9)
    line([(5.0, 31.6), (56.0, 32.2)], SEAM, 0.5)
    # S line Seitenschweller
    poly([(19.5, 38.8), (42.0, 38.8), (42.0, 40.6), (19.5, 40.6)], BODY_SHADE)
    line([(21.0, 39.0), (41.0, 39.0)], SHOULDER, 0.4)

    # Fenster
    poly([(9.6, 28.0), (11.6, 22.4), (30.0, 21.5), (34.6, 22.1), (42.2, 28.0)], GLASS)
    # Spiegelung
    poly([(28.0, 21.7), (31.5, 21.6), (26.0, 27.8), (22.5, 27.8)], GLASS_HI)
    poly([(36.0, 23.6), (37.2, 24.6), (34.5, 27.8), (33.0, 27.8)], GLASS_HI)
    # C-Säule in Wagenfarbe, B-Säule schwarz, Fensterleiste
    poly([(12.4, 22.4), (15.4, 22.2), (14.6, 28.0), (11.6, 28.0)], BODY)
    poly([(25.2, 21.7), (26.6, 21.7), (26.6, 28.0), (25.2, 28.0)], BLACK)
    line([(9.6, 28.2), (42.2, 28.2)], TRIM, 0.6)

    # Dachspoiler
    poly([(7.2, 21.4), (11.5, 20.0), (13.0, 20.4), (8.4, 22.2)], TRIM)

    # Spiegel
    poly([(40.6, 26.4), (43.4, 26.6), (43.8, 28.6), (40.8, 28.6)], BODY_SHADE)
    line([(40.8, 28.6), (43.8, 28.6)], TRIM, 0.5)

    # Türfugen und Griffe
    line([(26.4, 28.6), (26.0, 40.0)], SEAM, 0.4)
    line([(40.0, 28.6), (40.4, 39.0)], SEAM, 0.4)
    line([(20.0, 31.9), (22.6, 31.9)], SEAM, 0.7)
    line([(33.0, 32.1), (35.6, 32.1)], SEAM, 0.7)

    # Rückleuchte
    poly([(3.8, 29.6), (9.2, 30.0), (8.8, 31.8), (3.6, 31.6)], TAIL)
    line([(4.2, 30.2), (8.6, 30.4)], TAIL_HI, 0.5)
    # Diffusor hinten
    poly([(3.6, 38.6), (9.0, 38.6), (8.6, 41.2), (4.0, 41.0)], BLACK)

    # Matrix-LED-Scheinwerfer mit Tagfahrlicht-Strich
    poly([(53.6, 31.2), (59.4, 32.0), (60.2, 34.0), (54.6, 33.2)], GLASS)
    line([(54.0, 31.6), (59.6, 32.6)], LED, 0.7)
    # Singleframe-Grill und S line Lufteinlass
    poly([(60.0, 34.2), (61.4, 34.6), (61.2, 39.0), (60.2, 39.4)], BLACK)
    poly([(56.0, 37.4), (60.2, 37.4), (60.0, 40.6), (56.0, 40.8)], BLACK)

    # Radläufe und Räder
    for cx, cy in (REAR_WHEEL, FRONT_WHEEL):
        (x, y) = p(cx, cy)
        r = 7.5 * scale
        d.pieslice([x - r, y - r, x + r, y + r], 180, 360, fill=TRIM + (255,))
        d.rectangle([x - r, y - 0.2 * scale, x + r, y + 0.8 * scale], fill=TRIM + (255,))
        circle(cx, cy, 6.5, TIRE)
        circle(cx, cy, 4.8, RIM_DARK)
        # 5 Doppelspeichen
        for i in range(5):
            a = math.radians(i * 72 - 90)
            for off in (-0.16, 0.16):
                line([(cx, cy), (cx + math.cos(a + off) * 4.6, cy + math.sin(a + off) * 4.6)], RIM, 0.9)
        circle(cx, cy, 1.4, RIM)
        circle(cx, cy, 0.8, HUB)

    small = img.resize((size, size), Image.Resampling.BOX)

    # Kanten hart machen und eine dunkle Kontur ergänzen, damit das Auto vor jedem Hintergrund lesbar ist
    alpha = small.getchannel("A").point(lambda a: 255 if a >= 110 else 0)
    outline = alpha.filter(ImageFilter.MaxFilter(3))
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(Image.new("RGBA", (size, size), OUTLINE + (255,)), mask=outline)
    solid = small.copy()
    solid.putalpha(255)
    out.paste(solid, mask=alpha)
    return out


if __name__ == "__main__":
    target = sys.argv[1]
    size = int(sys.argv[2]) if len(sys.argv) > 2 else 64
    draw(size).save(target)
