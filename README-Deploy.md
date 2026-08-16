# Täglich veröffentlichen: Schritt für Schritt

Anleitungen, um die Homepage von einem Gerät aus einmal täglich neu bauen
und auf den Webspace laden zu lassen – für Synology-NAS, Linux-PC und
Windows-PC.

Geschrieben für Leute ohne Vorkenntnisse: Jeder Befehl steht vollständig
da und lässt sich abtippen oder kopieren.

Für zwei weitere Geräte gibt es eigene Dateien:

* **[README-Proxmox-Deploy.md](README-Proxmox-Deploy.md)** – ein Server mit
  Proxmox, eingerichtet in einem eigenen LXC-Container
* **[README-Unraid-Deploy.md](README-Unraid-Deploy.md)** – ein NAS mit
  Unraid, über Docker und das Plugin „User Scripts“

Was `deploy.py` überhaupt tut und wie `deploy.ini` ausgefüllt wird, steht
in der [README](README.md) unter „Veröffentlichen bei Alfahosting“.

## Inhalt

1. [Warum das sinnvoll ist](#warum-das-sinnvoll-ist)
2. [Zwei Entscheidungen vorab](#zwei-entscheidungen-vorab)
3. [Was alle Wege brauchen](#was-alle-wege-brauchen)
4. [Weg A – Synology-NAS mit dem Skript](#weg-a--synology-nas-mit-dem-skript)
5. [Weg B – Synology-NAS mit Docker](#weg-b--synology-nas-mit-docker)
6. [Weg C – Linux-PC](#weg-c--linux-pc)
7. [Weg D – Windows-PC](#weg-d--windows-pc)
8. [Inhalte pflegen: Ordner oder Git](#inhalte-pflegen-ordner-oder-git)
9. [Wenn etwas nicht klappt](#wenn-etwas-nicht-klappt)

---

## Warum das sinnvoll ist

Abgelaufene Kurstermine und Bekanntmachungen verschwinden beim **Bauen**,
nicht im Browser des Besuchers. Wer nicht daran denken möchte, lässt einen
Rechner die Seite einmal täglich neu bauen und hochladen.

Das kostet an den meisten Tagen nichts: `deploy.py` überträgt nur, was sich
geändert hat, und baut ohne Änderung nicht einmal eine Verbindung auf.

> **Und wenn sich keine Datei ändert, aber ein Kurs abläuft?** Dann wird
> trotzdem hochgeladen. Verglichen werden nicht die Textdateien, sondern
> die **gebauten** Seiten: Fällt ein Kurs heraus, sieht `index.html`
> anders aus als gestern, und genau das erkennt `deploy.py`. Nach jedem
> Build steht außerdem da, wann die nächste solche Änderung ansteht.

## Zwei Entscheidungen vorab

**Erstens: Wo soll es laufen?**

| Ort               | Passt, wenn …                                          |
| ----------------- | ------------------------------------------------------ |
| **NAS** (Synology)| das Gerät ohnehin durchläuft – dann klappt der tägliche Lauf zuverlässig |
| **Proxmox**       | ein Server mit Proxmox vorhanden ist – [eigene Anleitung](README-Proxmox-Deploy.md) |
| **Unraid**        | ein NAS mit Unraid vorhanden ist – [eigene Anleitung](README-Unraid-Deploy.md) |
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

## Was alle Wege brauchen

1. Das Projekt (dieser Ordner) auf dem Rechner, der veröffentlicht.
2. **Python 3** mit **Jinja2**. Flask aus `requirements.txt` wird *nicht*
   gebraucht – das ist nur für die lokale Vorschau.
3. Eine ausgefüllte `deploy.ini` (siehe [README](README.md), Abschnitt „Einmalig einrichten“).
4. Eine Datei, die nur das FTP-Passwort enthält.
5. Einen Zeitplaner: Aufgabenplaner (Synology), cron (Linux) oder
   Aufgabenplanung (Windows).

---

## Weg A – Synology-NAS mit dem Skript

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

## Weg B – Synology-NAS mit Docker

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

## Weg C – Linux-PC

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

## Weg D – Windows-PC

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

## Inhalte pflegen: Ordner oder Git

**Freigegebener Ordner:** Sie öffnen `translations/de.json` über die
Netzwerkfreigabe (bzw. direkt am PC), ändern den Text, speichern. Beim
nächsten Lauf ist es online. `MIT_GIT=0` lassen.

**Git:** Sie arbeiten wie gewohnt lokal, dann `git push`. Auf dem
veröffentlichenden Rechner `MIT_GIT=1` setzen – das Skript holt vor jedem
Lauf den neuen Stand. Wichtig: Auf diesem Rechner dürfen die Dateien
**nicht** von Hand geändert werden, sonst scheitert `git pull --ff-only`.

`deploy.ini`, die Passwortdatei und `.deploy-state.json` sind in
`.gitignore` eingetragen und gehen nie ins Repository.

## Wenn etwas nicht klappt

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
