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
app.py                  Flask-Server (nur für die lokale Arbeit)
build.py                Statischer Build nach dist/
deploy.py               lädt dist/ per FTPS auf den Webspace
deploy.ini.example      Vorlage für Domain und FTP-Zugang
content.py              Kursauswahl und Datumsformate
requirements.txt        Abhängigkeiten
templates/
  base.html             Grundgerüst (Head, Meta, hreflang)
  index.html            Startseite
  legal.html            Rahmen für Impressum und Datenschutz
  404.html              Fehlerseite
  partials/header.html  Kopfbereich mit Logo links oben
  partials/footer.html  Fußbereich
content/
  impressum.de.html     Impressum, deutsch  (dazu .en.html)
  datenschutz.de.html   Datenschutz, deutsch (dazu .en.html)
static/
  css/style.css
  js/main.js
  img/logo.png          Logo der Praxis (Original, transparent)
  img/logo-dark.png     aufgehellte Fassung für das dunkle Farbschema
  img/logo-mark.png     quadratisches Signet (Favicon)
  img/logo-mark-dark.png
translations/
  de.json  en.json
webroot/
  .htaccess             Apache-Konfiguration, kommt unverändert nach dist/
tools/
  prepare-logo.py       leitet die Logo-Varianten aus logo.png ab
```

## Starten

### Variante 1 – Flask (nur lokal)

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

### Variante 2 – statischer Build (das, was veröffentlicht wird)

```bash
python3 build.py --serve
```

Erzeugt den kompletten Ordner `dist/` und liefert ihn unter
<http://127.0.0.1:8000/> aus. Genau dieser Ordner geht später auf den
Webspace – siehe „Veröffentlichen bei Alfahosting“.

Die Domain wird aus `deploy.ini` gelesen. Ohne diese Datei oder für einen
einzelnen Lauf lässt sie sich auch direkt angeben:

```bash
python3 build.py --site-url https://www.ihre-domain.de
```

## Veröffentlichen bei Alfahosting

Auf dem normalen Webspace von Alfahosting läuft **kein Python**. Der
Flask-Server aus `app.py` ist deshalb nur für die Arbeit am eigenen Rechner
gedacht. Ins Netz geht der statische Build: reine HTML-, CSS-, JavaScript-
und Bilddateien, die jeder Webspace ausliefern kann.

### Einmalig einrichten

```bash
cp deploy.ini.example deploy.ini
```

Dann `deploy.ini` ausfüllen. Die Werte stehen im Kundenmenü von
Alfahosting:

| Eintrag              | Wo zu finden                                              |
| -------------------- | --------------------------------------------------------- |
| `[site] url`         | die eigene Domain, mit `https://`, ohne Schrägstrich am Ende |
| `[ftp] host`         | Kundenmenü → FTP-Zugänge                                   |
| `[ftp] user`         | ebenda, meist in der Art `web123`                          |
| `[ftp] remote_dir`   | Kundenmenü → Domains: das Verzeichnis, auf das die Domain zeigt |

`deploy.ini` steht in `.gitignore` und landet nicht im Repository. Das
Passwort gehört auch nicht in die Datei – es wird beim Hochladen abgefragt
oder aus der Umgebungsvariable `DEPLOY_FTP_PASSWORD` gelesen.

### Hochladen

```bash
python3 deploy.py --dry-run    # zeigt nur, was übertragen würde
python3 deploy.py              # baut und lädt hoch
```

`deploy.py` baut die Seite zuerst neu und spiegelt dann `dist/` auf den
Server. Die Verbindung läuft über FTPS, also verschlüsselt. Weitere
Schalter:

| Schalter      | Wirkung                                                     |
| ------------- | ----------------------------------------------------------- |
| `--dry-run`   | überträgt nichts, listet nur auf                            |
| `--no-build`  | lädt das vorhandene `dist/` hoch, ohne neu zu bauen         |
| `--delete`    | entfernt auf dem Server Dateien, die es lokal nicht mehr gibt |
| `--plain-ftp` | unverschlüsseltes FTP, nur falls FTPS nicht zustande kommt  |

Wer lieber ein FTP-Programm wie FileZilla nutzt: `python3 build.py`
ausführen und den **Inhalt** von `dist/` in das Domain-Verzeichnis laden –
also `index.html`, `en/`, `static/` und die versteckte Datei `.htaccess`.
In FileZilla müssen versteckte Dateien dafür eingeblendet sein
(Server → Versteckte Dateien anzeigen).

### Was mitgeliefert wird

* `.htaccess` – leitet auf HTTPS um, setzt die Fehlerseite, schaltet
  Komprimierung und Browser-Cache ein und ergänzt Sicherheits-Header.
  Jeder Block ist gegen fehlende Apache-Module abgesichert.
* `404.html` – eigene Fehlerseite im Design der Website
* `robots.txt` und `sitemap.xml` – mit der Domain aus `deploy.ini`

### Nach dem ersten Hochladen prüfen

1. Läuft die Seite über `https://`? Falls das Zertifikat noch fehlt, im
   Kundenmenü ein kostenloses anlegen – die Weiterleitung in der
   `.htaccess` setzt es voraus.
2. Führt eine erfundene Adresse wie `ihre-domain.de/gibtsnicht` zur
   eigenen Fehlerseite?
3. Erscheint die englische Fassung unter `ihre-domain.de/en/`?

CSS, JavaScript und Bilder werden mit einem Versionsstempel verlinkt
(`style.css?v=7392bb8c`), der sich bei jeder Änderung mitändert. Deshalb
dürfen sie lange im Browser-Cache liegen, ohne dass Besucher nach einer
Aktualisierung eine veraltete Fassung sehen.

## Inhalte anpassen

* **Texte, Adresse, Angebote:** `translations/de.json` und
  `translations/en.json`. Beide Dateien haben dieselbe Struktur; fehlt ein
  Schlüssel im Englischen, greift automatisch der deutsche Text.
* **Kurse pflegen:** `courses.items` in beiden Sprachdateien – das ist die
  einzige Stelle. Jeder Eintrag hat `title`, `text`, `start_date`, `scope`,
  `spots` und `price`. Das Startdatum steht als `JJJJ-MM-TT` dort, alles
  Weitere ergibt sich daraus beim Bauen:

  * die **Reihenfolge** der Kurse (nach Datum, unabhängig davon, wie sie in
    der Datei stehen),
  * welcher Kurs **hervorgehoben** wird – immer der nächste,
  * das **angezeigte Datum** in der jeweiligen Sprache („14. September“ /
    „14 September“); das Jahr erscheint nur, wenn der Termin nicht im
    laufenden Jahr liegt,
  * der **Hinweis im Kopfbereich** der Seite.

  **Abgelaufene Kurse verschwinden von selbst.** Ab dem Tag nach dem Start
  fällt ein Kurs beim nächsten Bauen heraus und der Hinweis oben rückt auf
  den folgenden Termin. Steht gar kein Kurs mehr an, entfällt der Hinweis
  und im Kursbereich erscheint der Text aus `courses.empty`.

  Anzupassen sind also nur noch Datum, freie Plätze und Preis – danach
  `python3 deploy.py`. Die Formulierungen drumherum stehen in
  `hero.course_teaser` (mit den Platzhaltern `{title}` und `{date}`) und in
  `formats` (Monatsnamen und Datumsmuster).
* **Therapien ergänzen:** einen weiteren Eintrag in `offer.items` anlegen
  (`title`, `text`, `meta`).
* **Farben:** die Design-Tokens ganz oben in `static/css/style.css`
  (`--blue-*`). Die Leitfarbe `--blue-600` (`#314F6F`) ist das Blau aus der
  Unterzeile des Logos, `--ink-900` die Schriftfarbe des Logos; die übrigen
  Stufen sind daraus abgeleitet. Das dunkle Farbschema nutzt dieselben Tokens.
  Alle Text-Hintergrund-Kombinationen liegen über dem Kontrastwert 4.5:1.
* **Logo:** `static/img/logo.png` austauschen (PNG mit transparentem
  Hintergrund) und danach einmal

  ```bash
  python3 tools/prepare-logo.py
  ```

  ausführen. Das Skript leitet daraus die aufgehellte Fassung für das dunkle
  Farbschema sowie das quadratische Signet fürs Favicon ab. Es kommt ohne
  Zusatzpakete aus. Der Schriftzug steckt in der Bilddatei – im Kopfbereich
  steht deshalb bewusst kein zusätzlicher Text daneben.

## Impressum und Datenschutz

Beide Seiten liegen als **Vorlage mit Platzhaltern** bereit, erreichbar über
den Fußbereich:

| Seite       | Deutsch              | Englisch                |
| ----------- | -------------------- | ----------------------- |
| Impressum   | `/impressum.html`    | `/en/impressum.html`    |
| Datenschutz | `/datenschutz.html`  | `/en/datenschutz.html`  |

Die Texte stehen als HTML-Bausteine in `content/` – nicht in den
JSON-Dateien, weil sich längere Fließtexte dort schlecht bearbeiten lassen.
Sie können die Dateien direkt bearbeiten oder komplett durch den Text Ihrer
Anwältin, Ihres Anwalts oder eines Generators ersetzen.

**Vor dem Veröffentlichen:**

1. Alle eingeklammerten Platzhalter ersetzen – sie sind auf der Seite mit
   gestricheltem Rahmen hervorgehoben, damit keiner übersehen wird.
2. Den Hinweiskasten „Diese Seite ist noch nicht ausgefüllt“ am Anfang der
   jeweiligen Datei löschen.
3. Die Texte rechtlich prüfen lassen.

Die englischen Fassungen sind als Übersetzung gekennzeichnet; verbindlich
ist die deutsche.

### Wichtig für die Datenschutzerklärung

Der Text beschreibt den heutigen Stand der Seite: rein statische
Auslieferung, **keine Cookies, keine Dienste Dritter, keine Formulare, keine
Schriftarten von fremden Servern**. Das wurde am gebauten Ergebnis geprüft.
Deshalb ist auch kein Einwilligungsbanner nötig.

Sobald etwas davon hinzukommt – ein Kontaktformular, eine eingebettete
Karte, eine Terminbuchung, Schriftarten von einem fremden Server oder
Statistik –, **muss der Text erweitert werden**, und je nach Dienst wird
eine Einwilligung erforderlich.

Zwei weitere Punkte:

* Mit dem Hoster ist ein **Vertrag über die Auftragsverarbeitung** nach
  Art. 28 DSGVO zu schließen; Alfahosting stellt einen solchen bereit.
* Die Erklärung deckt nur die Website ab. Für **Patientendaten** in der
  Praxis brauchen Sie eine gesonderte Datenschutzinformation.

Der Flask-Server aus `app.py` setzt ein Cookie zum Merken der Sprachwahl.
Das betrifft nur die lokale Arbeit – die veröffentlichte statische Fassung
tut das nicht.

## Umgesetzte Details

* Logo links oben, mit der Startseite verlinkt
* Leitfarbe aus dem Logo abgeleitet, helles und dunkles Farbschema
* Responsiv ab ca. 320 px: Burger-Menü, gestapelte Raster, flexible Typografie
* Sprachumschalter im Kopfbereich, `hreflang`-Verweise im `<head>`
* Kurse in einem eigenen, farblich abgesetzten Abschnitt mit Startdatum,
  freien Plätzen und Preis; Hinweis auf den nächsten Kurs bereits im
  Kopfbereich – beides aus derselben Liste erzeugt
* abgelaufene Kurstermine fallen automatisch heraus
* Sticky Header, Scroll-Reveal, Scrollspy, animierte Kennzahlen
* Ohne JavaScript bleiben alle Inhalte sichtbar und lesbar
* `prefers-reduced-motion` schaltet Animationen ab
* Sprungmarke zum Inhalt, sichtbare Fokusrahmen, ARIA-Attribute am Menü
* Impressum und Datenschutzerklärung in beiden Sprachen; der
  Sprachumschalter bleibt dabei auf der aufgerufenen Seite

## Hinweis

Adresse, Telefonnummer, E-Mail, Kennzahlen sowie die Kurstermine, Preise
und freien Plätze sind Platzhalter und vor dem Veröffentlichen zu ersetzen.
Weil abgelaufene Kurse automatisch herausfallen, sollte die Seite nach jeder
Terminänderung neu gebaut und hochgeladen werden – sonst bleibt der Stand
des letzten Builds stehen. Impressum und Datenschutz sind noch leere Links.

Das gelieferte Logo ist 200 × 42 Pixel groß. Im Kopfbereich wird es 32 Pixel
hoch dargestellt, was der Auflösung entspricht – auf Bildschirmen mit hoher
Pixeldichte wirkt es dadurch leicht weich. Eine größere Fassung (etwa
600 Pixel Breite) oder das Original als Vektordatei würde das beheben: Datei
als `static/img/logo.png` ablegen, `python3 tools/prepare-logo.py` ausführen,
fertig.
