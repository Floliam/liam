# Player Locator Bar (Forge 1.18.2)

Rein clientseitige HUD-Mod. Über der XP-Leiste erscheint eine zusätzliche Leiste:

- **Jeder andere Spieler ist ein farbiger Punkt** auf der Linie. Die Position zeigt die
  Richtung relativ zu deiner Blickrichtung — Mitte (weißer Strich) = geradeaus,
  links/rechts = links/rechts von dir.
- **Der nächste Spieler ist ein größerer Punkt.**
- Nur für den nächsten Spieler: **Höhe** rechts neben der Leiste (`Y 75 ▲12` = er steht
  auf Y 75, 12 Blöcke über dir) und **Entfernung** links (`23m`).
- Spieler außerhalb des Blickfelds kleben halbtransparent am linken/rechten Rand.
- Herzen, Rüstung und Hunger rücken 12 Pixel nach oben, damit nichts überlappt.

Die Mod liest nur, was dein Client ohnehin weiß. Sie verändert weder die Welt noch andere
Spieler und muss auf dem Server **nicht** installiert sein.

## Installation (CurseForge)

1. In CurseForge ein Profil mit **Minecraft 1.18.2 + Forge** anlegen (oder ein vorhandenes nehmen).
2. Profil → `…` → **Open Folder** → in den Ordner `mods` die Datei
   `playerlocatorbar-1.18.2-1.0.0.jar` legen.
3. Spiel über CurseForge starten — die Mod lädt automatisch mit.

## Bedienung & Einstellungen

- Taste **J** blendet die Leiste ein/aus (änderbar unter Optionen → Steuerung).
- Einstellungen: `config/playerlocatorbar-client.toml` im Profilordner (entsteht beim
  ersten Start): Blickfeld der Leiste (`fieldOfView`, 360 = Rundum-Kompass),
  maximale Entfernung, Name/Entfernung/Höhe ein/aus, unsichtbare Spieler ausblenden.

## Grenze

Der Client kennt andere Spieler nur, solange sie in Sichtweite geladen sind
(Entity-Tracking des Servers, meist etwa die Render-Distanz). Weiter entfernte
Spieler kann eine reine Client-Mod nicht anzeigen.

Hinweis: Manche Server verbieten Mods, die Spielerpositionen anzeigen — vorher die Regeln prüfen.

## Selbst bauen

```
cd minecraft-mod
./gradlew build      # Java 17 nötig, Ergebnis in build/libs/
```

Bei jedem Push baut GitHub Actions („Minecraft-Mod bauen“) das Jar automatisch und hängt
es als Artefakt an den Lauf.
