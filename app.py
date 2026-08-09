"""Spiraldynamik Praxis – Webserver.

Kleiner Flask-Server, der die Startseite ausliefert und die
Internationalisierung (Deutsch als Standard, Englisch zur Auswahl)
aus JSON-Dateien im Ordner ``translations/`` bereitstellt.
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

BASE_DIR = Path(__file__).resolve().parent
TRANSLATIONS_DIR = BASE_DIR / "translations"

DEFAULT_LANGUAGE = "de"
LANGUAGES = {
    "de": {"label": "Deutsch", "short": "DE"},
    "en": {"label": "English", "short": "EN"},
}
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

    response = make_response(
        render_template(
            "index.html",
            lang=lang,
            t=lambda key, default=None: translate(key, lang, default),
            s=strings,
            languages=LANGUAGES,
            default_language=DEFAULT_LANGUAGE,
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
