"""Aufbereitung der Kursdaten – gemeinsam genutzt von app.py und build.py.

Die Kursliste in ``translations/*.json`` ist die einzige Quelle. Daraus
ergeben sich

* die Reihenfolge der Kurse (nach Startdatum),
* welcher Kurs als nächster hervorgehoben wird,
* das angezeigte Datum in der jeweiligen Sprache,
* der Hinweis im Kopfbereich der Startseite.

Abgelaufene Kurse fallen automatisch heraus. Damit kann die Seite keinen
Termin bewerben, der schon vorbei ist, und der Hinweis oben kann der
Kursliste nicht widersprechen.

Maßgeblich ist ``start_date`` im Format JJJJ-MM-TT. Der Tag des Kursstarts
zählt noch als kommend.
"""

from __future__ import annotations

from datetime import date
from urllib.parse import quote


def format_date(iso_date: str, strings: dict, today: date | None = None) -> str:
    """Formatiert ein ISO-Datum in der Sprache der übergebenen Texte.

    Die Monatsnamen und das Muster stehen unter ``formats`` in den
    Übersetzungsdateien – im Code steht kein sprachabhängiger Text.
    Das Jahr erscheint nur, wenn der Termin nicht im laufenden Jahr liegt.
    """
    today = today or date.today()
    formats = strings.get("formats", {})
    months = formats.get("months") or []

    try:
        year, month, day = (int(part) for part in iso_date.split("-"))
        parsed = date(year, month, day)
    except (ValueError, AttributeError):
        # Unbrauchbares Datum lieber unverändert anzeigen als die Seite zerlegen.
        return iso_date

    month_name = months[parsed.month - 1] if len(months) == 12 else str(parsed.month)
    pattern = (
        formats.get("date", "{day}. {month}")
        if parsed.year == today.year
        else formats.get("date_with_year", "{day}. {month} {year}")
    )
    return (
        pattern.replace("{day}", str(parsed.day))
        .replace("{month}", month_name)
        .replace("{year}", str(parsed.year))
    )


def request_mailto(strings: dict, title: str, shown_date: str) -> str:
    """Baut die vorbereitete E-Mail für eine Kursanfrage.

    Betreff und Textkörper stehen unter ``courses.request`` in den
    Übersetzungsdateien und enthalten die Platzhalter ``{title}`` und
    ``{date}``. Der Textkörper nennt bereits die Felder, die wir brauchen –
    sonst kommt eine leere Mail an, und es folgt eine Rückfragerunde.
    """
    courses = strings.get("courses", {})
    request = courses.get("request", {})
    email = strings.get("contact", {}).get("email", "")

    def fill(pattern: str) -> str:
        return pattern.replace("{title}", title).replace("{date}", shown_date)

    subject = fill(request.get("subject", title))
    # Zeilenumbrüche im mailto gehören als CRLF kodiert.
    body = fill(request.get("body", "")).replace("\n", "\r\n")

    parts = ["subject=" + quote(subject, safe="")]
    if body:
        parts.append("body=" + quote(body, safe=""))
    return f"mailto:{email}?" + "&".join(parts)


def sort_key(course: dict) -> str:
    """Sortierschlüssel: ISO-Daten lassen sich als Text vergleichen."""
    return str(course.get("start_date", "9999-12-31"))


def upcoming_courses(strings: dict, today: date | None = None) -> list[dict]:
    """Kommende Kurse, nach Startdatum sortiert, mit angezeigtem Datum.

    Der erste Eintrag ist damit immer der nächste Kurs; die Vorlage hebt ihn
    über ``loop.first`` hervor. Kurse ohne ``start_date`` bleiben stehen und
    wandern ans Ende – so verschwindet nichts versehentlich.
    """
    today = today or date.today()
    limit = today.isoformat()

    courses = []
    for course in strings.get("courses", {}).get("items", []):
        start = course.get("start_date")
        if start and str(start) < limit:
            continue  # Termin liegt in der Vergangenheit
        prepared = dict(course)
        prepared["date"] = format_date(start, strings, today) if start else ""
        prepared["mailto"] = request_mailto(
            strings, str(prepared.get("title", "")), prepared["date"]
        )
        courses.append(prepared)

    return sorted(courses, key=sort_key)


def practice_slides(strings: dict, fallback: dict) -> list[dict]:
    """Bilder der Diashow.

    Die Dateinamen stehen nur in der Standardsprache – ein Foto ist nicht
    sprachabhängig. Beschreibung und Bildunterschrift kommen aus der aktiven
    Sprache, mit Rückfall auf die Standardsprache.
    """
    base = fallback.get("practice", {}).get("slides", [])
    texts = strings.get("practice", {}).get("slides", [])

    slides = []
    for index, entry in enumerate(base):
        image = entry.get("image")
        if not image:
            continue
        text = texts[index] if index < len(texts) else entry
        slides.append({
            "image": image,
            "alt": text.get("alt", entry.get("alt", "")),
            "caption": text.get("caption", entry.get("caption", "")),
        })
    return slides


def funding_logos(strings: dict, fallback: dict) -> list[dict]:
    """Logos der Förderer – wie bei den Praxisbildern.

    Dateiname und Verweis stehen in der Standardsprache, die
    Bildbeschreibung kommt aus der aktiven Sprache.
    """
    base = fallback.get("funding", {}).get("logos", [])
    texts = strings.get("funding", {}).get("logos", [])

    logos = []
    for index, entry in enumerate(base):
        image = entry.get("image")
        if not image:
            continue
        text = texts[index] if index < len(texts) else entry
        logos.append({
            "image": image,
            "alt": text.get("alt", entry.get("alt", "")),
            "url": entry.get("url", ""),
        })
    return logos


def course_teaser(strings: dict, courses: list[dict]) -> dict | None:
    """Hinweis auf den nächsten Kurs für den Kopfbereich.

    Gibt ``None`` zurück, wenn kein Kurs ansteht – die Vorlage lässt den
    Hinweis dann weg, statt einen leeren Platzhalter zu zeigen.
    """
    if not courses:
        return None

    teaser = strings.get("hero", {}).get("course_teaser", {})
    pattern = teaser.get("text", "{title} – {date}")
    next_course = courses[0]

    return {
        "label": teaser.get("label", ""),
        "text": (
            pattern.replace("{title}", str(next_course.get("title", "")))
            .replace("{date}", str(next_course.get("date", "")))
        ),
        "link": teaser.get("link", ""),
    }
