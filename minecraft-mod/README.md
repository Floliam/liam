# Player Locator Bar (Forge 1.18.2)

Rein clientseitige HUD-Mod. Über der XP-Leiste erscheint eine zusätzliche Leiste:

- **Jeder andere Spieler ist ein farbiger Punkt** auf der Linie. Die Position zeigt die
  Richtung relativ zu deiner Blickrichtung — Mitte (weißer Strich) = geradeaus,
  links/rechts = links/rechts von dir.
- **Der nächste Spieler ist ein größerer Punkt.**
- Nur für den nächsten Spieler: **Höhe** rechts neben der Leiste (`Y 75 ▲12` = er steht
  auf Y 75, 12 Blöcke über dir) und **Entfernung** links (`23m`).
- Spieler außerhalb des Blickfelds kleben halbtransparent am linken/rechten Rand.
- **Flug-Meldung:** Fliegt jemand ohne Elytra (o.ä.), bekommst du eine Meldung nur in
  deinen eigenen Chat, z. B. `[Ortungsleiste] Steve fliegt ohne Elytra (Y 85, 23m)`,
  dazu ein kurzer Ton. Andere Spieler und der Server sehen davon nichts.
- Herzen, Rüstung und Hunger rücken 12 Pixel nach oben, damit nichts überlappt.

Die Mod liest nur, was dein Client ohnehin weiß. Sie verändert weder die Welt noch andere
Spieler und muss auf dem Server **nicht** installiert sein.

## Installation (CurseForge)

1. In CurseForge ein Profil mit **Minecraft 1.18.2 + Forge** anlegen (oder ein vorhandenes nehmen).
2. Profil → `…` → **Open Folder** → in den Ordner `mods` die Datei
   `playerlocatorbar-1.18.2-1.1.1.jar` legen.
3. Spiel über CurseForge starten — die Mod lädt automatisch mit.

## Bedienung & Einstellungen

- Taste **J** blendet die Leiste ein/aus (änderbar unter Optionen → Steuerung).
- Einstellungen: `config/playerlocatorbar-client.toml` im Profilordner (entsteht beim
  ersten Start): Blickfeld der Leiste (`fieldOfView`, 360 = Rundum-Kompass),
  maximale Entfernung, Name/Entfernung/Höhe ein/aus, Spieler mit Unsichtbarkeitstrank
  anzeigen (`showInvisible`, standardmäßig an).

## Wie die Flug-Erkennung arbeitet

Der Server sagt dem Client nicht, ob jemand fliegt. Die Mod erkennt es an der Bewegung:
Wer frei in der Luft ist, wird durch die Schwerkraft immer schneller nach unten. Wer
stattdessen länger als 3 Sekunden schwebt, steigt oder gleichmäßig langsam sinkt, wird gemeldet.

Nicht gemeldet werden: Elytra-Gleiten, Reiten/Boot/Lore, Wasser und Lava, Leitern und Ranken,
Spinnennetz, Pulverschnee, Gerüste, Honigblöcke, Dreizack mit Sog, Zuschauer und (abschaltbar)
Kreativmodus. Ein Spieler wird erst wieder gemeldet, nachdem er gelandet ist.

Mögliche Fehlalarme: Spieler mit **Sanftfall- oder Schwebetrank** (deren Effekte schickt der
Server nicht an andere Spieler) und starke **Server-Lags**, bei denen Spieler in der Luft
einfrieren. Einstellungen im Abschnitt `[flightAlert]` der Config.

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
