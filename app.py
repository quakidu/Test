"""Körper im Einklang – Webserver.

Kleiner Flask-Server, der die Startseite ausliefert und die Texte aus
JSON-Dateien im Ordner ``translations/`` bereitstellt. Zurzeit gibt es nur
Deutsch; weitere Sprachen brauchen nur eine weitere JSON-Datei und einen
Eintrag in ``LANGUAGES``.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from flask import (
    Flask,
    abort,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)

import content

BASE_DIR = Path(__file__).resolve().parent
TRANSLATIONS_DIR = BASE_DIR / "translations"
CONTENT_DIR = BASE_DIR / "content"

# Rechtsseiten: Adresse, Textbaustein unter content/ und Titelschlüssel.
LEGAL_PAGES = {
    "impressum": {"title_key": "legal.imprint"},
    "datenschutz": {"title_key": "legal.privacy"},
}

DEFAULT_LANGUAGE = "de"

# Sprachen der Seite – dieselbe Liste wie in build.py. Ein Eintrag genügt;
# wie eine weitere Sprache hinzukommt, steht dort im Kommentar und
# Schritt für Schritt in README-Sprachen.md.
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

LANGUAGE_COOKIE = "lang"
LANGUAGE_COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # ein Jahr

# Deutsch ist der Standard. Auf True gesetzt, wird beim allerersten Besuch
# zusätzlich der Accept-Language-Header des Browsers berücksichtigt.
AUTO_DETECT_BROWSER_LANGUAGE = False

app = Flask(__name__)


# --------------------------------------------------------------------------
# Internationalisierung
# --------------------------------------------------------------------------
@lru_cache(maxsize=None)
def load_translations(lang: str) -> dict:
    """Lädt die Übersetzungsdatei einer Sprache (gecached)."""
    path = TRANSLATIONS_DIR / f"{lang}.json"
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _lookup(data: dict, key: str):
    """Löst einen Punkt-Schlüssel wie ``hero.title`` auf."""
    node = data
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def translate(key: str, lang: str = DEFAULT_LANGUAGE, default=None):
    """Übersetzt ``key``; fällt auf Deutsch und zuletzt auf den Schlüssel zurück."""
    value = _lookup(load_translations(lang), key)
    if value is None and lang != DEFAULT_LANGUAGE:
        value = _lookup(load_translations(DEFAULT_LANGUAGE), key)
    if value is None:
        return key if default is None else default
    return value


def resolve_language(url_lang: str | None) -> str:
    """Ermittelt die aktive Sprache: URL > Cookie > (Browser) > Standard."""
    if url_lang in LANGUAGES:
        return url_lang

    cookie_lang = request.cookies.get(LANGUAGE_COOKIE)
    if cookie_lang in LANGUAGES:
        return cookie_lang

    if AUTO_DETECT_BROWSER_LANGUAGE:
        browser_lang = request.accept_languages.best_match(LANGUAGES.keys())
        if browser_lang:
            return browser_lang

    return DEFAULT_LANGUAGE


# --------------------------------------------------------------------------
# Routen
# --------------------------------------------------------------------------
def render_home(lang: str):
    strings = load_translations(lang)
    # Kommende Kurse und der Hinweis oben stammen aus derselben Liste.
    courses = content.upcoming_courses(strings)

    response = make_response(
        render_template(
            "index.html",
            lang=lang,
            t=lambda key, default=None: translate(key, lang, default),
            s=strings,
            languages=LANGUAGES,
            default_language=DEFAULT_LANGUAGE,
            themes=THEMES,
            default_theme=DEFAULT_THEME,
            anchor_base="",
            page_url=lambda code, external=False: (
                url_for("home", _external=external) if code == DEFAULT_LANGUAGE
                else url_for("home_localized", lang_code=code, _external=external)
            ),
            json_ld=content.json_ld(content.structured_data(
                strings,
                load_translations(DEFAULT_LANGUAGE),
                url_for("home", _external=True),
                url_for("home", _external=True),
                lang,
                courses,
            )),
            courses=courses,
            news=content.current_news(strings),
            teaser=content.course_teaser(strings, courses),
            slides=content.practice_slides(strings, load_translations(DEFAULT_LANGUAGE)),
            logos=content.funding_logos(strings, load_translations(DEFAULT_LANGUAGE)),
            feedback=content.feedback_mailto(strings),
        )
    )
    response.set_cookie(
        LANGUAGE_COOKIE,
        lang,
        max_age=LANGUAGE_COOKIE_MAX_AGE,
        samesite="Lax",
    )
    return response


@app.route("/")
def home():
    """Startseite in der zuletzt gewählten bzw. der Standardsprache."""
    return render_home(resolve_language(None))


@app.route("/<lang_code>/")
@app.route("/<lang_code>")
def home_localized(lang_code: str):
    """Startseite unter einem expliziten Sprachpräfix, z. B. ``/en``."""
    if lang_code not in LANGUAGES:
        abort(404)
    if lang_code == DEFAULT_LANGUAGE:
        return redirect(url_for("home"))
    return render_home(lang_code)


def render_legal(lang: str, page: str):
    """Rechtsseite in der gewünschten Sprache; Text kommt aus content/."""
    strings = load_translations(lang)
    body = CONTENT_DIR / f"{page}.{lang}.html"
    if not body.exists():
        body = CONTENT_DIR / f"{page}.{DEFAULT_LANGUAGE}.html"

    def page_url(code: str, external: bool = False) -> str:
        if code == DEFAULT_LANGUAGE:
            return url_for("legal", page=page, _external=external)
        return url_for("legal_localized", lang_code=code, page=page, _external=external)

    response = make_response(
        render_template(
            "legal.html",
            lang=lang,
            t=lambda key, default=None: translate(key, lang, default),
            s=strings,
            languages=LANGUAGES,
            default_language=DEFAULT_LANGUAGE,
            themes=THEMES,
            default_theme=DEFAULT_THEME,
            anchor_base=url_for("home"),
            page_url=page_url,
            # Ohne Kurse: die gehören auf die Startseite, nicht hierher.
            json_ld=content.json_ld(content.structured_data(
                strings,
                load_translations(DEFAULT_LANGUAGE),
                page_url(lang, True),
                url_for("home", _external=True),
                lang,
                page_title=translate(LEGAL_PAGES[page]["title_key"], lang),
            )),
            page_title=translate(LEGAL_PAGES[page]["title_key"], lang),
            page_body=body.read_text(encoding="utf-8"),
        )
    )
    response.set_cookie(LANGUAGE_COOKIE, lang, max_age=LANGUAGE_COOKIE_MAX_AGE,
                        samesite="Lax")
    return response


# Die Adressen tragen bewusst die Endung .html – so sind sie identisch mit
# denen des statischen Builds, und /impressum kollidiert nicht mit dem
# Sprachpräfix /<lang_code>.
@app.route("/<page>.html")
def legal(page: str):
    """Rechtsseite in der Standardsprache, z. B. /impressum.html."""
    if page not in LEGAL_PAGES:
        abort(404)
    return render_legal(resolve_language(None), page)


@app.route("/<lang_code>/<page>.html")
def legal_localized(lang_code: str, page: str):
    """Rechtsseite unter einem Sprachpräfix, z. B. /en/impressum.html."""
    if lang_code not in LANGUAGES or page not in LEGAL_PAGES:
        abort(404)
    if lang_code == DEFAULT_LANGUAGE:
        return redirect(url_for("legal", page=page))
    return render_legal(lang_code, page)


@app.route("/api/translations/<lang_code>.json")
def api_translations(lang_code: str):
    """Übersetzungen als JSON – erlaubt das Umschalten ohne Reload."""
    if lang_code not in LANGUAGES:
        abort(404)
    return jsonify(load_translations(lang_code))


@app.errorhandler(404)
def not_found(_error):
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
