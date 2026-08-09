/**
 * Erzeugt die Logo-Dateien der Startseite als PNG mit transparentem Grund.
 *
 *   static/img/logo.png       – helle Variante (dunkles Grün)
 *   static/img/logo-dark.png  – Variante für das dunkle Farbschema
 *
 * Das Logo wird aus der Spiral-Geometrie berechnet und über einen
 * headless Chrome gerendert. Der Hintergrund bleibt transparent, damit
 * das Logo auf jeder Fläche freigestellt sitzt; die zweite Variante
 * sorgt für ausreichenden Kontrast auf dunklem Grund.
 *
 * Voraussetzung: ein laufender Chrome mit offenem DevTools-Port.
 *
 *   chrome --headless=new --remote-debugging-port=9222 about:blank
 *   node tools/export-logo.mjs
 *
 * Die Dateien liegen fertig im Repository – dieses Skript wird nur
 * gebraucht, wenn Größe oder Farben des Logos geändert werden sollen.
 */

import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SIZE = 384;           // Kantenlänge der Bilddatei in Pixeln
const DEBUG_PORT = process.env.CDP_PORT || 9222;

// Geometrie der Spirale: Startradius, Zuwachs pro Windung, Anzahl Windungen.
const GEO = { turns: 2.6, a: 4.0, b: 6.6, cx: 32, cy: 32 };
const STROKE = 2.9;
const PADDING = 4;

/** Archimedische Spirale als SVG-Pfad. */
function spiralPath({ turns = GEO.turns, a = GEO.a, b = GEO.b, steps = 200, cx = GEO.cx, cy = GEO.cy, phase = 0 } = {}) {
  const points = [];
  for (let i = 0; i <= steps; i += 1) {
    const t = (turns * 2 * Math.PI * i) / steps;
    const r = a + (b * t) / (2 * Math.PI);
    points.push([cx + r * Math.cos(t + phase), cy + r * Math.sin(t + phase)]);
  }
  const [first, ...rest] = points;
  return `M ${first[0].toFixed(1)} ${first[1].toFixed(1)} ` +
    rest.map(([x, y]) => `L ${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');
}

const VARIANTS = [
  {
    file: 'static/img/logo.png',
    stops: ['#6FA98A', '#3F7D5F', '#2C5C46'],
    dot: '#2C5C46',
  },
  {
    file: 'static/img/logo-dark.png',
    stops: ['#C3D8C9', '#9CBFA7', '#6FA98A'],
    dot: '#C3D8C9',
  },
];

function page({ stops, dot }) {
  const inner = spiralPath();
  const outer = spiralPath({ phase: Math.PI });

  // Bildausschnitt eng um die Spirale legen, damit das Motiv die Kachel füllt.
  const radius = GEO.a + GEO.b * GEO.turns + STROKE / 2 + PADDING;
  const view = `${GEO.cx - radius} ${GEO.cy - radius} ${radius * 2} ${radius * 2}`;

  return `<!doctype html><meta charset="utf-8">
<style>
  html, body { margin: 0; width: ${SIZE}px; height: ${SIZE}px; background: transparent; }
  svg { display: block; width: 100%; height: 100%; }
</style>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="${view}">
  <defs>
    <linearGradient id="g" x1="10" y1="8" x2="54" y2="56" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="${stops[0]}"/>
      <stop offset="0.55" stop-color="${stops[1]}"/>
      <stop offset="1" stop-color="${stops[2]}"/>
    </linearGradient>
  </defs>
  <g fill="none" stroke="url(#g)" stroke-linecap="round" stroke-linejoin="round">
    <path d="${inner}" stroke-width="${STROKE}"/>
    <path d="${outer}" stroke-width="${STROKE * 0.42}" opacity="0.42"/>
  </g>
  <circle cx="${GEO.cx}" cy="${GEO.cy}" r="${STROKE * 0.55}" fill="${dot}"/>
</svg>`;
}

/** Minimaler CDP-Client über den globalen WebSocket von Node. */
async function connect(url) {
  const target = await (
    await fetch(`http://127.0.0.1:${DEBUG_PORT}/json/new?${encodeURIComponent(url)}`, { method: 'PUT' })
  ).json();

  const ws = new WebSocket(target.webSocketDebuggerUrl);
  const pending = new Map();
  let id = 0;

  ws.addEventListener('message', (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      pending.get(message.id)(message.result);
      pending.delete(message.id);
    }
  });
  await new Promise((done) => ws.addEventListener('open', done));

  return {
    send: (method, params = {}) =>
      new Promise((res) => {
        const next = ++id;
        pending.set(next, res);
        ws.send(JSON.stringify({ id: next, method, params }));
      }),
    close: () => ws.close(),
  };
}

for (const variant of VARIANTS) {
  const dataUrl = 'data:text/html;base64,' + Buffer.from(page(variant), 'utf8').toString('base64');
  const cdp = await connect(dataUrl);

  await cdp.send('Page.enable');
  await cdp.send('Emulation.setDeviceMetricsOverride', {
    width: SIZE, height: SIZE, deviceScaleFactor: 1, mobile: false,
  });
  // Ohne diesen Override rendert Chrome eine weiße Seitenfläche mit.
  await cdp.send('Emulation.setDefaultBackgroundColorOverride', {
    color: { r: 0, g: 0, b: 0, a: 0 },
  });
  await new Promise((done) => setTimeout(done, 500));

  const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
  const path = resolve(ROOT, variant.file);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, Buffer.from(shot.data, 'base64'));
  console.log(`  ✓ ${variant.file}`);
  cdp.close();
}

process.exit(0);
