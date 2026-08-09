"""Statischer Build der Startseite.

Rendert dieselben Jinja-Templates wie ``app.py`` in den Ordner ``dist/``:

    dist/index.html      → Deutsch (Standard)
    dist/en/index.html   → Englisch
    dist/static/...      → CSS, JS, Bilder

Damit lässt sich die Seite ohne laufenden Server auf jedem statischen
Webspace veröffentlichen. Benötigt nur Jinja2.

    python3 build.py                       # nach dist/ bauen
    python3 build.py --serve               # bauen und lokal ausliefern
    python3 build.py --site-url https://…  # absolute URLs für hreflang
"""

from __future__ import annotations

import argparse
import json
import shutil
from functools import partial
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"

DEFAULT_LANGUAGE = "de"
LANGUAGES = {
    "de": {"label": "Deutsch", "short": "DE"},
    "en": {"label": "English", "short": "EN"},
}
DEFAULT_SITE_URL = "https://spiraldynamik-beispiel.ch"


def load_translations(lang: str) -> dict:
    path = BASE_DIR / "translations" / f"{lang}.json"
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def make_url_for(lang: str, site_url: str):
    """Baut einen ``url_for``-Ersatz mit relativen Pfaden für den Build."""
    # Deutsch liegt im Wurzelverzeichnis, andere Sprachen eine Ebene tiefer.
    prefix = "" if lang == DEFAULT_LANGUAGE else "../"

    def url_for(endpoint: str, **values):
        external = values.pop("_external", False)
        base = site_url.rstrip("/") + "/" if external else prefix

        if endpoint == "static":
            return base + "static/" + values["filename"]
        if endpoint == "home":
            return base if external else (prefix + "index.html")
        if endpoint == "home_localized":
            code = values["lang_code"]
            if code == DEFAULT_LANGUAGE:
                return base if external else (prefix + "index.html")
            return base + f"{code}/" if external else (prefix + f"{code}/index.html")
        raise ValueError(f"Unbekannter Endpoint: {endpoint}")

    return url_for


def translate(strings: dict, fallback: dict, key: str, default=None):
    for source in (strings, fallback):
        node = source
        for part in key.split("."):
            if not isinstance(node, dict) or part not in node:
                node = None
                break
            node = node[part]
        if node is not None:
            return node
    return key if default is None else default


def build(site_url: str = DEFAULT_SITE_URL) -> Path:
    env = Environment(
        loader=FileSystemLoader(BASE_DIR / "templates"),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("index.html")
    fallback = load_translations(DEFAULT_LANGUAGE)

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)
    shutil.copytree(BASE_DIR / "static", DIST_DIR / "static")

    for lang in LANGUAGES:
        strings = load_translations(lang)
        html = template.render(
            lang=lang,
            t=partial(translate, strings, fallback),
            s=strings,
            languages=LANGUAGES,
            default_language=DEFAULT_LANGUAGE,
            url_for=make_url_for(lang, site_url),
        )

        target = DIST_DIR / ("index.html" if lang == DEFAULT_LANGUAGE else f"{lang}/index.html")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        print(f"  ✓ {target.relative_to(BASE_DIR)}")

    return DIST_DIR


def serve(directory: Path, port: int = 8000) -> None:
    import functools
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(directory))
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"\nhttp://127.0.0.1:{port}/  (Strg+C beendet den Server)")
        httpd.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Statischen Build der Startseite erzeugen.")
    parser.add_argument("--serve", action="store_true", help="nach dem Build lokal ausliefern")
    parser.add_argument("--port", type=int, default=8000, help="Port für --serve")
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL, help="Basis-URL für hreflang-Links")
    args = parser.parse_args()

    print("Baue Startseite …")
    out = build(args.site_url)
    print(f"Fertig: {out}")

    if args.serve:
        serve(out, args.port)


if __name__ == "__main__":
    main()
