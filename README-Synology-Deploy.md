# Täglich veröffentlichen mit einem Synology-NAS

Schritt-für-Schritt-Anleitung, um die Homepage von einer DiskStation aus
einmal täglich neu bauen und auf den Webspace laden zu lassen.

Geschrieben für Leute ohne Vorkenntnisse: Jeder Befehl steht vollständig
da und lässt sich abtippen oder kopieren. Menüpfade nach DSM 7,
Beispielpfade für eine DS720+; bei anderen Modellen heißen die Menüpunkte
genauso.

Die Grundlagen – warum überhaupt täglich, was alle Wege brauchen, wie die
Texte gepflegt werden – stehen in
**[README-Deploy.md](README-Deploy.md)**. Was `deploy.py` tut und wie
`deploy.ini` ausgefüllt wird, steht in der [README](README.md) unter
„Veröffentlichen bei Alfahosting“.

---

## Inhalt

1. [Zwei Wege zur Auswahl](#1-zwei-wege-zur-auswahl)
2. [Ordner anlegen](#2-ordner-anlegen)
3. [SSH einschalten](#3-ssh-einschalten)
4. [Projekt auf das NAS bringen](#4-projekt-auf-das-nas-bringen)
5. [Zugangsdaten hinterlegen](#5-zugangsdaten-hinterlegen)
6. [Weg A – mit Python auf dem NAS](#6-weg-a--mit-python-auf-dem-nas)
7. [Weg B – mit Docker](#7-weg-b--mit-docker)
8. [Von Hand ausprobieren](#8-von-hand-ausprobieren)
9. [Aufgabenplaner einrichten](#9-aufgabenplaner-einrichten)
10. [Zeitzone prüfen](#10-zeitzone-prüfen)
11. [Später: Inhalte ändern](#11-später-inhalte-ändern)
12. [Sicherung](#12-sicherung)
13. [Häufige Stolpersteine](#13-häufige-stolpersteine)

---

## 1. Zwei Wege zur Auswahl

Beide führen zum selben Ergebnis. Sie unterscheiden sich nur darin, woher
Python kommt:

| | Weg A – Python auf dem NAS | Weg B – Docker |
| --- | --- | --- |
| Aufwand | etwas weniger | etwas mehr |
| Auf dem NAS installiert | Python 3 aus dem Paketzentrum | nur Container Manager |
| Passt, wenn … | Sie es einfach halten möchten | Sie ohnehin mit Containern arbeiten |

**Wenn Sie unsicher sind: Weg A.** Der Zeitplan kommt in beiden Fällen vom
Aufgabenplaner – Docker bringt keinen eigenen mit.

Die Schritte 2 bis 5 gelten für beide Wege. Danach folgen Sie entweder
Abschnitt 6 oder Abschnitt 7.

---

## 2. Ordner anlegen

Systemsteuerung → **Freigegebener Ordner** → **Erstellen**. Als Namen etwa
`web-praxis`.

Der Ordner liegt danach unter `/volume1/web-praxis` und ist im Netzwerk als
Laufwerk erreichbar – praktisch, wenn Sie die Texte später vom PC aus
bearbeiten möchten.

> Achten Sie bei den Berechtigungen darauf, dass nur Ihr eigener Benutzer
> Zugriff hat. Gleich liegt dort das FTP-Passwort.

---

## 3. SSH einschalten

Für die Einrichtung brauchen Sie eine Kommandozeile auf dem NAS.

Systemsteuerung → **Terminal & SNMP** → **SSH-Dienst aktivieren** →
*Übernehmen*.

Danach vom PC aus verbinden – unter Windows in der Eingabeaufforderung,
unter Linux und macOS im Terminal:

```bash
ssh IhrBenutzer@192.168.1.50      # IP-Adresse des NAS
```

Die IP-Adresse steht in der DSM-Oberfläche unter Systemsteuerung →
*Info-Center*.

> Wenn Sie fertig eingerichtet haben, können Sie den SSH-Dienst wieder
> abschalten. Der tägliche Lauf braucht ihn nicht.

---

## 4. Projekt auf das NAS bringen

Zwei Möglichkeiten:

### Über die Netzwerkfreigabe

Öffnen Sie `\\DiskStation\web-praxis` im Windows-Explorer (oder im Finder
über *Gehe zu → Mit Server verbinden*) und kopieren Sie den Projektordner
hinein. Er soll danach `site` heißen.

### Per Git

Dafür im Paketzentrum das Paket **Git Server** installieren – es bringt
den `git`-Befehl mit. Dann in der SSH-Sitzung:

```bash
cd /volume1/web-praxis
git clone <Adresse des Repositorys> site
```

Prüfen, ob es geklappt hat:

```bash
ls /volume1/web-praxis/site/deploy.py
```

Erscheint der Dateiname, liegt das Projekt richtig.

---

## 5. Zugangsdaten hinterlegen

**Konfiguration anlegen:**

```bash
cd /volume1/web-praxis/site
cp deploy.ini.example deploy.ini
vi deploy.ini
```

Auszufüllen sind `[site] url` sowie unter `[ftp]` die Werte `host`, `user`
und `remote_dir` – sie stehen im Kundenmenü des Hosters.

> **`vi` kurz erklärt**, falls Sie ihn nicht kennen: `i` drückt, um zu
> schreiben; `Esc`, um damit aufzuhören; dann `:wq` und `Enter` zum
> Speichern. Bequemer ist es, die Datei über die Netzwerkfreigabe mit
> einem gewohnten Editor zu bearbeiten.

**Passwortdatei anlegen.** Das Passwort gehört weder in `deploy.ini` noch
in das Skript:

```bash
printf '%s' 'IhrFtpPasswort' > /volume1/web-praxis/ftp-passwort
chmod 600 /volume1/web-praxis/ftp-passwort
```

`printf` statt `echo` – sonst landet ein Zeilenumbruch im Passwort, und
der Server lehnt die Anmeldung ab.

---

## 6. Weg A – mit Python auf dem NAS

**Python installieren:** Paketzentrum → nach *Python* suchen → **Python 3**
installieren. Danach in der SSH-Sitzung prüfen:

```bash
python3 --version
```

Kommt „command not found“, liegt es nur am Suchpfad. Schreiben Sie dann
überall statt `python3` den vollen Pfad:
`/var/packages/Python3/target/bin/python3`

**Umgebung für Jinja2 anlegen.** Eine „virtuelle Umgebung“ ist ein Ordner
mit einer eigenen Python-Installation – so bleiben die Zusatzpakete beim
Projekt:

```bash
cd /volume1/web-praxis
python3 -m venv venv
venv/bin/pip install jinja2
```

**Nur Jinja2 wird gebraucht.** Flask aus `requirements.txt` ist allein für
die lokale Vorschau da.

**Skript anpassen:** In `tools/deploy-taeglich.sh` stehen oben vier
Einstellungen. Bei den Pfaden aus dieser Anleitung passen sie bereits.
Setzen Sie nur `MIT_GIT=1`, wenn Sie in Schritt 4 Git genommen haben:

```bash
vi /volume1/web-praxis/site/tools/deploy-taeglich.sh
```

Weiter mit [Schritt 8](#8-von-hand-ausprobieren).

---

## 7. Weg B – mit Docker

**Container Manager installieren:** Paketzentrum → **Container Manager**
(bei älteren DSM-Versionen heißt das Paket *Docker*).

**Bild einmal bauen.** Im Projekt liegt ein `Dockerfile` mit allem Nötigen
– Python, Jinja2 und Git:

```bash
cd /volume1/web-praxis/site
sudo docker build -t praxis-deploy .
```

Das dauert beim ersten Mal ein paar Minuten. **Wiederholen müssen Sie es
nur, wenn sich das `Dockerfile` ändert – nicht bei Textänderungen.** Das
Projekt steckt nicht im Bild, sondern wird beim Start hineingereicht.

> Das Bild taucht **nicht** in der Container-Übersicht der Oberfläche auf.
> Die zeigt nur dauerhaft laufende Container; unserer läuft täglich ein
> paar Sekunden und verschwindet dann wieder. Das ist richtig so.

Der Befehl für einen Lauf sieht damit so aus:

```bash
sudo docker run --rm \
  -v /volume1/web-praxis/site:/app \
  -v /volume1/web-praxis/ftp-passwort:/pw:ro \
  praxis-deploy
```

Was die Zeilen bedeuten:

| Teil | Bedeutung |
| --- | --- |
| `--rm` | den Container nach dem Lauf wieder wegräumen |
| `-v …/site:/app` | das Projekt in den Container reichen |
| `-v …/ftp-passwort:/pw:ro` | die Passwortdatei, nur lesbar (`ro`) |

Für die Git-Variante zusätzlich `-e MIT_GIT=1` angeben.

---

## 8. Von Hand ausprobieren

Erst ein Lauf, der nichts überträgt.

**Weg A:**

```bash
sh /volume1/web-praxis/site/tools/deploy-taeglich.sh --dry-run
```

**Weg B:**

```bash
sudo docker run --rm \
  -v /volume1/web-praxis/site:/app \
  -v /volume1/web-praxis/ftp-passwort:/pw:ro \
  praxis-deploy sh tools/deploy-taeglich.sh --dry-run
```

Erwartet: die Seite wird gebaut, danach eine Liste „würde laden …“.

Wenn das passt, dieselbe Zeile **ohne** `--dry-run`. Beim ersten Mal
werden alle Dateien übertragen.

**Rufen Sie den Befehl gleich ein zweites Mal auf** – dann muss dort
stehen:

```
27 Dateien in dist/, davon 0 geändert
Nichts zu tun – der Server hat bereits diesen Stand.
```

Erscheint das, funktioniert alles: Bauen, Hochladen und das Erkennen von
Änderungen.

---

## 9. Aufgabenplaner einrichten

Systemsteuerung → **Aufgabenplaner** → **Erstellen** → **Geplante
Aufgabe** → **Benutzerdefiniertes Skript**.

| Feld | Eintrag |
| --- | --- |
| Aufgabenname | z. B. `Homepage veröffentlichen` |
| Benutzer | **Weg A:** der Besitzer des Ordners, nicht `root`. **Weg B:** `root` – anders lässt sich kein Container starten |
| Zeitplan | täglich, z. B. 05:00 |
| Benachrichtigung | E-Mail eintragen, **„Nur bei abnormalem Beenden“** anhaken |

Als **Befehl** – bei Weg A:

```bash
sh /volume1/web-praxis/site/tools/deploy-taeglich.sh
```

Bei Weg B, alles in einer Zeile:

```bash
docker run --rm -v /volume1/web-praxis/site:/app -v /volume1/web-praxis/ftp-passwort:/pw:ro praxis-deploy
```

Ohne die Einschränkung auf Fehler kommt jeden Morgen eine Mail, auch wenn
nichts passiert ist – nach einer Woche liest sie niemand mehr.

**Sofort testen**, ohne bis morgen zu warten: die Aufgabe markieren und
oben auf **Ausführen** klicken.

---

## 10. Zeitzone prüfen

Ob eine Bekanntmachung noch angezeigt wird, entscheidet das Datum des
NAS. Steht die Zeitzone falsch, verschwindet ein Hinweis womöglich einen
Tag zu früh.

Systemsteuerung → **Regionale Optionen** → *Zeit* → Zeitzone auf
`(GMT+01:00) Amsterdam, Berlin, …` stellen.

---

## 11. Später: Inhalte ändern

**Ohne Git:** Die JSON-Dateien liegen unter
`/volume1/web-praxis/site/translations/`. Öffnen Sie sie über die
Netzwerkfreigabe mit einem gewohnten Editor, ändern Sie den Text,
speichern – beim nächsten Lauf ist es online.

**Mit Git (`MIT_GIT=1`):** Sie arbeiten wie gewohnt am eigenen Rechner,
`git commit`, `git push`. Das NAS holt sich den Stand beim nächsten Lauf.
Soll es sofort online sein, im Aufgabenplaner auf **Ausführen**.

> Wichtig bei Git: Ändern Sie die Dateien **nicht** zusätzlich auf dem
> NAS. Sonst scheitert `git pull --ff-only`, und der tägliche Lauf bricht
> ab.

---

## 12. Sicherung

Zu sichern sind drei Dinge, die es nur auf dem NAS gibt:

| Was | Wo |
| --- | --- |
| Projekt und Texte | `/volume1/web-praxis/site` |
| Zugangsdaten | `/volume1/web-praxis/site/deploy.ini` |
| FTP-Passwort | `/volume1/web-praxis/ftp-passwort` |

Bei der Git-Variante stecken die Texte ohnehin im Repository; dann bleiben
nur die beiden Zugangsdateien.

Nehmen Sie den Ordner `web-praxis` in Ihre gewohnte Sicherung auf – etwa
über *Hyper Backup* oder eine Kopie auf einen USB-Datenträger.

---

## 13. Häufige Stolpersteine

| Meldung oder Symptom | Ursache und Abhilfe |
| --- | --- |
| `python3: command not found` | Paket *Python 3* fehlt, oder der Suchpfad greift nicht – vollen Pfad verwenden (Schritt 6) |
| `deploy.ini fehlt` | Schritt 5 nachholen; die Datei muss neben `deploy.py` liegen |
| `Passwortdatei nicht lesbar` | Pfad im Skript stimmt nicht, oder der Aufgaben-Benutzer darf die Datei nicht lesen |
| `530 Login incorrect` | In der Passwortdatei steckt ein Zeilenumbruch. Mit `printf` neu schreiben, nicht mit `echo` |
| `Verzeichnis … nicht gefunden` | `remote_dir` in `deploy.ini` prüfen – es ist der Pfad, auf den die Domain zeigt |
| `permission denied` beim `docker`-Befehl | Die Aufgabe läuft nicht als `root` (Weg B) |
| Läuft von Hand, aber nicht im Zeitplan | fast immer ein anderer Benutzer oder ein relativer Pfad – im Befehl alles ausschreiben |
| Hinweis verschwindet einen Tag zu früh | Zeitzone prüfen (Schritt 10) |
| Auf dem Server fehlt eine Datei | einmal `--all` anhängen |
| Passive FTP-Verbindung bleibt hängen | notfalls `passive = no` in `deploy.ini` |

**Was das NAS *nicht* tut:** Es stellt die Homepage nicht selbst ins Netz.
Ausgeliefert wird sie weiterhin vom Webspace des Hosters – das NAS baut
sie nur und lädt sie dorthin.
