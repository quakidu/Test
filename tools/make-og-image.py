"""Erzeugt die Vorschaubilder für geteilte Links (Open Graph).

Wenn jemand die Adresse der Seite in einem Messenger, in sozialen Netzwerken
oder in einer E-Mail teilt, zeigt das Programm eine Vorschaukarte. Ohne
hinterlegtes Bild bleibt sie leer oder greift sich irgendein Element von der
Seite.

Das Bild entsteht aus denselben Texten wie die Seite selbst – Praxisname,
Untertitel und Ort stehen in ``translations/<sprache>.json``. Der Dateiname
steht dort unter ``seo.og_image``. Nach einer Änderung an diesen Angaben
einmal aufrufen:

    python3 tools/make-og-image.py           # alle Sprachen
    python3 tools/make-og-image.py de        # nur Deutsch

Gebraucht werden nur die Standardbibliothek und Chromium (oder Chrome).
"""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
import sys
import re
import tempfile
from glob import glob
from pathlib import Path

from png import crop, read_png, write_png

BASE_DIR = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = BASE_DIR / "translations"
IMG_DIR = BASE_DIR / "static" / "img"
LOGO = IMG_DIR / "logo.png"

# Facebook, LinkedIn, WhatsApp und X erwarten dieses Seitenverhältnis.
WIDTH, HEIGHT = 1200, 630

BROWSERS = ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable"]

# Ordner, in denen manche Umgebungen einen mitgelieferten Chromium ablegen.
BROWSER_GLOBS = [
    "/opt/pw-browsers/chromium*/chrome-linux/chrome",
    "/opt/pw-browsers/chromium*/chrome-linux/headless_shell",
]

TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<meta charset="utf-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ background: #FFFFFF; }}
  /* Feste Größe und verstecktes Überlaufen: das Bild muss exakt
     {width} × {height} groß sein, egal wie lang die Texte sind. */
  .card {{
    position: absolute; inset: 0;
    width: {width}px; height: {height}px; overflow: hidden;
    display: flex; flex-direction: column; justify-content: space-between;
    padding: 64px 76px;
    background:
      radial-gradient(110% 85% at 100% 0%, rgba(60,98,136,.42) 0%, rgba(60,98,136,0) 62%),
      linear-gradient(160deg, #FFFFFF 0%, #F3F6F9 55%, #E5EBF1 100%);
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    color: #191E28;
  }}
  /* Ohne align-self zöge die Flex-Box das Bild in die Breite. Die Höhe
     bleibt nah an der Originalgröße des Logos, sonst wird es unscharf. */
  .logo {{ align-self: flex-start; height: 60px; width: auto; }}
  .eyebrow {{
    font-size: 26px; letter-spacing: .16em; text-transform: uppercase;
    color: #314F6F; font-weight: 600; margin-bottom: 18px;
  }}
  h1 {{ font-size: 68px; line-height: 1.08; font-weight: 700; max-width: 16ch; }}
  .lead {{ font-size: 30px; line-height: 1.35; color: #47536A; margin-top: 20px; max-width: 30ch; }}
  .foot {{ display: flex; align-items: center; gap: 24px; font-size: 25px; color: #47536A; }}
  .rule {{ flex: 1; height: 3px; background: #314F6F; opacity: .25; border-radius: 3px; }}
</style>
<body>
  <div class="card">
    <img class="logo" src="data:image/png;base64,{logo}" alt="">
    <div>
      <p class="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      <p class="lead">{lead}</p>
    </div>
    <div class="foot">
      <span>{founder}</span>
      <span class="rule"></span>
      <span>{city}</span>
    </div>
  </div>
</body>
</html>
"""


def escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def find_browser() -> str:
    for name in BROWSERS:
        path = shutil.which(name)
        if path:
            return path
    for pattern in BROWSER_GLOBS:
        for path in sorted(glob(pattern)):
            if Path(path).is_file():
                return path
    sys.exit("Kein Chromium/Chrome gefunden – bitte installieren oder "
             "static/img/og-bild.png von Hand anlegen (1200 × 630).")


def run(browser: str, arguments: list[str]) -> str:
    """Startet den Browser ohne Fenster und gibt seine Ausgabe zurück."""
    result = subprocess.run(
        [browser, "--headless", "--no-sandbox", "--disable-gpu",
         "--hide-scrollbars", *arguments],
        check=True, capture_output=True, text=True,
    )
    return result.stdout


def window_padding(browser: str, page: Path) -> tuple[int, int]:
    """Differenz zwischen Fenstergröße und tatsächlichem Sichtfeld."""
    probe = page.with_name("probe.html")
    probe.write_text(
        "<body><script>document.body.textContent = "
        "'VP:' + innerWidth + 'x' + innerHeight</script>",
        encoding="utf-8",
    )
    output = run(browser, ["--dump-dom", f"--window-size={WIDTH},{HEIGHT}",
                           probe.as_uri()])
    found = re.search(r"VP:(\d+)x(\d+)", output)
    if not found:
        return 0, 0
    return WIDTH - int(found.group(1)), HEIGHT - int(found.group(2))


def render(lang: str, browser: str) -> None:
    """Baut das Vorschaubild einer Sprache."""
    strings = json.loads((TRANSLATIONS_DIR / f"{lang}.json").read_text(encoding="utf-8"))
    seo = strings.get("seo", {})
    brand = strings.get("brand", {})

    name = seo.get("og_image")
    if not name:
        print(f"  · {lang}: kein seo.og_image hinterlegt – übersprungen")
        return
    target = IMG_DIR / name

    html = TEMPLATE.format(
        width=WIDTH,
        height=HEIGHT,
        logo=base64.b64encode(LOGO.read_bytes()).decode("ascii"),
        # Der Schriftzug steht schon im Logo; die große Zeile nennt deshalb
        # das Thema und den Ort – danach wird gesucht.
        eyebrow=escape(brand.get("tagline", "")),
        title=escape(strings.get("hero", {}).get("eyebrow", "")),
        lead=escape(" · ".join(filter(None, [
            strings.get("offer", {}).get("title", ""),
            strings.get("courses", {}).get("title", ""),
        ]))),
        founder=escape(", ".join(filter(None, [
            seo.get("founder", ""), seo.get("founder_role", "")
        ]))),
        city=escape(seo.get("city", "")),
    )

    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "og.html"
        page.write_text(html, encoding="utf-8")

        # Der Browser rechnet zur Fenstergröße noch eigene Ränder hinzu, das
        # Sichtfeld ist also kleiner als das Fenster. Wie viel kleiner, fragen
        # wir einmal ab, statt eine Zahl zu raten.
        pad_x, pad_y = window_padding(browser, page)
        shot = Path(tmp) / "shot.png"
        run(browser, [
            f"--screenshot={shot}",
            f"--window-size={WIDTH + pad_x},{HEIGHT + pad_y}",
            page.as_uri(),
        ])

        # Das Bild ist so groß wie das Fenster; der Rand unten gehört nicht dazu.
        _, _, channels, rows = read_png(shot)
        write_png(target, crop(rows, WIDTH, HEIGHT, channels), channels)

    print(f"  ✓ {target.relative_to(BASE_DIR)} ({WIDTH} × {HEIGHT})")


def main() -> None:
    wanted = sys.argv[1:] or [path.stem for path in sorted(TRANSLATIONS_DIR.glob("*.json"))]
    browser = find_browser()
    for lang in wanted:
        if not (TRANSLATIONS_DIR / f"{lang}.json").exists():
            sys.exit(f"Keine Übersetzungsdatei für „{lang}“ gefunden.")
        render(lang, browser)


if __name__ == "__main__":
    main()
