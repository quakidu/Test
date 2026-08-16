# Täglich veröffentlichen: Grundlagen

Die Homepage lässt sich von einem Rechner aus einmal täglich neu bauen und
auf den Webspace laden. Diese Datei erklärt, warum das sinnvoll ist, was
dafür überall gebraucht wird und wie die Texte danach gepflegt werden.

**Die Einrichtung selbst steht je Gerät in einer eigenen Anleitung –
Schritt für Schritt und ohne Vorkenntnisse:**

| Anleitung | Für wen |
| --- | --- |
| **[README-Synology-Deploy.md](README-Synology-Deploy.md)** | ein Synology-NAS, wahlweise mit Python oder mit Docker |
| **[README-Windows-Deploy.md](README-Windows-Deploy.md)** | ein Windows-PC, über die Aufgabenplanung |
| **[README-Linux-Deploy.md](README-Linux-Deploy.md)** | ein Linux-PC, über cron oder einen systemd-Timer |
| **[README-Proxmox-Deploy.md](README-Proxmox-Deploy.md)** | ein Server mit Proxmox, in einem eigenen LXC-Container |
| **[README-Unraid-Deploy.md](README-Unraid-Deploy.md)** | ein NAS mit Unraid, über Docker und „User Scripts“ |

Was `deploy.py` überhaupt tut und wie `deploy.ini` ausgefüllt wird, steht
in der [README](README.md) unter „Veröffentlichen bei Alfahosting“.

---

## Inhalt

1. [Warum das sinnvoll ist](#warum-das-sinnvoll-ist)
2. [Zwei Entscheidungen vorab](#zwei-entscheidungen-vorab)
3. [Was alle Wege brauchen](#was-alle-wege-brauchen)
4. [Inhalte pflegen: Ordner oder Git](#inhalte-pflegen-ordner-oder-git)
5. [Wenn etwas nicht klappt](#wenn-etwas-nicht-klappt)

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

---

## Zwei Entscheidungen vorab

**Erstens: Wo soll es laufen?**

| Ort | Passt, wenn … | Anleitung |
| --- | --- | --- |
| **NAS** | das Gerät ohnehin durchläuft – dann klappt der tägliche Lauf zuverlässig | [Synology](README-Synology-Deploy.md) · [Unraid](README-Unraid-Deploy.md) |
| **Server** | ein Proxmox-Host vorhanden ist | [Proxmox](README-Proxmox-Deploy.md) |
| **Desktop-PC** | kein NAS da ist. Achtung: Ist der Rechner um 5 Uhr aus, fällt der Lauf aus – beide Anleitungen zeigen, wie er nachgeholt wird | [Windows](README-Windows-Deploy.md) · [Linux](README-Linux-Deploy.md) |

**Zweitens: Wie kommen die Texte auf diesen Rechner?**

| Variante | Vorgehen |
| --- | --- |
| **Freigegebener Ordner** | Das Projekt liegt einmal auf dem Gerät. Sie öffnen die JSON-Dateien über die Netzwerkfreigabe und ändern sie dort. Kein Git nötig |
| **Git** | Sie arbeiten wie bisher am PC, `git push`, und das Gerät holt sich vor jedem Lauf den neuen Stand |

Für eine Person, die die Texte selbst pflegt, reicht der **freigegebene
Ordner**. **Git** lohnt sich, sobald mehrere Leute etwas ändern oder Sie
alte Stände zurückholen möchten. Beides funktioniert mit jeder der
Anleitungen – der Unterschied ist eine Zeile im Skript.

---

## Was alle Wege brauchen

1. Das Projekt (dieser Ordner) auf dem Rechner, der veröffentlicht.
2. **Python 3** mit **Jinja2**. Flask aus `requirements.txt` wird *nicht*
   gebraucht – das ist nur für die lokale Vorschau.
3. Eine ausgefüllte `deploy.ini` (siehe [README](README.md), Abschnitt „Einmalig einrichten“).
4. Eine Datei, die nur das FTP-Passwort enthält.
5. Einen Zeitplaner. Welcher, hängt vom Gerät ab: Aufgabenplaner
   (Synology), User Scripts (Unraid), cron oder systemd-Timer (Linux,
   Proxmox), Aufgabenplanung (Windows).

---

## Inhalte pflegen: Ordner oder Git

**Freigegebener Ordner:** Sie öffnen `translations/de.json` über die
Netzwerkfreigabe (bzw. direkt am PC), ändern den Text, speichern. Beim
nächsten Lauf ist es online. `MIT_GIT=0` lassen.

**Git:** Sie arbeiten wie gewohnt lokal, dann `git push`. Auf dem
veröffentlichenden Rechner `MIT_GIT=1` setzen – das Skript holt vor jedem
Lauf den neuen Stand. Wichtig: Auf diesem Rechner dürfen die Dateien
**nicht** von Hand geändert werden, sonst scheitert `git pull --ff-only`.

`deploy.ini`, die Passwortdatei, `.deploy-state.json` und
`.build-state.json` sind in `.gitignore` eingetragen und gehen nie ins
Repository.

---

## Wenn etwas nicht klappt

Diese Tabelle nennt die Fälle, die auf jedem Gerät vorkommen. Die
gerätespezifischen Meldungen stehen jeweils am Ende der einzelnen
Anleitung.

| Meldung                                   | Ursache und Abhilfe                         |
| ----------------------------------------- | ------------------------------------------- |
| `deploy.ini fehlt`                        | Schritt „Zugangsdaten“ nachholen            |
| `Passwortdatei nicht lesbar`              | Pfad im Skript stimmt nicht, oder die Rechte lassen den Aufgaben-Benutzer nicht lesen |
| `Verzeichnis … nicht gefunden`            | `remote_dir` in `deploy.ini` prüfen (Kundenmenü → Domains) |
| `530 Login incorrect`                     | Passwortdatei enthält einen Zeilenumbruch oder ein Leerzeichen zu viel |
| Läuft von Hand, aber nicht im Zeitplan    | fast immer relative Pfade oder ein anderer Benutzer – im Skript alles ausschreiben |
| Seite ändert sich nicht                   | `--all` erzwingt einmal die vollständige Übertragung |

**Zeitzone prüfen.** Das Ausblenden vergleicht mit dem Datum des Geräts.
Steht die Zeitzone falsch, verschwindet ein Hinweis einen Tag zu früh oder
zu spät. Wo sie eingestellt wird, steht in der jeweiligen Anleitung.

**`--delete` ist bewusst nicht gesetzt.** Mit dem Schalter räumt jeder Lauf
auf dem Server auf – dann darf im Zielverzeichnis nichts liegen, was nicht
aus `dist/` stammt. Wenn dort ausschließlich diese Seite liegt, können Sie
ihn im Skript an `deploy.py` anhängen.
