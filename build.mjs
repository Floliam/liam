/*
 * Baut aus der Artefakt-Quelle die eigenständige Seite für GitHub Pages.
 *
 *   src/werkbank.html   Quelle — nur der Seiteninhalt, ohne <html>/<head>/<body>.
 *                       In dieser Form erwartet sie der Artefakt-Veröffentlicher,
 *                       der die Hülle selbst ergänzt. Nur diese Datei wird bearbeitet.
 *   index.html          erzeugt — vollständiges Dokument. Wird mitversioniert,
 *                       damit GitHub Pages ohne Build-Schritt ausliefern kann.
 *
 * Aufruf:  node build.mjs
 */
import { readFileSync, writeFileSync } from 'node:fs';

const QUELLE = 'src/werkbank.html';
const ZIEL   = 'index.html';

const inhalt = readFileSync(QUELLE, 'utf8');

const verboten = /<!doctype|<html[\s>]|<head[\s>]|<body[\s>]/i.exec(inhalt);
if (verboten) {
  console.error(
    `${QUELLE} enthält "${verboten[0]}". Die Quelle darf nur den Seiteninhalt enthalten — ` +
    `die Dokumenthülle setzt dieses Skript bzw. der Artefakt-Veröffentlicher.`
  );
  process.exit(1);
}

const titel = (/<title>([^<]*)<\/title>/i.exec(inhalt) || [, 'Energieausweis-Werkbank'])[1];

/* <title> und <link> stehen in der Quelle am Dateianfang, weil der
   Artefakt-Veröffentlicher sie von dort einsammelt. Im eigenständigen
   Dokument gehören sie in den <head>, also hebt der Build sie hoch. */
const kopfzeilen = [];
const rumpf = inhalt.replace(
  /^(?:[ \t]*(?:<title>[^<]*<\/title>|<link\b[^>]*>)[ \t]*\r?\n)+/i,
  (block) => { kopfzeilen.push(block.trimEnd()); return ''; }
).trimStart();

/* Die Hülle spiegelt die des Artefakt-Veröffentlichers, damit die Seite hier
   und dort identisch rendert: Zeichensatz, Viewport, minimaler Reset. */
const seite = `<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Berechnung des Energieausweises nach OIB-Richtlinie 6 und ÖNORM B 8110-6 — mit vollständigem Rechenweg und Nachweisprüfung.">
<meta name="color-scheme" content="light dark">
${kopfzeilen.join('\n')}
<style>
:root{color-scheme:light dark}
body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#EDF0F1;color:#111A1D}
img{max-width:100%}
[hidden]:not([hidden=until-found]){display:none!important}
</style>
<!-- Erzeugt aus ${QUELLE} durch build.mjs — nicht direkt bearbeiten. -->
</head>
<body>
${rumpf}
</body>
</html>
`;

writeFileSync(ZIEL, seite);
console.log(`${ZIEL} geschrieben — "${titel}", ${(seite.length / 1024).toFixed(0)} kB.`);
