# Täglich veröffentlichen mit Unraid

Schritt-für-Schritt-Anleitung, um die Homepage von einem Unraid-Server aus
einmal täglich neu bauen und auf den Webspace laden zu lassen.

Geschrieben für Leute, die Unraid laufen haben, aber noch nie ein eigenes
Skript eingerichtet haben. Jeder Befehl steht vollständig da und lässt
sich abtippen oder kopieren.

Was `deploy.py` überhaupt tut und wie `deploy.ini` ausgefüllt wird, steht
in der [README](README.md) unter „Veröffentlichen bei Alfahosting“.
Anleitungen für andere Geräte: [README-Deploy.md](README-Deploy.md)
(Synology, Linux, Windows) und
[README-Proxmox-Deploy.md](README-Proxmox-Deploy.md).

---

## Inhalt

1. [Warum das sinnvoll ist](#1-warum-das-sinnvoll-ist)
2. [Die Besonderheit von Unraid](#2-die-besonderheit-von-unraid)
3. [Vorbereitung: zwei Plugins](#3-vorbereitung-zwei-plugins)
4. [Zeitzone prüfen](#4-zeitzone-prüfen)
5. [Ordner anlegen](#5-ordner-anlegen)
6. [Zugang über das Terminal](#6-zugang-über-das-terminal)
7. [Projekt auf den Server bringen](#7-projekt-auf-den-server-bringen)
8. [Zugangsdaten hinterlegen](#8-zugangsdaten-hinterlegen)
9. [Docker-Bild einmal bauen](#9-docker-bild-einmal-bauen)
10. [Von Hand ausprobieren](#10-von-hand-ausprobieren)
11. [Täglich laufen lassen](#11-täglich-laufen-lassen)
12. [Benachrichtigung bei Fehlern](#12-benachrichtigung-bei-fehlern)
13. [Später: Inhalte ändern](#13-später-inhalte-ändern)
14. [Sicherung](#14-sicherung)
15. [Häufige Stolpersteine](#15-häufige-stolpersteine)

---

## 1. Warum das sinnvoll ist

Abgelaufene Kurstermine und Bekanntmachungen verschwinden von der Seite,
wenn sie **gebaut** wird – nicht im Browser des Besuchers. Ohne
regelmäßigen Lauf steht am 1. September noch die Sommerpause auf der
Startseite.

Ein Unraid-Server läuft in aller Regel durch und ist damit ein guter Ort
für diese kleine tägliche Aufgabe. Sie kostet fast nichts: An den meisten
Tagen überträgt `deploy.py` gar nichts, weil sich nichts geändert hat.

Verglichen werden dabei die **gebauten** Seiten, nicht die Textdateien. Läuft ein Kurs oder eine Bekanntmachung ab, sieht die
gebaute Seite anders aus als am Vortag und wird hochgeladen, auch wenn
niemand einen Text bearbeitet hat.

**Was am Ende jeden Morgen um fünf passiert:**

1. (optional) den neuesten Stand der Texte per Git holen,
2. die Seite neu bauen,
3. nur die geänderten Dateien per FTPS auf den Webspace laden.

---

## 2. Die Besonderheit von Unraid

Unraid unterscheidet sich in einem Punkt von einem gewöhnlichen Linux, und
daran hängt der ganze Aufbau dieser Anleitung:

> **Das Betriebssystem läuft aus dem Arbeitsspeicher und wird bei jedem
> Neustart frisch vom USB-Stick geladen.** Alles, was Sie mit einem
> Paketmanager installieren, ist nach dem nächsten Neustart wieder weg.

Ein `pip install jinja2` auf der Kommandozeile hielte also genau bis zum
nächsten Neustart. Deshalb nehmen wir zwei Dinge, die Unraid dauerhaft
speichert:

| Baustein | Wofür | Bleibt erhalten, weil … |
| --- | --- | --- |
| **Docker** | liefert Python samt Jinja2 mit | Docker-Bilder liegen auf dem Array |
| **User Scripts** (Plugin) | startet das Ganze täglich | Skripte liegen auf dem USB-Stick unter `/boot` |

Das ist auf Unraid der übliche Weg und weniger Arbeit, als es klingt: ein
Bild einmal bauen, ein Skript einmal anlegen, fertig.

> **Ohne Docker geht es auch**, über das Plugin *NerdTools*, das Python
> nachrüstet. Das ist aber der brüchigere Weg: Nach einem Unraid-Update
> kann die Python-Version wechseln und die Umgebung passt nicht mehr. Wenn
> Sie Docker ohnehin nutzen – und das tun fast alle Unraid-Anwender –,
> nehmen Sie den Weg unten.

---

## 3. Vorbereitung: zwei Plugins

**Community Applications** ist der App-Store von Unraid. Fehlt er noch:
in der Weboberfläche auf **Plugins** → **Install Plugin** und diese
Adresse einfügen:

```
https://raw.githubusercontent.com/Squidly271/community.applications/master/plugins/community.applications.plg
```

Danach erscheint oben der neue Reiter **Apps**.

**User Scripts** ist das Plugin für den Zeitplan. Reiter **Apps** → oben
nach `User Scripts` suchen → beim Treffer von *Squid* auf **Install**.

Danach findet sich das Plugin unter **Settings → User Scripts**.

---

## 4. Zeitzone prüfen

Ob eine Bekanntmachung noch angezeigt wird, entscheidet das Datum des
Servers. Steht die Zeitzone falsch, verschwindet ein Hinweis womöglich
einen Tag zu früh.

**Settings → Date and Time** → *Time zone* auf `Europe/Berlin` (oder Ihre
Zeitzone) → **Apply**.

---

## 5. Ordner anlegen

Wir legen einen eigenen Share an, damit das Projekt nicht zwischen den
Docker-Daten verschwindet.

**Shares → Add Share**

| Feld | Eintrag |
| --- | --- |
| Share name | `praxis` |
| Use cache pool | `Yes` (schneller; falls kein Cache vorhanden: `No`) |
| Export | `No` – oder `Yes (private)`, wenn Sie die Texte übers Netzwerk bearbeiten möchten |

Der Ordner liegt danach unter `/mnt/user/praxis`.

> **Zum Export:** Steht er auf `No`, ist der Ordner nur auf dem Server
> selbst erreichbar – am sichersten, denn dort liegt gleich das
> FTP-Passwort. Wenn Sie die JSON-Dateien bequem vom PC aus ändern
> möchten, wählen Sie `Yes (private)` und geben nur Ihrem eigenen
> Benutzer Schreibrechte. Auf keinen Fall `Public`.

---

## 6. Zugang über das Terminal

Rechts oben in der Weboberfläche gibt es ein Symbol **>_** (Terminal).
Ein Klick öffnet eine Kommandozeile direkt im Browser – damit brauchen Sie
kein SSH einzuschalten.

Alle folgenden Befehle werden dort eingegeben. Sie arbeiten als `root`;
auf Unraid ist das normal.

---

## 7. Projekt auf den Server bringen

Zwei Wege. **Weg A** ist bequemer, wenn die Texte ohnehin in einem
Git-Repository liegen.

### Weg A – per Git klonen

Git ist auf Unraid nicht dabei, steckt aber im Docker-Bild, das wir gleich
bauen. Deshalb klonen wir mit einem kurzlebigen Container:

```bash
cd /mnt/user/praxis
docker run --rm -v /mnt/user/praxis:/work -w /work \
  alpine/git clone <Adresse des Repositorys> site
```

### Weg B – über das Netzwerk kopieren

Steht der Share auf `Yes (private)`, erscheint er im Windows-Explorer oder
im Finder als Netzlaufwerk `\\TOWER\praxis`. Kopieren Sie den Projektordner
dort hinein und benennen Sie ihn `site`.

Prüfen, ob es geklappt hat:

```bash
ls /mnt/user/praxis/site/deploy.py
```

Erscheint der Dateiname, liegt das Projekt richtig.

---

## 8. Zugangsdaten hinterlegen

**Konfiguration anlegen:**

```bash
cd /mnt/user/praxis/site
cp deploy.ini.example deploy.ini
nano deploy.ini
```

Auszufüllen sind `[site] url` sowie unter `[ftp]` die Werte `host`, `user`
und `remote_dir` – sie stehen im Kundenmenü des Hosters. Speichern in
`nano`: `Strg+O`, `Enter`, `Strg+X`.

**Passwortdatei anlegen.** Das Passwort gehört weder in `deploy.ini` noch
in das Skript:

```bash
printf '%s' 'IhrFtpPasswort' > /mnt/user/praxis/ftp-passwort
chmod 600 /mnt/user/praxis/ftp-passwort
```

`printf` statt `echo` – sonst landet ein Zeilenumbruch im Passwort, und
der Server lehnt die Anmeldung ab.

---

## 9. Docker-Bild einmal bauen

Im Projekt liegt ein `Dockerfile`. Daraus entsteht ein Bild mit Python,
Jinja2 und Git:

```bash
cd /mnt/user/praxis/site
docker build -t praxis-deploy .
```

Der erste Lauf dauert ein paar Minuten. **Wiederholen müssen Sie ihn nur,
wenn sich das `Dockerfile` ändert – nicht bei Textänderungen.** Das
Projekt steckt nicht im Bild, sondern wird beim Start hineingereicht.

Kontrolle:

```bash
docker images | grep praxis-deploy
```

> Das Bild taucht **nicht** im Docker-Reiter der Weboberfläche auf. Der
> zeigt nur dauerhaft laufende Container; unserer läuft täglich ein paar
> Sekunden und verschwindet dann wieder. Das ist richtig so.

---

## 10. Von Hand ausprobieren

Erst ein Lauf, der nichts überträgt:

```bash
docker run --rm \
  -v /mnt/user/praxis/site:/app \
  -v /mnt/user/praxis/ftp-passwort:/pw:ro \
  praxis-deploy sh tools/deploy-taeglich.sh --dry-run
```

Was die Zeilen bedeuten:

| Teil | Bedeutung |
| --- | --- |
| `--rm` | den Container nach dem Lauf wieder wegräumen |
| `-v …/site:/app` | das Projekt in den Container reichen |
| `-v …/ftp-passwort:/pw:ro` | die Passwortdatei, nur lesbar (`ro`) |
| `--dry-run` | bauen, aber nichts übertragen |

Erwartet: die Seite wird gebaut, danach eine Liste „würde laden …“.

Wenn das passt, der echte Lauf – dieselbe Zeile ohne `--dry-run`:

```bash
docker run --rm \
  -v /mnt/user/praxis/site:/app \
  -v /mnt/user/praxis/ftp-passwort:/pw:ro \
  praxis-deploy
```

Beim ersten Mal werden alle Dateien übertragen. **Rufen Sie den Befehl
gleich ein zweites Mal auf** – dann muss dort stehen:

```
27 Dateien in dist/, davon 0 geändert
Nichts zu tun – der Server hat bereits diesen Stand.
```

Erscheint das, funktioniert alles: Bauen, Hochladen und das Erkennen von
Änderungen.

> Für die Git-Variante aus Schritt 7 zusätzlich `-e MIT_GIT=1` angeben.
> Dann holt sich der Container vor jedem Lauf den neuen Stand.

---

## 11. Täglich laufen lassen

**Settings → User Scripts → Add New Script.** Als Namen etwa
`homepage-veroeffentlichen` eingeben.

Beim neuen Eintrag auf das Zahnrad → **Edit Script**. Den vorhandenen
Inhalt löschen und einsetzen:

```bash
#!/bin/bash
docker run --rm \
  -v /mnt/user/praxis/site:/app \
  -v /mnt/user/praxis/ftp-passwort:/pw:ro \
  praxis-deploy
```

Speichern. Die Zeile `#!/bin/bash` muss ganz oben stehen und darf nicht
fehlen.

**Zeitplan setzen:** in der Auswahlliste neben dem Skript
**Custom** wählen. Darunter erscheint ein Feld für den Zeitplan; dort
eintragen:

```
0 5 * * *
```

Das bedeutet „täglich um 05:00 Uhr“. Die fünf Felder sind Minute, Stunde,
Tag, Monat, Wochentag. Unten auf **Apply** klicken – ohne das wird der
Zeitplan nicht übernommen.

**Sofort testen**, ohne bis morgen zu warten: beim Skript auf **Run
Script**. Es öffnet sich ein Fenster mit der Ausgabe.

---

## 12. Benachrichtigung bei Fehlern

Standardmäßig meldet sich nichts, wenn ein Lauf scheitert. Unraid bringt
aber ein eigenes Benachrichtigungssystem mit (Glocke rechts oben, auf
Wunsch auch per E-Mail unter *Settings → Notifications*).

Dafür das Skript aus Schritt 11 so erweitern:

```bash
#!/bin/bash
AUSGABE=$(docker run --rm \
  -v /mnt/user/praxis/site:/app \
  -v /mnt/user/praxis/ftp-passwort:/pw:ro \
  praxis-deploy 2>&1)
ERGEBNIS=$?

echo "$AUSGABE"

if [ $ERGEBNIS -ne 0 ]; then
  /usr/local/emhttp/webGui/scripts/notify \
    -e "Homepage" \
    -s "Veroeffentlichen fehlgeschlagen" \
    -d "$(echo "$AUSGABE" | tail -n 3)" \
    -i alert
fi
```

Gemeldet wird nur der Fehlerfall. Bei einem stillen, erfolgreichen Lauf
passiert nichts – sonst käme jeden Morgen eine Meldung, die nach einer
Woche niemand mehr liest.

---

## 13. Später: Inhalte ändern

**Mit Git (`-e MIT_GIT=1`):** Sie ändern die Texte wie gewohnt am eigenen
Rechner, `git commit`, `git push`. Der Server holt sich den Stand beim
nächsten Lauf. Soll es sofort online sein: im User-Scripts-Plugin auf
**Run Script**.

**Ohne Git:** Die JSON-Dateien liegen unter
`/mnt/user/praxis/site/translations/`. Steht der Share auf
`Yes (private)`, bearbeiten Sie sie direkt über das Netzlaufwerk;
andernfalls im Terminal mit `nano`.

> Wichtig bei Git: Ändern Sie die Dateien **nicht** zusätzlich auf dem
> Server. Sonst scheitert `git pull --ff-only`, und der tägliche Lauf
> bricht ab.

---

## 14. Sicherung

Zu sichern sind drei Dinge, die es nur auf dem Server gibt:

| Was | Wo |
| --- | --- |
| Projekt und Texte | `/mnt/user/praxis/site` |
| Zugangsdaten | `/mnt/user/praxis/site/deploy.ini` |
| FTP-Passwort | `/mnt/user/praxis/ftp-passwort` |

Bei der Git-Variante stecken die Texte ohnehin im Repository; dann bleiben
nur die beiden Zugangsdateien.

Ein Backup-Plugin wie *Appdata Backup* sichert standardmäßig nur
`/mnt/user/appdata`. Nehmen Sie den Share `praxis` dort mit auf, oder
kopieren Sie die beiden Dateien gelegentlich von Hand an einen sicheren
Ort.

Das Skript aus dem User-Scripts-Plugin liegt auf dem USB-Stick und ist
damit in der Flash-Sicherung enthalten (**Main → Flash → Flash backup**).

---

## 15. Häufige Stolpersteine

| Meldung oder Symptom | Ursache und Abhilfe |
| --- | --- |
| `Unable to find image 'praxis-deploy'` | Schritt 9 fehlt oder wurde in einem anderen Verzeichnis ausgeführt |
| `deploy.ini fehlt` | Schritt 8 nachholen; die Datei muss neben `deploy.py` liegen |
| `Passwortdatei nicht lesbar` | Der Pfad hinter `-v` stimmt nicht, oder die Datei fehlt |
| `530 Login incorrect` | In der Passwortdatei steckt ein Zeilenumbruch. Mit `printf` neu schreiben, nicht mit `echo` |
| `Verzeichnis … nicht gefunden` | `remote_dir` in `deploy.ini` prüfen – es ist der Pfad, auf den die Domain zeigt |
| Skript läuft über **Run Script**, aber nicht nach Plan | Zeitplan auf `Custom` gestellt, aber **Apply** vergessen |
| Nach einem Neustart ist alles weg | Sie haben Python direkt auf dem Server installiert statt im Container – siehe Abschnitt 2 |
| Hinweis verschwindet einen Tag zu früh | Zeitzone prüfen (Schritt 4) |
| Auf dem Server fehlt eine Datei | einmal `--all` anhängen: `… praxis-deploy sh tools/deploy-taeglich.sh --all` |
| Verbindung bleibt hängen | passives FTP wird von der Firewall geblockt; notfalls `passive = no` in `deploy.ini` |

**Was der Server *nicht* tut:** Er stellt die Homepage nicht selbst ins
Netz. Ausgeliefert wird sie weiterhin vom Webspace des Hosters – Unraid
baut sie nur und lädt sie dorthin.
