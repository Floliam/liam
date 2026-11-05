# Dragon Finder (Forge 1.18.2, für Ice and Fire)

Rein clientseitige Mod: Sie läuft nur bei dir und muss auf dem Server **nicht** installiert sein.
Sie liest nur, was dein Client ohnehin weiß, und verändert nichts an Welt, Server oder anderen Spielern.

## Was sie zeigt

Oben links, zwei Zeilen:

```
Feuerdrache  143 m  ↗ NO  Y 85 ▲12
Goldhort (Feuerdrache)  412 m  ↙ SW  Y 40 ▼24
```

- **Nächster Drache:** Art (Feuer-, Eis-, Blitzdrache, ggf. mit Namen), Entfernung, Pfeil relativ
  zu deiner Blickrichtung (↑ = geradeaus), Himmelsrichtung, Höhe (Y) und wie viel höher/tiefer.
- **Nächster Drachenhort:** Stellen mit vielen Gold-, Silber- oder Kupferhaufen. So legt Ice and Fire
  Drachenhöhlen und -nester an. Gold = Feuerdrache, Silber = Eisdrache, Kupfer = Blitzdrache.
- **Chat-Meldung** (nur für dich) mit kurzem Ton, sobald ein neuer Drache oder Hort entdeckt wird.

Taste **K** blendet die Anzeige ein/aus (änderbar unter Optionen → Steuerung).

## Reichweite

- **Drachen:** nur solche, die der Server an deinen Client überträgt, also ungefähr innerhalb
  deiner Render-Distanz.
- **Horte:** alle Chunks, die dein Client geladen hat (Render-Distanz). Horte bleiben gespeichert,
  solange du in der Welt bist, auch wenn du dich wieder entfernst.
- Weiter entfernte Drachen kann keine Client-Mod finden: der Server schickt sie nicht.
  Tipp: Render-Distanz erhöhen (wenn der Server das erlaubt) und herumfliegen/reiten.

## Installation (CurseForge)

`dragonfinder-1.18.2-1.0.0.jar` in den `mods`-Ordner des Profils legen, in dem auch Ice and Fire ist.

## Einstellungen

`config/dragonfinder-client.toml`: Anzeige, Chat-Meldungen, Ton, welche Entities als Drache zählen,
welche Blöcke einen Hort anzeigen und ab wie vielen Haufen-Blöcken (`minBlocks`, Standard 8).

Hinweis: Manche Server verbieten Mods, die Mobs oder Strukturen orten. Vorher die Regeln prüfen.
