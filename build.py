"""Statischer Build der Startseite.

Rendert die Jinja-Templates in den Ordner ``dist/``:

    dist/index.html      → Deutsch (Standard)
    dist/en/index.html   → Englisch
    dist/404.html        → Fehlerseite
    dist/static/…        → CSS, JavaScript, Bilder
    dist/robots.txt      → Suchmaschinen-Hinweise
    dist/sitemap.xml     → Seitenverzeichnis
    dist/.htaccess       → Apache-Konfiguration (aus webroot/)

Der Inhalt von ``dist/`` wird unverändert auf den Webspace geladen –
siehe ``deploy.py`` und den Abschnitt „Veröffentlichen“ in der README.
Benötigt nur Jinja2.

    python3 build.py                       # nach dist/ bauen
    python3 build.py --serve               # bauen und lokal ausliefern
    python3 build.py --site-url https://…  # absolute URLs setzen
"""

from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import shutil
from datetime import date
from functools import partial
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

import content

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
WEBROOT_DIR = BASE_DIR / "webroot"
CONFIG_FILE = BASE_DIR / "deploy.ini"

DEFAULT_LANGUAGE = "de"
LANGUAGES = {
    "de": {"label": "Deutsch", "short": "DE"},
    "en": {"label": "English", "short": "EN"},
}
DEFAULT_SITE_URL = "https://www.beispiel-domain.de"
DEFAULT_BASE_PATH = "/"


def load_translations(lang: str) -> dict:
    path = BASE_DIR / "translations" / f"{lang}.json"
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def read_site_config() -> tuple[str, str]:
    """Holt Domain und Unterverzeichnis aus deploy.ini, falls vorhanden."""
    if not CONFIG_FILE.exists():
        return DEFAULT_SITE_URL, DEFAULT_BASE_PATH

    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE, encoding="utf-8")
    site = parser["site"] if parser.has_section("site") else {}
    return (
        site.get("url", DEFAULT_SITE_URL),
        site.get("base_path", DEFAULT_BASE_PATH),
    )


# --------------------------------------------------------------------------
# URL-Erzeugung
# --------------------------------------------------------------------------
def asset_version(filename: str) -> str:
    """Kurzer Hash über den Dateiinhalt – hängt als ?v= an statische Dateien.

    Dadurch dürfen CSS, JavaScript und Bilder lange im Browser-Cache
    bleiben: Ändert sich der Inhalt, ändert sich die URL.
    """
    path = BASE_DIR / "static" / filename
    if not path.exists():
        return ""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return "?v=" + digest[:8]


def make_url_for(lang: str, site_url: str, base_path: str, root_relative: bool = False):
    """Baut einen ``url_for``-Ersatz für den statischen Build.

    Normale Seiten verlinken relativ – so lässt sich ``dist/`` auch lokal
    oder in einem Unterordner öffnen. Die Fehlerseite braucht dagegen
    absolute Pfade: Apache liefert sie unter beliebigen URLs aus, relative
    Verweise würden dann ins Leere zeigen.
    """
    prefix = "" if lang == DEFAULT_LANGUAGE else "../"
    root = "/" + base_path.strip("/") + "/" if base_path.strip("/") else "/"

    def url_for(endpoint: str, **values):
        external = values.pop("_external", False)
        if external:
            base = site_url.rstrip("/") + root
        elif root_relative:
            base = root
        else:
            base = prefix

        if endpoint == "static":
            filename = values["filename"]
            return base + "static/" + filename + asset_version(filename)
        if endpoint == "home":
            if external or root_relative:
                return base
            return prefix + "index.html"
        if endpoint == "home_localized":
            code = values["lang_code"]
            if code == DEFAULT_LANGUAGE:
                return base if (external or root_relative) else (prefix + "index.html")
            if external or root_relative:
                return base + f"{code}/"
            return prefix + f"{code}/index.html"
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


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def page_url(site_url: str, base_path: str, lang: str) -> str:
    root = site_url.rstrip("/") + "/" + (base_path.strip("/") + "/" if base_path.strip("/") else "")
    return root if lang == DEFAULT_LANGUAGE else root + f"{lang}/"


def write_sitemap(site_url: str, base_path: str) -> None:
    today = date.today().isoformat()
    entries = "\n".join(
        f"  <url>\n"
        f"    <loc>{page_url(site_url, base_path, lang)}</loc>\n"
        f"    <lastmod>{today}</lastmod>\n"
        f"  </url>"
        for lang in LANGUAGES
    )
    (DIST_DIR / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n",
        encoding="utf-8",
    )


def write_robots(site_url: str, base_path: str) -> None:
    sitemap = site_url.rstrip("/") + "/" + (
        base_path.strip("/") + "/" if base_path.strip("/") else ""
    ) + "sitemap.xml"
    (DIST_DIR / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n" f"Sitemap: {sitemap}\n", encoding="utf-8"
    )


def build(site_url: str = DEFAULT_SITE_URL, base_path: str = DEFAULT_BASE_PATH) -> Path:
    env = Environment(
        loader=FileSystemLoader(BASE_DIR / "templates"),
        autoescape=select_autoescape(["html"]),
    )
    fallback = load_translations(DEFAULT_LANGUAGE)

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)
    shutil.copytree(BASE_DIR / "static", DIST_DIR / "static")

    # Startseite je Sprache
    index = env.get_template("index.html")
    for lang in LANGUAGES:
        strings = load_translations(lang)
        # Kommende Kurse und der Hinweis oben stammen aus derselben Liste.
        courses = content.upcoming_courses(strings)
        html = index.render(
            lang=lang,
            t=partial(translate, strings, fallback),
            s=strings,
            languages=LANGUAGES,
            default_language=DEFAULT_LANGUAGE,
            url_for=make_url_for(lang, site_url, base_path),
            anchor_base="",  # auf der Startseite genügen reine Anker
            courses=courses,
            teaser=content.course_teaser(strings, courses),
        )
        target = DIST_DIR / ("index.html" if lang == DEFAULT_LANGUAGE else f"{lang}/index.html")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        print(f"  ✓ {target.relative_to(BASE_DIR)}")

    # Fehlerseite in der Standardsprache, mit absoluten Pfaden
    strings = load_translations(DEFAULT_LANGUAGE)
    error_page = env.get_template("404.html").render(
        lang=DEFAULT_LANGUAGE,
        t=partial(translate, strings, fallback),
        s=strings,
        languages=LANGUAGES,
        default_language=DEFAULT_LANGUAGE,
        url_for=make_url_for(DEFAULT_LANGUAGE, site_url, base_path, root_relative=True),
        # Die Fehlerseite liegt nicht auf der Startseite: Anker brauchen den Pfad dorthin.
        anchor_base=make_url_for(DEFAULT_LANGUAGE, site_url, base_path, root_relative=True)("home"),
    )
    (DIST_DIR / "404.html").write_text(error_page, encoding="utf-8")
    print("  ✓ dist/404.html")

    write_sitemap(site_url, base_path)
    write_robots(site_url, base_path)
    print("  ✓ dist/sitemap.xml, dist/robots.txt")

    # Dateien, die unverändert ins Wurzelverzeichnis gehören (.htaccess …)
    if WEBROOT_DIR.exists():
        for item in WEBROOT_DIR.iterdir():
            if item.is_file():
                shutil.copy2(item, DIST_DIR / item.name)
                print(f"  ✓ dist/{item.name}")

    return DIST_DIR


def serve(directory: Path, port: int = 8000) -> None:
    import functools
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(directory))
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"\nhttp://127.0.0.1:{port}/  (Strg+C beendet den Server)")
        httpd.serve_forever()


def main() -> None:
    config_url, config_base = read_site_config()

    parser = argparse.ArgumentParser(description="Statischen Build der Startseite erzeugen.")
    parser.add_argument("--serve", action="store_true", help="nach dem Build lokal ausliefern")
    parser.add_argument("--port", type=int, default=8000, help="Port für --serve")
    parser.add_argument("--site-url", default=config_url, help="Domain der Seite, z. B. https://www.praxis.de")
    parser.add_argument("--base-path", default=config_base, help="Unterverzeichnis auf dem Webspace, Standard /")
    args = parser.parse_args()

    print(f"Baue Startseite für {args.site_url} …")
    out = build(args.site_url, args.base_path)
    print(f"Fertig: {out}")

    if args.serve:
        serve(out, args.port)


if __name__ == "__main__":
    main()
