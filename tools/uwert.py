#!/usr/bin/env python3
"""U-Wert-Rechner für mehrschichtige Bauteile.

Berechnet nach ÖNORM EN ISO 6946 (homogene Schichten):

    R_T = R_si + Σ d/λ + R_se        U = 1 / R_T

dazu den stationären Temperaturverlauf durch den Aufbau, die Prüfung gegen
U_max (OIB-Richtlinie 6, Tabelle 3) und den Temperaturfaktor f_Rsi gegen
Schimmelbildung (Grenzwert 0,71 nach ÖNORM B 8110-2).

Erzeugt einen Textbericht und eine SVG-Grafik: maßstäblicher Schnitt durch
den Aufbau mit eingezeichneter Temperaturkurve.

Nur Standardbibliothek. Werte und Typen entsprechen src/werkbank.html.

Aufruf:
    python3 tools/uwert.py                      # Beispielwand, schreibt uwert.svg
    python3 tools/uwert.py aufbau.json -o wand.svg
    python3 tools/uwert.py --materialien        # λ-Tabelle anzeigen

Format der JSON-Datei:
    {"name": "Außenwand", "typ": "awAussen",
     "schichten": [{"material": "Innenputz Kalk-Gips", "d_cm": 1.5},
                   {"name": "Sonderdämmung", "d_cm": 10, "lambda": 0.031}]}
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path

# Bauteiltypen: Bezeichnung, U_max [W/m²K], R_si, R_se [m²K/W]  (wie werkbank.html)
TYPEN = {
    "awAussen": ("Wand gegen Außenluft", 0.35, 0.13, 0.04),
    "awDach":   ("Wand gegen unbeheizten Dachraum", 0.35, 0.13, 0.04),
    "awUnbeh":  ("Wand gegen unbeheizt / Garage", 0.60, 0.13, 0.04),
    "awErd":    ("Wand erdberührt", 0.40, 0.17, 0.00),
    "awNachb":  ("Wand gegen Nachbargrundstück", 0.50, 0.13, 0.04),
    "awTrenn":  ("Trennwand zw. Nutzungseinheiten", 1.30, 0.13, 0.13),
    "dcAussen": ("Decke / Dachschräge gegen Außenluft", 0.20, 0.10, 0.04),
    "dcUnbeh":  ("Decke gegen unbeheizten Dachraum", 0.40, 0.10, 0.04),
    "dcGarage": ("Decke gegen Garage", 0.30, 0.17, 0.04),
    "dcTrenn":  ("Decke zw. Nutzungseinheiten", 0.90, 0.10, 0.10),
    "bdErd":    ("Boden erdberührt", 0.40, 0.17, 0.00),
    "bdAussen": ("Decke gegen Außenluft (abwärts)", 0.20, 0.17, 0.04),
}

# Rechenwerte λ [W/mK] — ÖNORM B 8110-7 / Herstellerangaben (wie werkbank.html)
MATERIALIEN = {
    "Stahlbeton": 2.30,
    "Vollziegel": 0.80,
    "Hochlochziegel ungefüllt": 0.45,
    "Hochlochziegel gefüllt": 0.09,
    "Kalksandstein": 1.10,
    "Porenbeton": 0.12,
    "Nadelholz": 0.13,
    "Innenputz Kalk-Gips": 0.70,
    "Außenputz Zement": 0.80,
    "Zementestrich": 1.40,
    "Gipskartonplatte": 0.25,
    "EPS-Fassadendämmung": 0.035,
    "Mineralwolle": 0.035,
    "XPS Perimeter": 0.035,
    "PUR / PIR": 0.024,
    "Holzfaserdämmplatte": 0.044,
    "Zellulose-Einblasdämmung": 0.041,
}

F_RSI_MIN = 0.71  # ÖNORM B 8110-2, Vermeidung von Schimmelbildung

BEISPIEL = {
    "name": "Außenwand EFH Tirol",
    "typ": "awAussen",
    "schichten": [
        {"material": "Innenputz Kalk-Gips", "d_cm": 1.5},
        {"material": "Hochlochziegel ungefüllt", "d_cm": 25},
        {"material": "EPS-Fassadendämmung", "d_cm": 18},
        {"material": "Außenputz Zement", "d_cm": 1.0},
    ],
}


@dataclass
class Schicht:
    name: str
    d: float    # Dicke [m]
    lam: float  # λ [W/mK]

    @property
    def r(self) -> float:
        return self.d / self.lam


@dataclass
class Ergebnis:
    name: str
    typ: str
    schichten: list[Schicht]
    rsi: float
    rse: float
    theta_i: float
    theta_e: float

    @property
    def sum_r(self) -> float:
        return sum(s.r for s in self.schichten)

    @property
    def rt(self) -> float:
        return self.rsi + self.sum_r + self.rse

    @property
    def u(self) -> float:
        return 1.0 / self.rt

    @property
    def umax(self) -> float:
        return TYPEN[self.typ][1]

    @property
    def f_rsi(self) -> float:
        return 1.0 - self.rsi * self.u

    @property
    def dicke(self) -> float:
        return sum(s.d for s in self.schichten)

    def temperaturen(self) -> list[float]:
        """Temperatur an jeder Schichtgrenze, innen → außen (n+1 Werte).

        Erster Wert ist die innere Oberfläche θ_si, letzter die äußere θ_se.
        """
        q = self.u * (self.theta_i - self.theta_e)  # Wärmestromdichte [W/m²]
        t = [self.theta_i - q * self.rsi]
        for s in self.schichten:
            t.append(t[-1] - q * s.r)
        return t


def lade_aufbau(daten: dict, theta_i: float, theta_e: float) -> Ergebnis:
    typ = daten.get("typ", "awAussen")
    if typ not in TYPEN:
        raise ValueError(f"Unbekannter Bauteiltyp '{typ}'. Erlaubt: {', '.join(TYPEN)}")
    roh = daten.get("schichten") or []
    if not roh:
        raise ValueError("Der Aufbau enthält keine Schichten.")
    schichten = []
    for i, s in enumerate(roh, 1):
        name = s.get("name") or s.get("material")
        if not name:
            raise ValueError(f"Schicht {i}: 'material' oder 'name' fehlt.")
        lam = s.get("lambda")
        if lam is None:
            if s.get("material") not in MATERIALIEN:
                raise ValueError(
                    f"Schicht {i}: Material '{s.get('material')}' unbekannt und kein 'lambda' angegeben."
                )
            lam = MATERIALIEN[s["material"]]
        d_cm = s.get("d_cm")
        if d_cm is None or float(d_cm) <= 0:
            raise ValueError(f"Schicht {i} ({name}): 'd_cm' muss > 0 sein.")
        if float(lam) <= 0:
            raise ValueError(f"Schicht {i} ({name}): λ muss > 0 sein.")
        schichten.append(Schicht(name, float(d_cm) / 100.0, float(lam)))
    _, _, rsi, rse = TYPEN[typ]
    return Ergebnis(daten.get("name", "Bauteil"), typ, schichten, rsi, rse, theta_i, theta_e)


def zahl(x: float, n: int) -> str:
    """Österreichische Schreibweise: Dezimalkomma."""
    return f"{x:.{n}f}".replace(".", ",")


def bericht(e: Ergebnis) -> str:
    typname, umax, _, _ = TYPEN[e.typ]
    temps = e.temperaturen()
    z = []
    z.append(f"{e.name}  —  {typname}")
    z.append("=" * 72)
    z.append(f"{'Schicht':<28}{'d [cm]':>8}{'λ [W/mK]':>10}{'R [m²K/W]':>11}{'θ außen [°C]':>14}")
    z.append("-" * 72)
    z.append(f"{'R_si (innen)':<28}{'':>8}{'':>10}{zahl(e.rsi, 3):>11}{zahl(temps[0], 1):>14}")
    for s, t in zip(e.schichten, temps[1:]):
        z.append(f"{s.name[:27]:<28}{zahl(s.d * 100, 1):>8}{zahl(s.lam, 3):>10}{zahl(s.r, 3):>11}{zahl(t, 1):>14}")
    z.append(f"{'R_se (außen)':<28}{'':>8}{'':>10}{zahl(e.rse, 3):>11}{zahl(e.theta_e, 1):>14}")
    z.append("-" * 72)
    z.append(f"{'Gesamtdicke':<28}{zahl(e.dicke * 100, 1):>8}")
    z.append("")
    z.append(f"R_T = {zahl(e.rsi, 2)} + {zahl(e.sum_r, 3)} + {zahl(e.rse, 2)} = {zahl(e.rt, 3)} m²K/W")
    z.append(f"U   = 1 / R_T = {zahl(e.u, 3)} W/m²K")
    z.append("")
    ok_u = e.u <= umax
    ok_f = e.f_rsi >= F_RSI_MIN
    z.append(f"U_max (OIB RL 6)     {zahl(umax, 2)} W/m²K   → {'erfüllt' if ok_u else 'NICHT erfüllt'}")
    z.append(f"f_Rsi = 1 − R_si·U   {zahl(e.f_rsi, 3)}  ≥ {zahl(F_RSI_MIN, 2)}  → {'erfüllt' if ok_f else 'NICHT erfüllt'}")
    z.append(f"θ_si bei θ_i = {zahl(e.theta_i, 0)} °C / θ_e = {zahl(e.theta_e, 0)} °C:  {zahl(temps[0], 1)} °C")
    return "\n".join(z)


# Farben je Materialgruppe (Dämmung gelb, Mauerwerk rot, Putz grau, Holz braun, Beton grau-blau)
def farbe(name: str, lam: float) -> str:
    n = name.lower()
    if lam <= 0.06:
        return "#f4d35e"
    if "holz" in n:
        return "#c08552"
    if "putz" in n or "gips" in n or "estrich" in n:
        return "#d9d4cc"
    if "beton" in n or "kalksand" in n:
        return "#9aa5b1"
    return "#c8553d"


def svg(e: Ergebnis) -> str:
    B, H = 760, 460
    ml, mr, mt, mb = 70, 70, 50, 150  # Ränder
    w, h = B - ml - mr, H - mt - mb
    sx = w / e.dicke
    temps = e.temperaturen()
    tlo, thi = min(e.theta_e, *temps), max(e.theta_i, *temps)
    pad = 0.15 * (thi - tlo) + 0.5
    tmin, tmax = tlo - pad, thi + pad

    def ty(t: float) -> float:
        return mt + h * (tmax - t) / (tmax - tmin)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{B}" height="{H}" viewBox="0 0 {B} {H}" '
         'font-family="Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{B}" height="{H}" fill="#ffffff"/>',
         f'<text x="{ml}" y="28" font-size="16" font-weight="bold">{escape(e.name)} — '
         f'U = {zahl(e.u, 3)} W/m²K</text>']

    # Schichten
    x = ml
    grenzen = [x]
    for i, s in enumerate(e.schichten):
        bw = s.d * sx
        o.append(f'<rect x="{x:.2f}" y="{mt}" width="{bw:.2f}" height="{h}" fill="{farbe(s.name, s.lam)}" '
                 'stroke="#333" stroke-width="1"/>')
        # Beschriftung unter dem Schnitt, gestaffelt gegen Überlappung schmaler Schichten
        cx = x + bw / 2
        ly = mt + h + 20 + (i % 2) * 34
        o.append(f'<line x1="{cx:.2f}" y1="{mt + h}" x2="{cx:.2f}" y2="{ly - 12}" stroke="#666"/>')
        o.append(f'<text x="{cx:.2f}" y="{ly}" text-anchor="middle">{escape(s.name)}</text>')
        o.append(f'<text x="{cx:.2f}" y="{ly + 14}" text-anchor="middle" fill="#555">'
                 f'{zahl(s.d * 100, 1)} cm · λ {zahl(s.lam, 3)}</text>')
        x += bw
        grenzen.append(x)

    # Temperaturkurve: Luft innen → Oberfläche → Schichtgrenzen → Luft außen
    pts = [(ml - 50, ty(e.theta_i)), (ml, ty(temps[0]))]
    pts += [(gx, ty(t)) for gx, t in zip(grenzen[1:], temps[1:])]
    pts.append((ml + w + 50, ty(e.theta_e)))
    o.append('<polyline fill="none" stroke="#1f5fa8" stroke-width="2.5" points="'
             + " ".join(f"{px:.2f},{py:.2f}" for px, py in pts) + '"/>')
    # Beschriften nur, wo Platz ist: Oberflächen immer, Schichtgrenzen ab 48 px Abstand
    n = len(grenzen) - 1
    beschr = [0]
    for i in range(1, n):
        if grenzen[i] - grenzen[beschr[-1]] >= 48 and grenzen[n] - grenzen[i] >= 48:
            beschr.append(i)
    beschr.append(n)
    for i, (gx, t) in enumerate(zip(grenzen, temps)):
        o.append(f'<circle cx="{gx:.2f}" cy="{ty(t):.2f}" r="3.5" fill="#1f5fa8"/>')
        if i in beschr:
            anker, dx = ("end", -6) if i == n else ("start", 6)
            o.append(f'<text x="{gx + dx:.2f}" y="{ty(t) - 8:.2f}" text-anchor="{anker}" fill="#1f5fa8" stroke="#fff" stroke-width="3" paint-order="stroke" '
                     f'font-size="11">{"θ_si " if i == 0 else "θ_se " if i == n else ""}{zahl(t, 1)} °C</text>')

    o.append(f'<text x="{ml - 50}" y="{ty(e.theta_i) + 20:.2f}" fill="#1f5fa8">innen {zahl(e.theta_i, 0)} °C</text>')
    o.append(f'<text x="{ml + w + 50}" y="{ty(e.theta_e) + 20:.2f}" text-anchor="end" fill="#1f5fa8">'
             f'außen {zahl(e.theta_e, 0)} °C</text>')

    ok = e.u <= e.umax and e.f_rsi >= F_RSI_MIN
    o.append(f'<text x="{ml}" y="{H - 14}" fill="{"#2e7d32" if ok else "#c62828"}">'
             f'U_max {zahl(e.umax, 2)} · f_Rsi {zahl(e.f_rsi, 3)} (min. {zahl(F_RSI_MIN, 2)}) · '
             f'R_T {zahl(e.rt, 3)} m²K/W · Dicke {zahl(e.dicke * 100, 1)} cm — '
             f'{"Anforderungen erfüllt" if ok else "Anforderung nicht erfüllt"}</text>')
    o.append("</svg>")
    return "\n".join(o)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="U-Wert, Temperaturverlauf und SVG-Schnitt für Bauteilaufbauten.")
    p.add_argument("aufbau", nargs="?", help="JSON-Datei mit dem Aufbau (ohne Angabe: Beispielwand)")
    p.add_argument("-o", "--svg", default="uwert.svg", help="Ausgabedatei der Grafik (Standard: uwert.svg)")
    p.add_argument("--ti", type=float, default=20.0, help="Innentemperatur θ_i [°C] (Standard 20)")
    p.add_argument("--te", type=float, default=-10.0, help="Außentemperatur θ_e [°C] (Standard −10)")
    p.add_argument("--materialien", action="store_true", help="λ-Tabelle und Bauteiltypen anzeigen")
    a = p.parse_args(argv)

    if a.materialien:
        print("Materialien (λ in W/mK):")
        for n, l in MATERIALIEN.items():
            print(f"  {n:<28}{zahl(l, 3):>7}")
        print("\nBauteiltypen (U_max · R_si · R_se):")
        for k, (n, um, ri, re) in TYPEN.items():
            print(f"  {k:<10}{n:<38}{zahl(um, 2):>6}{zahl(ri, 2):>6}{zahl(re, 2):>6}")
        return 0

    try:
        daten = json.loads(Path(a.aufbau).read_text(encoding="utf-8")) if a.aufbau else BEISPIEL
        e = lade_aufbau(daten, a.ti, a.te)
    except (OSError, json.JSONDecodeError, ValueError) as err:
        print(f"Fehler: {err}", file=sys.stderr)
        return 1

    print(bericht(e))
    Path(a.svg).write_text(svg(e), encoding="utf-8")
    print(f"\nGrafik geschrieben: {a.svg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
