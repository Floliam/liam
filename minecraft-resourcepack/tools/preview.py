"""Rendert ein Minecraft-Item-Modell (Quader-Elemente) als Vorschaubild, ohne Minecraft.

Benutzt dieselben Konventionen wie das Spiel: Element-Rotation um "origin", Flächen-UVs,
Display-Rotation als Euler-Quaternion wie com.mojang.math.Quaternion.

    python3 preview.py <pack-ordner> <ausgabe.png>
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

from build_model import corners

LIGHT = np.array([0.35, 0.85, 0.55])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def axis_rot(axis, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def euler_quat_matrix(x, y, z):
    """Wie new Quaternion(x, y, z, true) in Minecraft 1.18."""
    x, y, z = (math.radians(v) * 0.5 for v in (x, y, z))
    f, f1 = math.sin(x), math.cos(x)
    f2, f3 = math.sin(y), math.cos(y)
    f4, f5 = math.sin(z), math.cos(z)
    i = f * f3 * f5 + f1 * f2 * f4
    j = f1 * f2 * f5 - f * f3 * f4
    k = f * f2 * f5 + f1 * f3 * f4
    r = f1 * f3 * f5 - f * f2 * f4
    return np.array([
        [1 - 2 * (j * j + k * k), 2 * (i * j - k * r), 2 * (i * k + j * r)],
        [2 * (i * j + k * r), 1 - 2 * (i * i + k * k), 2 * (j * k - i * r)],
        [2 * (i * k - j * r), 2 * (j * k + i * r), 1 - 2 * (i * i + j * j)],
    ])


def render(model, tex, rotation, size=480, scale=1.0, bg=(0, 0, 0, 0), translation=(0, 0, 0)):
    tex = np.asarray(tex.convert("RGBA")).astype(np.float32)
    th, tw = tex.shape[:2]
    disp = euler_quat_matrix(*rotation)
    img = np.zeros((size, size, 4), np.float32)
    img[:] = bg
    zbuf = np.full((size, size), -1e9, np.float32)
    ppu = size / 16  # Pixel pro Modelleinheit
    trans = np.array(translation, float)
    ys, xs = np.mgrid[0:size, 0:size]
    sx = (xs + 0.5 - size / 2) / ppu
    sy = -(ys + 0.5 - size / 2) / ppu

    for el in model["elements"]:
        rot = el.get("rotation")
        for face, fd in el["faces"].items():
            pts = [np.array(c, float) for c in corners(face, el["from"], el["to"])]
            if rot:
                o = np.array(rot["origin"], float)
                m = axis_rot(rot["axis"], rot["angle"])
                pts = [m @ (q - o) + o for q in pts]
            pts = [disp @ ((q - 8.0) * scale) + trans for q in pts]
            tl, tr, bl = pts
            a, b = tr - tl, bl - tl
            n = np.cross(b, a)
            if np.linalg.norm(n) < 1e-9 or n[2] <= 0:
                continue  # Rückseite
            n = n / np.linalg.norm(n)
            shade = 0.55 + 0.45 * max(0.0, float(n @ (disp @ LIGHT)))
            det = a[0] * b[1] - a[1] * b[0]
            if abs(det) < 1e-9:
                continue
            dx, dy = sx - tl[0], sy - tl[1]
            s = (dx * b[1] - dy * b[0]) / det
            t = (a[0] * dy - a[1] * dx) / det
            mask = (s >= 0) & (s <= 1) & (t >= 0) & (t <= 1)
            if not mask.any():
                continue
            depth = tl[2] + s * a[2] + t * b[2]
            u1, v1, u2, v2 = fd["uv"]
            u = (u1 + s * (u2 - u1)) / 16 * tw
            v = (v1 + t * (v2 - v1)) / 16 * th
            ui = np.clip(u.astype(int), 0, tw - 1)
            vi = np.clip(v.astype(int), 0, th - 1)
            col = tex[vi, ui]
            mask &= (col[..., 3] > 25) & (depth > zbuf)
            zbuf[mask] = depth[mask]
            img[mask, :3] = col[mask, :3] * shade
            img[mask, 3] = 255
    return Image.fromarray(img.clip(0, 255).astype(np.uint8), "RGBA")


def sheet(pack_dir, out):
    with open(os.path.join(pack_dir, "assets/minecraft/models/item/totem_of_undying.json")) as fh:
        model = json.load(fh)
    tex = Image.open(os.path.join(pack_dir, "assets/minecraft/textures/item/audi_a3_totem.png"))
    gui = model["display"]["gui"]
    fixed = model["display"]["fixed"]
    views = [
        ("Inventar (so im Spiel)", gui["rotation"], gui["scale"][0], gui["translation"]),
        ("Totem-Animation (so im Spiel)", fixed["rotation"], fixed["scale"][0], fixed["translation"]),
        ("Front", [8, -90, 0], 1.9, (0, 0, 0)),
        ("Heck schräg", [18, 140, 0], 0.95, (0, 0, 0)),
    ]
    tile = 480
    canvas = Image.new("RGBA", (tile * 2, tile * 2), (0, 0, 0, 255))
    d = ImageDraw.Draw(canvas)
    for idx, (label, rot, sc, tr) in enumerate(views):
        ox, oy = (idx % 2) * tile, (idx // 2) * tile
        bg = (118, 150, 92, 255) if idx in (0, 3) else (62, 66, 78, 255)
        canvas.paste(Image.new("RGBA", (tile, tile), bg), (ox, oy))
        im = render(model, tex, rot, tile, sc, translation=tr)
        canvas.alpha_composite(im, (ox, oy))
        d.text((ox + 10, oy + 8), label, fill=(255, 255, 255, 255))
    canvas.convert("RGB").save(out)


if __name__ == "__main__":
    sheet(sys.argv[1], sys.argv[2])
