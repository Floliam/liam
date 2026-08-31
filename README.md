# Energieausweis-Werkbank

Berechnung des Energieausweises für beliebige Gebäude nach **OIB-Richtlinie 6** und
**ÖNORM B 8110-6** — mit vollständigem Rechenweg, Nachweisprüfung und druckbaren
Ausweis-Blättern. Eine einzelne HTML-Seite, ohne Installation, ohne Server, ohne
externe Bibliotheken.

**Öffnen:** https://floliam.github.io/liam/

## Was sie rechnet

Eingabe sind Geometrie, Bauteile, Fenster, Lüftung und Wärmeerzeuger. Ausgabe ist die
vollständige Kennzahlen-Kaskade:

```
U je Bauteil  →  L_T, L_V  →  Q_T, Q_V, Q_i, Q_s  →  η  →  HWB
                                                          ↓
                              HWB → HEB → EEB → PEB / CO₂ → Effizienzklasse
```

Dazu der Nachweis gegen alle fünf Anforderungssätze (RL 6:2023 Weg A und B,
RL 6:2025 Nachweisweg 1 und 2, NW 1 ab 2030) und gegen die U<sub>max</sub>-Tabelle
je Bauteil.

Drei Punkte, die über eine Formelsammlung hinausgehen:

- **Die Hüllfläche A wird nicht eingegeben**, sondern aus der Bauteil- und Fensterliste
  gebildet. A kann damit nicht von der Bauteilliste abweichen — der häufigste
  Geometriefehler ist konstruktiv ausgeschlossen.
- **Die Bilanz läuft dreimal:** im Standortklima für die Effizienzklasse, im
  Referenzklima als Vergleich, und im Referenzklima *ohne* Wärmerückgewinnung als
  Nachweisgröße HWB<sub>Ref,RK</sub>.
- **Primärenergie und CO₂ werden je Energieträger getrennt bewertet.** Hilfsenergie ist
  immer Strom, auch wenn der Kessel mit Öl läuft.

Der Tab *Rechenweg* zeigt jeden Schritt mit eingesetzten Zahlen, für alle drei
Durchgänge.

## Grenzen

**Vorbemessung, kein Nachweis.** Für die Einreichung gilt der Ausweis aus einem
registrierten Programm, erstellt von einer befugten Person nach Inaugenscheinnahme
des Gebäudes.

- Gerechnet wird die **Jahresbilanz**, nicht das Monatsverfahren. Zertifizierte Software
  rechnet monatsweise und kommt auf leicht andere Zahlen — bei sehr gut gedämmten
  Gebäuden (γ > 1) auf deutlich andere.
- Die **Klimadaten** sind editierbare Richtwerte für den Alpennordrand, keine
  nachgeschlagenen Normwerte. Verbindlich ist die ÖNORM B 8110-5.
- Die **Nutzungsprofile** der Kategorien 2 bis 12 sind grobe Richtwerte. Bei
  Nicht-Wohngebäuden fehlen Kühl-, Beleuchtungs- und Betriebsstrombedarf.

Alle Annahmen stehen im Tab *Referenz* offen und sind in der Eingabe überschreibbar.

## Verifikation

Das durchgerechnete Einfamilienhaus in Tirol ist als Vorlage hinterlegt und
reproduziert die unabhängig gerechneten Werte exakt:

| Größe | Werkbank | Referenz |
|---|---:|---:|
| Hüllfläche A | 361,6 m² | 361,6 m² |
| ℓ<sub>c</sub> | 1,239 m | 1,24 m |
| L<sub>T</sub> | 92,40 W/K | 92,40 W/K |
| γ | 0,387 | 0,387 |
| η | 0,996 | 0,996 |
| Q<sub>h</sub> | 7.288 kWh/a | 7.288 kWh/a |
| HWB<sub>SK</sub> | 45,6 kWh/m²a | 45,6 kWh/m²a |
| HWB<sub>SK</sub> Variante B | 37,6 kWh/m²a | 37,6 kWh/m²a |

Der Wandaufbau aus dem U-Wert-Kapitel (Innenputz / Hochlochziegel / 18 cm EPS / Putz)
ergibt U = 0,169 W/m²K.

## Aufbau des Repositories

| Datei | |
|---|---|
| `src/werkbank.html` | **Die Quelle.** Nur der Seiteninhalt, ohne `<html>`/`<head>`/`<body>` — in dieser Form erwartet sie der Artefakt-Veröffentlicher, der die Dokumenthülle selbst ergänzt. Nur diese Datei wird bearbeitet. |
| `index.html` | **Erzeugt.** Vollständiges Dokument für GitHub Pages und zum lokalen Öffnen. Wird mitversioniert, damit Pages ohne Build-Schritt ausliefern kann. Nicht direkt bearbeiten. |
| `build.mjs` | Erzeugt `index.html` aus der Quelle: setzt die Dokumenthülle, hebt `<title>` und die Font-Links in den `<head>`. |

Nach jeder Änderung an der Quelle:

```sh
node build.mjs
```

Das Skript bricht ab, wenn in der Quelle `<!doctype>`, `<html>`, `<head>` oder `<body>`
auftaucht — damit sie als Artefakt gültig bleibt.

## GitHub Pages einrichten

Einmalig, nach dem Merge nach `main`:

**Settings → Pages → Build and deployment → Source: *Deploy from a branch*,
Branch: `main` / `/ (root)` → Save.**

Nach ein bis zwei Minuten ist die Seite unter https://floliam.github.io/liam/
erreichbar. Jeder weitere Push auf `main` veröffentlicht automatisch.

## Grundlagen

- OIB-Richtlinie 6, Ausgaben 2023 und September 2025, samt Leitfaden
- ÖNORM B 8110-5 (Klimadaten und Nutzungsprofile), B 8110-6 (Rechenverfahren HWB)
- ÖNORM H 5055 bis H 5059 (Ausweisinhalte, Heiz-, Raumluft-, Kühltechnik, Beleuchtung)
- Energieausweis-Vorlage-Gesetz 2012 (EAVG 2012)

Bauwesen ist in Österreich Landessache: verbindlich ist immer die Fassung, die das
jeweilige Bundesland in seiner Bautechnikverordnung für verbindlich erklärt hat.
