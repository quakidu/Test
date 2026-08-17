# Körper im Einklang – Homepage

Startseite der Praxis für ganzheitliche Therapie: Therapieangebot und Kurse
nach dem Konzept der Spiraldynamik, auf Deutsch, optimiert für Desktop und
mobile Geräte. Weitere Sprachen lassen sich jederzeit ergänzen – die
Mehrsprachigkeit ist vollständig angelegt.

## Technik

| Bereich       | Umsetzung                                                          |
| ------------- | ------------------------------------------------------------------ |
| Python        | `app.py` (Flask-Server), `build.py` (statischer Build)              |
| HTML          | Jinja2-Templates in `templates/`                                    |
| CSS           | `static/css/style.css` – eigene Design-Tokens, Grid/Flexbox         |
| JavaScript    | `static/js/main.js` – ohne Framework, keine externen Abhängigkeiten |
| JSON          | `translations/de.json` – alle Texte, je Sprache eine Datei          |

Alle Inhalte liegen in den JSON-Dateien. Templates, CSS und JS enthalten
keinen fest verdrahteten Text – siehe „Eine weitere Sprache hinzufügen“.

## Projektstruktur

```
app.py                  Flask-Server (nur für die lokale Arbeit)
build.py                Statischer Build nach dist/
deploy.py               lädt dist/ per FTPS auf den Webspace
deploy.ini.example      Vorlage für Domain und FTP-Zugang
content.py              Kursauswahl, Datumsformate, strukturierte Daten
requirements.txt        Abhängigkeiten
Dockerfile              Bild für den täglichen Lauf im Container
README-Deploy.md          täglich veröffentlichen: Grundlagen, Übersicht
README-Synology-Deploy.md   … Schritt für Schritt auf einem Synology-NAS
README-Windows-Deploy.md    … auf einem Windows-PC
README-Linux-Deploy.md      … auf einem Linux-PC
README-Proxmox-Deploy.md    … in einem Proxmox-Container
README-Unraid-Deploy.md     … auf einem Unraid-Server
README-Android-Test.md    Seite auf einem Android-Gerät ansehen
README-Android-Git.md     Git auf Android einrichten
README-Farben.md          die Seite umfärben (Leitfarbe, Logo, Vorschaubild)
README-Themes.md          ein weiteres Thema (Darstellung) hinzufügen
templates/
  base.html             Grundgerüst (Head, Meta, hreflang)
  index.html            Startseite
  legal.html            Rahmen für Impressum und Datenschutz
  404.html              Fehlerseite
  partials/header.html  Kopfbereich mit Logo links oben
  partials/footer.html  Fußbereich
  partials/theme-icons.html  Symbole der Themenwahl
content/
  impressum.de.html     Impressum; je Sprache eine Datei
  datenschutz.de.html   Datenschutz; je Sprache eine Datei
static/
  css/style.css
  js/main.js
  img/logo.png          Logo der Praxis (Original, transparent)
  img/logo-dark.png     aufgehellte Fassung für das dunkle Farbschema
  img/logo-mark.png     quadratisches Signet (Favicon)
  img/logo-mark-dark.png
  img/praxis-1.jpg …    Platzhalter für die Diashow, bitte ersetzen
  img/therapeut.jpg     Platzhalter für das Porträt, bitte ersetzen
  img/foerderer-1.png … Platzhalter für die Förderlogos, bitte ersetzen
  img/og-bild.png       Vorschaubild für geteilte Links (erzeugt)
translations/
  de.json               alle Texte; je Sprache eine solche Datei
webroot/
  .htaccess             Apache-Konfiguration, kommt unverändert nach dist/
tools/
  png.py                PNG lesen und schreiben (Standardbibliothek)
  prepare-logo.py       leitet die Logo-Varianten aus logo.png ab
  make-og-image.py      erzeugt die Vorschaubilder für geteilte Links
  deploy-taeglich.sh    täglich bauen und laden (Synology, Linux, Docker)
  deploy-taeglich.cmd   dasselbe für die Aufgabenplanung von Windows
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
| `/<code>`                    | Startseite in einer weiteren Sprache        |
| `/api/translations/de.json`  | Texte als JSON                             |

Die zuletzt gewählte Sprache wird in einem Cookie (`lang`) gespeichert.
Soll beim ersten Besuch zusätzlich die Browsersprache ausgewertet werden,
in `app.py` `AUTO_DETECT_BROWSER_LANGUAGE = True` setzen. Beides wirkt sich
erst aus, sobald es mehr als eine Sprache gibt.

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

### Am Telefon ansehen

Die meisten Besucher kommen mit dem Telefon. Wie sich die gebaute Seite
auf einem Android-Gerät ansehen lässt – im WLAN vom Rechner aus, ganz
ohne Rechner über Termux oder mit den Entwicklerwerkzeugen über USB –,
steht in **[README-Android-Test.md](README-Android-Test.md)**. Der
Kurzweg:

```bash
python3 build.py --serve --host 0.0.0.0
```

`--host 0.0.0.0` macht die Vorschau im heimischen Netzwerk erreichbar;
die Ausgabe nennt die Adresse zum Eintippen. Ohne diesen Zusatz hört der
Server nur auf den eigenen Rechner.

Wie Git auf einem Android-Gerät eingerichtet wird, steht in
**[README-Android-Git.md](README-Android-Git.md)**.

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
oder aus der Umgebungsvariable `DEPLOY_FTP_PASSWORD` gelesen. Wie sich die
Variable setzen lässt, steht weiter unten unter „Das Passwort“.

### Hochladen

Drei Wege führen zum Ziel. Alle laden denselben Ordner `dist/` hoch – sie
unterscheiden sich nur darin, womit.

#### Weg 1 – `deploy.py` (empfohlen)

```bash
python3 deploy.py --dry-run    # zeigt nur, was übertragen würde
python3 deploy.py              # baut und lädt hoch
```

`deploy.py` baut die Seite zuerst neu und spiegelt dann `dist/` auf den
Server. Die Verbindung läuft über FTPS, also verschlüsselt – auch die
Datenverbindung, nicht nur die Anmeldung. Weitere Schalter:

| Schalter      | Wirkung                                                     |
| ------------- | ----------------------------------------------------------- |
| `--dry-run`   | überträgt nichts, listet nur auf                            |
| `--no-build`  | lädt das vorhandene `dist/` hoch, ohne neu zu bauen         |
| `--delete`    | entfernt auf dem Server Dateien, die es lokal nicht mehr gibt |
| `--plain-ftp` | unverschlüsseltes FTP, nur falls FTPS nicht zustande kommt  |
| `--all`       | alle Dateien übertragen, auch unveränderte                  |

#### Übertragen wird nur, was sich geändert hat

Verglichen werden die **gebauten** Dateien in `dist/`, nicht die
Textdateien. Das ist der wichtige Unterschied: Ein Kurs, der über Nacht in
die Vergangenheit rutscht, verschwindet beim Bauen aus `index.html` – die
gebaute Seite sieht anders aus, obwohl niemand etwas bearbeitet hat, und
wird deshalb hochgeladen.

Welche Dateien zuletzt oben lagen, merkt sich `.deploy-state.json` als
Liste von Prüfsummen (lokal, gitignoriert). An einem Tag, an dem wirklich
nichts passiert ist, baut das Skript gar keine Verbindung auf und fragt
auch kein Passwort ab:

```
23 Dateien in dist/, davon 0 geändert
Nichts zu tun – der Server hat bereits diesen Stand.
```

Am Tag danach, an dem ein Kurs herausfällt:

```
23 Dateien in dist/, davon 3 geändert
  geladen  index.html
  geladen  llms.txt
  geladen  sitemap.xml
Fertig: 3 Dateien übertragen, 20 unverändert
```

Damit das verlässlich funktioniert, trägt die `sitemap.xml` je Adresse das
Datum der letzten **inhaltlichen** Änderung, nicht das Baudatum. Sonst
wäre sie jeden Tag eine geänderte Datei – und die Angabe gegenüber
Suchmaschinen wäre unwahr. Gemerkt wird das in `.build-state.json`
(ebenfalls lokal und gitignoriert).

Nach jedem Build steht außerdem da, wann sich die Seite das nächste Mal
von allein ändert:

```
Nächste Änderung durch Zeitablauf: 31.08.2026 (in 15 Tagen) –
Bekanntmachung „Sommerpause“ endet
```

Zeigt `deploy.ini` auf einen anderen Server oder ein anderes Verzeichnis,
gilt der gemerkte Stand nicht mehr und es wird wieder alles übertragen.
Dasselbe erzwingt `--all`, falls auf dem Server einmal etwas fehlt. Wer
den Vergleich dauerhaft nicht möchte, schaltet ihn in `deploy.ini` ab:

```ini
[deploy]
always_upload = yes
```

Soll das täglich von allein passieren, führen eigene Dateien Schritt für
Schritt durch die Einrichtung – siehe „Täglich automatisch
veröffentlichen“ weiter unten.

#### Das Passwort: abfragen lassen oder `DEPLOY_FTP_PASSWORD` setzen

Im Normalfall ist nichts zu tun. Fehlt die Umgebungsvariable, fragt
`deploy.py` das Passwort ab – es landet dann nirgends, weder in einer
Datei noch in der Shell-History:

```bash
python3 deploy.py
FTP-Passwort: ▮
```

Die Variable brauchen Sie nur, wenn niemand tippen kann – etwa bei einem
automatischen Upload.

**Nur für einen einzelnen Aufruf** (Linux, macOS):

```bash
 DEPLOY_FTP_PASSWORD='geheim' python3 deploy.py
```

Das Leerzeichen ganz am Anfang ist Absicht: In bash (mit
`HISTCONTROL=ignorespace`) und in zsh (mit `setopt HIST_IGNORE_SPACE`)
hält es die Zeile aus der History heraus. Ohne diese Einstellung steht
das Passwort anschließend in `~/.bash_history`.

**Für das aktuelle Fenster**, danach wieder entfernen:

```bash
# Linux, macOS
export DEPLOY_FTP_PASSWORD='geheim'
python3 deploy.py
unset DEPLOY_FTP_PASSWORD
```

```powershell
# Windows PowerShell
$env:DEPLOY_FTP_PASSWORD = 'geheim'
python deploy.py
Remove-Item Env:DEPLOY_FTP_PASSWORD
```

```cmd
:: Windows Eingabeaufforderung
set DEPLOY_FTP_PASSWORD=geheim
python deploy.py
set DEPLOY_FTP_PASSWORD=
```

Bei Sonderzeichen im Passwort:

* Linux und macOS: **einfache** Anführungszeichen nehmen. In doppelten
  würden `$` und `` ` `` ausgewertet, in interaktiver bash auch `!`.
* Windows `set`: **keine** Anführungszeichen – sie würden Teil des
  Passworts. Ein Leerzeichen hinter dem Passwort zählt ebenfalls mit,
  und ein `%` im Passwort liest cmd als Variablenanfang.
* Ein leerer Wert wirkt wie „nicht gesetzt“ – dann wird wieder gefragt.

**Dauerhaft setzen** (`~/.bashrc`, `~/.zshrc`, unter Windows
„Umgebungsvariablen für dieses Konto bearbeiten“) ist möglich, aber dann
liegt das Passwort im Klartext in einer Datei bzw. in der Registry, und
jedes gestartete Programm kann es lesen. Für die Arbeit von Hand lieber
abfragen lassen; für einen automatisch laufenden Upload ist es der
praktikable Weg.

#### Weg 2 – FTP-Programm wie FileZilla

```bash
python3 build.py --site-url https://www.ihre-domain.de
```

Danach den **Inhalt** von `dist/` in das Domain-Verzeichnis laden – also
`index.html`, `en/`, `static/`, `robots.txt`, `sitemap.xml`, `llms.txt`
und die versteckte Datei `.htaccess`. In FileZilla müssen versteckte
Dateien dafür eingeblendet sein (Server → Versteckte Dateien anzeigen).
Fehlt die `.htaccess`, fehlen HTTPS-Weiterleitung, eigene Fehlerseite,
Komprimierung und Sicherheits-Header.

#### Weg 3 – Dateimanager im Kundenmenü

Bietet das Paket einen Dateimanager, geht es auch ohne FTP-Programm:
`dist/` als ZIP packen, hochladen, auf dem Server entpacken. Für
regelmäßige Änderungen umständlich, aber brauchbar, wenn gerade kein
anderes Werkzeug zur Hand ist. Auch hier auf die `.htaccess` achten –
manche Dateimanager übergehen Dateien, die mit einem Punkt beginnen.

#### Die Domain muss bei jedem Weg stimmen

Ob aus `deploy.ini` (`[site] url`) oder per `--site-url`: Die Domain
steckt in der kanonischen Adresse, in den `hreflang`-Angaben, in
`sitemap.xml`, `robots.txt`, `llms.txt` und in den Vorschaubildern für
geteilte Links. Steht dort die falsche Domain, zeigen alle diese Angaben
auf die falsche Stelle – sichtbar ist davon zunächst nichts.

### Was mitgeliefert wird

* `.htaccess` – leitet auf HTTPS um, setzt die Fehlerseite, schaltet
  Komprimierung und Browser-Cache ein und ergänzt Sicherheits-Header.
  Jeder Block ist gegen fehlende Apache-Module abgesichert.
* `404.html` – eigene Fehlerseite im Design der Website
* `robots.txt`, `sitemap.xml` und `llms.txt` – mit der Domain aus
  `deploy.ini`

### Nach dem ersten Hochladen prüfen

1. Läuft die Seite über `https://`? Falls das Zertifikat noch fehlt, im
   Kundenmenü ein kostenloses anlegen – die Weiterleitung in der
   `.htaccess` setzt es voraus.
2. Führt eine erfundene Adresse wie `ihre-domain.de/gibtsnicht` zur
   eigenen Fehlerseite?
3. Sind Impressum und Datenschutzerklärung erreichbar?
4. Sind `/robots.txt`, `/sitemap.xml` und `/llms.txt` erreichbar, und
   steht darin die richtige Domain?

CSS, JavaScript und Bilder werden mit einem Versionsstempel verlinkt
(`style.css?v=7392bb8c`), der sich bei jeder Änderung mitändert. Deshalb
dürfen sie lange im Browser-Cache liegen, ohne dass Besucher nach einer
Aktualisierung eine veraltete Fassung sehen.

## Täglich automatisch veröffentlichen

Abgelaufene Kurstermine und Bekanntmachungen verschwinden beim **Bauen**,
nicht im Browser des Besuchers. Wer nicht daran denken möchte, lässt einen
Rechner die Seite einmal täglich neu bauen und hochladen. Das kostet an
den meisten Tagen nichts: `deploy.py` überträgt nur, was sich geändert
hat, und baut ohne Änderung nicht einmal eine Verbindung auf.

Die Einrichtung ist je nach Gerät verschieden und in eigenen Dateien
Schritt für Schritt beschrieben – jeweils von vorn, ohne Vorkenntnisse:

| Anleitung | Für wen |
| --- | --- |
| **[README-Deploy.md](README-Deploy.md)** | **Hier anfangen.** Grundlagen für alle Geräte: was gebraucht wird, wie die Texte gepflegt werden |
| [README-Synology-Deploy.md](README-Synology-Deploy.md) | ein Synology-NAS, wahlweise mit Python oder mit Docker |
| [README-Windows-Deploy.md](README-Windows-Deploy.md) | ein Windows-PC, über die Aufgabenplanung |
| [README-Linux-Deploy.md](README-Linux-Deploy.md) | ein Linux-PC, über cron oder einen systemd-Timer |
| [README-Proxmox-Deploy.md](README-Proxmox-Deploy.md) | ein Server mit Proxmox, in einem eigenen LXC-Container |
| [README-Unraid-Deploy.md](README-Unraid-Deploy.md) | ein NAS mit Unraid, über Docker und „User Scripts“ |

Wer nur gelegentlich von Hand veröffentlicht, braucht davon nichts: Dafür
genügt `python3 deploy.py` wie oben beschrieben.

## Eine weitere Sprache hinzufügen

Die Seite erscheint zurzeit nur auf Deutsch. Die Mehrsprachigkeit ist
aber vollständig angelegt: Sprachumschalter, Sprachordner,
`hreflang`-Verweise und der Rückfall auf die deutschen Texte sind da und
schalten sich ein, sobald eine zweite Sprache eingetragen ist.

Vier Schritte, am Beispiel Englisch:

1. **Textdatei anlegen** – am einfachsten als Kopie:

   ```bash
   cp translations/de.json translations/en.json
   ```

   Dann in `en.json` die Werte übersetzen. Die Struktur muss gleich
   bleiben; die Schlüssel links vom Doppelpunkt werden **nicht** übersetzt.
   Was fehlt, füllt automatisch der deutsche Text – Sie können also
   abschnittsweise vorgehen.

2. **Sprache eintragen**, in `build.py` *und* in `app.py` jeweils bei
   `LANGUAGES`:

   ```python
   LANGUAGES = {
       "de": {"label": "Deutsch", "short": "DE", "locale": "de_DE"},
       "en": {"label": "English", "short": "EN", "locale": "en_GB"},
   }
   ```

   | Feld | Wofür |
   | --- | --- |
   | `label` | vollständiger Name, erscheint als Tooltip |
   | `short` | Kürzel im Umschalter |
   | `locale` | für `og:locale` im Kopf der Seite |

3. **Rechtstexte** (optional): `content/impressum.en.html` und
   `content/datenschutz.en.html` anlegen. Fehlen sie, erscheint der
   deutsche Text – eine Seite ohne Impressum gibt es also nie.

4. **Vorschaubild** (optional): In `en.json` unter `seo.og_image` einen
   eigenen Dateinamen eintragen, dann

   ```bash
   python3 tools/make-og-image.py
   ```

Danach `python3 build.py` – fertig. Der Build legt `dist/en/` an, der
Umschalter erscheint im Kopfbereich, `hreflang` und `x-default` stehen im
`<head>`, `llms.txt` nennt die zusätzliche Fassung, und die Sitemap führt
beide Sprachen.

**Zum Entfernen** genügt es, den Eintrag aus beiden `LANGUAGES` zu
löschen. Die Textdatei kann liegen bleiben; gebaut wird nur, was dort
steht.

## Darstellung: helles und dunkles Thema

Im Kopfbereich steht rechts eine Wahl mit drei Knöpfen:

| Knopf | Bedeutung |
| --- | --- |
| ◐ | **Wie das Gerät** – folgt der Einstellung von Betriebssystem oder Browser (Standard) |
| ☀ | **Hell** |
| ☾ | **Dunkel** |

Die Wahl bleibt im Browser gespeichert und gilt beim nächsten Besuch
weiter. „Wie das Gerät“ reagiert auch während des Besuchs, wenn das
Betriebssystem etwa abends auf Dunkel umstellt. Ohne JavaScript
erscheint die Wahl nicht; dann gilt die Vorgabe des Betriebssystems.

Zwei Anleitungen, die leicht verwechselt werden:

| Sie möchten … | Anleitung |
| --- | --- |
| die Seite **umfärben** – neue Leitfarbe für Hell und Dunkel | **[README-Farben.md](README-Farben.md)** |
| eine **weitere Darstellung** anbieten, etwa ein warmes Thema neben Hell und Dunkel | **[README-Themes.md](README-Themes.md)** |

Der Unterschied: Beim Umfärben ändert sich die Seite für alle. Ein
weiteres Thema kommt als vierter Knopf hinzu, und jeder Besucher wählt
selbst.

Themenwahl und Sprachwahl sind voneinander unabhängig: Beide stehen
nebeneinander im Kopfbereich, beide erscheinen ab zwei Einträgen, und der
Umbruchpunkt zum Burger-Menü (1200 px) ist so gewählt, dass **beide
zusammen** in eine Zeile passen.

## Inhalte anpassen

* **Texte, Adresse, Angebote:** `translations/de.json` und
  Kommt eine weitere Sprache dazu, bekommt sie eine eigene Datei mit
  derselben Struktur; fehlt dort ein Schlüssel, greift der deutsche Text.
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
  * der **Hinweis auf den nächsten Kurs** im Abschnitt
    „Aktuelles aus der Praxis“.

  **Abgelaufene Kurse verschwinden von selbst.** Ab dem Tag nach dem Start
  fällt ein Kurs beim nächsten Bauen heraus und der Hinweis unter den
  Bekanntmachungen rückt auf den folgenden Termin. Steht gar kein Kurs mehr
  an, entfällt der Hinweis und im Kursbereich erscheint der Text aus
  `courses.empty`.

  Anzupassen sind also nur noch Datum, freie Plätze und Preis – danach
  `python3 deploy.py`. Die Formulierungen drumherum stehen in
  `hero.course_teaser` (mit den Platzhaltern `{title}` und `{date}`) und in
  `formats` (Monatsnamen und Datumsmuster).
* **„Platz anfragen“:** Der Button öffnet das E-Mail-Programm mit fertigem
  Betreff (Kurs und Starttermin) und einem vorbereiteten Text, der bereits
  nach Name, Telefon und Rückfragen fragt – sonst kommt eine leere Mail an.
  Beide Texte stehen unter `courses.request` und dürfen die Platzhalter
  `{title}` und `{date}` enthalten. Weil nicht überall ein Mailprogramm
  eingerichtet ist, stehen unter den Karten zusätzlich E-Mail-Adresse und
  Telefonnummer als anklickbarer Text (`courses.alt_label`).

  Denselben Hinweis gibt es unter dem Knopf „E-Mail schreiben“ im
  Kontaktbereich und unter „Rückmeldung schreiben“ im Abschnitt „Stimmen“ –
  an diesen beiden Stellen ohne Telefonnummer, weil dort schriftlich
  geantwortet werden soll. Alle drei greifen auf `contact.mail_hint` zu,
  damit die Formulierung nicht auseinanderläuft.

  Wenn Anmeldungen später wirklich über die Seite laufen sollen, wäre ein
  Formular der nächste Schritt – dafür braucht es serverseitigen Code (bei
  Alfahosting per PHP möglich), einen Spam-Schutz und einen zusätzlichen
  Abschnitt in der Datenschutzerklärung.
* **Therapien ergänzen:** einen weiteren Eintrag in `offer.items` anlegen
  (`title`, `text`, `meta`).

* **Bekanntmachungen (Abschnitt „Aktuelles aus der Praxis“):** kurze
  Hinweise mit begrenzter Gültigkeit – Schließzeiten, Vertretung, neue
  Kurstermine. Sie stehen unter `news.items` und der Abschnitt folgt direkt
  auf den Kopfbereich, damit niemand einen Termin anfragt, ohne von der
  Sommerpause gelesen zu haben.

  Am Ende des Abschnitts steht zusätzlich der **Hinweis auf den nächsten
  Kurs**. Er wird aus der Kursliste erzeugt, ist also nicht von Hand zu
  pflegen, und führt in den Kursbereich. Er steht hinter den eigenen
  Hinweisen: Eine Schließzeit wiegt schwerer als ein freier Kursplatz.
  Seine Formulierung steht weiterhin unter `hero.course_teaser`.

  Jeder Eintrag hat drei Felder:

  | Feld        | Bedeutung                                              |
  | ----------- | ------------------------------------------------------ |
  | `title`     | Überschrift des Hinweises                              |
  | `text`      | ein bis drei Sätze                                     |
  | `hide_from` | Datum `JJJJ-MM-TT`, **ab** dem der Hinweis verschwindet |

  **`hide_from` ist der erste Tag ohne den Hinweis**, nicht der letzte
  mit ihm. Für „Praxis bis einschließlich 30. August geschlossen“ steht
  dort also `2026-08-31`: Am 30. ist der Hinweis noch zu sehen, am 31.
  nicht mehr.

  **Das Datum erscheint nirgends auf der Seite.** Es steuert nur die
  Anzeige und steht auch nicht im Quelltext der fertigen Seite.

  Weiteres Verhalten:

  1. Die Reihenfolge stammt aus der Sprachdatei – was oben steht,
     erscheint zuerst.
  2. Sind alle Hinweise abgelaufen **und steht auch kein Kurs mehr an**,
     entfällt der ganze Abschnitt. Ein leerer Kasten wäre schlechter als
     keiner.
  3. Ein Eintrag ohne `hide_from` bleibt stehen, bis Sie ihn löschen. Der
     Build weist darauf hin, ebenso auf ein unbrauchbares Datum – ein
     falsch geschriebenes Datum lässt den Hinweis stehen, statt ihn
     stillschweigend verschwinden zu lassen.
  4. Aktuelle Bekanntmachungen stehen zusätzlich in `llms.txt`, und zwar
     an erster Stelle: Eine Schließzeit ist die Antwort, die im Zweifel
     vor allen anderen zählt.

  **Wichtig:** Die Seite ist statisch. Das Ausblenden geschieht beim
  Bauen, nicht im Browser des Besuchers. Ein abgelaufener Hinweis
  verschwindet also erst, wenn die Seite neu gebaut und hochgeladen wird
  – genau wie bei den Kursterminen.

* **Abschnitt „Konzept“:** unter `about` und in mehrere Teile gegliedert,
  damit sich Umfang und Tiefe getrennt anpassen lassen:

  | Schlüssel        | Was daraus wird                                       |
  | ---------------- | ----------------------------------------------------- |
  | `lead`           | der einleitende Absatz unter der Überschrift          |
  | `body`           | Liste von Absätzen: das Bauprinzip am Beispiel Fuß    |
  | `features`       | die vier Karten zur Arbeitsweise                      |
  | `examples`       | Körperregionen, an denen das Prinzip ansetzt          |
  | `origin`         | Herkunft des Konzepts und Ausbildungsweg              |

  Jede Liste darf länger oder kürzer sein – das Layout passt sich an.
  Zwei Dinge sollten beim Umschreiben erhalten bleiben:

  1. **Keine Wirkungsversprechen.** Formulierungen wie „beseitigt
     Schmerzen“ oder „heilt Hallux valgus“ sind im Heilmittelwerbegesetz
     (§ 11 HWG) geregelt. Die vorhandenen Texte beschreiben, wie gearbeitet
     wird, und was das Ziel ist – nicht, was garantiert eintritt.
  2. **Spiraldynamik® ist ein geschütztes Konzept**, kein allgemeiner
     Fachbegriff. Der Absatz `origin` nennt deshalb Herkunft und
     Ausbildungsweg. Wer damit wirbt, sollte die Zusatzausbildung
     tatsächlich haben – dieselbe Anforderung wie beim Abschnitt
     „Therapeut“.

  Der Text landet zusätzlich in `llms.txt`; Sprachmodelle beantworten
  „Was ist Spiraldynamik?“ dann mit dieser Fassung.
* **Praxis-Bilder:** Die Diashow zeigt die Dateien aus `static/img/`, die
  unter `practice.slides` eingetragen sind. Mitgeliefert sind vier
  **Platzhalter** (`praxis-1.jpg` … `praxis-4.jpg`), die als solche
  erkennbar sind – bitte durch eigene Fotos ersetzen:

  1. Fotos im Seitenverhältnis 3 : 2 aufnehmen oder zuschneiden, etwa
     1600 × 1067 Pixel, als JPEG mit mittlerer Qualität (Ziel: unter
     300 KB je Bild, sonst lädt die Seite auf dem Handy spürbar langsamer).
  2. Unter demselben Dateinamen nach `static/img/` legen – dann ist keine
     weitere Änderung nötig. Bei anderen Namen die Einträge in
     `practice.slides` anpassen.
  3. `alt` beschreibt das Bild für Menschen, die es nicht sehen können;
     `caption` ist die Bildunterschrift. Der Dateiname steht nur in
     `de.json` – ein Foto ist nicht sprachabhängig; Beschreibung und
     Unterschrift stehen in beiden Dateien.

  Weitere Bilder: einfach einen Eintrag mehr in beiden Sprachdateien.
  Weniger als zwei Bilder blenden die Bedienelemente automatisch aus.

* **Abschnitt „Therapeut“:** Name, Berufsbezeichnung, die beiden Absätze und
  die Tabelle mit Ausbildung und Qualifikation stehen unter `therapist` in
  beiden Sprachdateien. **Alles darin ist mit `[Platzhalter]` markiert und
  muss ersetzt werden** – es sind Beispieltexte, keine Angaben über eine
  echte Person.

  Beim Ausfüllen zu beachten:

  1. „Physiotherapeut“ ist eine **geschützte Berufsbezeichnung**; sie darf
     nur führen, wer die staatliche Anerkennung hat. Dasselbe gilt für
     Zertifikatsstufen der Spiraldynamik® Akademie – bitte genau so
     angeben, wie sie auf der Urkunde stehen.
  2. **Keine Heilversprechen.** Für Aussagen über Wirkung und Erfolg gilt
     hier dasselbe wie im Rest der Seite (§ 11 Heilmittelwerbegesetz).
  3. Einträge in `therapist.facts`, die nicht zutreffen, einfach löschen –
     die Liste passt sich an.
  4. `therapist.name` sollte mit `seo.founder` übereinstimmen. Weichen die
     beiden voneinander ab, meldet der Build das.

  **Kennzahlen:** Die drei Zahlen unter den Absätzen (Jahre Erfahrung,
  Behandlungen, Kurse pro Jahr) stehen unter `therapist.stats` und zählen
  beim Erscheinen hoch. Es sind **Platzhalterwerte** – bitte auf die
  eigenen anpassen oder Einträge löschen, die Sie nicht belegen können.
  Achten Sie darauf, dass „Jahre Erfahrung“ nicht dem Eintrag „Erfahrung“
  in der Qualifikationsliste widerspricht.

  **Porträtfoto:** `static/img/therapeut.jpg` ist ein erkennbarer
  Platzhalter. Bitte durch ein echtes Foto ersetzen – Hochformat 3 : 4,
  etwa 900 × 1200 Pixel, JPEG unter 300 KB. Ein Stockfoto wirkt hier
  gegenteilig: Besucher prüfen an dieser Stelle, ob die Person real ist.
  Das Bild erscheint zusätzlich als `Person.image` in den strukturierten
  Daten und ist damit der Beleg für die Angaben im Seitenkopf.

* **Terminvergabe und Terminabsage:** die beiden Hinweise unten in der
  Kontaktkarte stehen unter `contact.notes`. Die genannte Frist von
  **24 Stunden** ist ein üblicher, aber frei gewählter Wert – bitte an die
  eigene Handhabung anpassen. Ein Ausfallhonorar ist bewusst nicht
  erwähnt: Das lässt sich nicht einseitig über die Website festlegen,
  sondern muss mit den Patientinnen und Patienten vereinbart sein. Wenn
  eine solche Vereinbarung besteht, kann der Satz dort ergänzt werden.

* **Rückmeldungen (Abschnitt „Stimmen“):** die veröffentlichten Zuschriften
  stehen unter `testimonials.items` mit `name`, `context` und `text`. Die
  drei mitgelieferten Einträge sind als **Beispiele gekennzeichnet** – vor
  dem Veröffentlichen ersetzen oder löschen. Ist die Liste leer, erscheint
  statt der Karten der Text aus `testimonials.empty`; die Einladung zum
  Schreiben bleibt.

  **Rückmeldungen kommen nicht automatisch auf die Seite.** Die
  Schaltfläche „Rückmeldung schreiben“ öffnet eine vorbereitete E-Mail an
  die Praxisadresse, die bereits nach der gewünschten Namensnennung und
  nach der ausdrücklichen Zustimmung zur Veröffentlichung fragt. Sie
  übernehmen den Text dann von Hand in beide Sprachdateien. Das ist so
  gewollt – die Gründe stehen unten unter „Warum Rückmeldungen von Hand
  eingetragen werden“.

* **Förderhinweis:** Text und Logos stehen unter `funding`. Die drei
  mitgelieferten Logos sind **Platzhalter** – bitte durch die echten
  Logos der Förderer ersetzen:

  1. Am besten PNG mit transparentem Hintergrund. Die Höhe begrenzt das
     Layout auf 56 Pixel, die Breite ergibt sich; unterschiedliche
     Seitenverhältnisse sind also kein Problem.
  2. Unter demselben Dateinamen nach `static/img/` legen oder die Einträge
     in `funding.logos` anpassen.
  3. `alt` beschreibt das Logo für Menschen, die es nicht sehen können –
     dort gehört der Name der Einrichtung hinein.
  4. Ist bei einem Eintrag `url` gefüllt, wird das Logo zu einem Verweis
     auf die Website des Förderers (öffnet in einem neuen Tab).

  Der Logo-Streifen bleibt in beiden Farbschemata **weiß**. Das ist
  Absicht: Förderlogos sind meist dunkel auf transparentem Grund und
  würden auf dunklem Untergrund verschwinden.

  Der Text („Der Aufbau der Praxis wurde von den folgenden Einrichtungen
  unterstützt …“) ist ein Vorschlag. Achten Sie darauf, dass die Aussage
  zur tatsächlichen Förderung passt – und prüfen Sie die Auflagen der
  Fördermittelgeber: Bei öffentlichen Programmen sind Wortlaut, Logo und
  Platzierung des Hinweises oft genau vorgeschrieben.

  Sind keine Logos hinterlegt, entfällt der ganze Abschnitt.

* **Karte im Kontaktbereich:** Adresse und Einbett-Adresse stehen unter
  `contact.map` in beiden Sprachdateien. Am einfachsten: bei Google Maps den
  Standort suchen, „Teilen → Karte einbetten“ wählen und die Adresse aus dem
  `src`-Attribut nach `embed_url` kopieren; `link_url` ist der Verweis
  „Route planen“. Beide Werte müssen in `de.json`
  übereinstimmen – eine Adresse ist nicht sprachabhängig.

  **Die Karte lädt erst auf Klick.** Vorher geht keine Anfrage an Google.
  Das ist kein Zufall, sondern der Grund, warum die Seite ohne
  Einwilligungsbanner auskommt: Ohne Klick werden keine Daten an Dritte
  übertragen. Wird die Karte irgendwann direkt eingebunden, ist ein Banner
  erforderlich und die Datenschutzerklärung erneut anzupassen.

* **Farben:** die Design-Tokens ganz oben in `static/css/style.css`
  (`--blue-*`). Die Leitfarbe `--blue-600` (`#314F6F`) ist das Blau aus der
  Unterzeile des Logos, `--ink-900` die Schriftfarbe des Logos; die übrigen
  Stufen sind daraus abgeleitet. Das dunkle Farbschema nutzt dieselben Tokens.
  Alle Text-Hintergrund-Kombinationen liegen über dem Kontrastwert 4.5:1.

  Die Seite ganz umfärben – neue Leitfarbe, Logo, Vorschaubild? Die
  Schritt-für-Schritt-Anleitung steht in
  **[README-Farben.md](README-Farben.md)**. Sie nennt auch die
  Farbangaben, die außerhalb des Stylesheets liegen – im Logo, in der
  Browserleiste und im Vorschaubild – und sonst leicht übersehen werden.
* **Logo:** `static/img/logo.png` austauschen (PNG mit transparentem
  Hintergrund) und danach einmal

  ```bash
  python3 tools/prepare-logo.py
  ```

  ausführen. Das Skript leitet daraus die aufgehellte Fassung für das dunkle
  Farbschema sowie das quadratische Signet fürs Favicon ab. Es kommt ohne
  Zusatzpakete aus. Der Schriftzug steckt in der Bilddatei – im Kopfbereich
  steht deshalb bewusst kein zusätzlicher Text daneben.

## Gefunden werden: Suchmaschinen und Antwortdienste

Drei Wege führen heute zur Praxis, und alle drei brauchen dieselbe Grundlage:

* **SEO** – die klassische Trefferliste bei Google und Bing.
* **GEO** – der örtliche Teil davon: die Karte, der Eintrag „in Ihrer Nähe“,
  die Route. Hier zählt vor allem, dass Anschrift, Telefonnummer und
  Öffnungszeiten **überall gleich** lauten.
* **AIO** – Antworten von Sprachmodellen (ChatGPT, Gemini, Perplexity,
  Claude). Die lesen kein Layout, sondern Text und maschinenlesbare Angaben.

Alles, was diese drei brauchen, steht an **einer** Stelle: im Block `seo` in
`translations/de.json`. Daraus baut der Build den
Kopf der Seite, die strukturierten Daten, `llms.txt` und die Vorschaubilder.

### Welche Informationen müssen hinterlegt werden?

| Feld            | Beispiel (Vorlage)                                     | Wofür                                        |
| --------------- | ------------------------------------------------------ | -------------------------------------------- |
| `legal_name`    | `Körper im Einklang – Praxis für ganzheitliche Therapie`| voller Name, wie im Impressum                |
| `founder`       | `Test User`                                            | die Person, nach der gesucht wird            |
| `founder_role`  | `Physiotherapeut und Spiraldynamik-Fachkraft`          | Qualifikation, erscheint in Antworten        |
| `street`        | `Musterstraße 12`                                      | Anschrift für Karte und Route                |
| `postal_code`   | `12345`                                                | dito                                         |
| `city`          | `Musterstadt`                                          | **der wichtigste Ortsbezug**                 |
| `region`        | `Bayern`                                               | Bundesland, optional                         |
| `country`       | `DE`                                                   | Ländercode                                   |
| `latitude`      | `48.137154`                                            | genauer Punkt auf der Karte                  |
| `longitude`     | `11.576124`                                            | dito                                         |
| `area_served`   | `["Musterstadt", "Umgebung von Musterstadt"]`          | Einzugsgebiet                                |
| `price_range`   | `€€`                                                   | grobe Preislage                              |
| `founding_year` | `2014`                                                 | seit wann es die Praxis gibt, optional       |
| `opening_hours` | `Mo–Fr 08:00–19:00`                                    | maschinenlesbare Öffnungszeiten              |
| `same_as`       | `["https://www.instagram.com/…"]`                      | weitere Profile, bestätigen die Identität    |
| `keywords`      | `["Spiraldynamik", "Physiotherapie", "Musterstadt", …]`| Themen der Praxis                            |
| `og_image`      | `og-bild.png`                                          | Vorschaubild für geteilte Links              |

Dazu kommen drei Texte, die schon gefüllt sind und beim Umzug auf die echten
Daten mitgeändert werden sollten:

* `meta.title` – **„Spiraldynamik in Musterstadt – Körper im Einklang“**
  (Thema + Ort + Name, höchstens 60 Zeichen)
* `meta.description` – **„Praxis Körper im Einklang in Musterstadt:
  Physiotherapie nach Spiraldynamik, Bewegungsanalyse und Kurse für Füße und
  Rücken. Termine bei Test User.“** (120–165 Zeichen)
* `hero.eyebrow` – **„Spiraldynamik in Musterstadt“**, die erste sichtbare
  Zeile der Seite

Der Build meldet nach jedem Lauf, was fehlt oder nicht zusammenpasst – etwa
wenn `seo.city` nicht in `contact.address` vorkommt oder der Titel zu lang
ist. Die Meldungen brechen den Build nicht ab, sie stehen nur am Ende.

### Koordinaten herausfinden

`latitude` und `longitude` sind bewusst leer: geraten wären sie schlimmer als
gar nicht. So kommen Sie an die richtigen Werte:

1. Die Adresse in Google Maps oder OpenStreetMap suchen.
2. Rechtsklick auf die Praxis → die beiden Zahlen erscheinen
   (z. B. `48.137154, 11.576124`).
3. Die erste Zahl nach `latitude`, die zweite nach `longitude` eintragen.

Ohne die beiden Werte fehlt in den strukturierten Daten nur der
Kartenpunkt – alles andere funktioniert.

### Was daraus gebaut wird

* **Strukturierte Daten** (JSON-LD, `content.py`) im Kopf jeder Seite: die
  Praxis als `Physiotherapy` mit Anschrift, Öffnungszeiten und Einzugsgebiet,
  `Test User` als `Person` mit Porträt und Qualifikationen aus dem Abschnitt
  „Therapeut“, jeder kommende Kurs als `Course` mit Starttermin und Preis.
  Abgelaufene Kurse fallen automatisch heraus – auch hier.
* **`llms.txt`** im Wurzelverzeichnis: die ganze Seite als knapper Text, den
  Sprachmodelle sicher lesen können. Wird bei jedem Build neu erzeugt.
* **`robots.txt`** mit ausdrücklichen Einträgen für GPTBot, ClaudeBot,
  PerplexityBot, Google-Extended und andere. Sie sind **erlaubt**, damit die
  Praxis in solchen Antworten auftauchen kann. Wer das nicht möchte, ändert
  in `build.py` (`write_robots`) das jeweilige `Allow: /` in `Disallow: /`.
* **Vorschaubild** für geteilte Links, je Sprache:

  ```bash
  python3 tools/make-og-image.py        # beide Sprachen
  ```

  Das Bild entsteht aus Logo, Ort und Namen – nach einer Änderung an diesen
  Angaben einmal neu erzeugen. Gebraucht wird dafür Chromium oder Chrome.
* **Kanonische Adresse**, Open Graph und Twitter-Card. Die Fehlerseite
  trägt `noindex`. `hreflang`-Verweise kommen automatisch dazu, sobald es
  eine zweite Sprache gibt.

### Was der Code nicht leisten kann

Für den örtlichen Teil (GEO) ist der wichtigste Schritt außerhalb dieser
Seite: ein **Eintrag bei Google Unternehmensprofil** (früher „Google My
Business“) und bei Bing Places, mit **exakt derselben** Schreibweise von
Name, Anschrift und Telefonnummer wie im Impressum. Weicht auch nur die
Straßenabkürzung ab, zählen Suchmaschinen das als zwei verschiedene Betriebe.
Ist das Profil angelegt, gehört seine Adresse zusätzlich in `seo.same_as`.

## Impressum und Datenschutz

Beide Seiten liegen als **Vorlage mit Platzhaltern** bereit, erreichbar über
den Fußbereich:

| Seite       | Adresse              |
| ----------- | -------------------- |
| Impressum   | `/impressum.html`    |
| Datenschutz | `/datenschutz.html`  |

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

Kommt später eine weitere Sprache dazu, sollte deren Fassung als
Übersetzung gekennzeichnet und die deutsche für verbindlich erklärt
werden.

### Wichtig für die Datenschutzerklärung

Der Text beschreibt den heutigen Stand der Seite: statische Auslieferung,
**keine Cookies, keine Formulare, keine Schriftarten von fremden Servern**.
Einziger Dienst eines Dritten ist die Google-Karte im Kontaktbereich – und
die wird erst nach einem Klick geladen (Abschnitt 6 der Erklärung). Beides
wurde am gebauten Ergebnis geprüft: Vor dem Klick gehen null Anfragen an
fremde Adressen hinaus und es werden null Cookies gesetzt. Deshalb ist kein
Einwilligungsbanner nötig.

Sobald weiteres hinzukommt – ein Kontaktformular, eine Terminbuchung,
Schriftarten von einem fremden Server oder Statistik –, **muss der Text
erweitert werden**, und je nach Dienst wird eine Einwilligung erforderlich.
Dasselbe gilt, wenn die Karte künftig direkt statt auf Klick geladen wird.

Zwei weitere Punkte:

* Mit dem Hoster ist ein **Vertrag über die Auftragsverarbeitung** nach
  Art. 28 DSGVO zu schließen; Alfahosting stellt einen solchen bereit.
* Die Erklärung deckt nur die Website ab. Für **Patientendaten** in der
  Praxis brauchen Sie eine gesonderte Datenschutzinformation.

Der Flask-Server aus `app.py` setzt ein Cookie zum Merken der Sprachwahl.
Das betrifft nur die lokale Arbeit – die veröffentlichte statische Fassung
tut das nicht.

## Warum Rückmeldungen von Hand eingetragen werden

Ein Formular, das Bewertungen direkt auf der Seite veröffentlicht, wäre
technisch machbar, wäre hier aber die schlechtere Lösung:

* **Rechtlich.** Eine veröffentlichte Rückmeldung ist eine Aussage über eine
  Gesundheitsbehandlung. Sie darf nur mit ausdrücklicher Einwilligung der
  schreibenden Person erscheinen, und diese Einwilligung muss nachweisbar
  sein. Beim Weg über E-Mail liegt sie schriftlich vor.
* **Werberecht.** Für Heilberufe gelten beim Werben mit Äußerungen Dritter
  besondere Grenzen (§ 11 Heilmittelwerbegesetz). Was erscheint, sollte
  jemand gelesen haben.
* **Missbrauch.** Ein offenes Formular zieht Spam an, und für fremde
  Inhalte auf der eigenen Seite haftet man ab Kenntnis. Ohne Prüfung
  landet irgendwann Werbung oder Beleidigendes auf der Startseite.
* **Technik.** Der Webspace liefert statische Dateien aus. Direktes
  Veröffentlichen bräuchte serverseitigen Code samt Speicher, Moderation
  und Löschfunktion – deutlich mehr Aufwand als der jetzige Weg.

Der Aufwand pro Zuschrift beträgt: Text in `testimonials.items` einfügen,
`python3 deploy.py`. Bei einer kleinen Praxis sind das ein paar Minuten im
Quartal.

## Umgesetzte Details

* Logo links oben, mit der Startseite verlinkt
* Leitfarbe aus dem Logo abgeleitet, helles und dunkles Farbschema
* Responsiv ab ca. 320 px: Burger-Menü, gestapelte Raster, flexible Typografie
* Mehrsprachigkeit angelegt: Sprachumschalter und `hreflang`-Verweise
  erscheinen automatisch ab der zweiten Sprache
* Wahl der Darstellung (Gerätevorgabe, hell, dunkel), gespeichert im
  Browser und ohne Aufblitzen beim Laden
* Kurse in einem eigenen, farblich abgesetzten Abschnitt mit Startdatum,
  freien Plätzen und Preis; Hinweis auf den nächsten Kurs schon bei den
  Bekanntmachungen – beides aus derselben Liste erzeugt
* abgelaufene Kurstermine und Bekanntmachungen fallen automatisch heraus;
  der Upload erkennt das, weil er die gebauten Dateien vergleicht
* Abschnitt „Stimmen“ mit Rückmeldungen; Zuschriften erreichen die Praxis
  per E-Mail und werden von Hand veröffentlicht
* Förderhinweis am Seitenende mit den Logos der Förderer in einer Zeile
* Karte im Kontaktbereich nach dem Zwei-Klick-Prinzip: keine Verbindung zu
  Google, solange niemand „Karte laden“ drückt
* Diashow im Praxis-Bereich: Wischen, Pfeile, Punkte und automatischer
  Wechsel, der bei eigener Bedienung endgültig stoppt und bei
  `prefers-reduced-motion` gar nicht erst anläuft
* Sticky Header, Scroll-Reveal, Scrollspy, animierte Kennzahlen
* Ohne JavaScript bleiben alle Inhalte sichtbar und lesbar
* `prefers-reduced-motion` schaltet Animationen ab
* Sprungmarke zum Inhalt, sichtbare Fokusrahmen, ARIA-Attribute am Menü
* Impressum und Datenschutzerklärung in beiden Sprachen; der
  Sprachumschalter bleibt dabei auf der aufgerufenen Seite

## Hinweis

Adresse, Telefonnummer, E-Mail, die Kennzahlen im Abschnitt „Therapeut“
sowie die Kurstermine, Preise
und freien Plätze sind Platzhalter und vor dem Veröffentlichen zu ersetzen.
Weil abgelaufene Kurse und Bekanntmachungen automatisch herausfallen, sollte
die Seite regelmäßig neu gebaut und hochgeladen werden – das Ausblenden
geschieht beim Bauen, nicht im Browser. Ohne neuen Build bleibt der Stand des
letzten Builds stehen. Impressum und Datenschutz sind noch leere Links.

Das gelieferte Logo ist 200 × 42 Pixel groß. Im Kopfbereich wird es 32 Pixel
hoch dargestellt, was der Auflösung entspricht – auf Bildschirmen mit hoher
Pixeldichte wirkt es dadurch leicht weich. Eine größere Fassung (etwa
600 Pixel Breite) oder das Original als Vektordatei würde das beheben: Datei
als `static/img/logo.png` ablegen, `python3 tools/prepare-logo.py` ausführen,
fertig.
