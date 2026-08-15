# Täglich veröffentlichen mit Proxmox

Schritt-für-Schritt-Anleitung, um die Homepage von einem Proxmox-Server
aus einmal täglich neu bauen und auf den Webspace laden zu lassen.

Geschrieben für Leute, die Proxmox zwar installiert haben, aber noch nie
einen Container von Hand eingerichtet haben. Jeder Befehl steht
vollständig da und lässt sich abtippen oder kopieren.

Die allgemeine Erklärung – warum überhaupt täglich, was `deploy.py` tut –
steht in der [README](README.md) im Abschnitt „Täglich automatisch
veröffentlichen“. Diese Datei behandelt nur den Weg über Proxmox.

---

## Inhalt

1. [Warum das sinnvoll ist](#1-warum-das-sinnvoll-ist)
2. [LXC-Container oder virtuelle Maschine?](#2-lxc-container-oder-virtuelle-maschine)
3. [Vorbereitung: Vorlage herunterladen](#3-vorbereitung-vorlage-herunterladen)
4. [Container anlegen](#4-container-anlegen)
5. [Erster Start und Anmeldung](#5-erster-start-und-anmeldung)
6. [Grundeinrichtung im Container](#6-grundeinrichtung-im-container)
7. [Projekt in den Container bringen](#7-projekt-in-den-container-bringen)
8. [Python-Umgebung anlegen](#8-python-umgebung-anlegen)
9. [Zugangsdaten hinterlegen](#9-zugangsdaten-hinterlegen)
10. [Von Hand ausprobieren](#10-von-hand-ausprobieren)
11. [Täglich laufen lassen](#11-täglich-laufen-lassen)
12. [Ergebnis prüfen und Fehler finden](#12-ergebnis-prüfen-und-fehler-finden)
13. [Sicherung einrichten](#13-sicherung-einrichten)
14. [Später: Inhalte ändern](#14-später-inhalte-ändern)
15. [Häufige Stolpersteine](#15-häufige-stolpersteine)

---

## 1. Warum das sinnvoll ist

Abgelaufene Kurstermine und Bekanntmachungen verschwinden von der Seite,
wenn sie **gebaut** wird – nicht im Browser des Besuchers. Ohne
regelmäßigen Lauf steht am 1. September noch die Sommerpause auf der
Startseite.

Ein Proxmox-Server läuft in aller Regel durch. Damit ist er ein guter Ort
für diese kleine tägliche Aufgabe: Der Container braucht nur wenige
Minuten Rechenzeit im Monat und an den meisten Tagen überträgt er gar
nichts, weil sich nichts geändert hat.

**Was der Container am Ende tut**, jeden Morgen um fünf:

1. (optional) den neuesten Stand der Texte per Git holen,
2. die Seite neu bauen,
3. nur die geänderten Dateien per FTPS auf den Webspace laden.

---

## 2. LXC-Container oder virtuelle Maschine?

Proxmox kann beides. Für diese Aufgabe ist ein **LXC-Container** die
richtige Wahl:

| | LXC-Container | Virtuelle Maschine |
| --- | --- | --- |
| Arbeitsspeicher | 512 MB reichen | mindestens 1–2 GB |
| Festplatte | 4 GB reichen | ab 10 GB |
| Startzeit | Sekunden | eine halbe Minute |
| Aufwand | gering | eigener Kernel, eigene Updates |

Eine VM bringt hier keinen Vorteil. Ein Container genügt, weil nur Python
und ein Zeitplaner darin laufen.

**Unprivilegiert oder privilegiert?** Nehmen Sie einen **unprivilegierten**
Container (Standardeinstellung). Er ist besser vom Server getrennt. Für
unsere Zwecke fehlt ihm nichts.

**Als Vorlage** eignet sich **Debian 12**. Es ist klein, stabil, und
Python 3 samt Git sind mit einem Befehl installiert.

> **Nicht auf dem Proxmox-Server selbst installieren.** Technisch ginge
> das, aber der Host sollte schlank bleiben: Jedes zusätzliche Paket dort
> kann bei einem Proxmox-Update Ärger machen. Ein Container ist außerdem
> in einer Minute gesichert oder wieder gelöscht.

---

## 3. Vorbereitung: Vorlage herunterladen

Eine „Vorlage“ (Template) ist ein fertiges Debian-Grundsystem.

**In der Weboberfläche:** links im Baum auf den Server klicken →
`local (Servername)` → **CT Templates** → **Templates** → in der Liste
`debian-12-standard` auswählen → **Download**.

**Oder auf der Kommandozeile** (Weboberfläche → Server → **Shell**):

```bash
pveam update
pveam available --section system | grep debian-12
pveam download local debian-12-standard_12.7-1_amd64.tar.zst
```

Die Versionsnummer im Dateinamen ändert sich mit der Zeit – nehmen Sie
die, die `pveam available` anzeigt.

---

## 4. Container anlegen

Rechts oben in der Weboberfläche auf **Create CT**. Der Assistent führt
durch mehrere Reiter:

**General**

| Feld | Eintrag |
| --- | --- |
| Node | Ihr Server |
| CT ID | z. B. `120` (jede freie Nummer) |
| Hostname | `homepage-deploy` |
| Unprivileged container | **angehakt lassen** |
| Password | ein Passwort für den Benutzer `root` **im Container** – notieren! |

**Template**

| Feld | Eintrag |
| --- | --- |
| Storage | `local` |
| Template | die eben geladene `debian-12-standard…` |

**Disks**

| Feld | Eintrag |
| --- | --- |
| Disk size | `4` (GiB) – mehr braucht es nicht |

**CPU**

| Feld | Eintrag |
| --- | --- |
| Cores | `1` |

**Memory**

| Feld | Eintrag |
| --- | --- |
| Memory | `512` (MiB) |
| Swap | `512` |

**Network**

| Feld | Eintrag |
| --- | --- |
| Bridge | `vmbr0` |
| IPv4 | `DHCP` |

DHCP genügt: Der Container ruft nur nach außen, es muss ihn niemand
finden.

**DNS**: leer lassen, dann erbt er die Einstellungen des Servers.

Zum Schluss **Confirm** → Haken bei *Start after created* → **Finish**.

Wer lieber tippt, kann dasselbe in einer Zeile haben:

```bash
pct create 120 local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst \
  --hostname homepage-deploy \
  --unprivileged 1 \
  --cores 1 --memory 512 --swap 512 \
  --rootfs local-lvm:4 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1 \
  --start 1
```

---

## 5. Erster Start und Anmeldung

Links im Baum den Container `120 (homepage-deploy)` auswählen →
**Console**. Es erscheint eine Anmeldezeile:

```
homepage-deploy login: root
Password: (das in Schritt 4 vergebene Passwort)
```

Vom Proxmox-Server aus geht es auch ohne Passwort:

```bash
pct enter 120
```

Alles Folgende passiert **im Container**, nicht auf dem Proxmox-Server.
Sie erkennen das am Eingabeprompt `root@homepage-deploy:~#`.

---

## 6. Grundeinrichtung im Container

**System aktualisieren und Pakete installieren:**

```bash
apt update && apt upgrade -y
apt install -y python3-venv git ca-certificates cron
```

Was wofür ist:

| Paket | Wofür |
| --- | --- |
| `python3-venv` | Python samt der Möglichkeit, eine eigene Umgebung anzulegen |
| `git` | nur für die Variante „Texte per Git pflegen“ |
| `ca-certificates` | Wurzelzertifikate – ohne sie schlägt die verschlüsselte FTPS-Verbindung fehl |
| `cron` | der Zeitplaner. In manchen Debian-Vorlagen fehlt er |

**Zeitzone setzen – das ist wichtig.** Ob eine Bekanntmachung noch
angezeigt wird, entscheidet das Datum des Systems. Steht die Zeitzone auf
UTC, verschwindet ein Hinweis unter Umständen einen Tag zu früh:

```bash
ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime
echo "Europe/Berlin" > /etc/timezone
date        # zur Kontrolle: zeigt jetzt die richtige Uhrzeit
```

> Der Befehl `timedatectl set-timezone` funktioniert in unprivilegierten
> Containern oft nicht – deshalb der Weg über die Verknüpfung.

**Arbeitsverzeichnis anlegen:**

```bash
mkdir -p /opt/praxis
cd /opt/praxis
```

> Wir arbeiten hier als `root`. Das ist vertretbar, weil der Container
> unprivilegiert ist und nur diese eine Aufgabe hat. Wer lieber einen
> eigenen Benutzer möchte: `adduser praxis`, danach alle Pfade unter
> `/home/praxis` anlegen und den cron-Eintrag mit diesem Benutzer
> vornehmen.

---

## 7. Projekt in den Container bringen

Drei Wege. **Weg A ist der bequemste**, wenn die Texte ohnehin in einem
Git-Repository liegen.

### Weg A – per Git klonen (empfohlen)

```bash
cd /opt/praxis
git clone <Adresse des Repositorys> site
```

Bei einem privaten Repository fragt Git nach Zugangsdaten. Für GitHub
nehmen Sie dafür ein **Personal Access Token** statt des Passworts, oder
Sie hinterlegen einen SSH-Schlüssel.

Damit der tägliche Lauf später nicht nach Zugangsdaten fragt, einmalig:

```bash
git config --global credential.helper store
cd /opt/praxis/site && git pull        # einmal Zugangsdaten eingeben
```

Das Token liegt danach im Klartext in `/root/.git-credentials`. In diesem
abgeschotteten Container ist das vertretbar; ein Token nur mit Leserecht
zu erzeugen, ist trotzdem die bessere Wahl.

### Weg B – vom Proxmox-Server hineinkopieren

Liegt das Projekt schon auf dem Proxmox-Server, geht es ohne Git. Auf dem
**Server** (nicht im Container):

```bash
tar czf /tmp/site.tar.gz -C /pfad/zum/projekt .
pct push 120 /tmp/site.tar.gz /tmp/site.tar.gz
pct exec 120 -- sh -c 'mkdir -p /opt/praxis/site && tar xzf /tmp/site.tar.gz -C /opt/praxis/site'
```

### Weg C – per SFTP vom eigenen Rechner

Dafür muss ein SSH-Zugang in den Container möglich sein:

```bash
apt install -y openssh-server
systemctl enable --now ssh
ip addr show eth0 | grep inet        # zeigt die IP des Containers
```

Danach mit einem Programm wie FileZilla oder WinSCP auf diese IP
verbinden und den Projektordner nach `/opt/praxis/site` hochladen.

---

## 8. Python-Umgebung anlegen

Eine „virtuelle Umgebung“ ist ein Ordner mit einer eigenen
Python-Installation. So bleiben die Zusatzpakete beim Projekt und
vermischen sich nicht mit dem System.

```bash
cd /opt/praxis
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install jinja2
```

**Nur Jinja2 wird gebraucht.** Flask aus `requirements.txt` ist allein für
die lokale Vorschau da und hat im Container nichts zu suchen.

Kontrolle:

```bash
/opt/praxis/venv/bin/python -c "import jinja2; print(jinja2.__version__)"
```

Es sollte eine Versionsnummer erscheinen, etwa `3.1.4`.

---

## 9. Zugangsdaten hinterlegen

**Konfiguration anlegen:**

```bash
cd /opt/praxis/site
cp deploy.ini.example deploy.ini
nano deploy.ini
```

Auszufüllen sind `[site] url` sowie unter `[ftp]` die Werte `host`, `user`
und `remote_dir` – sie stehen im Kundenmenü des Hosters. Speichern in
`nano`: `Strg+O`, `Enter`, `Strg+X`.

**Passwortdatei anlegen.** Das Passwort gehört weder in `deploy.ini` noch
in den cron-Eintrag:

```bash
printf '%s' 'IhrFtpPasswort' > /opt/praxis/ftp-passwort
chmod 600 /opt/praxis/ftp-passwort
```

`printf` statt `echo` – sonst landet ein Zeilenumbruch im Passwort, und
der Server lehnt die Anmeldung ab.

**Skript anpassen:**

```bash
nano /opt/praxis/site/tools/deploy-taeglich.sh
```

Die vier Zeilen oben ändern in:

```sh
PROJEKT="${PROJEKT:-/opt/praxis/site}"
PYTHON="${PYTHON:-/opt/praxis/venv/bin/python}"
PASSWORTDATEI="${PASSWORTDATEI:-/opt/praxis/ftp-passwort}"
MIT_GIT="${MIT_GIT:-1}"      # 0, wenn Sie Weg B oder C genommen haben
```

Und ausführbar machen:

```bash
chmod +x /opt/praxis/site/tools/deploy-taeglich.sh
```

---

## 10. Von Hand ausprobieren

Erst ein Lauf, der nichts überträgt:

```bash
/opt/praxis/site/tools/deploy-taeglich.sh --dry-run
```

Erwartet: die Seite wird gebaut, danach eine Liste „würde laden …“.

Wenn das passt, der echte Lauf:

```bash
/opt/praxis/site/tools/deploy-taeglich.sh
```

Beim ersten Mal werden alle Dateien übertragen. **Rufen Sie den Befehl
gleich ein zweites Mal auf** – dann muss dort stehen:

```
27 Dateien in dist/, davon 0 geändert
Nichts zu tun – der Server hat bereits diesen Stand.
```

Erscheint das, funktioniert alles: Bauen, Hochladen und das Erkennen von
Änderungen.

---

## 11. Täglich laufen lassen

### Einfach: cron

```bash
crontab -e
```

Beim ersten Aufruf fragt Debian nach einem Editor – wählen Sie `nano`.
Ganz unten anfügen:

```
0 5 * * * /opt/praxis/site/tools/deploy-taeglich.sh >> /var/log/praxis-deploy.log 2>&1
```

Das bedeutet: **täglich um 05:00 Uhr**. Die fünf Felder sind Minute,
Stunde, Tag, Monat, Wochentag. Der hintere Teil schreibt Ausgabe *und*
Fehlermeldungen in eine Protokolldatei – ohne ihn verschwindet beides
ungesehen.

Kontrolle, dass der Eintrag steht:

```bash
crontab -l
```

### Etwas besser: systemd-Timer

Ein Timer hat zwei Vorteile: Die Ausgabe landet automatisch im
Systemprotokoll, und mit `Persistent=true` wird ein verpasster Lauf
nachgeholt, wenn der Container einmal aus war.

```bash
nano /etc/systemd/system/praxis-deploy.service
```

```ini
[Unit]
Description=Homepage bauen und hochladen
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/opt/praxis/site/tools/deploy-taeglich.sh
```

```bash
nano /etc/systemd/system/praxis-deploy.timer
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
systemctl daemon-reload
systemctl enable --now praxis-deploy.timer
systemctl list-timers praxis-deploy.timer
```

Einmal sofort auslösen, ohne bis morgen zu warten:

```bash
systemctl start praxis-deploy.service
journalctl -u praxis-deploy.service -n 30
```

Nehmen Sie **entweder** cron **oder** den Timer, nicht beides.

---

## 12. Ergebnis prüfen und Fehler finden

**Bei cron:**

```bash
tail -n 40 /var/log/praxis-deploy.log
```

**Beim Timer:**

```bash
journalctl -u praxis-deploy.service --since "2 days ago"
```

An einem Tag ohne Änderung sollte dort nur stehen:

```
Nichts zu tun – der Server hat bereits diesen Stand.
```

**Möchten Sie im Fehlerfall eine E-Mail?** cron verschickt nur Mails,
wenn ein Mailprogramm installiert ist. Am wenigsten Aufwand macht
`msmtp`:

```bash
apt install -y msmtp msmtp-mta
nano /etc/msmtprc
```

```
defaults
tls on
auth on

account standard
host smtp.ihr-anbieter.de
port 587
from praxis-nas@ihre-domain.de
user praxis-nas@ihre-domain.de
password IhrMailPasswort

account default : standard
```

```bash
chmod 600 /etc/msmtprc
```

Danach im crontab oben zusätzlich `MAILTO="ihre@adresse.de"` eintragen –
und die Umleitung in die Protokolldatei entfernen, sonst gibt es nichts
zu verschicken. cron meldet sich dann nur, wenn das Skript etwas ausgibt
oder mit einem Fehler endet.

---

## 13. Sicherung einrichten

Der Container ist schnell wieder aufgesetzt, aber `deploy.ini`, die
Passwortdatei und – bei den Wegen B und C – die Texte stecken nur darin.
Proxmox sichert einen Container in einem Rutsch:

Container `120` auswählen → **Backup** → **Backup now**, Modus
*Snapshot*, Komprimierung *ZSTD*.

Regelmäßig geht es über **Datacenter → Backup → Add**: dort den Container
auswählen, Zeitplan z. B. wöchentlich, Aufbewahrung „letzte 4“.

Vor größeren Änderungen im Container lohnt außerdem ein Schnappschuss:
Container → **Snapshots** → **Take Snapshot**. Geht etwas schief, sind Sie
mit einem Klick wieder auf dem alten Stand.

---

## 14. Später: Inhalte ändern

**Mit Git (`MIT_GIT=1`):** Sie ändern die Texte wie gewohnt am eigenen
Rechner, `git commit`, `git push`. Der Container holt sich den Stand beim
nächsten Lauf. Soll es sofort online sein:

```bash
pct exec 120 -- /opt/praxis/site/tools/deploy-taeglich.sh
```

**Ohne Git:** Die JSON-Dateien liegen im Container unter
`/opt/praxis/site/translations/`. Bearbeiten lassen sie sich per SFTP
(Weg C in Schritt 7) oder direkt mit `nano`.

> Wichtig bei Git: Ändern Sie die Dateien **nicht** zusätzlich im
> Container. Sonst scheitert `git pull --ff-only`, und der tägliche Lauf
> bricht ab.

---

## 15. Häufige Stolpersteine

| Meldung oder Symptom | Ursache und Abhilfe |
| --- | --- |
| `deploy.ini fehlt` | Schritt 9 nachholen; die Datei muss neben `deploy.py` liegen |
| `Passwortdatei nicht lesbar` | Pfad im Skript stimmt nicht, oder die Datei gehört einem anderen Benutzer |
| `530 Login incorrect` | In der Passwortdatei steckt ein Zeilenumbruch. Mit `printf` neu schreiben, nicht mit `echo` |
| `certificate verify failed` | `apt install ca-certificates` vergessen |
| `Verzeichnis … nicht gefunden` | `remote_dir` in `deploy.ini` prüfen – es ist der Pfad, auf den die Domain zeigt |
| Von Hand klappt es, per cron nicht | cron kennt kaum Umgebungsvariablen. Im Skript alle Pfade vollständig ausschreiben, keine Abkürzung `~` |
| `crontab: command not found` | `apt install cron`, danach `systemctl enable --now cron` |
| Hinweis verschwindet einen Tag zu früh | Zeitzone im Container prüfen (Schritt 6) |
| Auf dem Server fehlt eine Datei | einmal `--all` anhängen: `… /deploy-taeglich.sh --all` |
| Passive FTP-Verbindung bleibt hängen | Firewall zwischen Container und Internet prüfen; notfalls `passive = no` in `deploy.ini` |

**Was der Container *nicht* tut:** Er stellt die Homepage nicht selbst ins
Netz. Ausgeliefert wird sie weiterhin vom Webspace des Hosters – der
Container baut sie nur und lädt sie dorthin.
