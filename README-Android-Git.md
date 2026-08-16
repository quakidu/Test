# Git auf einem Android-Gerät einrichten

Schritt-für-Schritt-Anleitung, um Git auf einem Android-Telefon oder
-Tablet zu installieren und mit dem Repository der Homepage zu verbinden.
Danach können Sie unterwegs Texte ändern, die Änderung sichern und
hochladen.

Geschrieben für Leute ohne Vorkenntnisse: Jeder Befehl steht vollständig
da und lässt sich abtippen oder kopieren.

Wie Sie die Seite auf dem Telefon ansehen, steht in
**[README-Android-Test.md](README-Android-Test.md)**.

---

## Inhalt

1. [Was Git hier tut](#1-was-git-hier-tut)
2. [Termux installieren](#2-termux-installieren)
3. [Git installieren und einrichten](#3-git-installieren-und-einrichten)
4. [Anmeldung: Token oder SSH-Schlüssel](#4-anmeldung-token-oder-ssh-schlüssel)
5. [Das Repository holen](#5-das-repository-holen)
6. [Der tägliche Ablauf](#6-der-tägliche-ablauf)
7. [Texte auf dem Telefon bearbeiten](#7-texte-auf-dem-telefon-bearbeiten)
8. [Wo die Dateien liegen sollten](#8-wo-die-dateien-liegen-sollten)
9. [Häufige Stolpersteine](#9-häufige-stolpersteine)

---

## 1. Was Git hier tut

Git verwaltet die Textdateien der Homepage. Es merkt sich jede Änderung
mit Datum und Begründung, und es gleicht den Stand zwischen Ihren Geräten
ab.

Für die Praxis heißt das: Sie ändern am Telefon eine Kurszeit, sichern
die Änderung (`commit`) und laden sie hoch (`push`). Der Rechner oder das
NAS holt sie sich beim nächsten Lauf (`pull`) und veröffentlicht die
Seite.

> **Git veröffentlicht nichts.** Es bringt Ihre Änderung nur ins
> Repository. Auf den Webspace kommt sie erst durch `deploy.py` – siehe
> [README-Deploy.md](README-Deploy.md).

---

## 2. Termux installieren

Android bringt keine Kommandozeile mit. **Termux** liefert eine nach.

Nehmen Sie die Fassung von **F-Droid**, nicht die aus dem Play Store: Die
dortige wird seit Jahren nicht mehr gepflegt, und Paketinstallationen
schlagen dort fehl.

1. <https://f-droid.org/> im Browser des Telefons öffnen und
   *Download F-Droid* antippen.
2. Die heruntergeladene Datei öffnen. Android fragt nach der Erlaubnis,
   Apps aus dieser Quelle zu installieren – für diesen Vorgang zulassen.
3. F-Droid öffnen, nach `Termux` suchen, installieren.

Beim ersten Start dauert es einen Moment, bis die Eingabezeile erscheint.

> **Die Zusatzzeile über der Tastatur** enthält `Strg`, `Alt`, Pfeiltasten
> und `Tab`. `Strg+C` bricht einen laufenden Befehl ab, `Tab` vervollständigt
> Datei- und Befehlsnamen – das spart auf einer Telefontastatur viel.

---

## 3. Git installieren und einrichten

**Pakete installieren:**

```bash
pkg update && pkg upgrade -y
pkg install -y git openssh
```

| Paket | Wofür |
| --- | --- |
| `git` | die Versionsverwaltung selbst |
| `openssh` | nur nötig, wenn Sie sich mit einem SSH-Schlüssel anmelden |

**Name und E-Mail hinterlegen.** Beides steht später in jeder Änderung,
damit nachvollziehbar bleibt, wer was geändert hat:

```bash
git config --global user.name "Ihr Name"
git config --global user.email "ihre@adresse.de"
```

**Standardzweig festlegen**, sonst warnt Git bei jedem neuen Projekt:

```bash
git config --global init.defaultBranch main
```

Kontrolle:

```bash
git --version
git config --global --list
```

---

## 4. Anmeldung: Token oder SSH-Schlüssel

Zum Hochladen muss sich Git bei GitHub (oder GitLab) ausweisen. Ein
gewöhnliches Passwort reicht dafür nicht mehr.

| | Token | SSH-Schlüssel |
| --- | --- | --- |
| Einrichtung | schneller | ein paar Schritte mehr |
| Läuft ab | ja, je nach Wahl | nein |
| Liegt auf dem Telefon | im Klartext | als Datei, auf Wunsch mit Passwort |

**Für ein Telefon empfehle ich den SSH-Schlüssel.** Ein Telefon geht
leichter verloren als ein Rechner; einen Schlüssel können Sie einzeln
zurückziehen, ohne andere Geräte zu stören.

### Variante 1 – SSH-Schlüssel

**Schlüssel erzeugen:**

```bash
ssh-keygen -t ed25519 -C "Telefon"
```

Dreimal `Enter` drücken (Speicherort übernehmen, kein Passwort – oder
eines vergeben, dann fragt Git bei jedem Hochladen danach).

**Öffentlichen Teil anzeigen:**

```bash
cat ~/.ssh/id_ed25519.pub
```

Es erscheint eine lange Zeile, die mit `ssh-ed25519` beginnt. Halten Sie
den Finger darauf, um sie zu markieren und zu kopieren.

**Bei GitHub eintragen:** github.com im Browser öffnen → Profilbild →
*Settings* → *SSH and GPG keys* → **New SSH key** → Titel z. B.
`Telefon`, die kopierte Zeile einfügen → *Add SSH key*.

**Prüfen:**

```bash
ssh -T git@github.com
```

Beim ersten Mal fragt SSH, ob der Rechner bekannt ist – mit `yes`
antworten. Erwartet wird dann etwa:

```
Hi IhrName! You've successfully authenticated, but GitHub does not provide shell access.
```

Diese Meldung ist der Erfolg, keine Fehlermeldung.

### Variante 2 – Personal Access Token

**Token erzeugen:** github.com → Profilbild → *Settings* →
*Developer settings* → *Personal access tokens* → *Tokens (classic)* →
**Generate new token**. Als Berechtigung genügt `repo`. Laufzeit wählen,
erzeugen, den angezeigten Wert **sofort kopieren** – er erscheint kein
zweites Mal.

**In Termux hinterlegen**, damit er nicht bei jedem Mal neu getippt werden
muss:

```bash
git config --global credential.helper store
```

Beim ersten `git push` fragt Git nach Benutzername und Passwort. Als
Passwort geben Sie den **Token** ein, nicht Ihr GitHub-Passwort.

> Der Token liegt danach im Klartext in `~/.git-credentials`. Auf einem
> Telefon ist das der Grund, warum ich den SSH-Schlüssel bevorzuge.

---

## 5. Das Repository holen

**Mit SSH-Schlüssel:**

```bash
cd ~
git clone git@github.com:IhrName/IhrRepository.git praxis
cd praxis
```

**Mit Token:**

```bash
cd ~
git clone https://github.com/IhrName/IhrRepository.git praxis
cd praxis
```

Prüfen, ob es geklappt hat:

```bash
ls
git status
```

`ls` sollte unter anderem `build.py` und `translations` zeigen,
`git status` „nothing to commit, working tree clean“.

---

## 6. Der tägliche Ablauf

Immer dieselben vier Schritte:

```bash
cd ~/praxis

git pull                       # 1. neuesten Stand holen
nano translations/de.json      # 2. ändern (siehe Abschnitt 7)
git add -A                     # 3. Änderungen vormerken
git commit -m "Kurstermin im Herbst angepasst"
git push                       # 4. hochladen
```

**Zu `git commit -m`:** In die Anführungszeichen kommt eine kurze
Beschreibung dessen, was Sie geändert haben. Sie steht später in der
Liste der Änderungen – „Sommerpause eingetragen“ hilft in einem halben
Jahr weiter als „Update“.

**Womit was geprüft wird:**

| Befehl | Zeigt |
| --- | --- |
| `git status` | was geändert, aber noch nicht gesichert ist |
| `git diff` | die Änderungen Zeile für Zeile (`q` beendet die Anzeige) |
| `git log --oneline -5` | die letzten fünf Änderungen |

> **`git pull` zuerst**, jedes Mal. Sonst laufen der Stand am Telefon und
> der am Rechner auseinander, und beim Hochladen gibt es Konflikte.

---

## 7. Texte auf dem Telefon bearbeiten

Die Texte stehen in `translations/de.json`. Zwei Wege:

### Im Terminal mit nano

```bash
nano translations/de.json
```

| Taste | Wirkung |
| --- | --- |
| Pfeiltasten | bewegen den Cursor |
| `Strg+W` | suchen |
| `Strg+O`, dann `Enter` | speichern |
| `Strg+X` | beenden |

`Strg` liegt in der Zusatzzeile über der Tastatur.

### Mit einer Editor-App

Bequemer auf einem großen Display. Dafür muss der Ordner für andere Apps
sichtbar sein:

```bash
termux-setup-storage      # einmalig, Android fragt nach der Erlaubnis
```

Danach liegt der gemeinsame Speicher unter `~/storage/shared`. Kopieren
Sie die Datei zum Bearbeiten hin und zurück:

```bash
cp translations/de.json ~/storage/shared/Download/
# … in einer Editor-App bearbeiten und speichern …
cp ~/storage/shared/Download/de.json translations/
```

> **Achten Sie auf UTF-8** und darauf, dass die Datei gültiges JSON
> bleibt: Anführungszeichen, Kommas und Klammern müssen stimmen. Prüfen
> lässt sich das sofort:
>
> ```bash
> python -c "import json;json.load(open('translations/de.json'));print('JSON in Ordnung')"
> ```
>
> (Dafür muss `pkg install python` gelaufen sein – siehe
> [README-Android-Test.md](README-Android-Test.md).)

---

## 8. Wo die Dateien liegen sollten

**Im Termux-Heimatverzeichnis** (`~/praxis`), nicht im gemeinsamen
Speicher (`~/storage/shared`).

Der Grund: Auf dem gemeinsamen Speicher verwaltet Android die
Zugriffsrechte selbst. Git kann dort keine Dateirechte setzen und keine
symbolischen Verknüpfungen anlegen – ein `git clone` schlägt fehl oder
das Repository verhält sich merkwürdig.

Umgekehrt heißt das: Andere Apps sehen `~/praxis` nicht. Zum Bearbeiten
mit einer Editor-App den Umweg über `~/storage/shared/Download` nehmen,
wie in Abschnitt 7 beschrieben.

---

## 9. Häufige Stolpersteine

| Meldung oder Symptom | Ursache und Abhilfe |
| --- | --- |
| `pkg: command not found` | Termux stammt aus dem Play Store – über F-Droid neu installieren |
| `Unable to locate package git` | zuerst `pkg update` ausführen |
| `Permission denied (publickey)` | Der öffentliche Schlüssel ist nicht bei GitHub eingetragen (Abschnitt 4) |
| `Support for password authentication was removed` | Sie haben Ihr GitHub-Passwort statt eines Tokens verwendet |
| `Author identity unknown` | `git config --global user.name` und `user.email` fehlen (Abschnitt 3) |
| `Updates were rejected` | Auf dem Server liegt ein neuerer Stand: erst `git pull`, dann erneut `git push` |
| `error: cannot lock ref` oder seltsame Rechte-Fehler | Das Repository liegt im gemeinsamen Speicher – nach `~` verschieben (Abschnitt 8) |
| `fatal: not a git repository` | Sie sind im falschen Ordner: `cd ~/praxis` |
| Termux vergisst alles nach dem Neustart | Das darf nicht passieren – Termux speichert dauerhaft. Prüfen Sie, ob Android die App „optimiert“ und im Hintergrund löscht (Einstellungen → Akku) |
| Konflikt nach gleichzeitiger Änderung | `git status` zeigt die betroffene Datei. Sie mit `nano` öffnen, die Markierungen `<<<<<<<`, `=======`, `>>>>>>>` samt der ungewollten Fassung entfernen, dann `git add` und `git commit` |

**Wenn gar nichts mehr geht:** Der einfachste Ausweg ist, den Ordner zu
löschen und neu zu klonen. Alles, was gesichert und hochgeladen war,
liegt im Repository:

```bash
cd ~
rm -rf praxis
git clone git@github.com:IhrName/IhrRepository.git praxis
```

Vorher mit `git status` prüfen, ob noch ungesicherte Änderungen darin
stecken.
