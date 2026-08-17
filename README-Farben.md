# Die Farben der Seite ändern

Schritt-für-Schritt-Anleitung, um die Homepage umzufärben – etwa weil die
Praxis ein neues Logo bekommt oder das Blau einem Grün weichen soll.

Geschrieben für Leute ohne Vorkenntnisse: Jeder Handgriff steht
vollständig da, jeder Codeblock lässt sich kopieren.

> **Nicht zu verwechseln mit [README-Themes.md](README-Themes.md).**
> Dort geht es darum, eine **zusätzliche** Darstellung anzulegen, die
> die Besucher rechts oben auswählen können. Hier geht es um die Farben
> der Seite selbst – hell und dunkel gleichermaßen.

---

## Inhalt

1. [Wie die Farben zusammenhängen](#1-wie-die-farben-zusammenhängen)
2. [Überblick: sechs Handgriffe](#2-überblick-sechs-handgriffe)
3. [Schritt 1 – Die Leitfarbe festlegen](#3-schritt-1--die-leitfarbe-festlegen)
4. [Schritt 2 – Die neun Stufen ableiten](#4-schritt-2--die-neun-stufen-ableiten)
5. [Schritt 3 – Die Werte eintragen](#5-schritt-3--die-werte-eintragen)
6. [Schritt 4 – Die Schriftfarben](#6-schritt-4--die-schriftfarben)
7. [Schritt 5 – Das dunkle Thema](#7-schritt-5--das-dunkle-thema)
8. [Schritt 6 – Die Stellen außerhalb des Stylesheets](#8-schritt-6--die-stellen-außerhalb-des-stylesheets)
9. [Kontrast prüfen](#9-kontrast-prüfen)
10. [Ansehen und abnehmen](#10-ansehen-und-abnehmen)
11. [Zurücknehmen](#11-zurücknehmen)
12. [Häufige Stolpersteine](#12-häufige-stolpersteine)

---

## 1. Wie die Farben zusammenhängen

Im Stylesheet steht keine einzige Farbe direkt an einem Bauteil. Statt

```css
.btn { background: #314F6F; }
```

steht dort

```css
.btn { background: var(--accent); }
```

Dazwischen liegen **zwei Ebenen**, und das ist der Kern der Sache:

```
   Palette              Rolle                  Bauteil
   ────────────         ─────────────          ─────────────
   --blue-600     →     --accent         →     Schaltflächen,
   (#314F6F)            („die Leitfarbe")      aktive Zustände,
                                               Linien, Zahlen …
```

* Die **Palette** (`--blue-50` bis `--blue-800`, `--ink-*`) sind die
  reinen Farbwerte. Sie sagen nichts darüber, wofür sie gebraucht werden.
* Die **Rollen** (`--accent`, `--text`, `--bg` …) sagen, welche Farbe
  wofür zuständig ist.

**Sie ändern nur die Palette.** Die Rollen bleiben, wie sie sind – und
damit auch alle Bauteile. Ein einziger Block mit fünfzehn Zeilen bestimmt
das Aussehen der ganzen Seite.

> **Warum die Zwischenebene?** Das Stylesheet greift an über
> dreihundert Stellen auf einen Token zu. Stünden dort feste Farbwerte,
> müssten Sie jede einzelne davon suchen und beurteilen. So sind es
> fünfzehn Zeilen an einer Stelle.

---

## 2. Überblick: sechs Handgriffe

| Schritt | Datei | Dauer |
| --- | --- | --- |
| 1. Leitfarbe festlegen | – | 10 Min. |
| 2. Neun Stufen ableiten | – | 10 Min. |
| 3. Werte eintragen | `static/css/style.css` | 5 Min. |
| 4. Schriftfarben | `static/css/style.css` | 5 Min. |
| 5. Dunkles Thema | `static/css/style.css` | 10 Min. |
| 6. Stellen außerhalb | `templates/base.html`, `tools/make-og-image.py`, `static/img/` | 15 Min. |

Rechnen Sie mit einer Stunde. Der längste Teil ist Schritt 1.

---

## 3. Schritt 1 – Die Leitfarbe festlegen

Die Leitfarbe ist der Ton, der auf Schaltflächen, Linien und
Hervorhebungen erscheint. Zurzeit ist es `#314F6F` – ein gedecktes Blau,
das aus der Unterzeile des Logos stammt.

**Nehmen Sie die Farbe aus Ihrem Logo.** Das ist keine Vorschrift,
sondern der kürzeste Weg zu einem stimmigen Bild: Wenn Logo und Seite
denselben Ton tragen, wirkt beides wie aus einem Guss.

**So lesen Sie eine Farbe aus dem Logo ab:**

1. `static/img/logo.png` doppelklicken – es öffnet sich die
   Bildvorschau des Betriebssystems.
2. Unter Windows das Programm **Paint** verwenden: Datei öffnen, dann
   die Pipette (🖉) anklicken und auf die gewünschte Stelle klicken.
   Danach *Farben bearbeiten* – dort stehen die Werte.
3. Unter macOS die **Digitale Farbmesser**-App (in
   *Programme → Dienstprogramme*).
4. Ohne Zusatzprogramm geht es im Browser: das Bild öffnen und in den
   Entwicklerwerkzeugen die Pipette benutzen (Taste **F12**).

Sie brauchen den Wert in der Schreibweise `#RRGGBB`, also sechs Zeichen
nach dem Doppelkreuz.

**Worauf zu achten ist:** Die Leitfarbe muss **dunkel genug** sein, damit
weiße Schrift darauf lesbar bleibt – sie trägt die Schaltflächen. Ein
sattes Mittelblau, Waldgrün, Weinrot oder Anthrazit funktioniert. Ein
helles Gelb oder Türkis nicht.

Für diese Anleitung nehmen wir als Beispiel ein **gedecktes Grün**:
`#2F6B4F`.

---

## 4. Schritt 2 – Die neun Stufen ableiten

Die Seite braucht nicht eine Farbe, sondern eine Reihe: sehr helle Töne
für Flächen, mittlere für Ränder, dunkle für Schrift. Zurzeit sind es
neun Stufen von `--blue-50` (fast weiß) bis `--blue-800` (fast schwarz).

**Der einfachste Weg** ist ein kostenloser Farbtongenerator im Netz.
Suchen Sie nach *color shades generator* oder *tailwind palette
generator*, geben Sie Ihre Leitfarbe ein und lassen Sie sich die Stufen
50 bis 900 ausgeben. Übernehmen Sie daraus die neun, die Sie brauchen.

**Von Hand geht es auch.** Die Stufen unterscheiden sich vor allem in der
Helligkeit. Ein Umrechner nach *HSL* (Suchbegriff *hex to hsl*) zeigt
Ihnen drei Zahlen: Farbton, Sättigung, Helligkeit. Farbton lassen Sie
stehen, die Helligkeit setzen Sie der Reihe nach auf:

| Stufe | Helligkeit | Wofür |
| --- | --- | --- |
| `50` | 96 % | ganz leicht getönte Flächen |
| `100` | 91 % | – |
| `200` | 82 % | helle Schrift auf dunklem Grund |
| `300` | 70 % | Ränder, Nebenformen |
| `400` | 56 % | Leitfarbe im dunklen Thema |
| `500` | 43 % | – |
| `600` | **Ihr Wert** | die Leitfarbe |
| `700` | 24 % | Leitfarbe als Schriftfarbe |
| `800` | 17 % | dunkelste Stufe |

Die Sättigung dürfen Sie bei den hellen Stufen etwas zurücknehmen, sonst
wirken sie grell.

Für unser Grün ergäbe das etwa:

```
50  #F1F7F3    300 #93BFA8    600 #2F6B4F
100 #DFEDE5    400 #63A183    700 #255540
200 #C0DACC    500 #3F8664    800 #1A3C2D
```

---

## 5. Schritt 3 – Die Werte eintragen

Öffnen Sie `static/css/style.css`. Ganz oben, im Abschnitt
**„1. Design-Tokens"**, steht der Block:

```css
  --blue-50:  #F2F5F9;
  --blue-100: #E0E8F1;
  --blue-200: #C3D2E2;
  --blue-300: #9BB2CB;
  --blue-400: #6E8EB0;
  --blue-500: #4A6C91;
  --blue-600: #314F6F;
  --blue-700: #263F59;
  --blue-800: #1B2D40;
```

Ersetzen Sie **nur die Werte rechts**, nicht die Namen links:

```css
  --blue-50:  #F1F7F3;
  --blue-100: #DFEDE5;
  --blue-200: #C0DACC;
  --blue-300: #93BFA8;
  --blue-400: #63A183;
  --blue-500: #3F8664;
  --blue-600: #2F6B4F;
  --blue-700: #255540;
  --blue-800: #1A3C2D;
```

> **Die Namen bleiben „blue", obwohl es Grün ist?** Ja – und das ist
> Absicht. Die Namen stehen an fünfundzwanzig weiteren Stellen im
> Stylesheet; sie umzubenennen bringt nichts als Gelegenheit für
> Tippfehler. Wen es stört, der ersetzt `--blue-` überall durch
> `--marke-`; das Suchen und Ersetzen des Editors erledigt das in einem
> Zug. Nötig ist es nicht.

Speichern und einmal ansehen (Abschnitt 10). Der größte Teil der Seite
trägt jetzt schon die neue Farbe.

---

## 6. Schritt 4 – Die Schriftfarben

Direkt darunter stehen die Grautöne für Schrift und Flächen:

```css
  --neutral-50:  #FAFBFC;   /* Grundfläche der Seite */
  --neutral-100: #F2F4F7;

  --ink-900: #191E28;       /* Fließtext und Überschriften */
  --ink-700: #2E3644;
  --ink-500: #566173;       /* Nebentexte */
  --ink-300: #8A94A5;
```

**Diese dürfen Sie stehen lassen.** Neutrale Grautöne passen zu jeder
Leitfarbe, und die Kontraste sind geprüft.

**Wenn Sie mögen**, geben Sie ihnen einen Hauch Ihrer Farbe – das wirkt
wärmer. Nehmen Sie dazu die Grautöne und verschieben Sie den Farbton
leicht in Richtung Ihrer Leitfarbe, bei sehr geringer Sättigung (unter
10 %). Prüfen Sie danach unbedingt den Kontrast (Abschnitt 9).

Eine Zeile weiter unten steht außerdem:

```css
  --bg-tinted:     var(--blue-50);
```

Das ist die abgesetzte Fläche, auf der jeder zweite Abschnitt liegt. Sie
zieht Ihre neue Farbe automatisch mit – ändern müssen Sie hier nichts.

---

## 7. Schritt 5 – Das dunkle Thema

Etwas weiter unten, im Abschnitt **„1b. Themen"**, stehen die Werte des
dunklen Themas:

```css
  --dunkel-bg:            #0E131A;
  --dunkel-bg-elevated:   #151C25;
  --dunkel-bg-tinted:     #121821;
  --dunkel-text:          #E7ECF3;
  --dunkel-text-muted:    #A0AABA;
  --dunkel-border:        rgba(199, 215, 235, 0.14);
  --dunkel-border-strong: rgba(199, 215, 235, 0.26);
  --dunkel-on-accent:     #0D121A;
```

Auch diese dürfen bleiben – es sind fast neutrale Töne mit einem leichten
Stich ins Blaue. Wollen Sie den Stich anpassen, gehen Sie genauso vor wie
im vorigen Schritt.

**Die Leitfarbe im Dunkeln zieht von selbst mit.** Der Block darunter
greift auf dieselbe Palette zurück:

```css
:root[data-theme="dark"] {
  --accent:        var(--blue-400);   /* heller als im Hellen */
  --accent-soft:   var(--blue-300);
  --accent-ink:    var(--blue-200);
  …
}
```

Auf dunklem Grund braucht es einen **helleren** Ton als auf hellem –
deshalb `--blue-400` statt `--blue-600`. Da Sie beide Stufen ersetzt
haben, stimmt das weiterhin.

---

## 8. Schritt 6 – Die Stellen außerhalb des Stylesheets

Drei Farbangaben liegen außerhalb von `style.css`, weil ein Bild und die
Browserleiste keine Design-Tokens lesen können. Ohne sie bleibt an drei
Stellen das alte Blau stehen. Eine vierte Stelle ist absichtlich fest –
auch sie steht unten, damit Sie nicht danach suchen.

### a) Das Logo

Der Schriftzug steckt als Bild in `static/img/logo.png`. Tauschen Sie die
Datei aus (PNG mit durchsichtigem Hintergrund) und rufen Sie danach
**einmal** auf:

```bash
python3 tools/prepare-logo.py
```

Das Skript leitet daraus die aufgehellte Fassung für das dunkle Thema und
das quadratische Signet für das Lesezeichen-Symbol ab. Es braucht keine
Zusatzpakete.

### b) Die Leiste des Browsers auf dem Telefon

In `templates/base.html`, gleich am Anfang:

```html
<meta name="theme-color" content="#FAFBFC">
```

Das ist die Grundfläche des hellen Themas. Haben Sie `--neutral-50`
geändert, tragen Sie denselben Wert hier ein.

> Sobald JavaScript läuft, setzt `main.js` die Farbe des gewählten Themas
> nach. Dieser Wert gilt für den Moment davor – und für Besucher ohne
> JavaScript.

### c) Das Vorschaubild für geteilte Links

Teilt jemand die Adresse in einem Messenger, erscheint eine Vorschaukarte.
Ein Bild kann keine Design-Tokens lesen – seine Farben stehen deshalb
noch einmal in `tools/make-og-image.py`, oben unter den Einstellungen:

```python
FARBE_SCHRIFT = "#191E28"  # entspricht --ink-900
FARBE_LEIT    = "#314F6F"  # entspricht --blue-600, die Leitfarbe
FARBE_NEBEN   = "#47536A"  # Nebentext

FARBE_FLAECHE_HELL  = "#FFFFFF"
FARBE_FLAECHE_MITTE = "#F3F6F9"  # in der Nähe von --blue-50
FARBE_FLAECHE_TIEF  = "#E5EBF1"  # in der Nähe von --blue-100
FARBE_SCHLEIER      = "rgba(60, 98, 136, .42)"
```

Die oberen drei sind Schrift und Leitfarbe, die unteren vier die Fläche
des Bildes: ein Verlauf von hell nach etwas dunkler, darüber ein
Schleier in der Leitfarbe.

> **`FARBE_SCHLEIER` sieht anders aus als die übrigen.** Sie muss
> durchscheinen, deshalb die Schreibweise `rgba(rot, grün, blau,
> Deckkraft)` statt `#RRGGBB`. Die ersten drei Zahlen sind Ihre
> Leitfarbe – ein Umrechner im Netz (*hex to rgb*) nennt sie Ihnen. Die
> letzte Zahl, `.42`, ist die Deckkraft und bleibt stehen.

Tragen Sie dort Ihre Werte ein und erzeugen Sie das Bild neu:

```bash
python3 tools/make-og-image.py
```

Gebraucht wird dafür Chromium oder Chrome.

### d) Die Förderlogos

Der Kasten mit den Förderlogos bleibt **weiß** – in jedem Thema und in
jeder Farbe. Das ist Absicht: Fremde Logos sind für weißen Grund gemacht
und sähen auf farbigem Grund nach Fehler aus. Hier ist nichts zu tun.

---

## 9. Kontrast prüfen

Farben, die auf dem Bildschirm des Gestalters gut aussehen, sind auf
einem billigen Notebook bei Sonnenlicht manchmal nicht mehr zu lesen.
Deshalb gibt es Mindestwerte:

| Was | Mindestkontrast |
| --- | --- |
| Fließtext auf der Fläche | **4,5 : 1** |
| Große Überschriften | **3 : 1** |
| Schrift auf der Leitfarbe | **4,5 : 1** |

**So prüfen Sie:** Suchen Sie im Netz nach *contrast checker*, geben Sie
zwei Farbwerte ein und lesen Sie das Verhältnis ab. Oder – ohne fremde
Seite – in Chrome: **F12**, ein Textelement anklicken, im Feld `color`
auf das Farbquadrat klicken. Der Wert steht direkt dabei, mit Häkchen
oder Kreuz.

**Diese Paare sollten Sie prüfen:**

1. `--ink-900` auf `--neutral-50` (Fließtext, hell)
2. `--ink-500` auf `--neutral-50` (Nebentext, hell)
3. `#FFFFFF` auf `--blue-600` (Schrift auf der Schaltfläche)
4. `--dunkel-text` auf `--dunkel-bg` (Fließtext, dunkel)
5. `--blue-400` auf `--dunkel-bg` (Leitfarbe im Dunkeln)

Die mitgelieferten Farben liegen alle über 4,5 : 1.

---

## 10. Ansehen und abnehmen

```bash
python3 build.py --serve
```

Dann <http://127.0.0.1:8000/> öffnen.

**Diese Liste durchgehen** – die Stellen, an denen eine vergessene Farbe
auffällt:

| Stelle | Worauf achten |
| --- | --- |
| Kopfbereich | Die weichen Farbschleier hinter der Überschrift |
| Schriftzug oben links | Passt das Logo zur neuen Fläche? |
| Schaltflächen | Schrift darauf gut lesbar |
| Abschnitte | Der Wechsel heller/abgesetzter Flächen ist zu erkennen |
| Kurse | Die Karte des nächsten Kurses hebt sich ab |
| Ablauf | Die Punkte auf der Linie treffen die Fläche |
| Bekanntmachungen | Die farbige Kante links |
| Text markieren | Markierung und Schrift bleiben lesbar |
| Dunkles Thema | Rechts oben auf ☾ schalten und alles noch einmal |

Danach **auf dem Telefon ansehen**: siehe
[README-Android-Test.md](README-Android-Test.md).

Zum Schluss das Vorschaubild ansehen –
`static/img/og-bild.png` einfach doppelklicken.

---

## 11. Zurücknehmen

Alle Änderungen dieser Anleitung betreffen wenige Dateien. Sind sie noch
nicht eingecheckt, zeigt

```bash
git diff
```

sie auf einen Blick, und

```bash
git checkout -- .
```

verwirft sie wieder. Das Logo und das Vorschaubild sind dann ebenfalls
zurückgesetzt.

---

## 12. Häufige Stolpersteine

| Symptom | Ursache und Abhilfe |
| --- | --- |
| Gar nichts ändert sich | Die Seite wurde nicht neu gebaut, oder der Browser zeigt die alte Fassung – mit **Strg + F5** neu laden |
| Nur ein Teil der Seite färbt sich um | Eine der neun Zeilen wurde übersehen. Alle `--blue-*` von 50 bis 800 durchgehen |
| Die Schaltflächen sind kaum zu lesen | `--blue-600` ist zu hell für weiße Schrift. Eine dunklere Leitfarbe wählen |
| Im dunklen Thema wirkt alles blass | `--blue-400` ist zu blass. Im Dunkeln darf die Leitfarbe kräftiger sein |
| Die helle Fläche sticht ins Auge | `--blue-50` hat zu viel Sättigung. Sie darf kaum farbig sein |
| Der Schriftzug oben links passt nicht mehr | Das Logo ist noch das alte – Schritt 6a |
| Die Leiste auf dem Telefon bleibt alt | `theme-color` in `templates/base.html` – Schritt 6b |
| Geteilte Links zeigen die alte Farbe | `tools/make-og-image.py` und Bild neu erzeugen – Schritt 6c. Messenger merken sich die Vorschau oft tagelang |
| Der Kasten mit den Förderlogos bleibt weiß | Das ist Absicht – Schritt 6d |
| Nach dem Umfärben fehlt der Abschnittswechsel | `--neutral-50` und `--blue-50` liegen zu dicht beieinander. Sie sollen sich leicht unterscheiden |

**Wenn gar nichts passt:** `git checkout -- .` setzt alles zurück, und
Sie fangen mit einer anderen Leitfarbe neu an.
