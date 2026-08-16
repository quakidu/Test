# Die Homepage auf einem Android-Gerät ausprobieren

Schritt-für-Schritt-Anleitung, um die Seite auf einem Android-Telefon oder
-Tablet anzusehen, bevor sie ins Netz geht.

Geschrieben für Leute ohne Vorkenntnisse: Jeder Befehl steht vollständig
da und lässt sich abtippen oder kopieren.

Wie man Git auf Android einrichtet, steht in
**[README-Android-Git.md](README-Android-Git.md)**. Was `build.py` und
`deploy.py` tun, steht in der [README](README.md).

---

## Inhalt

1. [Warum überhaupt am Telefon prüfen](#1-warum-überhaupt-am-telefon-prüfen)
2. [Drei Wege zur Auswahl](#2-drei-wege-zur-auswahl)
3. [Weg A – vom PC aus ins WLAN](#3-weg-a--vom-pc-aus-ins-wlan)
4. [Weg B – alles auf dem Telefon mit Termux](#4-weg-b--alles-auf-dem-telefon-mit-termux)
5. [Weg C – Entwicklerwerkzeuge über USB](#5-weg-c--entwicklerwerkzeuge-über-usb)
6. [Was Sie sich ansehen sollten](#6-was-sie-sich-ansehen-sollten)
7. [Häufige Stolpersteine](#7-häufige-stolpersteine)

---

## 1. Warum überhaupt am Telefon prüfen

Die meisten Besucher einer Praxisseite kommen mit dem Telefon. Am
Bildschirm des Rechners lässt sich das nur zum Teil nachstellen: Der
schmale Browser zeigt zwar das Layout, aber nicht,

* wie groß die Schaltflächen sich unter dem Daumen anfühlen,
* ob sich die Diashow **wischen** lässt,
* was beim Tippen auf eine `mailto:`-Adresse passiert – auf dem Telefon
  ist fast immer ein Mailprogramm eingerichtet, auf dem Rechner oft nicht,
* ob die Adresse im Kontaktbereich die Karten-App öffnet,
* wie die Seite im dunklen Erscheinungsbild des Telefons wirkt.

---

## 2. Drei Wege zur Auswahl

| | Weg A – vom PC aus | Weg B – Termux | Weg C – über USB |
| --- | --- | --- | --- |
| Auf dem Telefon zu installieren | nichts | Termux | nichts |
| Gut für | den Alltag: schnell ansehen | unterwegs, ohne PC | Fehlersuche mit Entwicklerwerkzeugen |
| Voraussetzung | beide im selben WLAN | – | USB-Kabel, Chrome auf dem PC |

**Wenn Sie unsicher sind: Weg A.** Er braucht auf dem Telefon nichts als
den Browser.

---

## 3. Weg A – vom PC aus ins WLAN

Der Rechner baut die Seite und liefert sie aus; das Telefon ruft sie über
das heimische WLAN ab.

**Schritt 1 – Beide Geräte ins gleiche WLAN.** Das Telefon darf nicht über
Mobilfunk laufen; ein Gäste-WLAN trennt die Geräte oft ab.

**Schritt 2 – Auf dem Rechner die Vorschau starten.** Wichtig ist
`--host 0.0.0.0` – ohne diesen Zusatz hört der Server nur auf den
Rechner selbst, und das Telefon bekommt keine Verbindung:

```bash
python3 build.py --serve --host 0.0.0.0
```

Die Ausgabe nennt die Adresse gleich mit:

```
http://127.0.0.1:8000/  (Strg+C beendet den Server)
http://192.168.1.42:8000/  aus dem gleichen Netzwerk, etwa vom Telefon

Der Server ist damit im ganzen Netzwerk erreichbar – nur zum Ausprobieren gedacht.
```

**Schritt 3 – Am Telefon aufrufen.** Im Browser die zweite Adresse
eintippen, hier also `192.168.1.42:8000`. Das `http://` können Sie
weglassen.

> **Tipp:** Legen Sie die Adresse auf den Startbildschirm (Chrome-Menü →
> *Zum Startbildschirm hinzufügen*). Dann sind Sie beim nächsten Mal mit
> einem Tippen da.

**Schritt 4 – Nach jeder Änderung.** Der Server liefert den gebauten
Stand aus `dist/` aus. Ändern Sie einen Text, muss neu gebaut werden:
`Strg+C`, dann den Befehl aus Schritt 2 noch einmal. Am Telefon danach die
Seite neu laden.

> **Wenn das Telefon keine Verbindung bekommt**, blockiert meist die
> Firewall des Rechners den Port 8000. Unter Windows erscheint beim ersten
> Start eine Abfrage – dort *Privates Netzwerk* zulassen. Unter Linux
> hilft `sudo ufw allow 8000/tcp`, falls `ufw` läuft.

**Zum Schluss:** Der Server ist offen, solange er läuft. Beenden Sie ihn
mit `Strg+C`, wenn Sie fertig sind.

---

## 4. Weg B – alles auf dem Telefon mit Termux

**Termux** ist eine Linux-Umgebung für Android. Damit läuft der Build
komplett auf dem Telefon – ohne Rechner, auch unterwegs.

**Schritt 1 – Termux installieren.** Nehmen Sie die Fassung von
**F-Droid**, nicht die aus dem Play Store: Die dortige wird seit Jahren
nicht mehr gepflegt und lässt sich nicht aktualisieren.

1. <https://f-droid.org/> im Browser des Telefons öffnen,
   *Download F-Droid* antippen, die heruntergeladene Datei installieren.
   Android fragt dabei nach der Erlaubnis, Apps aus dieser Quelle zu
   installieren – das ist für diesen einen Vorgang nötig.
2. In F-Droid nach `Termux` suchen und installieren.

**Schritt 2 – Termux einrichten.** App öffnen, dann eintippen:

```bash
pkg update && pkg upgrade -y
pkg install -y python
```

Bei `pkg upgrade` fragt Termux gelegentlich, ob eine
Konfigurationsdatei ersetzt werden soll – die Vorgabe (`N`) ist richtig.

**Schritt 3 – Jinja2 nachinstallieren.** Mehr braucht der Build nicht;
Flask aus `requirements.txt` ist nur für die Vorschau am Rechner:

```bash
pip install jinja2
```

**Schritt 4 – Das Projekt auf das Telefon holen.** Am einfachsten per
Git – wie das eingerichtet wird, steht in
[README-Android-Git.md](README-Android-Git.md):

```bash
git clone <Adresse des Repositorys> praxis
cd praxis
```

Ohne Git: Das Projekt als ZIP auf das Telefon kopieren, dann

```bash
termux-setup-storage          # einmalig, fragt nach der Erlaubnis
cd ~
unzip ~/storage/downloads/praxis.zip -d praxis
cd praxis
```

**Schritt 5 – Bauen und ansehen.**

```bash
python build.py --serve
```

Dann im Browser des Telefons aufrufen:

```
http://localhost:8000
```

Termux muss dabei laufen. Wechseln Sie einfach mit der App-Umschaltung
zwischen Browser und Termux hin und her.

> **Damit Android Termux nicht abschaltet**, während Sie im Browser sind:
> In der Termux-Benachrichtigung auf **Acquire wakelock** tippen. Nach dem
> Ausprobieren wieder freigeben, sonst zieht es Akku.

**Schritt 6 – Beenden.** In Termux `Strg+C` (die Taste `Strg` liegt in der
Zusatzzeile über der Tastatur).

> **Was auf dem Telefon nicht geht:** `tools/make-og-image.py` und
> `tools/prepare-logo.py` brauchen einen Browser bzw. erzeugen Bilder –
> das erste läuft unter Termux nicht. Für die Vorschau ist beides nicht
> nötig; die Bilder liegen ja schon im Projekt.

---

## 5. Weg C – Entwicklerwerkzeuge über USB

Damit sehen Sie am großen Bildschirm, was der Browser des Telefons
tatsächlich anzeigt – samt Fehlermeldungen und Netzwerkverkehr. Nützlich,
wenn etwas nur auf dem Telefon nicht stimmt.

**Schritt 1 – Entwickleroptionen freischalten.** Einstellungen → *Über das
Telefon* → siebenmal auf **Build-Nummer** tippen. Danach erscheinen die
*Entwickleroptionen* in den Einstellungen.

**Schritt 2 – USB-Debugging einschalten.** Einstellungen →
*Entwickleroptionen* → **USB-Debugging** aktivieren.

**Schritt 3 – Telefon anstecken.** Am Telefon die Rückfrage
*USB-Debugging zulassen?* bestätigen.

**Schritt 4 – Am Rechner in Chrome** die Adresse `chrome://inspect`
öffnen. Unter *Remote Target* erscheint das Telefon mit den offenen
Tabs; **inspect** öffnet die gewohnten Entwicklerwerkzeuge.

> Praktisch dabei: Unter *Port forwarding* lässt sich `8000` auf
> `localhost:8000` des Rechners legen. Dann erreicht das Telefon die
> Vorschau **ohne** WLAN und ohne `--host 0.0.0.0` – einfach über das
> Kabel.

---

## 6. Was Sie sich ansehen sollten

Eine kurze Liste zum Durchgehen:

| Stelle | Worauf achten |
| --- | --- |
| Kopfbereich | Burger-Menü öffnet und schließt, alle sieben Punkte erreichbar |
| Themenwahl | im geöffneten Menü; hell und dunkel umschalten |
| Bekanntmachungen | Karten lesbar, Kurshinweis führt zu den Kursen |
| Kurse | „Platz anfragen“ öffnet das Mailprogramm mit fertigem Betreff |
| Diashow „Praxis“ | lässt sich **wischen**, Punkte springen mit |
| Kontakt | Telefonnummer wählt, E-Mail öffnet das Mailprogramm |
| Karte | erst nach dem Tippen auf „Karte laden“ erscheint Google Maps |
| Fußbereich | Impressum und Datenschutz erreichbar |
| Quer halten | Layout bleibt heil, nichts läuft seitlich heraus |
| Dunkles Erscheinungsbild | Systemeinstellung umschalten, Seite neu laden |

---

## 7. Häufige Stolpersteine

| Symptom | Ursache und Abhilfe |
| --- | --- |
| Telefon erreicht die Adresse nicht | `--host 0.0.0.0` vergessen, oder die Firewall des Rechners blockiert Port 8000 |
| „Verbindung abgelehnt“ trotz gleichem WLAN | Gäste-WLAN trennt Geräte voneinander – ins normale WLAN wechseln |
| Adresse hat sich geändert | Der Router vergibt beim nächsten Mal womöglich eine andere. Die Ausgabe von `--serve` nennt die aktuelle |
| Änderung am Text ist nicht zu sehen | Der Build läuft nicht automatisch: `Strg+C`, Befehl erneut aufrufen, am Telefon neu laden |
| Alte Fassung bleibt hartnäckig | Im Browser des Telefons den Cache leeren oder ein privates Fenster öffnen |
| `pkg: command not found` | Sie haben die Termux-Fassung aus dem Play Store – über F-Droid neu installieren |
| `pip install jinja2` scheitert | zuerst `pkg update && pkg upgrade` ausführen |
| Termux hört mitten im Test auf | Wakelock setzen (Schritt 5 in Weg B) |
| Karte lädt nicht | Das ist Absicht: Sie wird erst nach dem Tippen geladen. Ohne Internet bleibt der Platzhalter stehen |

**Was diese Vorschau nicht prüft:** Sie läuft über `http://` ohne
Verschlüsselung und unter einer IP-Adresse statt der echten Domain. Die
Weiterleitung auf HTTPS, die Fehlerseite und die Sicherheits-Header
stecken in der `.htaccess` und greifen erst auf dem Webspace.
