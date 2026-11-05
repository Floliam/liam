"""Baut das 3D-Totem: weißer Audi A3 Sportback S line (2017), silberne Felgen, schwarze Details.

Erzeugt das Minecraft-Item-Modell (Quader-Elemente) und eine Textur-Atlas-PNG, in der jede
sichtbare Fläche passend zu ihrer Größe bemalt ist.

    python3 build_model.py <pack-ordner>
"""
import json
import math
import os
import sys

from PIL import Image

PXU = 8  # Texturpixel pro Modelleinheit
ATLAS = 512
DETAIL_PXU = 20  # Front und Heck feiner, damit Ringe, Grill und Leuchten lesbar sind
TEXTURE = "minecraft:item/audi_a3_totem"
Y_OFF = 5.4  # Auto (Höhe 0..5,1) in die Mitte des 16er-Modellwürfels schieben

# ---------------------------------------------------------------- Farben
WHITE = (241, 243, 246)
WHITE_LOW = (229, 232, 237)
WHITE_HI = (255, 255, 255)
SEAM = (170, 176, 186)
SHADOW_LINE = (198, 203, 211)
BLACK = (20, 20, 24)
BLACK_HI = (33, 34, 40)
TRIM = (32, 33, 38)
GLASS = (26, 32, 44)
GLASS_HI = (70, 88, 110)
RED = (176, 14, 26)
RED_HI = (255, 78, 78)
LED = (226, 243, 255)
HEADLIGHT = (40, 48, 62)
SKIRT = (96, 101, 112)
PLATE = (236, 236, 236)
PLATE_BLUE = (24, 64, 176)
PLATE_TEXT = (40, 40, 44)
CHROME = (196, 201, 210)
TIRE = (24, 24, 28)
TIRE_WALL = (44, 45, 50)
RIM = (204, 209, 216)
RIM_HI = (232, 235, 240)
RIM_GAP = (52, 55, 63)
RING_FRONT = (150, 154, 163)  # Ringe auf dem schwarzen Grill: Anthrazit-Glanz, damit sie erkennbar bleiben

FRONT_X = 15.5
REAR_X = 0.5
CENTER_Z = 8.0
WHEEL_R = 1.25
WHEEL_Y = 1.25
REAR_WHEEL_X = 3.1
FRONT_WHEEL_X = 12.3


# ---------------------------------------------------------------- Malfunktionen
# Jede bekommt den absoluten Punkt P=(x,y,z) auf der (unrotierten) Fläche und s,t in [0,1]
# (s nach rechts, t nach unten, so wie man die Fläche von außen sieht).

BELT_Y = 3.1      # Oberkante Karosserie / Fensterlinie
ROOF_Y = 4.95     # Dachhöhe
NOSE_Y = 2.75     # Oberkante Frontschürze, darüber die schräge Haubenspitze


def side_body(p, s, t):
    x, y, _ = p
    between_wheels = 4.5 < x < 10.9
    if y < 1.0 and not between_wheels:
        return BLACK
    # S line Schweller: dunkle Kante mit Lichtlinie
    if between_wheels and y < 1.2:
        return WHITE_HI if y > 1.1 else SKIRT
    # Tornadolinie (scharfe Schulter-Lichtkante)
    if 2.68 <= y <= 2.78 and 0.9 < x < 15.0:
        return WHITE_HI
    if 2.6 <= y < 2.68 and 0.9 < x < 15.0:
        return SHADOW_LINE
    # Dynamiklinie unten, steigt nach hinten leicht an
    if 4.5 < x < 13.6 and abs(y - (1.5 + (13.6 - x) * 0.012)) < 0.04:
        return SHADOW_LINE
    # Scheinwerfer laufen um die Ecke
    if x > 14.4 and 2.2 + (15.5 - x) * 0.25 < y < NOSE_Y:
        return LED if abs(y - 2.55) < 0.05 else HEADLIGHT
    # S line Front-Lufteinlass mit senkrechten Lamellen
    if x > 14.7 and 1.05 < y < 1.95:
        return BLACK_HI if int(x * 10) % 3 == 0 else BLACK
    # Rückleuchten ziehen in die Seitenwand
    if x < 1.35 and 2.45 < y < 2.92:
        return RED_HI if abs(y - 2.66) < 0.04 else RED
    # Türfugen, Griffe, S line Plakette
    if 1.2 < y < BELT_Y and (abs(x - 6.4) < 0.06 or abs(x - 10.55) < 0.06 or abs(x - 4.62) < 0.06):
        return SEAM
    if 2.33 < y < 2.47 and (5.0 < x < 5.6 or 8.9 < x < 9.5):
        return SEAM if y < 2.42 else WHITE_HI
    if 11.0 < x < 11.5 and 2.08 < y < 2.2:
        return RED if x < 11.1 else TRIM
    # Radlauf-Kante leicht ausgestellt
    for cx in (REAR_WHEEL_X, FRONT_WHEEL_X):
        d = math.hypot(x - cx, y - WHEEL_Y)
        if 1.42 < d < 1.52 and y > WHEEL_Y:
            return SHADOW_LINE
    return WHITE if y > 1.9 else WHITE_LOW


def in_poly(u, v, pts):
    inside = False
    j = len(pts) - 1
    for i in range(len(pts)):
        (xi, yi), (xj, yj) = pts[i], pts[j]
        if (yi > v) != (yj > v) and u < (xj - xi) * (v - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def rings(u, v, cy, r, th):
    """0 = kein Ring, 1 = Ringkörper, 2 = Glanzkante am Ring."""
    best = 0
    for k in (-1.5, -0.5, 0.5, 1.5):
        d = abs(math.hypot(u - k * r * 1.62, v - cy) - r)
        if d < th / 2:
            return 1
        if d < th / 2 + 0.035:
            best = 2
    return best


PLATE_TEXT_STR = "KU*555BP"  # * = Landeswappen (Tirol) zwischen Bezirk und Nummer
PLATE_PX = (64, 14)
FONT = {
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "*": ["010", "111", "101", "111", "010"],
}
A_GLYPH = ["010", "101", "111", "101", "101"]
AT_RED = (200, 16, 46)


def make_plate():
    w, h = PLATE_PX
    img = Image.new("RGB", (w, h), PLATE)
    px = img.load()
    for x in range(w):
        px[x, 0] = px[x, h - 1] = PLATE_TEXT
        px[x, 1] = px[x, h - 2] = AT_RED  # rot-weiß-rote Randstreifen
    for y in range(h):
        px[0, y] = px[w - 1, y] = PLATE_TEXT
    for y in range(1, h - 1):  # EU-Feld mit "A"
        for x in range(1, 8):
            px[x, y] = PLATE_BLUE
    for (dx, dy) in ((3, 2), (5, 2), (2, 3), (6, 3), (3, 4), (5, 4)):
        px[dx, dy] = (255, 204, 0)
    for gy, row in enumerate(A_GLYPH):
        for gx, c in enumerate(row):
            if c == "1":
                px[3 + gx, 7 + gy] = (255, 255, 255)
    x = 10
    for ch in PLATE_TEXT_STR:
        glyph = FONT[ch]
        gy0 = 3 if ch != "*" else 4
        for gy, row in enumerate(glyph):
            for gx, c in enumerate(row):
                if c == "1":
                    px[x + gx, gy0 + gy] = AT_RED if ch == "*" else PLATE_TEXT
        x += len(glyph[0]) + 2
    return img


PLATE_IMG = make_plate()


def plate_paint(p, s, t):
    w, h = PLATE_PX
    return PLATE_IMG.getpixel((min(w - 1, int(s * w)), min(h - 1, int(t * h))))


def honeycomb(u, v):
    row = math.floor(v / 0.16)
    cu = (u / 0.22 + (row % 2) * 0.5) % 1.0
    cv = (v / 0.16) % 1.0
    return BLACK_HI if cu < 0.18 or cv < 0.18 else BLACK


# Singleframe: breites Sechseck, oben angeschrägte Ecken
GRILLE = [(-1.25, 2.62), (1.25, 2.62), (1.85, 2.15), (1.55, 1.0), (-1.55, 1.0), (-1.85, 2.15)]
GRILLE_IN = [(-1.18, 2.55), (1.18, 2.55), (1.76, 2.13), (1.49, 1.07), (-1.49, 1.07), (-1.76, 2.13)]


def front_face(p, s, t):
    _, y, z = p
    u = -(z - CENTER_Z)  # von vorne gesehen: links negativ
    au = abs(u)
    if y < 0.95:
        return BLACK
    if in_poly(u, y, GRILLE):
        if not in_poly(u, y, GRILLE_IN):
            return TRIM
        ring = rings(u, y, 2.3, 0.23, 0.07)
        if ring == 1:
            return BLACK
        if ring == 2:
            return RING_FRONT
        return honeycomb(u, y)
    # Matrix-LED-Scheinwerfer, unten zur Mitte hin angeschrägt
    if au > 1.95 and 2.2 + max(0.0, 2.6 - au) * 0.6 < y < NOSE_Y:
        if abs(y - 2.55) < 0.05 and au > 2.1:
            return LED if int(au * 10) % 4 != 0 else HEADLIGHT  # unterbrochenes LED-Tagfahrlicht
        if 2.32 < y < 2.46 and au > 2.3:
            return GLASS_HI if int(au * 6) % 2 else HEADLIGHT
        return HEADLIGHT
    # S line Lufteinlässe mit Lamellen
    if 1.05 < y < 1.95 and 2.05 < au < 3.1:
        if au < 2.12 or au > 3.03 or y < 1.12 or y > 1.88:
            return TRIM
        return BLACK_HI if abs(y - 1.5) < 0.04 else BLACK
    return WHITE


def rear_face(p, s, t):
    _, y, z = p
    u = z - CENTER_Z  # von hinten gesehen: links negativ
    au = abs(u)
    if y < 1.3:
        # S line Diffusor mit grauem Einsatz und zwei Endrohren
        for cu in (-2.5, -2.0):
            d = math.hypot((u - cu) / 0.22, (y - 1.0) / 0.12)
            if d < 1.0:
                return (60, 62, 68) if d < 0.55 else CHROME
        if 0.85 < y < 1.15 and au < 1.6:
            return (88, 92, 101) if int(u * 6) % 2 else (70, 73, 81)
        return BLACK
    # breite Rückleuchten mit LED-Bogen
    if 2.42 < y < 2.92 and au > 1.45 + (y - 2.42) * 0.3:
        if abs(y - 2.66) < 0.04 or (abs(y - 2.55) < 0.04 and au > 2.4):
            return RED_HI
        return RED
    if 1.38 < y < 1.48 and 2.6 < au < 3.1:
        return RED
    ring = rings(u, y, 2.42, 0.25, 0.07)
    if ring == 1:
        return BLACK
    if abs(y - 2.2) < 0.03 and au < 1.4:
        return SHADOW_LINE  # Heckklappen-Kante
    return WHITE if y > 1.9 else WHITE_LOW


def top_body(p, s, t):
    x, _, z = p
    if x > 11.0 and abs(abs(z - CENTER_Z) - 1.7) < 0.06:
        return SHADOW_LINE  # Haubenkanten
    return WHITE


def nose_top(p, s, t):
    _, _, z = p
    au = abs(z - CENTER_Z)
    # Scheinwerfer laufen von vorne auf die schräge Haubenspitze
    if au > 1.95 and s > 0.45 + (3.2 - au) * 0.12:
        return LED if abs(s - 0.8) < 0.05 else HEADLIGHT
    if abs(au - 1.7) < 0.06:
        return SHADOW_LINE
    return WHITE


def roof(p, s, t):
    x, _, z = p
    if abs(abs(z - CENTER_Z) - 2.55) < 0.06:
        return SHADOW_LINE
    return WHITE


# A3 Sportback: Dach läuft fast bis ans Heck und fällt erst am Ende leicht zum Spoiler ab,
# die Heckscheibe steht steil (22,5° aus der Senkrechten).
ROOF_BREAK_X = 2.3
ROOF_END = (1.5, ROOF_Y - 0.8 * 0.414)  # Dachende / Spoiler
TAILGATE_Y = 3.3  # Unterkante Heckscheibe


def roof_line(x):
    return ROOF_Y if x >= ROOF_BREAK_X else ROOF_Y - (ROOF_BREAK_X - x) * 0.414


def cabin_side(p, s, t):
    x, y, _ = p
    # Fensterlinie: oben sinkt sie nach hinten leicht, unten steigt sie an -> spitz zulaufend
    top = roof_line(x) - 0.16 - max(0.0, 5.0 - x) * 0.05
    bottom = BELT_Y + 0.23 + max(0.0, 4.6 - x) * 0.22
    rear_edge = 2.2 + (y - 3.4) * 0.9  # Hinterkante Dreiecksfenster, parallel zur Heckscheibe
    if y > top + 0.06 or y < bottom - 0.08 or x < rear_edge - 0.1:
        return WHITE  # breite D-Säule und Dachrahmen in Wagenfarbe
    if y > top or y < bottom or x < rear_edge or x > 9.55:
        return TRIM  # schwarze Fensterleisten (Black-Optik)
    if 3.85 < x < 3.97 or 6.25 < x < 6.6:
        return BLACK  # Steg zum Dreiecksfenster, B-Säule
    k = x - (y - 3.38) * 0.8
    if 4.6 < k < 4.9 or 7.6 < k < 7.8:
        return GLASS_HI
    return GLASS


def windshield(p, s, t):
    if t < 0.08 or s < 0.03 or s > 0.97:
        return TRIM
    if t > 0.9:
        return BLACK
    k = s + t * 0.5
    if 0.32 < k < 0.4 or 0.7 < k < 0.74:
        return GLASS_HI
    return GLASS


def hatch(p, s, t):
    if t < 0.06 or t > 0.94:
        return BLACK
    if s < 0.04 or s > 0.96:
        return TRIM
    k = s + t * 0.4
    if 0.3 < k < 0.36:
        return GLASS_HI
    return GLASS


def rim(p, s, t):
    du, dv = (s - 0.5) * 2, (t - 0.5) * 2
    r = math.hypot(du, dv) * WHEEL_R
    if r > WHEEL_R:
        return None
    if r > 0.93:
        return TIRE_WALL if abs(r - 1.1) < 0.03 else TIRE
    if r > 0.86:
        return RIM_HI  # Felgenhorn
    if r < 0.17:
        return BLACK  # Nabendeckel
    if r < 0.24:
        return RIM
    # 10 Speichen (5 Doppelspeichen), silber
    a = math.degrees(math.atan2(dv, du)) % 72
    if 8 < a < 22 or 26 < a < 40:
        return RIM_HI if r > 0.7 and (a < 10 or a > 38) else RIM
    return RIM_GAP


def solid(color):
    return lambda p, s, t: color


# ---------------------------------------------------------------- Geometrie
FACES = ("north", "south", "east", "west", "up", "down")


def corners(face, f, t):
    """Ecken (oben links, oben rechts, unten links) so wie Minecraft die Fläche texturiert."""
    x1, y1, z1 = f
    x2, y2, z2 = t
    return {
        "north": ((x2, y2, z1), (x1, y2, z1), (x2, y1, z1)),
        "south": ((x1, y2, z2), (x2, y2, z2), (x1, y1, z2)),
        "east": ((x2, y2, z2), (x2, y2, z1), (x2, y1, z2)),
        "west": ((x1, y2, z1), (x1, y2, z2), (x1, y1, z1)),
        "up": ((x1, y2, z1), (x2, y2, z1), (x1, y2, z2)),
        "down": ((x1, y1, z2), (x2, y1, z2), (x1, y1, z1)),
    }[face]


def element(name, f, t, paint, rotation=None, faces=FACES):
    return {"name": name, "from": f, "to": t, "paint": paint, "rotation": rotation, "faces": faces}


def body_paint(face, el):
    if face in ("north", "south"):
        return side_body
    if face == "east":
        return front_face if el["to"][0] >= 15.0 else solid(WHITE)
    if face == "west":
        return rear_face if el["from"][0] <= 0.6 else solid(WHITE)
    if face == "up":
        return top_body
    return solid(BLACK)


def build_elements():
    zl, zr = 4.8, 11.2
    els = []
    body = lambda n, f, t: els.append(element(n, f, t, body_paint))
    body("rear bumper", [0.5, 0.75, zl], [1.7, BELT_Y, zr])
    body("rear arch", [1.7, 2.65, zl - 0.08], [4.5, BELT_Y, zr + 0.08])
    body("doors", [4.5, 0.75, zl], [10.9, BELT_Y, zr])
    body("front arch", [10.9, 2.65, zl - 0.08], [13.7, BELT_Y, zr + 0.08])
    body("front bumper", [13.7, 0.75, zl], [15.5, NOSE_Y, zr])
    body("hood", [11.0, 3.0, 4.9], [14.3, 3.25, 11.1])
    # Schräge Haubenspitze: vorne auf Höhe der Schürze, hinten bündig mit der Haube
    def nose_paint(face, el):
        return {"up": nose_top, "north": side_body, "south": side_body}.get(face, solid(WHITE))

    els.append(element("nose", [14.2, 1.95, zl + 0.02], [15.5, NOSE_Y, zr - 0.02], nose_paint,
                       {"angle": -22.5, "axis": "z", "origin": [15.5, NOSE_Y, 8]}))

    for n, x1, x2 in (("rear tub", 1.7, 4.5), ("front tub", 10.9, 13.7)):
        els.append(element(n, [x1, 0.95, 5.9], [x2, 2.65, 10.1], lambda face, el: solid(BLACK)))

    def cabin_paint(face, el):
        return {"north": cabin_side, "south": cabin_side, "up": roof, "east": solid(GLASS)}.get(face, solid(WHITE))

    els.append(element("cabin", [ROOF_BREAK_X, BELT_Y, 5.2], [9.65, ROOF_Y, 10.8], cabin_paint))
    # Unter dem abfallenden Dachende: D-Säule
    els.append(element("cabin rear", [ROOF_END[0], BELT_Y, 5.2], [ROOF_BREAK_X, ROOF_END[1] - 0.04, 10.8], cabin_paint))
    roof_len = (ROOF_BREAK_X - ROOF_END[0]) / math.cos(math.radians(22.5))
    els.append(element("roof rear", [ROOF_BREAK_X - roof_len, ROOF_Y - 0.5, 5.3], [ROOF_BREAK_X, ROOF_Y, 10.7],
                       lambda face, el: roof if face == "up" else solid(WHITE),
                       {"angle": 22.5, "axis": "z", "origin": [ROOF_BREAK_X, ROOF_Y, 8]}))

    # Windschutzscheibe 45° geneigt, unten an der Haube, oben an der Dachkante
    ws_len = (ROOF_Y - 3.2) * math.sqrt(2)

    def windshield_paint(face, el):
        return {"east": windshield, "north": solid(GLASS), "south": solid(GLASS)}.get(face, solid(BLACK))

    els.append(element("windshield", [10.1, 3.2, 5.3], [11.4, 3.2 + ws_len, 10.7], windshield_paint,
                       {"angle": 45, "axis": "z", "origin": [11.4, 3.2, 8]}))

    # Steile Heckscheibe (22,5° aus der Senkrechten) vom Spoiler bis zur Heckklappe
    rw_h = ROOF_END[1] - TAILGATE_Y
    rw_x = ROOF_END[0] - rw_h * math.tan(math.radians(22.5))

    def hatch_paint(face, el):
        return {"west": hatch, "up": solid(BLACK)}.get(face, solid(WHITE))

    els.append(element("rear window", [rw_x, TAILGATE_Y, 5.3],
                       [rw_x + 0.55, TAILGATE_Y + rw_h / math.cos(math.radians(22.5)), 10.7],
                       hatch_paint, {"angle": -22.5, "axis": "z", "origin": [rw_x, TAILGATE_Y, 8]}))
    # Heckklappe unterhalb der Scheibe
    body("tailgate", [0.6, BELT_Y, 5.0], [1.7, TAILGATE_Y, 11.0])

    # Abstehender Dachspoiler mit dritter Bremsleuchte
    def spoiler_paint(face, el):
        if face == "west":
            return lambda p, s, t: RED if 0.42 < s < 0.58 and t > 0.55 else BLACK
        return solid(BLACK)

    els.append(element("roof spoiler", [ROOF_END[0] - 0.3, ROOF_END[1] - 0.12, 5.35],
                       [ROOF_END[0] + 0.25, ROOF_END[1] + 0.05, 10.65], spoiler_paint))

    # Haifischflossen-Antenne
    els.append(element("antenna", [2.6, ROOF_Y, 7.85], [3.4, ROOF_Y + 0.18, 8.15], lambda face, el: solid(BLACK)))
    els.append(element("antenna tip", [2.6, ROOF_Y + 0.18, 7.88], [3.0, ROOF_Y + 0.32, 8.12],
                       lambda face, el: solid(BLACK)))

    # Österreichische Kennzeichen als eigene, feiner aufgelöste Flächen
    els.append(element("plate front", [15.52, 1.12, 6.65], [15.52, 1.72, 9.35],
                       lambda face, el: plate_paint, None, ("east",)))
    els.append(element("plate rear", [0.48, 1.48, 6.65], [0.48, 2.08, 9.35],
                       lambda face, el: plate_paint, None, ("west",)))

    for n, z1, z2 in (("mirror left", 4.45, 5.2), ("mirror right", 10.8, 11.55)):
        els.append(element(n, [9.25, 3.3, z1], [9.85, 3.75, z2], lambda face, el: solid(BLACK)))

    a = WHEEL_R * math.tan(math.radians(22.5))
    for side, z1, z2, zrim, rim_face in (("left", 4.85, 5.9, 4.84, "north"), ("right", 10.1, 11.15, 11.16, "south")):
        for axle, cx in (("rear", REAR_WHEEL_X), ("front", FRONT_WHEEL_X)):
            origin = [cx, WHEEL_Y, (z1 + z2) / 2]
            for i, (hx, hy) in enumerate(((WHEEL_R, a), (a, WHEEL_R), (WHEEL_R, a), (a, WHEEL_R))):
                rot = {"angle": 45, "axis": "z", "origin": origin} if i >= 2 else None
                els.append(element(f"tire {axle} {side} {i}", [cx - hx, WHEEL_Y - hy, z1], [cx + hx, WHEEL_Y + hy, z2],
                                   lambda face, el: solid(TIRE), rot))
            els.append(element(f"rim {axle} {side}", [cx - WHEEL_R, 0.0, zrim], [cx + WHEEL_R, 2 * WHEEL_R, zrim],
                               lambda face, el: rim, None, (rim_face,)))
    return els



def face_size(face, f, t):
    dx, dy, dz = (t[i] - f[i] for i in range(3))
    return {"north": (dx, dy), "south": (dx, dy), "east": (dz, dy), "west": (dz, dy), "up": (dx, dz), "down": (dx, dz)}[face]


# ---------------------------------------------------------------- Atlas
class Packer:
    def __init__(self, size):
        self.size = size
        self.x = self.y = self.row = 0

    def alloc(self, w, h):
        if self.x + w > self.size:
            self.x, self.y, self.row = 0, self.y + self.row + 1, 0
        if self.y + h > self.size:
            raise RuntimeError("Atlas zu klein")
        pos = (self.x, self.y)
        self.x += w + 1
        self.row = max(self.row, h)
        return pos


def paint_face(paint, face, el, w, h):
    tl, tr, bl = (list(c) for c in corners(face, el["from"], el["to"]))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for j in range(h):
        t = (j + 0.5) / h
        for i in range(w):
            s = (i + 0.5) / w
            p = tuple(tl[k] + s * (tr[k] - tl[k]) + t * (bl[k] - tl[k]) for k in range(3))
            c = paint(p, s, t)
            if c is not None:
                px[i, j] = c + (255,)
    return img


def build(pack_dir):
    els = build_elements()
    atlas = Image.new("RGBA", (ATLAS, ATLAS), (0, 0, 0, 0))
    packer = Packer(ATLAS)
    solid_cache = {}
    model_elements = []

    for el in els:
        faces = {}
        for face in el["faces"]:
            paint = el["paint"](face, el)
            w_u, h_u = face_size(face, el["from"], el["to"])
            probe = paint((0, 0, 0), 0.5, 0.5)
            is_solid = paint.__name__ == "<lambda>" and paint((1, 1, 1), 0.1, 0.9) == probe
            if is_solid:
                if probe not in solid_cache:
                    x, y = packer.alloc(4, 4)
                    atlas.paste(Image.new("RGBA", (4, 4), probe + (255,)), (x, y))
                    solid_cache[probe] = (x + 1, y + 1, x + 3, y + 3)
                region = solid_cache[probe]
            else:
                pxu = DETAIL_PXU if paint in (front_face, rear_face, nose_top) else PXU
                w, h = max(1, round(w_u * pxu)), max(1, round(h_u * pxu))
                if paint is plate_paint:
                    w, h = PLATE_PX
                x, y = packer.alloc(w, h)
                atlas.paste(paint_face(paint, face, el, w, h), (x, y))
                region = (x, y, x + w, y + h)
            uv = [round(v * 16 / ATLAS, 4) for v in region]
            faces[face] = {"uv": uv, "texture": "#car"}
        shift = lambda v: [round(v[0], 4), round(v[1] + Y_OFF, 4), round(v[2], 4)]
        me = {"name": el["name"], "from": shift(el["from"]), "to": shift(el["to"]), "faces": faces}
        if el["rotation"]:
            me["rotation"] = dict(el["rotation"], origin=shift(el["rotation"]["origin"]))
        model_elements.append(me)

    model = {
        "credit": "Weißer Audi A3 Sportback S line Totem",
        "texture_size": [ATLAS, ATLAS],
        "textures": {"car": TEXTURE, "particle": TEXTURE},
        "elements": model_elements,
        "display": DISPLAY,
    }
    tex_path = os.path.join(pack_dir, "assets/minecraft/textures/item/audi_a3_totem.png")
    model_path = os.path.join(pack_dir, "assets/minecraft/models/item/totem_of_undying.json")
    os.makedirs(os.path.dirname(tex_path), exist_ok=True)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    atlas.save(tex_path)
    with open(model_path, "w") as fh:
        json.dump(model, fh, indent=1)
    return model, atlas


# Schräg von vorne (Front rechts, linke Fahrzeugseite sichtbar), leicht von oben
DISPLAY = {
    "gui": {"rotation": [22, -38, 0], "translation": [0, 0, 0], "scale": [0.8, 0.8, 0.8]},
    "fixed": {"rotation": [12, -32, 0], "translation": [0, 0, 0], "scale": [0.85, 0.85, 0.85]},
    "ground": {"rotation": [0, -38, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]},
    "head": {"rotation": [0, -90, 0], "translation": [0, 3, 0], "scale": [0.8, 0.8, 0.8]},
    "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.38, 0.38, 0.38]},
    # Waagrecht in der Hand, Front mit Kennzeichen schräg zur Kamera (mit Perspektive nachgerechnet)
    "firstperson_righthand": {"rotation": [-10, -160, 10], "translation": [-1, 3.5, -1], "scale": [0.62, 0.62, 0.62]},
    "firstperson_lefthand": {"rotation": [-10, -20, 10], "translation": [1, 3.5, -1], "scale": [0.62, 0.62, 0.62]},
}

if __name__ == "__main__":
    build(sys.argv[1])
