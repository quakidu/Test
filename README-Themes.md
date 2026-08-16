# Ein neues Thema hinzufügen

Schritt-für-Schritt-Anleitung, um der Homepage eine weitere Darstellung
zu geben – etwa ein warmes, augenschonendes Thema neben Hell und Dunkel.

Geschrieben für Leute ohne Vorkenntnisse: Jeder Handgriff steht
vollständig da, jeder Codeblock lässt sich kopieren. Die Anleitung
beschreibt den Weg an einem durchgehenden Beispiel namens **„sepia“**.

---

## Inhalt

1. [Was ein Thema ist](#1-was-ein-thema-ist)
2. [Wie die Wahl funktioniert](#2-wie-die-wahl-funktioniert)
3. [Überblick: fünf Handgriffe](#3-überblick-fünf-handgriffe)
4. [Schritt 1 – Farben aussuchen](#4-schritt-1--farben-aussuchen)
5. [Schritt 2 – Farbwerte eintragen](#5-schritt-2--farbwerte-eintragen)
6. [Schritt 3 – Themenblock anlegen](#6-schritt-3--themenblock-anlegen)
7. [Schritt 4 – Thema anmelden](#7-schritt-4--thema-anmelden)
8. [Schritt 5 – Symbol und Beschriftung](#8-schritt-5--symbol-und-beschriftung)
9. [Ausprobieren](#9-ausprobieren)
10. [Ein Thema wieder entfernen](#10-ein-thema-wieder-entfernen)
11. [Häufige Stolpersteine](#11-häufige-stolpersteine)

---

## 1. Was ein Thema ist

Im Stylesheet steht keine einzige Farbe direkt an einem Bauteil. Statt

```css
.notice { background: #FFFFFF; }
```

steht dort

```css
.notice { background: var(--bg-elevated); }
```

`--bg-elevated` ist ein **Token** – ein benannter Platzhalter. Was dahinter
steckt, entscheidet das Thema. Ein neues Thema ist deshalb nichts weiter
als ein Satz neuer Werte für dieselben Token-Namen. Sie müssen kein
einziges Bauteil anfassen.

**Diese Token bestimmt ein Thema.** Die Liste ist vollständig – wer alle
setzt, hat nichts übersehen:

| Token | Wofür |
| --- | --- |
| `--bg` | Grundfläche der Seite |
| `--bg-elevated` | Karten, Kästen, das mobile Menü – liegt optisch „oben“ |
| `--bg-tinted` | leicht abgesetzte Abschnitte (Bekanntmachungen, Therapeut, Stimmen) |
| `--text` | Fließtext und Überschriften |
| `--text-muted` | Nebentexte, Beschriftungen, Bildunterschriften |
| `--border` | feine Trennlinien und Kartenränder |
| `--border-strong` | betonte Ränder, etwa beim Überfahren mit der Maus |
| `--accent` | Leitfarbe: Schaltflächen, aktive Zustände, die Kante der Hinweise |
| `--accent-soft` | hellere Nebenform der Leitfarbe, etwa die Linie vor „Kurse“ |
| `--accent-ink` | Leitfarbe als **Schriftfarbe** auf hellem Grund |
| `--on-accent` | Schriftfarbe **auf** der Leitfarbe, etwa in der Schaltfläche |
| `--shadow-md`, `--shadow-lg` | Schlagschatten; im Dunkeln tiefer als im Hellen |
| `--glow-1`, `--glow-2`, `--glow-3` | die drei weichen Farbschleier im Kopfbereich |
| `--accent-fade` | das auslaufende Ende des farbigen Titels im Kopfbereich |
| `--selection-bg`, `--selection-text` | markierter Text |
| `--logo-hell`, `--logo-dunkel` | welche der beiden Logofassungen sichtbar ist – siehe unten |

> **Zum Logo:** Es liegt in zwei Fassungen im Quelltext – eine mit
> dunklem, eine mit hellem Schriftzug. Sichtbar ist immer nur eine.
> Vorgabe ist die dunkle Schrift, passend für helle Themen. **Ein Thema
> auf dunklem Grund muss umschalten:**
>
> ```css
>   --logo-hell:   none;
>   --logo-dunkel: block;
> ```
>
> Wer das vergisst, hat einen dunklen Schriftzug auf dunkler Fläche –
> gerade noch zu erahnen, aber nicht zu lesen.

Nicht jedes Thema muss alle setzen: Was fehlt, behält den Wert aus dem
hellen Grundsatz. Für ein dunkles Thema wäre das aber fatal – dunkle
Fläche mit dunkler Schrift. **Im Zweifel alle setzen.**

Mehr als diese Liste gibt es nicht. Kein Abschnitt der Seite hat eigene
Farben: Die Abschnitte wechseln zwischen `--bg` und `--bg-tinted`, die
Karten liegen alle auf `--bg-elevated`. Wer die Liste durchgeht, hat die
ganze Seite umgefärbt.

> **Eine Fläche bleibt immer weiß:** der Kasten mit den Förderlogos
> (`--logo-plate`). Solche Logos sind für weißen Grund gemacht; auf
> farbigem Grund sähen sie nach Fehler aus. Das ist Absicht – nur wer
> einen sehr guten Grund hat, ändert diesen einen Wert.

---

## 2. Wie die Wahl funktioniert

Zwei Attribute am `<html>`-Element, und der Unterschied ist wichtig:

| Attribut | Steht an | Inhalt |
| --- | --- | --- |
| `data-theme-choice` | `<html>` | was **gewählt** wurde – auch `auto` |
| `data-theme` | `<html>` | was daraus **folgt** – immer ein konkretes Thema |
| `data-set-theme` | Knopf | welches Thema dieser Knopf setzt |

Steht die Wahl auf `auto`, schaut ein kleines Skript nach, ob das Gerät
hell oder dunkel eingestellt ist, und schreibt das Ergebnis nach
`data-theme`. Das Stylesheet muss `auto` deshalb nicht kennen – es
braucht nur einen Block je echtem Thema.

Das Skript steht **im Kopf der Seite**, also vor dem ersten gezeichneten
Bild. Sonst blitzte beim Laden kurz das falsche Thema auf.

Ohne JavaScript erscheint die Wahl gar nicht; dann gilt die Vorgabe des
Betriebssystems. Ein Knopf, der nichts bewirkt, wäre schlechter als
keiner.

---

## 3. Überblick: fünf Handgriffe

| Schritt | Datei |
| --- | --- |
| 1. Farben aussuchen | – |
| 2. Farbwerte eintragen | `static/css/style.css` |
| 3. Themenblock anlegen | `static/css/style.css` |
| 4. Thema anmelden | `build.py` **und** `app.py` |
| 5. Symbol und Beschriftung | `templates/partials/theme-icons.html`, `translations/de.json` |

Rechnen Sie mit einer halben Stunde – der längste Teil ist das Aussuchen
der Farben.

---

## 4. Schritt 1 – Farben aussuchen

Für ein stimmiges Thema genügen wenige Entscheidungen:

1. **Eine Grundfläche** (`--bg`) – die Farbe, die den größten Teil des
   Bildschirms füllt.
2. **Eine etwas hellere oder dunklere Fläche** (`--bg-elevated`) für
   Karten. Sie muss sich von der Grundfläche unterscheiden lassen, ohne
   zu springen.
3. **Eine Schriftfarbe** (`--text`) mit **kräftigem Kontrast** zur
   Grundfläche.
4. **Eine Leitfarbe** (`--accent`) für Schaltflächen.

**Prüfen Sie den Kontrast**, bevor Sie weitermachen. Text auf Fläche
sollte mindestens **4,5 : 1** erreichen, große Überschriften **3 : 1**.
Kostenlose Prüfer gibt es im Netz unter dem Stichwort *contrast checker*;
in den Entwicklerwerkzeugen von Chrome steht der Wert beim Anklicken
einer Textfarbe direkt dabei.

Für das Beispiel „sepia“:

| Rolle | Wert |
| --- | --- |
| Grundfläche | `#F4ECDF` |
| Karten | `#FDF8EF` |
| abgesetzte Abschnitte | `#EDE2D0` |
| Schrift | `#3A2E1F` |
| Nebentext | `#6B5B45` |
| Leitfarbe | `#8A5A2B` |
| Schrift auf der Leitfarbe | `#FDF8EF` |

---

## 5. Schritt 2 – Farbwerte eintragen

Öffnen Sie `static/css/style.css`. Suchen Sie den Abschnitt
**„1b. Themen“** – etwa in Zeile 72.

Dort steht ein `:root`-Block mit den Werten des dunklen Themas
(`--dunkel-*`). **Direkt darunter, noch im selben Block**, ergänzen Sie
Ihre Werte:

```css
  --dunkel-shadow-lg: 0 28px 60px -30px rgba(0, 0, 0, 0.9);

  /* Werte des Themas „sepia“ */
  --sepia-bg:            #F4ECDF;
  --sepia-bg-elevated:   #FDF8EF;
  --sepia-bg-tinted:     #EDE2D0;
  --sepia-text:          #3A2E1F;
  --sepia-text-muted:    #6B5B45;
  --sepia-border:        rgba(58, 46, 31, 0.16);
  --sepia-border-strong: rgba(58, 46, 31, 0.30);
  --sepia-accent:        #8A5A2B;
  --sepia-accent-soft:   #B08243;
  --sepia-accent-ink:    #6A4420;
  --sepia-on-accent:     #FDF8EF;
}
```

**Warum getrennt?** Die Farbwerte stehen so genau einmal. Der Block im
nächsten Schritt bildet sie nur ab – wer später eine Farbe ändert, muss
sie an einer einzigen Stelle ändern.

**Zu den Rändern:** `rgba(58, 46, 31, 0.16)` ist die Schriftfarbe mit
16 % Deckkraft. Nehmen Sie die drei Zahlen Ihrer Schriftfarbe; ein
Umrechner von `#3A2E1F` nach `58, 46, 31` findet sich im Netz unter *hex
to rgb*.

---

## 6. Schritt 3 – Themenblock anlegen

Etwas weiter unten in derselben Datei steht der Block
`:root[data-theme="dark"]`. **Direkt davor** kommt Ihr Block:

```css
/* Thema „sepia“ */
:root[data-theme="sepia"] {
  color-scheme: light;
  --bg:            var(--sepia-bg);
  --bg-elevated:   var(--sepia-bg-elevated);
  --bg-tinted:     var(--sepia-bg-tinted);
  --text:          var(--sepia-text);
  --text-muted:    var(--sepia-text-muted);
  --border:        var(--sepia-border);
  --border-strong: var(--sepia-border-strong);
  --accent:        var(--sepia-accent);
  --accent-soft:   var(--sepia-accent-soft);
  --accent-ink:    var(--sepia-accent-ink);
  --on-accent:     var(--sepia-on-accent);
  --glow-1:        #E3CFAE;
  --glow-2:        #EFE0C8;
  --glow-3:        #D8BE95;
  --accent-fade:   #C99A5E;
  --selection-bg:  #E3CFAE;
  --selection-text: var(--sepia-text);
}
```

Zwei Zeilen verdienen eine Erklärung:

* **`color-scheme`** sagt dem Browser, ob es sich um ein helles oder
  dunkles Thema handelt. Danach richtet er Bildlaufleisten und
  Formularfelder. `light` oder `dark` – etwas anderes gibt es nicht.
* **`--shadow-md` und `--shadow-lg`** fehlen hier mit Absicht: Die
  Schatten des hellen Grundsatzes passen zu einem hellen Thema. Für ein
  **dunkles** Thema müssten Sie sie mitsetzen, sonst sind die Schatten
  kaum zu sehen. Ein dunkles Thema braucht außerdem `--logo-hell` und
  `--logo-dunkel` aus Abschnitt 1.

---

## 7. Schritt 4 – Thema anmelden

Damit der Knopf erscheint, muss das Thema in **beiden** Python-Dateien
stehen: `build.py` erzeugt die veröffentlichte Seite, `app.py` die
Vorschau am eigenen Rechner.

Suchen Sie in beiden Dateien nach `THEMES` und ergänzen Sie eine Zeile:

```python
THEMES = {
    "auto": {"icon": "auto"},
    "light": {"icon": "sun"},
    "dark": {"icon": "moon"},
    "sepia": {"icon": "sepia"},
}
```

Der Schlüssel links – hier `sepia` – muss **genau** dem Namen in
`[data-theme="sepia"]` entsprechen. `icon` verweist auf das Symbol aus
dem nächsten Schritt.

> Die Reihenfolge im Block ist die Reihenfolge der Knöpfe. `auto` steht
> vorn, weil es die Vorgabe ist.

---

## 8. Schritt 5 – Symbol und Beschriftung

**Symbol.** Öffnen Sie `templates/partials/theme-icons.html`. Dort steht
je Symbol ein Zweig. Ergänzen Sie einen weiteren **vor** `{%- else -%}`:

```jinja
  {%- elif name == 'sepia' -%}
    <path d="M6 20c0-6 3-10 12-16-1 9-4 13-12 16z"/>
    <path d="M6 20c4-2 7-4 9-7"/>
```

Das ist ein Blatt, gezeichnet in einem Feld von 24 × 24 Einheiten. Wer
nicht selbst zeichnen möchte, findet unter dem Stichwort *feather icons*
oder *lucide icons* freie Strichzeichnungen zum Kopieren – achten Sie auf
`viewBox="0 0 24 24"` und darauf, nur die Zeilen zwischen `<svg>` und
`</svg>` zu übernehmen.

> **Wenn Sie den Zweig weglassen**, erscheint ein schlichter Kreis. Der
> Knopf funktioniert trotzdem – Sie können das Symbol also später
> nachliefern.

**Beschriftung.** In `translations/de.json` unter `theme.options` eine
Zeile ergänzen:

```json
"theme": {
  "label": "Darstellung",
  "options": {
    "auto": "Wie das Gerät",
    "light": "Hell",
    "dark": "Dunkel",
    "sepia": "Warm"
  }
}
```

Der Text erscheint als Kurzhinweis beim Überfahren und wird
Screenreadern vorgelesen. Gibt es weitere Sprachen, gehört die Zeile in
jede Sprachdatei; fehlt sie dort, greift der deutsche Text.

---

## 9. Ausprobieren

```bash
python3 build.py --serve
```

Dann <http://127.0.0.1:8000/> öffnen. Rechts oben steht nun ein vierter
Knopf.

**Diese Liste durchgehen** – die Stellen, an denen sich ein
unvollständiges Thema verrät:

| Stelle | Worauf achten |
| --- | --- |
| Schriftzug oben links | Gut lesbar auf der Grundfläche (`--logo-hell`, `--logo-dunkel`) |
| Kopfbereich | Die drei Farbschleier passen zum Thema, nicht mehr blau |
| Titel im Kopfbereich | Der farbige Verlauf läuft im Thema aus (`--accent-fade`) |
| Kurse | Die Karten heben sich von der Fläche ab (`--bg-elevated` gegen `--bg-tinted`) |
| Nächster Kurs | Die erste Karte ist als hervorgehoben zu erkennen |
| Kurse / Angebot | Der Haarstrich zwischen beiden Abschnitten ist zu sehen (`--border`) |
| Bekanntmachungen | Die farbige Kante links ist zu erkennen |
| Schaltflächen | Schrift auf der Leitfarbe ist gut lesbar (`--on-accent`) |
| Karte im Kontakt | Der Platzhalter vor dem Klick passt sich an |
| Text markieren | Markierung und Schrift bleiben lesbar |
| Fußbereich | Trennlinien sind sichtbar, aber nicht aufdringlich |
| Förderlogos | Kasten bleibt weiß – das ist Absicht |

Danach **auf dem Telefon ansehen**: siehe
[README-Android-Test.md](README-Android-Test.md).

Zum Schluss die Wahl umschalten und die Seite neu laden – das Thema muss
erhalten bleiben.

---

## 10. Ein Thema wieder entfernen

Die Zeile aus `THEMES` in `build.py` und `app.py` löschen – das genügt.
Der Knopf verschwindet, CSS-Block und Beschriftung stören nicht weiter.

Hat jemand das Thema bereits gewählt, liegt die Wahl noch in seinem
Browser. Das Skript prüft aber, ob es die Wahl überhaupt gibt, und fällt
sonst auf `auto` zurück – niemand bleibt auf einem Thema sitzen, das es
nicht mehr gibt.

---

## 11. Häufige Stolpersteine

| Symptom | Ursache und Abhilfe |
| --- | --- |
| Der Knopf erscheint nicht | `THEMES` nur in einer der beiden Dateien ergänzt, oder die Seite wurde nicht neu gebaut |
| Knopf da, aber nichts passiert | Der Schlüssel in `THEMES` und der Name in `[data-theme="…"]` stimmen nicht überein – Schreibweise prüfen |
| Nur ein Teil der Seite färbt sich um | Ein Token fehlt im Block. Die vollständige Liste steht in Abschnitt 1 |
| Der Kopfbereich bleibt blau | `--glow-1` bis `--glow-3` fehlen |
| Der Schriftzug oben links ist kaum zu sehen | Dunkles Thema ohne `--logo-hell: none` und `--logo-dunkel: block` |
| Karten und Fläche sehen gleich aus | `--bg-elevated` und `--bg-tinted` liegen zu dicht beieinander – einen der beiden deutlicher absetzen |
| Kurse und Angebot verschwimmen ineinander | `--border` ist zu schwach: den Haarstrich zwischen den beiden abgesetzten Abschnitten sichtbarer machen |
| Schrift auf Schaltflächen unlesbar | `--on-accent` fehlt oder passt nicht zur Leitfarbe |
| Bildlaufleisten passen nicht | `color-scheme` fehlt oder steht auf dem falschen Wert |
| Beim Laden blitzt kurz ein anderes Thema auf | Das darf nicht passieren – prüfen Sie, ob das Skript im `<head>` von `templates/base.html` noch vollständig ist |
| Statt eines Symbols ein Kreis | Der Zweig in `theme-icons.html` fehlt oder der Name unter `icon` stimmt nicht |
| Statt der Beschriftung steht `theme.options.sepia` | Der Eintrag in `translations/de.json` fehlt |
| Im dunklen Thema sind Schatten unsichtbar | `--shadow-md` und `--shadow-lg` mitsetzen |

**Wenn gar nichts passt:** Alle Änderungen dieser Anleitung betreffen
fünf Stellen. `git diff` zeigt sie auf einen Blick, `git checkout -- .`
verwirft sie wieder.
