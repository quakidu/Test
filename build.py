"""Statischer Build der Startseite.

Rendert die Jinja-Templates in den Ordner ``dist/``:

    dist/index.html      → Deutsch (Standard)
    dist/en/index.html   → Englisch
    dist/404.html        → Fehlerseite
    dist/static/…        → CSS, JavaScript, Bilder
    dist/robots.txt      → Suchmaschinen-Hinweise
    dist/sitemap.xml     → Seitenverzeichnis
    dist/llms.txt        → Kurzfassung der Seite für Sprachmodelle
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

# Rechtsseiten: Dateiname, Textbaustein unter content/ und Titelschlüssel.
LEGAL_PAGES = {
    "impressum": {"file": "impressum.html", "title_key": "legal.imprint"},
    "datenschutz": {"file": "datenschutz.html", "title_key": "legal.privacy"},
}
INDEX_FILE = "index.html"


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
        if endpoint == "legal":
            page_file = LEGAL_PAGES[values["page"]]["file"]
            if external or root_relative:
                folder = "" if lang == DEFAULT_LANGUAGE else f"{lang}/"
                return base + folder + page_file
            # Die Rechtsseite der aktuellen Sprache liegt im selben Verzeichnis.
            return page_file
        raise ValueError(f"Unbekannter Endpoint: {endpoint}")

    return url_for


def make_page_url(lang: str, page_file: str, site_url: str, base_path: str,
                  root_relative: bool = False):
    """Verweise auf dieselbe Seite in den anderen Sprachen.

    Damit bleibt der Sprachumschalter auf der Seite, auf der man gerade ist,
    statt immer zur Startseite zu springen.
    """
    prefix = "" if lang == DEFAULT_LANGUAGE else "../"
    root = "/" + base_path.strip("/") + "/" if base_path.strip("/") else "/"

    def page_url(code: str, external: bool = False) -> str:
        folder = "" if code == DEFAULT_LANGUAGE else f"{code}/"
        if external:
            # Startseiten als Verzeichnis-URL, ohne index.html
            name = "" if page_file == INDEX_FILE else page_file
            return site_url.rstrip("/") + root + folder + name
        if root_relative:
            return root + folder + page_file
        if code == lang:
            return page_file  # dieselbe Sprache liegt im selben Verzeichnis
        return prefix + folder + page_file

    return page_url


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
    locations = []
    for lang in LANGUAGES:
        root = page_url(site_url, base_path, lang)
        locations.append(root)
        locations.extend(root + page["file"] for page in LEGAL_PAGES.values())

    entries = "\n".join(
        f"  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{today}</lastmod>\n"
        f"  </url>"
        for loc in locations
    )
    (DIST_DIR / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n",
        encoding="utf-8",
    )


# Sammler, die Inhalte für Sprachmodelle und Antwortdienste lesen. Sie sind
# hier ausdrücklich erlaubt, damit die Praxis in solchen Antworten auftaucht.
# Wer das nicht möchte, ändert unten Allow in Disallow – siehe README.
AI_AGENTS = [
    ("GPTBot", "ChatGPT / OpenAI"),
    ("OAI-SearchBot", "ChatGPT-Suche"),
    ("ChatGPT-User", "Abruf beim Klick in ChatGPT"),
    ("ClaudeBot", "Claude / Anthropic"),
    ("Claude-User", "Abruf beim Klick in Claude"),
    ("PerplexityBot", "Perplexity"),
    ("Google-Extended", "Google Gemini / AI Overviews"),
    ("Applebot-Extended", "Apple Intelligence"),
    ("Bingbot", "Bing und Copilot"),
]


def write_robots(site_url: str, base_path: str) -> None:
    root = site_url.rstrip("/") + "/" + (
        base_path.strip("/") + "/" if base_path.strip("/") else ""
    )
    lines = [
        "# Suchmaschinen und Antwortdienste dürfen die Seite vollständig lesen.",
        "User-agent: *",
        "Allow: /",
        "",
    ]
    for agent, note in AI_AGENTS:
        lines += [f"# {note}", f"User-agent: {agent}", "Allow: /", ""]
    lines += [
        f"Sitemap: {root}sitemap.xml",
        "",
        f"# Kurzfassung der Seite für Sprachmodelle: {root}llms.txt",
        "",
    ]
    (DIST_DIR / "robots.txt").write_text("\n".join(lines), encoding="utf-8")


def write_llms_txt(site_url: str, base_path: str, strings: dict) -> None:
    """Kurzfassung der Seite als reiner Text (``llms.txt``).

    Antwortdienste lesen lieber wenige klare Zeilen als ein Layout. Die
    Datei fasst zusammen, was auf der Startseite steht – Quelle sind
    dieselben Sprachdateien, damit sie nicht auseinanderlaufen kann.
    """
    root = site_url.rstrip("/") + "/" + (
        base_path.strip("/") + "/" if base_path.strip("/") else ""
    )
    seo = strings.get("seo", {})
    contact = strings.get("contact", {})
    def one_line(text: str) -> str:
        """Mehrzeilige Angaben (Adresse, Öffnungszeiten) in eine Zeile."""
        return ", ".join(part.strip() for part in str(text).splitlines() if part.strip())

    lines = [
        f"# {seo.get('legal_name') or strings.get('brand', {}).get('name', '')}",
        "",
        f"> {strings.get('meta', {}).get('description', '')}",
        "",
        "## Praxis",
        "",
        f"- Inhaber: {seo.get('founder', '')}, {seo.get('founder_role', '')}",
        f"- Adresse: {one_line(contact.get('address', ''))}",
        f"- Telefon: {contact.get('phone', '')}",
        f"- E-Mail: {contact.get('email', '')}",
        f"- Öffnungszeiten: {one_line(contact.get('hours', ''))}",
        f"- Einzugsgebiet: {', '.join(seo.get('area_served', []))}",
    ]

    therapist = strings.get("therapist", {})
    if therapist:
        lines += ["", f"## {therapist.get('name', '')}", "",
                  f"- {therapist.get('role', '')}"]
        lines += [f"- {fact.get('label', '')}: {fact.get('value', '')}"
                  for fact in therapist.get("facts", [])]
        lines += [""] + [one_line(text) for text in therapist.get("text", [])]

    lines += ["", "## Angebot", ""]
    for item in strings.get("offer", {}).get("items", []):
        lines.append(f"- {item.get('title', '')}: {item.get('text', '')} ({item.get('meta', '')})")

    lines += ["", "## Kurse", ""]
    courses = content.upcoming_courses(strings)
    if courses:
        for course in courses:
            lines.append(
                f"- {course.get('title', '')} (Start: {course.get('start_date', '')}, "
                f"{course.get('scope', '')}, {course.get('price', '')}): {course.get('text', '')}"
            )
    else:
        lines.append(f"- {strings.get('courses', {}).get('empty', '')}")

    lines += [
        "",
        "## Seiten",
        "",
        f"- [Startseite]({root}): Angebot, Kurse, Ablauf und Kontakt",
        f"- [English version]({root}en/): the same information in English",
        f"- [Impressum]({root}impressum.html): Anbieterkennzeichnung",
        f"- [Datenschutz]({root}datenschutz.html): Umgang mit Daten",
        "",
        "## Hinweise",
        "",
        "- Termine werden telefonisch oder per E-Mail vereinbart; es gibt keine Online-Buchung.",
        "- Absagen bitte spätestens 24 Stunden vorher.",
        "- Rückmeldungen auf der Seite werden von Hand geprüft und nur mit Zustimmung veröffentlicht.",
        "- Die Angaben auf dieser Seite ersetzen keine ärztliche Beratung oder Diagnose.",
        "",
    ]
    (DIST_DIR / "llms.txt").write_text("\n".join(lines), encoding="utf-8")


def check_seo(strings: dict, lang: str) -> list[str]:
    """Prüft die maschinenlesbaren Angaben gegen den sichtbaren Text.

    Strukturierte Daten dürfen nichts behaupten, was auf der Seite nicht
    steht – sonst gilt das als irreführend. Statt den Build abzubrechen,
    gibt es Hinweise: die Vorlagenwerte sollen ja bewusst ersetzt werden.
    """
    notes = []
    seo = strings.get("seo", {})
    address = strings.get("contact", {}).get("address", "")

    for field, label in (("street", "Straße"), ("postal_code", "Postleitzahl"),
                         ("city", "Ort")):
        value = str(seo.get(field, "")).strip()
        if value and value not in address:
            notes.append(
                f"[{lang}] seo.{field} „{value}“ steht nicht in contact.address – "
                f"Adresse und strukturierte Daten müssen übereinstimmen."
            )

    for field in ("latitude", "longitude"):
        if not seo.get(field):
            notes.append(f"[{lang}] seo.{field} fehlt – ohne Koordinaten entfällt "
                         f"die Ortsangabe für Kartendienste.")

    therapist = strings.get("therapist", {})
    if therapist and seo.get("founder") and therapist.get("name") != seo.get("founder"):
        notes.append(f"[{lang}] therapist.name „{therapist.get('name')}“ und "
                     f"seo.founder „{seo.get('founder')}“ sind verschieden – "
                     f"beide beschreiben dieselbe Person.")

    for image in (seo.get("og_image"), therapist.get("image")):
        if image and not (BASE_DIR / "static" / "img" / image).exists():
            notes.append(f"[{lang}] static/img/{image} fehlt.")

    title = strings.get("meta", {}).get("title", "")
    if len(title) > 60:
        notes.append(f"[{lang}] meta.title ist {len(title)} Zeichen lang – "
                     f"Suchmaschinen zeigen etwa 60.")
    description = strings.get("meta", {}).get("description", "")
    if not 120 <= len(description) <= 165:
        notes.append(f"[{lang}] meta.description ist {len(description)} Zeichen lang – "
                     f"gut sind 120 bis 165.")
    return notes


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
        home_url = page_url(site_url, base_path, lang)
        html = index.render(
            lang=lang,
            t=partial(translate, strings, fallback),
            s=strings,
            languages=LANGUAGES,
            default_language=DEFAULT_LANGUAGE,
            url_for=make_url_for(lang, site_url, base_path),
            page_url=make_page_url(lang, INDEX_FILE, site_url, base_path),
            json_ld=content.json_ld(content.structured_data(
                strings, fallback, home_url, home_url, lang, courses
            )),
            anchor_base="",  # auf der Startseite genügen reine Anker
            courses=courses,
            teaser=content.course_teaser(strings, courses),
            slides=content.practice_slides(strings, fallback),
            logos=content.funding_logos(strings, fallback),
            feedback=content.feedback_mailto(strings),
        )
        target = DIST_DIR / ("index.html" if lang == DEFAULT_LANGUAGE else f"{lang}/index.html")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        print(f"  ✓ {target.relative_to(BASE_DIR)}")

    # Impressum und Datenschutzerklärung
    legal = env.get_template("legal.html")
    for lang in LANGUAGES:
        strings = load_translations(lang)
        url_for = make_url_for(lang, site_url, base_path)
        for name, page in LEGAL_PAGES.items():
            body_file = BASE_DIR / "content" / f"{name}.{lang}.html"
            if not body_file.exists():
                body_file = BASE_DIR / "content" / f"{name}.{DEFAULT_LANGUAGE}.html"

            html = legal.render(
                lang=lang,
                t=partial(translate, strings, fallback),
                s=strings,
                languages=LANGUAGES,
                default_language=DEFAULT_LANGUAGE,
                url_for=url_for,
                page_url=make_page_url(lang, page["file"], site_url, base_path),
                # Ohne Kurse: die gehören auf die Startseite, nicht hierher.
                json_ld=content.json_ld(content.structured_data(
                    strings, fallback,
                    make_page_url(lang, page["file"], site_url, base_path)(lang, True),
                    page_url(site_url, base_path, lang), lang,
                    page_title=translate(strings, fallback, page["title_key"]),
                )),
                # Die Anker der Navigation zeigen auf die Startseite.
                anchor_base=url_for("home"),
                page_title=translate(strings, fallback, page["title_key"]),
                page_body=body_file.read_text(encoding="utf-8"),
            )
            target = DIST_DIR / (page["file"] if lang == DEFAULT_LANGUAGE
                                 else f"{lang}/{page['file']}")
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
        page_url=make_page_url(DEFAULT_LANGUAGE, INDEX_FILE, site_url, base_path,
                               root_relative=True),
        # Die Fehlerseite liegt nicht auf der Startseite: Anker brauchen den Pfad dorthin.
        anchor_base=make_url_for(DEFAULT_LANGUAGE, site_url, base_path, root_relative=True)("home"),
    )
    (DIST_DIR / "404.html").write_text(error_page, encoding="utf-8")
    print("  ✓ dist/404.html")

    write_sitemap(site_url, base_path)
    write_robots(site_url, base_path)
    write_llms_txt(site_url, base_path, fallback)
    print("  ✓ dist/sitemap.xml, dist/robots.txt, dist/llms.txt")

    # Dateien, die unverändert ins Wurzelverzeichnis gehören (.htaccess …)
    if WEBROOT_DIR.exists():
        for item in WEBROOT_DIR.iterdir():
            if item.is_file():
                shutil.copy2(item, DIST_DIR / item.name)
                print(f"  ✓ dist/{item.name}")

    notes = []
    for lang in LANGUAGES:
        notes.extend(check_seo(load_translations(lang), lang))
    if notes:
        print("\nHinweise zu den Suchmaschinen-Angaben:")
        for note in notes:
            print(f"  · {note}")

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
