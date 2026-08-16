# Täglich veröffentlichen mit einem Linux-PC

Schritt-für-Schritt-Anleitung, um die Homepage von einem Linux-Rechner aus
einmal täglich neu bauen und auf den Webspace laden zu lassen.

Geschrieben für Leute ohne Vorkenntnisse: Jeder Befehl steht vollständig
da und lässt sich abtippen oder kopieren. Die Beispiele nutzen `apt`
(Debian, Ubuntu, Mint); bei Fedora heißt der Paketbefehl `dnf`, bei
openSUSE `zypper`, bei Arch `pacman`.

Die Grundlagen – warum überhaupt täglich, was alle Wege brauchen, wie die
Texte gepflegt werden – stehen in
**[README-Deploy.md](README-Deploy.md)**. Was `deploy.py` tut und wie
`deploy.ini` ausgefüllt wird, steht in der [README](README.md) unter
„Veröffentlichen bei Alfahosting“.

> **Ein Rechner, der aus ist, veröffentlicht nichts.** Auf einem
> Arbeitsplatz-PC ist das der wunde Punkt: Ist er um fünf Uhr morgens
> ausgeschaltet, fällt der Lauf aus. Schritt 7 zeigt deshalb zwei
> Zeitplaner – und der zweite holt verpasste Läufe nach.

**Unterschiede zur Windows-Anleitung:** Python ist meist schon
installiert; der Zeitplan läuft über cron oder einen systemd-Timer statt
über die Aufgabenplanung; statt `deploy-taeglich.cmd` kommt
`deploy-taeglich.sh` zum Einsatz; und Dateirechte lassen sich mit
`chmod 600` in einem Befehl setzen.

---

## Inhalt

1. [Python und Git bereitstellen](#1-python-und-git-bereitstellen)
2. [Ordner und Umgebung anlegen](#2-ordner-und-umgebung-anlegen)
3. [Projekt ablegen](#3-projekt-ablegen)
4. [Zugangsdaten hinterlegen](#4-zugangsdaten-hinterlegen)
5. [Skript anpassen](#5-skript-anpassen)
6. [Von Hand ausprobieren](#6-von-hand-ausprobieren)
7. [Täglich laufen lassen](#7-täglich-laufen-lassen)
8. [Zeitzone prüfen](#8-zeitzone-prüfen)
9. [Später: Inhalte ändern](#9-später-inhalte-ändern)
10. [Sicherung](#10-sicherung)
11. [Häufige Stolpersteine](#11-häufige-stolpersteine)

---

## 1. Python und Git bereitstellen

Python 3 ist auf den meisten Linux-Systemen schon dabei. Prüfen:

```bash
python3 --version
```

Nachinstalliert wird nur, was fehlt:

```bash
sudo apt update
sudo apt install -y python3-venv git ca-certificates
```

| Paket | Wofür |
| --- | --- |
| `python3-venv` | erlaubt eine eigene Umgebung für die Zusatzpakete |
| `git` | nur für die Variante „Texte per Git pflegen“ |
| `ca-certificates` | Wurzelzertifikate; ohne sie schlägt die verschlüsselte FTPS-Verbindung fehl |

---

## 2. Ordner und Umgebung anlegen

Eine „virtuelle Umgebung“ ist ein Ordner mit einer eigenen
Python-Installation. So bleiben die Zusatzpakete beim Projekt und
vermischen sich nicht mit dem System.

```bash
mkdir -p ~/praxis
cd ~/praxis
python3 -m venv venv
venv/bin/pip install jinja2
```

**Nur Jinja2 wird gebraucht.** Flask aus `requirements.txt` ist allein für
die lokale Vorschau da.

Kontrolle:

```bash
~/praxis/venv/bin/python -c "import jinja2; print(jinja2.__version__)"
```

---

## 3. Projekt ablegen

Das Projekt gehört nach `~/praxis/site`. Entweder kopieren, oder:

```bash
git clone <Adresse des Repositorys> ~/praxis/site
```

Prüfen:

```bash
ls ~/praxis/site/deploy.py
```

---

## 4. Zugangsdaten hinterlegen

**Konfiguration anlegen:**

```bash
cd ~/praxis/site
cp deploy.ini.example deploy.ini
nano deploy.ini
```

Auszufüllen sind `[site] url` sowie unter `[ftp]` die Werte `host`, `user`
und `remote_dir` – sie stehen im Kundenmenü des Hosters. Speichern in
`nano`: `Strg+O`, `Enter`, `Strg+X`.

**Passwortdatei anlegen.** Das Passwort gehört weder in `deploy.ini` noch
in das Skript:

```bash
printf '%s' 'IhrFtpPasswort' > ~/praxis/ftp-passwort
chmod 600 ~/praxis/ftp-passwort
```

`printf` statt `echo` – sonst landet ein Zeilenumbruch im Passwort, und
der Server lehnt die Anmeldung ab. `chmod 600` bedeutet: nur Sie dürfen
die Datei lesen.

---

## 5. Skript anpassen

Mitgeliefert ist `~/praxis/site/tools/deploy-taeglich.sh`. Oben stehen
vier Einstellungen:

```bash
nano ~/praxis/site/tools/deploy-taeglich.sh
```

Tragen Sie dort **vollständige Pfade** ein – mit Ihrem echten
Benutzernamen statt `IhrName`:

```sh
PROJEKT="${PROJEKT:-/home/IhrName/praxis/site}"
PYTHON="${PYTHON:-/home/IhrName/praxis/venv/bin/python}"
PASSWORTDATEI="${PASSWORTDATEI:-/home/IhrName/praxis/ftp-passwort}"
MIT_GIT="${MIT_GIT:-0}"        # 1, wenn Sie in Schritt 3 Git genommen haben
```

> **Kein `~` verwenden.** In der eigenen Sitzung funktioniert die
> Abkürzung, im Zeitplan aber nicht zuverlässig – das ist die häufigste
> Ursache dafür, dass ein Skript von Hand läuft und nachts nicht.

Ausführbar machen:

```bash
chmod +x ~/praxis/site/tools/deploy-taeglich.sh
```

---

## 6. Von Hand ausprobieren

Erst ein Lauf, der nichts überträgt:

```bash
~/praxis/site/tools/deploy-taeglich.sh --dry-run
```

Erwartet: die Seite wird gebaut, danach eine Liste „würde laden …“.

Wenn das passt, dieselbe Zeile **ohne** `--dry-run`. Beim ersten Mal
werden alle Dateien übertragen.

**Rufen Sie den Befehl gleich ein zweites Mal auf** – dann muss dort
stehen:

```
23 Dateien in dist/, davon 0 geändert
Nichts zu tun – der Server hat bereits diesen Stand.
```

Erscheint das, funktioniert alles: Bauen, Hochladen und das Erkennen von
Änderungen.

---

## 7. Täglich laufen lassen

Zwei Möglichkeiten. **cron** ist in zwei Zeilen eingerichtet, der
**systemd-Timer** kann dafür verpasste Läufe nachholen – auf einem
Rechner, der nicht durchläuft, ist das der wichtigere Punkt.

### Einfach: cron

```bash
crontab -e
```

Beim ersten Aufruf wird nach einem Editor gefragt – wählen Sie `nano`.
Ganz unten anfügen (mit Ihrem echten Benutzernamen):

```
0 5 * * * /home/IhrName/praxis/site/tools/deploy-taeglich.sh >> /home/IhrName/praxis/deploy.log 2>&1
```

Das bedeutet **täglich um 05:00 Uhr**. Die fünf Felder sind Minute,
Stunde, Tag, Monat, Wochentag. Der hintere Teil schreibt Ausgabe *und*
Fehlermeldungen in eine Protokolldatei – ohne ihn verschwindet beides
ungesehen.

Kontrolle:

```bash
crontab -l                       # zeigt den Eintrag
tail -n 40 ~/praxis/deploy.log   # zeigt den letzten Lauf
```

### Besser auf einem Arbeitsplatz-PC: systemd-Timer

Vorteile: Die Ausgabe landet automatisch im Systemprotokoll, und
`Persistent=true` holt einen verpassten Lauf nach, sobald der Rechner
wieder läuft.

Zwei Dateien anlegen – hier als Dienste des eigenen Benutzers, dafür
braucht es kein `sudo`:

```bash
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/praxis-deploy.service
```

```ini
[Unit]
Description=Homepage bauen und hochladen

[Service]
Type=oneshot
ExecStart=/home/IhrName/praxis/site/tools/deploy-taeglich.sh
```

```bash
nano ~/.config/systemd/user/praxis-deploy.timer
```

```ini
[Unit]
Description=Homepage taeglich veroeffentlichen

[Timer]
OnCalendar=*-*-* 05:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Aktivieren und prüfen:

```bash
systemctl --user daemon-reload
systemctl --user enable --now praxis-deploy.timer
systemctl --user list-timers praxis-deploy.timer
```

Einmal sofort auslösen, ohne bis morgen zu warten:

```bash
systemctl --user start praxis-deploy.service
journalctl --user -u praxis-deploy.service -n 30
```

> Benutzer-Dienste laufen nur, solange Sie angemeldet sind. Soll der Timer
> unabhängig davon laufen, einmalig
> `sudo loginctl enable-linger $USER` ausführen.

Nehmen Sie **entweder** cron **oder** den Timer, nicht beides.

---

## 8. Zeitzone prüfen

Ob eine Bekanntmachung noch angezeigt wird, entscheidet das Datum des
Rechners:

```bash
timedatectl                                  # zeigt die Zeitzone
sudo timedatectl set-timezone Europe/Berlin  # falls sie falsch steht
```

---

## 9. Später: Inhalte ändern

**Ohne Git:** Die JSON-Dateien liegen unter `~/praxis/site/translations/`.
Ändern, speichern – beim nächsten Lauf ist es online.

**Mit Git (`MIT_GIT=1`):** Sie arbeiten wie gewohnt, `git commit`,
`git push`. Der Rechner holt sich den Stand beim nächsten Lauf. Soll es
sofort online sein:

```bash
~/praxis/site/tools/deploy-taeglich.sh
```

> Wichtig bei Git: Ändern Sie die Dateien **nicht** zusätzlich in diesem
> Ordner, wenn er nur veröffentlichen soll. Sonst scheitert
> `git pull --ff-only`, und der tägliche Lauf bricht ab.

---

## 10. Sicherung

Zu sichern sind drei Dinge, die es nur auf diesem Rechner gibt:

| Was | Wo |
| --- | --- |
| Projekt und Texte | `~/praxis/site` |
| Zugangsdaten | `~/praxis/site/deploy.ini` |
| FTP-Passwort | `~/praxis/ftp-passwort` |

Bei der Git-Variante stecken die Texte ohnehin im Repository; dann bleiben
nur die beiden Zugangsdateien.

---

## 11. Häufige Stolpersteine

| Meldung oder Symptom | Ursache und Abhilfe |
| --- | --- |
| `python3: command not found` | `sudo apt install python3` |
| `ensurepip is not available` | `sudo apt install python3-venv` |
| `certificate verify failed` | `sudo apt install ca-certificates` |
| `deploy.ini fehlt` | Schritt 4 nachholen; die Datei muss neben `deploy.py` liegen |
| `Passwortdatei nicht lesbar` | Pfad im Skript stimmt nicht, oder die Datei gehört einem anderen Benutzer |
| `Permission denied` beim Aufruf | `chmod +x tools/deploy-taeglich.sh` vergessen (Schritt 5) |
| `530 Login incorrect` | In der Passwortdatei steckt ein Zeilenumbruch. Mit `printf` neu schreiben, nicht mit `echo` |
| `Verzeichnis … nicht gefunden` | `remote_dir` in `deploy.ini` prüfen – es ist der Pfad, auf den die Domain zeigt |
| Von Hand klappt es, per cron nicht | fast immer ein `~` oder ein relativer Pfad im Skript – vollständig ausschreiben (Schritt 5) |
| Timer läuft nicht nach dem Abmelden | `sudo loginctl enable-linger $USER` (Schritt 7) |
| Hinweis verschwindet einen Tag zu früh | Zeitzone prüfen (Schritt 8) |
| Auf dem Server fehlt eine Datei | einmal `--all` anhängen |
| Passive FTP-Verbindung bleibt hängen | notfalls `passive = no` in `deploy.ini` |

**Was der Rechner *nicht* tut:** Er stellt die Homepage nicht selbst ins
Netz. Ausgeliefert wird sie weiterhin vom Webspace des Hosters – der PC
baut sie nur und lädt sie dorthin.
