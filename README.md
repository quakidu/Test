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
content.py              Kursauswahl, Datumsformate, strukturierte Daten
requirements.txt        Abhängigkeiten
Dockerfile              Bild für den täglichen Lauf im Container
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
  img/praxis-1.jpg …    Platzhalter für die Diashow, bitte ersetzen
  img/therapeut.jpg     Platzhalter für das Porträt, bitte ersetzen
  img/foerderer-1.png … Platzhalter für die Förderlogos, bitte ersetzen
  img/og-bild.png       Vorschaubild für geteilte Links (erzeugt)
  img/og-bild-en.png    dasselbe für die englische Fassung
translations/
  de.json  en.json
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

**Übertragen wird nur, was sich geändert hat.** Welche Dateien zuletzt
oben lagen, merkt sich `.deploy-state.json` als Liste von Prüfsummen
(lokal, gitignoriert). Hat sich nichts geändert, baut das Skript gar keine
Verbindung auf und fragt auch kein Passwort ab:

```
27 Dateien in dist/, davon 0 geändert
Nichts zu tun – der Server hat bereits diesen Stand.
```

Zeigt `deploy.ini` auf einen anderen Server oder ein anderes Verzeichnis,
gilt der gemerkte Stand nicht mehr und es wird wieder alles übertragen.
Dasselbe erzwingt `--all`, falls auf dem Server einmal etwas fehlt.

Soll das täglich von allein passieren, steht die Schritt-für-Schritt-
Anleitung weiter unten unter „Täglich automatisch veröffentlichen“.

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
3. Erscheint die englische Fassung unter `ihre-domain.de/en/`?
4. Sind `/robots.txt`, `/sitemap.xml` und `/llms.txt` erreichbar, und
   steht darin die richtige Domain?

CSS, JavaScript und Bilder werden mit einem Versionsstempel verlinkt
(`style.css?v=7392bb8c`), der sich bei jeder Änderung mitändert. Deshalb
dürfen sie lange im Browser-Cache liegen, ohne dass Besucher nach einer
Aktualisierung eine veraltete Fassung sehen.

## Täglich automatisch veröffentlichen

Abgelaufene Kurstermine und Bekanntmachungen verschwinden beim **Bauen**,
nicht im Browser des Besuchers. Wer nicht daran denken möchte, lässt einen
Rechner die Seite einmal täglich neu bauen und hochladen.

Das kostet an den meisten Tagen nichts: `deploy.py` überträgt nur, was sich
geändert hat, und baut ohne Änderung nicht einmal eine Verbindung auf.

### Zwei Entscheidungen vorab

**Erstens: Wo soll es laufen?**

| Ort               | Passt, wenn …                                          |
| ----------------- | ------------------------------------------------------ |
| **NAS** (Synology)| das Gerät ohnehin durchläuft – dann klappt der tägliche Lauf zuverlässig |
| **Desktop-PC**    | kein NAS da ist. Achtung: Ist der Rechner um 5 Uhr aus, passiert nichts |

**Zweitens: Wie kommen die Texte auf diesen Rechner?**

| Variante                | Vorgehen                                              |
| ----------------------- | ----------------------------------------------------- |
| **Freigegebener Ordner**| Das Projekt liegt einmal auf dem NAS. Sie öffnen die JSON-Dateien vom PC aus über die Netzwerkfreigabe und ändern sie dort. Kein Git nötig |
| **Git**                 | Sie arbeiten wie bisher am PC, `git push`, und der Rechner holt sich vor jedem Lauf den neuen Stand |

Für eine Person, die die Texte selbst pflegt, reicht der **freigegebene
Ordner**. **Git** lohnt sich, sobald mehrere Leute etwas ändern oder Sie
alte Stände zurückholen möchten. Beides funktioniert mit jedem der Wege
unten – der Unterschied ist eine Zeile im Skript.

### Was alle Wege brauchen

1. Das Projekt (dieser Ordner) auf dem Rechner, der veröffentlicht.
2. **Python 3** mit **Jinja2**. Flask aus `requirements.txt` wird *nicht*
   gebraucht – das ist nur für die lokale Vorschau.
3. Eine ausgefüllte `deploy.ini` (siehe „Einmalig einrichten“ oben).
4. Eine Datei, die nur das FTP-Passwort enthält.
5. Einen Zeitplaner: Aufgabenplaner (Synology), cron (Linux) oder
   Aufgabenplanung (Windows).

---

### Weg A – Synology-NAS mit dem Skript

Der einfachere der beiden NAS-Wege. Beispiel für eine DS720+ unter DSM 7;
Menüpunkte heißen bei anderen Modellen genauso.

**Schritt 1 – Ordner anlegen.** Systemsteuerung → *Freigegebener Ordner* →
*Erstellen*. Name z. B. `web-praxis`. Er liegt danach unter
`/volume1/web-praxis` und ist im Netzwerk als Laufwerk erreichbar.

**Schritt 2 – SSH einschalten.** Systemsteuerung → *Terminal & SNMP* →
*SSH-Dienst aktivieren*. Danach vom PC aus verbinden (Windows:
`Eingabeaufforderung`, Linux: Terminal):

```bash
ssh IhrBenutzer@192.168.1.50      # IP des NAS
```

**Schritt 3 – Python installieren.** Paketzentrum → nach *Python* suchen →
*Python 3* installieren. Dann in der SSH-Sitzung prüfen:

```bash
python3 --version
```

Kommt „command not found“, liegt es am Suchpfad; dann statt `python3`
überall `/var/packages/Python3/target/bin/python3` schreiben.

**Schritt 4 – Umgebung für Jinja2 anlegen.**

```bash
cd /volume1/web-praxis
python3 -m venv venv
venv/bin/pip install jinja2
```

**Schritt 5 – Projekt ablegen.** Entweder über die Netzwerkfreigabe in
`web-praxis` hineinkopieren (Zielordner: `site`), oder per Git:

```bash
cd /volume1/web-praxis
git clone <Adresse des Repositorys> site
```

Für Git braucht es das Paket *Git Server* aus dem Paketzentrum; es bringt
den `git`-Befehl mit.

**Schritt 6 – Zugangsdaten hinterlegen.**

```bash
cd /volume1/web-praxis/site
cp deploy.ini.example deploy.ini
vi deploy.ini                       # Domain, Host, Benutzer, remote_dir

printf '%s' 'IhrFtpPasswort' > /volume1/web-praxis/ftp-passwort
chmod 600 /volume1/web-praxis/ftp-passwort
```

`printf` statt `echo`, damit kein Zeilenumbruch im Passwort landet.

**Schritt 7 – Skript anpassen und ausprobieren.** In
`tools/deploy-taeglich.sh` stehen oben vier Einstellungen. Bei den obigen
Pfaden passen sie bereits; nur `MIT_GIT=1` setzen, wenn Sie Schritt 5 mit
Git gemacht haben. Dann ein Probelauf, der nichts überträgt:

```bash
sh tools/deploy-taeglich.sh --dry-run
```

Sieht das gut aus, einmal echt laufen lassen:

```bash
sh tools/deploy-taeglich.sh
```

**Schritt 8 – Aufgabenplaner einrichten.** Systemsteuerung →
*Aufgabenplaner* → *Erstellen* → *Geplante Aufgabe* → *Benutzerdefiniertes
Skript*.

| Feld              | Eintrag                                                    |
| ----------------- | ---------------------------------------------------------- |
| Aufgabenname      | z. B. `Homepage veröffentlichen`                            |
| Benutzer          | nicht `root`, sondern der Besitzer des Ordners              |
| Zeitplan          | täglich, z. B. 05:00                                        |
| Befehl            | `sh /volume1/web-praxis/site/tools/deploy-taeglich.sh`      |
| Benachrichtigung  | E-Mail eintragen, **„Nur bei abnormalem Beenden“** anhaken  |

Ohne die Einschränkung auf Fehler kommt jeden Morgen eine Mail, auch wenn
nichts passiert ist – nach einer Woche liest sie niemand mehr.

---

### Weg B – Synology-NAS mit Docker

Gleiches Ergebnis, aber ohne Python auf dem NAS: Alles Nötige steckt im
Container. Der Zeitplan kommt weiterhin vom Aufgabenplaner – Docker
bringt keinen eigenen mit.

**Ehrlich gesagt:** Wenn Sie nicht ohnehin mit Containern arbeiten, ist
Weg A einfacher. Der Vorteil hier ist, dass auf dem NAS nichts installiert
wird außer Docker selbst.

**Schritt 1 – Container Manager installieren.** Paketzentrum →
*Container Manager* (bei älteren DSM-Versionen heißt das Paket *Docker*).

**Schritt 2 bis 3 – Ordner, SSH, Projekt und Zugangsdaten** genau wie in
Weg A, Schritte 1, 2, 5 und 6. Python und das venv entfallen.

**Schritt 4 – Bild einmal bauen.** Im Projekt liegt ein `Dockerfile`. In
der SSH-Sitzung:

```bash
cd /volume1/web-praxis/site
sudo docker build -t praxis-deploy .
```

Das dauert beim ersten Mal ein paar Minuten. Wiederholen müssen Sie es
nur, wenn sich das `Dockerfile` ändert – **nicht** bei Textänderungen: Das
Projekt steckt nicht im Bild, sondern wird beim Start hineingereicht.

**Schritt 5 – Probelauf.**

```bash
sudo docker run --rm \
  -v /volume1/web-praxis/site:/app \
  -v /volume1/web-praxis/ftp-passwort:/pw:ro \
  praxis-deploy sh tools/deploy-taeglich.sh --dry-run
```

Was die Zeilen bedeuten:

| Teil                          | Bedeutung                                    |
| ----------------------------- | -------------------------------------------- |
| `--rm`                        | Container nach dem Lauf wieder wegräumen      |
| `-v …/site:/app`              | das Projekt in den Container reichen          |
| `-v …/ftp-passwort:/pw:ro`    | die Passwortdatei, nur lesbar (`ro`)          |

Ohne `--dry-run` läuft es echt. Für die Git-Variante zusätzlich
`-e MIT_GIT=1` angeben – `git` ist im Bild enthalten.

**Schritt 6 – Aufgabenplaner einrichten** wie in Weg A, Schritt 8, nur mit
diesem Befehl (alles in einer Zeile):

```bash
docker run --rm -v /volume1/web-praxis/site:/app -v /volume1/web-praxis/ftp-passwort:/pw:ro praxis-deploy
```

Hier muss der Benutzer `root` sein oder der Docker-Gruppe angehören –
anders lässt sich kein Container starten.

---

### Weg C – Linux-PC

**Schritt 1 – Python und Jinja2.**

```bash
sudo apt install python3-venv git      # Debian/Ubuntu
mkdir -p ~/praxis && cd ~/praxis
python3 -m venv venv
venv/bin/pip install jinja2
```

**Schritt 2 – Projekt ablegen**, entweder kopieren nach `~/praxis/site`
oder:

```bash
git clone <Adresse des Repositorys> ~/praxis/site
```

**Schritt 3 – Zugangsdaten.**

```bash
cd ~/praxis/site
cp deploy.ini.example deploy.ini && nano deploy.ini
printf '%s' 'IhrFtpPasswort' > ~/praxis/ftp-passwort
chmod 600 ~/praxis/ftp-passwort
```

**Schritt 4 – Skript anpassen.** In `tools/deploy-taeglich.sh` die vier
Pfade auf `/home/IhrName/praxis/…` ändern (`~` versteht cron nicht
zuverlässig – bitte ausschreiben). Probelauf:

```bash
sh tools/deploy-taeglich.sh --dry-run
```

**Schritt 5 – cron eintragen.**

```bash
crontab -e
```

und als Zeile einfügen:

```
0 5 * * * /home/IhrName/praxis/site/tools/deploy-taeglich.sh >> /home/IhrName/praxis/deploy.log 2>&1
```

`0 5 * * *` heißt „täglich um 05:00“. Die Umleitung schreibt Ausgabe und
Fehler in eine Datei – ohne sie verschwindet beides ungesehen. Das Skript
muss dafür ausführbar sein: `chmod +x tools/deploy-taeglich.sh`.

---

### Weg D – Windows-PC

**Schritt 1 – Python installieren.** Von <https://www.python.org/downloads/>
holen und im Installationsfenster **„Add python.exe to PATH“ ankreuzen** –
sonst findet die Aufgabenplanung Python später nicht.

**Schritt 2 – Ordner und Umgebung.** Eingabeaufforderung öffnen:

```cmd
mkdir C:\Praxis
cd C:\Praxis
py -3 -m venv venv
venv\Scripts\pip install jinja2
```

**Schritt 3 – Projekt ablegen** nach `C:\Praxis\site` – kopieren oder,
mit installiertem [Git für Windows](https://git-scm.com/download/win):

```cmd
git clone <Adresse des Repositorys> C:\Praxis\site
```

**Schritt 4 – Zugangsdaten.** `deploy.ini.example` nach `deploy.ini`
kopieren und ausfüllen. Dann eine Textdatei `C:\Praxis\ftp-passwort.txt`
anlegen, die **nur** das Passwort enthält – ohne Leerzeichen am
Zeilenende, die zählten mit. Über Rechtsklick → *Eigenschaften* →
*Sicherheit* die Zugriffsrechte auf Ihr Benutzerkonto beschränken.

**Schritt 5 – Skript anpassen und testen.** In
`tools\deploy-taeglich.cmd` stehen oben vier Einstellungen; bei den
Pfaden oben passen sie bereits. Probelauf in der Eingabeaufforderung:

```cmd
C:\Praxis\site\tools\deploy-taeglich.cmd --dry-run
```

**Schritt 6 – Aufgabenplanung einrichten.** Startmenü → *Aufgabenplanung*
→ rechts *Einfache Aufgabe erstellen*.

| Schritt        | Eintrag                                               |
| -------------- | ----------------------------------------------------- |
| Name           | z. B. `Homepage veröffentlichen`                       |
| Trigger        | *Täglich*, Uhrzeit z. B. 05:00                         |
| Aktion         | *Programm starten*                                     |
| Programm       | `C:\Praxis\site\tools\deploy-taeglich.cmd`             |
| „Starten in“   | `C:\Praxis\site`                                       |

Danach in den Eigenschaften der Aufgabe:

* **„Unabhängig von der Benutzeranmeldung ausführen“** lässt die Aufgabe
  auch laufen, wenn niemand angemeldet ist – Windows verlangt dafür Ihr
  Windows-Kennwort.
* **„Aufgabe so schnell wie möglich nach einem verpassten Start
  ausführen“** anhaken. Sonst fällt der Lauf aus, wenn der Rechner um
  5 Uhr aus war.

---

### Inhalte pflegen: Ordner oder Git

**Freigegebener Ordner:** Sie öffnen `translations/de.json` über die
Netzwerkfreigabe (bzw. direkt am PC), ändern den Text, speichern. Beim
nächsten Lauf ist es online. `MIT_GIT=0` lassen.

**Git:** Sie arbeiten wie gewohnt lokal, dann `git push`. Auf dem
veröffentlichenden Rechner `MIT_GIT=1` setzen – das Skript holt vor jedem
Lauf den neuen Stand. Wichtig: Auf diesem Rechner dürfen die Dateien
**nicht** von Hand geändert werden, sonst scheitert `git pull --ff-only`.

`deploy.ini`, die Passwortdatei und `.deploy-state.json` sind in
`.gitignore` eingetragen und gehen nie ins Repository.

### Wenn etwas nicht klappt

| Meldung                                   | Ursache und Abhilfe                         |
| ----------------------------------------- | ------------------------------------------- |
| `deploy.ini fehlt`                        | Schritt „Zugangsdaten“ nachholen            |
| `Passwortdatei nicht lesbar`              | Pfad im Skript stimmt nicht, oder die Rechte lassen den Aufgaben-Benutzer nicht lesen |
| `Verzeichnis … nicht gefunden`            | `remote_dir` in `deploy.ini` prüfen (Kundenmenü → Domains) |
| `530 Login incorrect`                     | Passwortdatei enthält einen Zeilenumbruch oder ein Leerzeichen zu viel |
| Läuft von Hand, aber nicht im Zeitplan    | fast immer relative Pfade oder ein anderer Benutzer – im Skript alles ausschreiben |
| Seite ändert sich nicht                   | `--all` erzwingt einmal die vollständige Übertragung |

**Zeitzone prüfen.** Das Ausblenden vergleicht mit dem Datum des Geräts.
Steht die Zeitzone falsch (Synology: Systemsteuerung → *Regionale
Optionen*), verschwindet ein Hinweis einen Tag zu früh oder zu spät.

**`--delete` ist bewusst nicht gesetzt.** Mit dem Schalter räumt jeder Lauf
auf dem Server auf – dann darf im Zielverzeichnis nichts liegen, was nicht
aus `dist/` stammt. Wenn dort ausschließlich diese Seite liegt, können Sie
ihn im Skript an `deploy.py` anhängen.

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
  „Route planen“. Beide Werte müssen in `de.json` und `en.json`
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
`translations/de.json` und `translations/en.json`. Daraus baut der Build den
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
* **Kanonische Adresse**, `hreflang` für Deutsch/Englisch und `x-default`,
  Open Graph und Twitter-Card. Die Fehlerseite trägt `noindex`.

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
* Sprachumschalter im Kopfbereich, `hreflang`-Verweise im `<head>`
* Kurse in einem eigenen, farblich abgesetzten Abschnitt mit Startdatum,
  freien Plätzen und Preis; Hinweis auf den nächsten Kurs schon bei den
  Bekanntmachungen – beides aus derselben Liste erzeugt
* abgelaufene Kurstermine und Bekanntmachungen fallen automatisch heraus
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
