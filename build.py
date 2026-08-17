"""Statischer Build der Startseite.

Rendert die Jinja-Templates in den Ordner ``dist/``:

    dist/index.html      → Startseite in der Standardsprache
    dist/<code>/…        → weitere Sprachen, sobald welche eingetragen sind
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
    python3 build.py --serve --host 0.0.0.0  # auch fürs Telefon im WLAN
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

# Sprachen der Seite. Ein Eintrag genügt – Sprachumschalter, hreflang-
# Verweise und die Sprachordner erscheinen erst ab der zweiten Sprache.
#
# Eine Sprache hinzufügen:
#   1. translations/<code>.json anlegen (am einfachsten als Kopie von de.json)
#   2. hier einen Eintrag ergänzen, z. B.
#        "en": {"label": "English", "short": "EN", "locale": "en_GB"},
#   3. dieselbe Zeile in app.py ergänzen
#   4. optional content/impressum.<code>.html und datenschutz.<code>.html
#      anlegen; fehlen sie, erscheint der deutsche Text
#
# ``locale`` steht im Kopf der Seite unter og:locale.
# Schritt für Schritt, mit den Stellen, die Mühe machen: README-Sprachen.md
LANGUAGES = {
    "de": {"label": "Deutsch", "short": "DE", "locale": "de_DE"},
}
# Themen der Seite. Der Schlüssel steht als ``data-theme`` am
# <html>-Element und wählt damit den passenden Block in style.css;
# ``auto`` ist kein eigener Block, sondern wird beim Laden zur
# Systemvorgabe aufgelöst. ``icon`` benennt das Symbol in
# templates/partials/theme-icons.html, die Beschriftung steht unter
# ``theme.options`` in den Sprachdateien.
#
# Ein Thema hinzufügen: Wertesatz und Block in style.css anlegen, hier
# eintragen, Symbol ergänzen, Beschriftung in jede Sprachdatei.
THEMES = {
    "auto": {"icon": "auto"},
    "light": {"icon": "sun"},
    "dark": {"icon": "moon"},
}
DEFAULT_THEME = "auto"

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


# ``lastmod`` in der Sitemap soll sagen, wann sich die Seite zuletzt
# geändert hat – nicht, wann zuletzt gebaut wurde. Stünde dort das
# Baudatum, meldete ein täglicher Lauf jeden Tag eine Änderung: gegenüber
# Suchmaschinen unwahr, und die Sitemap selbst wäre täglich eine geänderte
# Datei, die hochgeladen werden müsste.
#
# Deshalb merkt sich ``.build-state.json`` je Adresse eine Prüfsumme der
# gebauten Seite und das Datum, an dem sie zuletzt anders aussah. Fehlt die
# Datei – etwa nach einem frischen Klon –, gilt für alle Seiten das heutige
# Datum. Das ist nicht falsch: Dort steht die Seite gerade zum ersten Mal.
BUILD_STATE_FILE = BASE_DIR / ".build-state.json"


def load_build_state() -> dict:
    if not BUILD_STATE_FILE.exists():
        return {}
    try:
        data = json.loads(BUILD_STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def write_sitemap(site_url: str, base_path: str) -> None:
    today = date.today().isoformat()
    previous = load_build_state()
    state: dict[str, dict] = {}

    # Adresse und zugehörige Datei im Build – aus derselben Quelle, damit
    # die Sitemap nichts aufführt, was es nicht gibt.
    pages: list[tuple[str, Path]] = []
    for lang in LANGUAGES:
        folder = DIST_DIR if lang == DEFAULT_LANGUAGE else DIST_DIR / lang
        root = page_url(site_url, base_path, lang)
        pages.append((root, folder / INDEX_FILE))
        for page in LEGAL_PAGES.values():
            pages.append((root + page["file"], folder / page["file"]))

    entries = []
    for loc, path in pages:
        if not path.exists():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        before = previous.get(loc, {})
        lastmod = before.get("lastmod", today) if before.get("hash") == digest else today
        state[loc] = {"hash": digest, "lastmod": lastmod}
        entries.append(
            f"  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"  </url>"
        )

    (DIST_DIR / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries) + "\n"
        "</urlset>\n",
        encoding="utf-8",
    )
    BUILD_STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
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
    ]

    # Bekanntmachungen zuerst: Eine Schließzeit ist die Antwort, die im
    # Zweifel vor allen anderen zählt. Abgelaufene sind hier schon heraus.
    news = content.current_news(strings)
    if news:
        lines += [f"## {strings.get('news', {}).get('title', '')}", ""]
        lines += [f"- {item.get('title', '')}: {item.get('text', '')}"
                  for item in news]
        lines += [""]

    lines += [
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

    about = strings.get("about", {})
    if about:
        lines += ["", f"## {about.get('title', '')}", "", about.get("lead", "")]
        for paragraph in about.get("body", []):
            lines += ["", one_line(paragraph)]
        if about.get("examples"):
            lines += ["", f"{about.get('examples_title', '')}:"]
            lines += [f"- {item.get('title', '')}: {item.get('text', '')}"
                      for item in about["examples"]]
        if about.get("origin"):
            lines += ["", one_line(about["origin"])]

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
    ]
    # Weitere Sprachen erscheinen hier automatisch, sobald es sie gibt.
    lines += [
        f"- [{meta['label']}]({root}{code}/): dieselben Angaben auf "
        f"{meta['label']}"
        for code, meta in LANGUAGES.items() if code != DEFAULT_LANGUAGE
    ]
    lines += [
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

    # Ein unbrauchbares Datum lässt die Bekanntmachung dauerhaft stehen.
    # Das fällt ohne Hinweis erst auf, wenn sie längst überholt ist.
    for item in strings.get("news", {}).get("items", []):
        hide_from = item.get("hide_from")
        title = item.get("title", "")
        if not hide_from:
            notes.append(f"[{lang}] Bekanntmachung „{title}“ hat kein "
                         f"hide_from – sie bleibt stehen, bis sie jemand löscht.")
        elif not content.is_valid_date(hide_from):
            notes.append(f"[{lang}] Bekanntmachung „{title}“: hide_from "
                         f"„{hide_from}“ ist kein Datum im Format JJJJ-MM-TT – "
                         f"der Hinweis wird weiter angezeigt.")

    title = strings.get("meta", {}).get("title", "")
    if len(title) > 60:
        notes.append(f"[{lang}] meta.title ist {len(title)} Zeichen lang – "
                     f"Suchmaschinen zeigen etwa 60.")
    description = strings.get("meta", {}).get("description", "")
    if not 120 <= len(description) <= 165:
        notes.append(f"[{lang}] meta.description ist {len(description)} Zeichen lang – "
                     f"gut sind 120 bis 165.")
    return notes


# Blöcke, welche die Vorlagen unmittelbar durchlaufen (``s.hero`` und so
# fort). Für einzelne Texte gibt es den Rückfall auf die Standardsprache;
# eine Schleife über einen fehlenden Block lässt sich damit aber nicht
# retten – deshalb müssen diese Blöcke in jeder Sprachdatei stehen.
TEMPLATE_BLOCKS = ("hero", "about", "offer", "approach", "therapist",
                   "practice", "courses", "testimonials", "contact")


def check_translations(strings: dict, fallback: dict, lang: str) -> tuple[list[str], list[str]]:
    """Vergleicht eine Sprachdatei mit der Standardsprache.

    Gibt zwei Listen zurück: Fehler, die den Build anhalten, und Hinweise,
    die ihn nur begleiten. Die Trennung folgt der Technik – was die
    Vorlage durchläuft, muss da sein; alles Übrige holt der Rückfall.
    """
    if lang == DEFAULT_LANGUAGE:
        return [], []

    fehler = [
        f"[{lang}] Der Block „{block}“ fehlt in translations/{lang}.json – "
        f"die Vorlage durchläuft ihn und kann ihn nicht ersetzen."
        for block in TEMPLATE_BLOCKS
        if block in fallback and not isinstance(strings.get(block), dict)
    ]

    hinweise = [
        f"[{lang}] Der Block „{block}“ fehlt – dort erscheinen vorerst die "
        f"Texte der Standardsprache."
        for block in fallback
        if block not in TEMPLATE_BLOCKS and block not in strings
    ]

    # Kurse und Bekanntmachungen liest der Build unmittelbar aus der
    # aktiven Sprache; ein Rückfall findet hier bewusst nicht statt, damit
    # niemand versehentlich deutsche Termine in einer anderen Sprache
    # ausliefert. Ein leerer Abschnitt soll aber auffallen.
    for block in ("courses", "news"):
        if (block in strings and not strings.get(block, {}).get("items")
                and fallback.get(block, {}).get("items")):
            hinweise.append(
                f"[{lang}] „{block}.items“ ist leer – in dieser Sprache "
                f"erscheint der Abschnitt ohne Einträge."
            )
    return fehler, hinweise


def build(site_url: str = DEFAULT_SITE_URL, base_path: str = DEFAULT_BASE_PATH) -> Path:
    env = Environment(
        loader=FileSystemLoader(BASE_DIR / "templates"),
        autoescape=select_autoescape(["html"]),
    )
    fallback = load_translations(DEFAULT_LANGUAGE)

    # Vor dem ersten Rendern prüfen: Eine unvollständige Sprachdatei soll
    # eine verständliche Meldung geben, keinen Python-Fehlerbericht.
    fehler, sprachhinweise = [], []
    for lang in LANGUAGES:
        a, b = check_translations(load_translations(lang), fallback, lang)
        fehler.extend(a)
        sprachhinweise.extend(b)
    if fehler:
        print("Die Sprachdateien sind unvollständig:")
        for eintrag in fehler:
            print(f"  · {eintrag}")
        print("\nAm einfachsten ist es, die Datei als Kopie von "
              f"translations/{DEFAULT_LANGUAGE}.json anzulegen und darin zu "
              "übersetzen.\nSchritt für Schritt: README-Sprachen.md")
        raise SystemExit(1)

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
            themes=THEMES,
            default_theme=DEFAULT_THEME,
            url_for=make_url_for(lang, site_url, base_path),
            page_url=make_page_url(lang, INDEX_FILE, site_url, base_path),
            json_ld=content.json_ld(content.structured_data(
                strings, fallback, home_url, home_url, lang, courses
            )),
            anchor_base="",  # auf der Startseite genügen reine Anker
            courses=courses,
            news=content.current_news(strings),
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
                themes=THEMES,
                default_theme=DEFAULT_THEME,
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
        themes=THEMES,
        default_theme=DEFAULT_THEME,
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

    # Wann ändert sich die Seite das nächste Mal von allein? Das beantwortet
    # die Frage, ob ein täglicher Lauf demnächst etwas zu tun bekommt.
    upcoming = content.next_scheduled_change(fallback)
    if upcoming:
        tage = "morgen" if upcoming["days"] == 1 else f"in {upcoming['days']} Tagen"
        print(f"\nNächste Änderung durch Zeitablauf: {upcoming['date'].strftime('%d.%m.%Y')} "
              f"({tage}) – {upcoming['text']}")
    else:
        print("\nKeine zeitgesteuerte Änderung mehr offen: Alle Kurse und "
              "Bekanntmachungen sind ohne Enddatum oder bereits abgelaufen.")

    if sprachhinweise:
        print("\nHinweise zu den Sprachdateien:")
        for note in sprachhinweise:
            print(f"  · {note}")

    notes = []
    for lang in LANGUAGES:
        notes.extend(check_seo(load_translations(lang), lang))
    if notes:
        print("\nHinweise zu den Suchmaschinen-Angaben:")
        for note in notes:
            print(f"  · {note}")

    return DIST_DIR


def local_addresses() -> list[str]:
    """Adressen, unter denen dieser Rechner im Netzwerk erreichbar ist.

    Gedacht für ``--host 0.0.0.0``: Dann steht in der Ausgabe gleich die
    Adresse, die man am Telefon eintippen kann.
    """
    import socket

    found = []
    try:
        # Verbindet nichts, ermittelt aber die Adresse der Schnittstelle,
        # über die es hinausginge.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("192.0.2.1", 80))  # reservierte Test-Adresse
            found.append(probe.getsockname()[0])
    except OSError:
        pass
    return found


def serve(directory: Path, port: int = 8000, host: str = "127.0.0.1") -> None:
    import functools
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(directory))
    with ThreadingHTTPServer((host, port), handler) as httpd:
        print(f"\nhttp://127.0.0.1:{port}/  (Strg+C beendet den Server)")
        if host not in ("127.0.0.1", "localhost"):
            for address in local_addresses():
                print(f"http://{address}:{port}/  aus dem gleichen Netzwerk, "
                      f"etwa vom Telefon")
            print("\nDer Server ist damit im ganzen Netzwerk erreichbar – "
                  "nur zum Ausprobieren gedacht.")
        httpd.serve_forever()


def main() -> None:
    config_url, config_base = read_site_config()

    parser = argparse.ArgumentParser(description="Statischen Build der Startseite erzeugen.")
    parser.add_argument("--serve", action="store_true", help="nach dem Build lokal ausliefern")
    parser.add_argument("--port", type=int, default=8000, help="Port für --serve")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Adresse für --serve; 0.0.0.0 macht die Vorschau "
                             "im ganzen Netzwerk erreichbar, etwa fürs Telefon")
    parser.add_argument("--site-url", default=config_url, help="Domain der Seite, z. B. https://www.praxis.de")
    parser.add_argument("--base-path", default=config_base, help="Unterverzeichnis auf dem Webspace, Standard /")
    args = parser.parse_args()

    print(f"Baue Startseite für {args.site_url} …")
    out = build(args.site_url, args.base_path)
    print(f"Fertig: {out}")

    if args.serve:
        serve(out, args.port, args.host)


if __name__ == "__main__":
    main()
