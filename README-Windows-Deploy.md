# Täglich veröffentlichen mit einem Windows-PC

Schritt-für-Schritt-Anleitung, um die Homepage von einem Windows-Rechner
aus einmal täglich neu bauen und auf den Webspace laden zu lassen.

Geschrieben für Leute ohne Vorkenntnisse: Jeder Befehl steht vollständig
da und lässt sich abtippen oder kopieren.

Die Grundlagen – warum überhaupt täglich, was alle Wege brauchen, wie die
Texte gepflegt werden – stehen in
**[README-Deploy.md](README-Deploy.md)**. Was `deploy.py` tut und wie
`deploy.ini` ausgefüllt wird, steht in der [README](README.md) unter
„Veröffentlichen bei Alfahosting“.

> **Ein Rechner, der aus ist, veröffentlicht nichts.** Auf einem
> Arbeitsplatz-PC ist das der wunde Punkt: Ist er um fünf Uhr morgens
> ausgeschaltet, fällt der Lauf aus. In Schritt 7 stellen wir deshalb ein,
> dass ein verpasster Start nachgeholt wird, sobald der Rechner wieder
> läuft. Wer ein NAS oder einen kleinen Server hat, ist damit besser
> bedient – siehe die anderen Anleitungen.

---

## Inhalt

1. [Python installieren](#1-python-installieren)
2. [Ordner und Umgebung anlegen](#2-ordner-und-umgebung-anlegen)
3. [Projekt ablegen](#3-projekt-ablegen)
4. [Zugangsdaten hinterlegen](#4-zugangsdaten-hinterlegen)
5. [Skript anpassen](#5-skript-anpassen)
6. [Von Hand ausprobieren](#6-von-hand-ausprobieren)
7. [Aufgabenplanung einrichten](#7-aufgabenplanung-einrichten)
8. [Zeitzone prüfen](#8-zeitzone-prüfen)
9. [Später: Inhalte ändern](#9-später-inhalte-ändern)
10. [Sicherung](#10-sicherung)
11. [Häufige Stolpersteine](#11-häufige-stolpersteine)

---

## 1. Python installieren

Von <https://www.python.org/downloads/> die aktuelle Version für Windows
herunterladen und starten.

> **Im ersten Fenster unbedingt „Add python.exe to PATH“ ankreuzen.**
> Ohne diesen Haken findet die Aufgabenplanung Python später nicht, und
> der tägliche Lauf scheitert wortlos.

Danach die **Eingabeaufforderung** öffnen (Windows-Taste drücken, `cmd`
tippen, Enter) und prüfen:

```cmd
py --version
```

Es sollte eine Versionsnummer erscheinen, etwa `Python 3.12.4`.

---

## 2. Ordner und Umgebung anlegen

Eine „virtuelle Umgebung“ ist ein Ordner mit einer eigenen
Python-Installation. So bleiben die Zusatzpakete beim Projekt und
vermischen sich nicht mit dem System.

In der Eingabeaufforderung:

```cmd
mkdir C:\Praxis
cd C:\Praxis
py -3 -m venv venv
venv\Scripts\pip install jinja2
```

**Nur Jinja2 wird gebraucht.** Flask aus `requirements.txt` ist allein für
die lokale Vorschau da.

Kontrolle:

```cmd
C:\Praxis\venv\Scripts\python -c "import jinja2; print(jinja2.__version__)"
```

Es sollte eine Versionsnummer erscheinen, etwa `3.1.4`.

---

## 3. Projekt ablegen

Das Projekt gehört nach `C:\Praxis\site`. Zwei Möglichkeiten:

### Kopieren

Entpacken oder kopieren Sie den Projektordner dorthin. Danach muss es
`C:\Praxis\site\deploy.py` geben.

### Per Git

Dafür [Git für Windows](https://git-scm.com/download/win) installieren
(alle Vorgaben im Installationsfenster können so bleiben). Dann:

```cmd
git clone <Adresse des Repositorys> C:\Praxis\site
```

Prüfen, ob es geklappt hat:

```cmd
dir C:\Praxis\site\deploy.py
```

---

## 4. Zugangsdaten hinterlegen

**Konfiguration anlegen.** Im Explorer nach `C:\Praxis\site` wechseln, die
Datei `deploy.ini.example` kopieren und die Kopie in `deploy.ini`
umbenennen. Dann mit dem Editor öffnen (Rechtsklick → *Öffnen mit* →
*Editor*).

Auszufüllen sind `[site] url` sowie unter `[ftp]` die Werte `host`, `user`
und `remote_dir` – sie stehen im Kundenmenü des Hosters.

> Windows blendet Dateiendungen oft aus. Falls aus `deploy.ini`
> versehentlich `deploy.ini.txt` wird: Im Explorer unter *Ansicht* die
> **Dateinamenerweiterungen** einblenden und den Namen korrigieren.

**Passwortdatei anlegen.** Eine neue Textdatei `C:\Praxis\ftp-passwort.txt`
erstellen, die in der ersten Zeile **nur** das FTP-Passwort enthält.

> **Keine Leerzeichen am Zeilenende** – sie zählten zum Passwort, und der
> Server lehnte die Anmeldung ab. Ein Zeilenumbruch am Ende ist dagegen
> unproblematisch; das Skript liest nur die erste Zeile.

Zugriff einschränken: Rechtsklick auf die Datei → *Eigenschaften* →
*Sicherheit* → *Bearbeiten* → alle Gruppen außer Ihrem eigenen
Benutzerkonto entfernen.

---

## 5. Skript anpassen

Mitgeliefert ist `C:\Praxis\site\tools\deploy-taeglich.cmd`. Öffnen Sie
die Datei mit dem Editor (Rechtsklick → *Bearbeiten*). Oben stehen vier
Einstellungen:

```cmd
set "PROJEKT=C:\Praxis\site"
set "PYTHON=C:\Praxis\venv\Scripts\python.exe"
set "PASSWORTDATEI=C:\Praxis\ftp-passwort.txt"
set "MIT_GIT=0"
```

Bei den Pfaden aus dieser Anleitung passen sie bereits. Setzen Sie nur
`MIT_GIT=1`, wenn Sie in Schritt 3 Git genommen haben.

---

## 6. Von Hand ausprobieren

Erst ein Lauf, der nichts überträgt. In der Eingabeaufforderung:

```cmd
C:\Praxis\site\tools\deploy-taeglich.cmd --dry-run
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

> Ein Doppelklick auf die `.cmd`-Datei funktioniert auch – das Fenster
> schließt sich danach allerdings sofort wieder. Zum Lesen der Ausgabe
> also lieber über die Eingabeaufforderung aufrufen.

---

## 7. Aufgabenplanung einrichten

Windows-Taste drücken, `Aufgabenplanung` tippen, öffnen. Rechts auf
**Einfache Aufgabe erstellen**.

| Seite des Assistenten | Eintrag |
| --- | --- |
| Name | z. B. `Homepage veröffentlichen` |
| Trigger | **Täglich**, Startzeit z. B. 05:00 |
| Aktion | **Programm starten** |
| Programm/Skript | `C:\Praxis\site\tools\deploy-taeglich.cmd` |
| „Starten in (optional)“ | `C:\Praxis\site` |

Am Ende **„Beim Klicken auf ‚Fertig stellen‘ die Eigenschaften öffnen“**
ankreuzen. Im Eigenschaften-Fenster noch zwei Einstellungen:

**Reiter *Allgemein*:**

* **„Unabhängig von der Benutzeranmeldung ausführen“** – dann läuft die
  Aufgabe auch, wenn niemand angemeldet ist. Windows verlangt dafür beim
  Speichern Ihr Windows-Kennwort.

**Reiter *Bedingungen* und *Einstellungen*:**

* Unter *Bedingungen* den Haken bei **„Aufgabe nur starten, falls
  Computer im Netzbetrieb ist“** entfernen, wenn es ein Notebook ist –
  sonst passiert im Akkubetrieb nichts.
* Unter *Einstellungen* **„Aufgabe so schnell wie möglich nach einem
  verpassten Start ausführen“** ankreuzen. Das ist der wichtigste Haken
  auf einem Arbeitsplatz-PC: Er holt den Lauf nach, wenn der Rechner um
  fünf Uhr aus war.

**Sofort testen**, ohne bis morgen zu warten: die Aufgabe in der Liste
markieren und rechts auf **Ausführen** klicken. Das Ergebnis steht in der
Spalte *Letztes Ausführungsergebnis*; `0x0` bedeutet „ohne Fehler“.

---

## 8. Zeitzone prüfen

Ob eine Bekanntmachung noch angezeigt wird, entscheidet das Datum des
Rechners. Einstellungen → *Zeit und Sprache* → *Datum und Uhrzeit* → die
Zeitzone prüfen.

---

## 9. Später: Inhalte ändern

**Ohne Git:** Die JSON-Dateien liegen unter
`C:\Praxis\site\translations\`. Öffnen Sie `de.json` mit einem Editor
(gut geeignet: Notepad++ oder VS Code), ändern Sie den Text, speichern –
beim nächsten Lauf ist es online.

> Achten Sie darauf, die Datei als **UTF-8** zu speichern, sonst werden
> Umlaute zerlegt. Der Windows-Editor macht das seit Windows 10 von
> selbst.

**Mit Git (`MIT_GIT=1`):** Sie arbeiten wie gewohnt, `git commit`,
`git push`. Der Rechner holt sich den Stand beim nächsten Lauf. Soll es
sofort online sein, in der Aufgabenplanung auf **Ausführen**.

> Wichtig bei Git: Ändern Sie die Dateien **nicht** zusätzlich auf diesem
> Rechner, wenn er nur veröffentlichen soll. Sonst scheitert
> `git pull --ff-only`, und der tägliche Lauf bricht ab.

---

## 10. Sicherung

Zu sichern sind drei Dinge, die es nur auf diesem Rechner gibt:

| Was | Wo |
| --- | --- |
| Projekt und Texte | `C:\Praxis\site` |
| Zugangsdaten | `C:\Praxis\site\deploy.ini` |
| FTP-Passwort | `C:\Praxis\ftp-passwort.txt` |

Bei der Git-Variante stecken die Texte ohnehin im Repository; dann bleiben
nur die beiden Zugangsdateien. Nehmen Sie den Ordner `C:\Praxis` in Ihre
gewohnte Sicherung auf.

---

## 11. Häufige Stolpersteine

| Meldung oder Symptom | Ursache und Abhilfe |
| --- | --- |
| `'py' ist nicht als Befehl erkannt` | Bei der Installation fehlte der Haken „Add python.exe to PATH“. Python erneut ausführen → *Modify* → Haken setzen |
| `Der Befehl "git" ist nicht erkannt` | Git für Windows fehlt (Schritt 3), oder die Eingabeaufforderung wurde seither nicht neu geöffnet |
| `deploy.ini fehlt` | Die Datei heißt vermutlich `deploy.ini.txt` – Dateiendungen einblenden (Schritt 4) |
| `Passwortdatei nicht gefunden` | Pfad in `deploy-taeglich.cmd` prüfen |
| `530 Login incorrect` | Leerzeichen am Ende der Passwortzeile, oder die Datei ist nicht als reiner Text gespeichert |
| `Verzeichnis … nicht gefunden` | `remote_dir` in `deploy.ini` prüfen – es ist der Pfad, auf den die Domain zeigt |
| Aufgabe endet mit `0x1` | Über die Eingabeaufforderung aufrufen; dort steht die eigentliche Meldung |
| Aufgabe läuft nie | Rechner war aus. Haken „nach einem verpassten Start ausführen“ setzen (Schritt 7) |
| Umlaute in der Ausgabe zerlegt | nur eine Anzeigefrage der Eingabeaufforderung; die hochgeladene Seite ist davon nicht betroffen |
| Umlaute **auf der Seite** falsch | Die JSON-Datei wurde nicht als UTF-8 gespeichert (Schritt 9) |
| Hinweis verschwindet einen Tag zu früh | Zeitzone prüfen (Schritt 8) |
| Auf dem Server fehlt eine Datei | einmal `--all` anhängen |

**Was der Rechner *nicht* tut:** Er stellt die Homepage nicht selbst ins
Netz. Ausgeliefert wird sie weiterhin vom Webspace des Hosters – der PC
baut sie nur und lädt sie dorthin.
