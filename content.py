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

import json
import re
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


def build_mailto(email: str, subject: str, body: str = "") -> str:
    """Setzt eine mailto-Adresse zusammen und kodiert sie korrekt.

    Zeilenumbrüche gehören als CRLF hinein, alles Übrige prozentkodiert.
    """
    parts = ["subject=" + quote(subject, safe="")]
    if body:
        parts.append("body=" + quote(body.replace("\n", "\r\n"), safe=""))
    return f"mailto:{email}?" + "&".join(parts)


def request_mailto(strings: dict, title: str, shown_date: str) -> str:
    """Baut die vorbereitete E-Mail für eine Kursanfrage.

    Betreff und Textkörper stehen unter ``courses.request`` in den
    Übersetzungsdateien und enthalten die Platzhalter ``{title}`` und
    ``{date}``. Der Textkörper nennt bereits die Felder, die wir brauchen –
    sonst kommt eine leere Mail an, und es folgt eine Rückfragerunde.
    """
    request = strings.get("courses", {}).get("request", {})
    email = strings.get("contact", {}).get("email", "")

    def fill(pattern: str) -> str:
        return pattern.replace("{title}", title).replace("{date}", shown_date)

    return build_mailto(email, fill(request.get("subject", title)),
                        fill(request.get("body", "")))


def feedback_mailto(strings: dict) -> str:
    """Vorbereitete E-Mail für eine Rückmeldung.

    Der Textkörper fragt bereits ab, was wir zum Veröffentlichen brauchen:
    den Text, die gewünschte Namensnennung und die ausdrückliche
    Zustimmung. Rückmeldungen erscheinen nicht automatisch auf der Seite –
    sie werden von Hand in die Sprachdateien übernommen.
    """
    request = strings.get("testimonials", {}).get("request", {})
    email = strings.get("contact", {}).get("email", "")
    return build_mailto(email, request.get("subject", ""), request.get("body", ""))


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


# --------------------------------------------------------------------------
# Strukturierte Daten (JSON-LD)
# --------------------------------------------------------------------------
# Suchmaschinen und Antwortsysteme lesen den sichtbaren Text nur ungenau.
# Die Angaben unten stehen deshalb zusätzlich maschinenlesbar im Kopf der
# Seite – nach dem Vokabular von schema.org. Alle Werte stammen aus den
# Übersetzungsdateien; hier steht nichts, was nicht auch auf der Seite steht.
# Leere Felder werden weggelassen: eine fehlende Angabe ist besser als eine
# erfundene.

_PRICE_PATTERN = re.compile(r"(\d+(?:[.,]\d+)?)")

_CURRENCIES = {"€": "EUR", "EUR": "EUR", "CHF": "CHF", "$": "USD", "£": "GBP"}


def _prune(value):
    """Entfernt leere Felder aus verschachtelten Strukturen."""
    if isinstance(value, dict):
        cleaned = {k: _prune(v) for k, v in value.items()}
        return {k: v for k, v in cleaned.items() if v not in (None, "", [], {})}
    if isinstance(value, list):
        cleaned = [_prune(v) for v in value]
        return [v for v in cleaned if v not in (None, "", [], {})]
    return value


def parse_price(text: str) -> dict:
    """Zerlegt eine Preisangabe wie ``240 €`` in Betrag und Währung.

    Ohne erkennbare Zahl kommt ein leeres Ergebnis zurück – dann entfällt
    die Preisangabe in den strukturierten Daten, statt eine falsche zu
    behaupten.
    """
    if not text:
        return {}
    match = _PRICE_PATTERN.search(str(text))
    if not match:
        return {}
    currency = next(
        (code for symbol, code in _CURRENCIES.items() if symbol in str(text)), "EUR"
    )
    return {"price": match.group(1).replace(",", "."), "currency": currency}


def _postal_address(seo: dict) -> dict:
    return {
        "@type": "PostalAddress",
        "streetAddress": seo.get("street", ""),
        "postalCode": seo.get("postal_code", ""),
        "addressLocality": seo.get("city", ""),
        "addressRegion": seo.get("region", ""),
        "addressCountry": seo.get("country", ""),
    }


def _opening_hours(seo: dict) -> list[dict]:
    hours = []
    for entry in seo.get("opening_hours", []):
        days = entry.get("days") or []
        if not days:
            continue
        hours.append({
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": [f"https://schema.org/{day}" for day in days],
            "opens": entry.get("opens", ""),
            "closes": entry.get("closes", ""),
        })
    return hours


def _course_nodes(strings: dict, courses: list[dict], practice_id: str,
                  site_url: str, seo: dict, lang: str) -> list[dict]:
    """Ein ``Course``-Eintrag je kommendem Kurs.

    Die Kurse stammen aus derselben Liste wie der sichtbare Abschnitt, also
    ohne abgelaufene Termine. Ein Kurs ohne Startdatum bekommt keine
    ``CourseInstance`` – ein Termin, den wir nicht kennen, wird auch nicht
    behauptet.
    """
    nodes = []
    for course in courses:
        title = str(course.get("title", ""))
        if not title:
            continue

        price = parse_price(course.get("price", ""))
        instance = {
            "@type": "CourseInstance",
            "courseMode": "Onsite",
            "startDate": course.get("start_date", ""),
            "location": {
                "@type": "Place",
                "name": strings.get("brand", {}).get("name", ""),
                "address": _postal_address(seo),
            },
        }
        nodes.append({
            "@type": "Course",
            "@id": f"{site_url}#kurs-{len(nodes) + 1}",
            "name": title,
            "description": course.get("text", ""),
            "provider": {"@id": practice_id},
            "inLanguage": lang,
            "hasCourseInstance": instance if course.get("start_date") else None,
            "offers": {
                "@type": "Offer",
                "price": price.get("price", ""),
                "priceCurrency": price.get("currency", ""),
                "availability": "https://schema.org/InStock",
                "url": site_url + "#courses",
            } if price else None,
        })
    return nodes


def structured_data(strings: dict, fallback: dict, page_url: str, site_url: str,
                    lang: str, courses: list[dict] | None = None,
                    page_title: str = "") -> dict:
    """Baut den JSON-LD-Graphen für eine Seite.

    ``page_url`` ist die absolute Adresse der gerade gebauten Seite,
    ``site_url`` die der Startseite in derselben Sprache – Kurse und
    Abschnitte werden von den Rechtsseiten aus dorthin verlinkt.
    """
    seo = strings.get("seo") or fallback.get("seo") or {}
    contact = strings.get("contact", {})
    brand = strings.get("brand", {})
    meta = strings.get("meta", {})

    site_url = site_url.rstrip("/") + "/"
    practice_id = f"{site_url}#praxis"
    person_id = f"{site_url}#gruender"

    practice = {
        "@type": ["Physiotherapy", "MedicalBusiness", "LocalBusiness"],
        "@id": practice_id,
        "name": brand.get("name", ""),
        "legalName": seo.get("legal_name", ""),
        "description": meta.get("description", ""),
        "url": site_url,
        "telephone": contact.get("phone", ""),
        "email": contact.get("email", ""),
        "address": _postal_address(seo),
        # Koordinaten nur, wenn beide hinterlegt sind – eine halbe Angabe
        # wäre schlimmer als keine.
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": seo.get("latitude", ""),
            "longitude": seo.get("longitude", ""),
        } if seo.get("latitude") and seo.get("longitude") else None,
        "openingHoursSpecification": _opening_hours(seo),
        "areaServed": [
            {"@type": "Place", "name": name} for name in seo.get("area_served", [])
        ],
        "priceRange": seo.get("price_range", ""),
        "foundingDate": seo.get("founding_year", ""),
        "medicalSpecialty": "https://schema.org/PhysicalTherapy",
        "knowsAbout": seo.get("keywords", []),
        "sameAs": seo.get("same_as", []),
        "founder": {"@id": person_id},
        "employee": {"@id": person_id},
        "logo": site_url + "static/img/logo.png",
        "image": site_url + "static/img/logo.png",
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": strings.get("offer", {}).get("title", ""),
            "itemListElement": [
                {
                    "@type": "Offer",
                    "itemOffered": {
                        "@type": "Service",
                        "name": item.get("title", ""),
                        "description": item.get("text", ""),
                        "serviceType": "Physiotherapie",
                        "provider": {"@id": practice_id},
                    },
                }
                for item in strings.get("offer", {}).get("items", [])
            ],
        },
    }

    person = {
        "@type": "Person",
        "@id": person_id,
        "name": seo.get("founder", ""),
        "jobTitle": seo.get("founder_role", ""),
        "worksFor": {"@id": practice_id},
        "knowsAbout": seo.get("keywords", []),
    }

    website = {
        "@type": "WebSite",
        "@id": f"{site_url}#website",
        "url": site_url,
        "name": brand.get("name", ""),
        "inLanguage": lang,
        "publisher": {"@id": practice_id},
    }

    webpage = {
        "@type": "WebPage",
        "@id": page_url,
        "url": page_url,
        "name": page_title or meta.get("title", ""),
        "description": meta.get("description", ""),
        "inLanguage": lang,
        "isPartOf": {"@id": f"{site_url}#website"},
        "about": {"@id": practice_id},
    }

    graph = [practice, person, website, webpage]
    graph.extend(_course_nodes(strings, courses or [], practice_id, site_url, seo, lang))

    return _prune({"@context": "https://schema.org", "@graph": graph})


def json_ld(data: dict) -> str:
    """Serialisiert den Graphen für ein ``<script>``-Element.

    ``<``, ``>`` und ``&`` werden als Unicode-Escape geschrieben. Damit kann
    ein Inhalt aus den Sprachdateien das Script-Element nicht vorzeitig
    beenden, auch ohne HTML-Escaping durch Jinja.
    """
    text = json.dumps(data, ensure_ascii=False, indent=2)
    return (
        text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    )
