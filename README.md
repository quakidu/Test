# Körper im Einklang – Homepage

Startseite der Praxis für ganzheitliche Therapie: Therapieangebot und Kurse
nach dem Konzept der Spiraldynamik, zweisprachig (Deutsch als Standard,
Englisch zur Auswahl), optimiert für Desktop und mobile Geräte.

## Technik

| Bereich       | Umsetzung                                                          |
| ------------- | ------------------------------------------------------------------ |
| Python        | `app.py` (Flask-Server), `build.py` (statischer Build)              |
| HTML          | Jinja2-Templates in `templates/`                                    |
| CSS           | `static/css/style.css` – eigene Design-Tokens, Grid/Flexbox         |
| JavaScript    | `static/js/main.js` – ohne Framework, keine externen Abhängigkeiten |
| JSON          | `translations/de.json`, `translations/en.json` – alle Texte         |

Alle Inhalte liegen in den JSON-Dateien. Templates, CSS und JS enthalten
keinen fest verdrahteten Text – neue Sprachen brauchen nur eine weitere
JSON-Datei plus einen Eintrag in `LANGUAGES`.

## Projektstruktur

```
app.py                  Flask-Server (dynamisch)
build.py                Statischer Build nach dist/
requirements.txt        Abhängigkeiten
templates/
  base.html             Grundgerüst (Head, Meta, hreflang)
  index.html            Startseite
  partials/header.html  Kopfbereich mit Logo links oben
  partials/footer.html  Fußbereich
static/
  css/style.css
  js/main.js
  img/logo.png          Logo der Praxis (Original, transparent)
  img/logo-dark.png     aufgehellte Fassung für das dunkle Farbschema
  img/logo-mark.png     quadratisches Signet (Favicon)
  img/logo-mark-dark.png
translations/
  de.json  en.json
tools/
  prepare-logo.py       leitet die Logo-Varianten aus logo.png ab
```

## Starten

### Variante 1 – Flask (dynamisch)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Danach im Browser: <http://127.0.0.1:5000/>

Routen:

| Route                        | Bedeutung                                  |
| ---------------------------- | ------------------------------------------ |
| `/`                          | Startseite, Standardsprache Deutsch        |
| `/en`                        | Startseite auf Englisch                    |
| `/api/translations/de.json`  | Übersetzungen als JSON                     |

Die zuletzt gewählte Sprache wird in einem Cookie (`lang`) gespeichert.
Soll beim ersten Besuch zusätzlich die Browsersprache ausgewertet werden,
in `app.py` `AUTO_DETECT_BROWSER_LANGUAGE = True` setzen.

### Variante 2 – statischer Build (nur Jinja2 nötig)

```bash
python3 build.py --serve
```

Erzeugt `dist/index.html` (Deutsch), `dist/en/index.html` (Englisch) und
`dist/static/` und liefert das Ergebnis unter <http://127.0.0.1:8000/> aus.
Der Ordner `dist/` lässt sich unverändert auf jeden Webspace kopieren.

Für korrekte `hreflang`-Angaben die eigene Domain mitgeben:

```bash
python3 build.py --site-url https://ihre-domain.ch
```

## Inhalte anpassen

* **Texte, Adresse, Angebote:** `translations/de.json` und
  `translations/en.json`. Beide Dateien haben dieselbe Struktur; fehlt ein
  Schlüssel im Englischen, greift automatisch der deutsche Text.
* **Angebote ergänzen:** einen weiteren Eintrag in `offer.items` anlegen und
  `"type"` auf `"therapy"` oder `"course"` setzen – der Filter auf der Seite
  richtet sich danach.
* **Farben:** die Design-Tokens ganz oben in `static/css/style.css`
  (`--green-*`). Das dunkle Farbschema nutzt dieselben Tokens.
* **Logo:** `static/img/logo.png` austauschen (PNG mit transparentem
  Hintergrund) und danach einmal

  ```bash
  python3 tools/prepare-logo.py
  ```

  ausführen. Das Skript leitet daraus die aufgehellte Fassung für das dunkle
  Farbschema sowie das quadratische Signet fürs Favicon ab. Es kommt ohne
  Zusatzpakete aus. Der Schriftzug steckt in der Bilddatei – im Kopfbereich
  steht deshalb bewusst kein zusätzlicher Text daneben.

## Umgesetzte Details

* Logo links oben, mit der Startseite verlinkt
* Dezentes Grün als Leitfarbe, helles und dunkles Farbschema
* Responsiv ab ca. 320 px: Burger-Menü, gestapelte Raster, flexible Typografie
* Sprachumschalter im Kopfbereich, `hreflang`-Verweise im `<head>`
* Sticky Header, Scroll-Reveal, Scrollspy, animierte Kennzahlen,
  Filter für Therapien/Kurse
* Ohne JavaScript bleiben alle Inhalte sichtbar und lesbar
* `prefers-reduced-motion` schaltet Animationen ab
* Sprungmarke zum Inhalt, sichtbare Fokusrahmen, ARIA-Attribute am Menü

## Hinweis

Adresse, Telefonnummer, E-Mail und Kennzahlen sind Platzhalter und vor dem
Veröffentlichen zu ersetzen. Impressum und Datenschutz sind noch leere Links.

Das gelieferte Logo ist 200 × 42 Pixel groß. Im Kopfbereich wird es 32 Pixel
hoch dargestellt, was der Auflösung entspricht – auf Bildschirmen mit hoher
Pixeldichte wirkt es dadurch leicht weich. Eine größere Fassung (etwa
600 Pixel Breite) oder das Original als Vektordatei würde das beheben: Datei
als `static/img/logo.png` ablegen, `python3 tools/prepare-logo.py` ausführen,
fertig.
