# Eine weitere Sprache hinzufügen

Schritt-für-Schritt-Anleitung, um die Homepage in einer zweiten Sprache
anzubieten – etwa auf Englisch für Zugezogene und Reisende.

Geschrieben für Leute ohne Vorkenntnisse: Jeder Handgriff steht
vollständig da, jeder Codeblock lässt sich kopieren. Die Anleitung
beschreibt den Weg an einem durchgehenden Beispiel: **Englisch**.

---

## Inhalt

1. [Was schon vorbereitet ist](#1-was-schon-vorbereitet-ist)
2. [Überblick: vier Handgriffe](#2-überblick-vier-handgriffe)
3. [Schritt 1 – Die Textdatei anlegen](#3-schritt-1--die-textdatei-anlegen)
4. [Schritt 2 – Übersetzen](#4-schritt-2--übersetzen)
5. [Was nicht übersetzt wird](#5-was-nicht-übersetzt-wird)
6. [Datumsangaben und Monatsnamen](#6-datumsangaben-und-monatsnamen)
7. [Schritt 3 – Die Sprache anmelden](#7-schritt-3--die-sprache-anmelden)
8. [Schritt 4 – Rechtstexte und Vorschaubild](#8-schritt-4--rechtstexte-und-vorschaubild)
9. [Was der Build daraus macht](#9-was-der-build-daraus-macht)
10. [Kurse und Bekanntmachungen pflegen](#10-kurse-und-bekanntmachungen-pflegen)
11. [Welche Sprache ein Besucher sieht](#11-welche-sprache-ein-besucher-sieht)
12. [Eine Sprache wieder entfernen](#12-eine-sprache-wieder-entfernen)
13. [Häufige Stolpersteine](#13-häufige-stolpersteine)

---

## 1. Was schon vorbereitet ist

Die Seite erscheint zurzeit nur auf Deutsch. **Die Mehrsprachigkeit ist
aber vollständig angelegt** und wartet nur auf einen zweiten Eintrag:

| Vorhanden | Erscheint, sobald es zwei Sprachen gibt |
| --- | --- |
| Sprachumschalter im Kopfbereich | ja – vorher wäre er ein Knopf ohne Wahl |
| eigener Ordner je Sprache (`/en/`) | ja |
| `hreflang`-Verweise für Suchmaschinen | ja |
| `x-default` auf die deutsche Fassung | ja |
| Rückfall auf den deutschen Text | wirkt sofort |
| Sitemap mit beiden Fassungen | ja |
| `llms.txt` nennt beide Fassungen | ja |

**Sie schreiben also keine Technik, nur Texte.** Und Sie müssen nicht
alles auf einmal übersetzen: Was in der neuen Datei fehlt, füllt
automatisch der deutsche Text. Sie können abschnittsweise vorgehen und
zwischendurch jederzeit veröffentlichen.

> **Warum steht der Umschalter noch nicht da?** Weil ein Umschalter mit
> nur einem Eintrag nichts umschaltet. Dasselbe gilt für die
> Themenwahl – erst ab zwei Möglichkeiten erscheint sie. Beide stehen
> nebeneinander im Kopfbereich und kommen sich nicht ins Gehege.

---

## 2. Überblick: vier Handgriffe

| Schritt | Datei | Dauer |
| --- | --- | --- |
| 1. Textdatei anlegen | `translations/en.json` | 1 Min. |
| 2. Übersetzen | `translations/en.json` | Stunden bis Tage |
| 3. Sprache anmelden | `build.py` **und** `app.py` | 2 Min. |
| 4. Rechtstexte, Vorschaubild | `content/`, `tools/` | 30 Min. |

Die Technik ist in fünf Minuten erledigt. Die Zeit steckt im Übersetzen –
die Datei enthält rund zwanzig Textblöcke.

---

## 3. Schritt 1 – Die Textdatei anlegen

**Legen Sie die neue Datei als Kopie an.** Nicht von Hand neu schreiben:

```bash
cp translations/de.json translations/en.json
```

Unter Windows in der PowerShell:

```powershell
Copy-Item translations\de.json translations\en.json
```

**Warum kopieren und nicht neu anfangen?** Die Vorlagen durchlaufen neun
Blöcke unmittelbar – `hero`, `about`, `offer`, `approach`, `therapist`,
`practice`, `courses`, `testimonials` und `contact`. Für einzelne Texte
gibt es den Rückfall auf Deutsch, für eine Schleife über einen fehlenden
Block nicht. Fehlt einer, hält der Build an und sagt Ihnen, welcher:

```
Die Sprachdateien sind unvollständig:
  · [en] Der Block „hero“ fehlt in translations/en.json – die Vorlage
    durchläuft ihn und kann ihn nicht ersetzen.
```

Aus einer Kopie kann das nicht passieren.

**Der Dateiname ist der Sprachcode.** `en.json` für Englisch, `fr.json`
für Französisch. Zwei Kleinbuchstaben nach ISO 639-1; eine Liste findet
sich im Netz unter *ISO 639-1*.

---

## 4. Schritt 2 – Übersetzen

Öffnen Sie `translations/en.json` in einem Texteditor. Die Datei sieht so
aus:

```json
{
  "meta": {
    "title": "Körper im Einklang – Spiraldynamik in Musterstadt",
    "description": "Physiotherapie und Kurse nach dem Konzept …"
  },
  "hero": {
    "title_line1": "Bewegung,",
    "title_line2": "die gut tut."
  }
}
```

**Die Regel ist einfach:** Links vom Doppelpunkt steht der Schlüssel – der
bleibt. Rechts steht der Text – der wird übersetzt.

```json
  "hero": {
    "title_line1": "Movement",          ← übersetzt
    "title_line2": "that does good."    ← übersetzt
  }
```

Nicht `"title_line1"` zu `"erste_zeile"` machen. Danach sucht das
Programm, und es findet nichts mehr.

**Achten Sie auf die Zeichensetzung von JSON:**

* Jeder Text steht in geraden doppelten Anführungszeichen `"…"`.
  Typografische Anführungszeichen („…") gehören **in** den Text, nicht um
  ihn herum.
* Nach jedem Eintrag steht ein Komma – außer nach dem letzten in einer
  Klammer.
* Kommt ein Anführungszeichen im Text selbst vor, muss ein Rückstrich
  davor: `"Der Kurs \"Gesunde Füße\""`.

> **Tipp:** Fügen Sie die Datei nach dem Übersetzen einmal in einen
> *JSON validator* im Netz ein, oder rufen Sie auf:
>
> ```bash
> python3 -m json.tool translations/en.json > /dev/null
> ```
>
> Kommt keine Meldung, ist die Datei in Ordnung. Andernfalls nennt sie
> Zeile und Spalte des Fehlers.

**Sie dürfen abschnittsweise vorgehen.** Übersetzen Sie zuerst, was
Besucher zuerst sehen – `meta`, `nav`, `hero`, `about`, `offer`,
`contact`. Der Rest erscheint vorerst auf Deutsch. Der Build sagt Ihnen
nach jedem Lauf, welche Blöcke noch fehlen.

**Die Blöcke der Reihe nach:**

| Block | Was darin steht |
| --- | --- |
| `meta` | Seitentitel und Beschreibung für Suchmaschinen |
| `brand` | Praxisname und Unterzeile |
| `nav` | die Menüpunkte |
| `theme` | Beschriftung der Darstellungswahl (Hell, Dunkel, Wie das Gerät) |
| `hero` | Kopfbereich mit Überschrift und den drei Schritten |
| `news` | Bekanntmachungen – siehe Abschnitt 10 |
| `about` | das Konzept der Spiraldynamik |
| `offer` | die Therapieangebote |
| `approach` | der Ablauf in vier Schritten |
| `therapist` | Vorstellung, Zahlen, Ausbildungsweg |
| `contact` | Anschrift, Zeiten, Hinweise zur Terminvergabe |
| `footer` | Fußbereich |
| `error` | die Fehlerseite |
| `courses` | die Kurse – siehe Abschnitt 10 |
| `formats` | Monatsnamen und Datumsmuster – siehe Abschnitt 6 |
| `legal` | Überschriften von Impressum und Datenschutz |
| `practice` | Diashow der Räume |
| `funding` | Förderhinweis |
| `testimonials` | Rückmeldungen |
| `seo` | Angaben für Suchmaschinen und Antwortdienste |

---

## 5. Was nicht übersetzt wird

Manche Werte sehen aus wie Text, sind aber Daten. Übersetzt man sie,
gehen Termine, Bilder oder Verweise verloren.

| Wert | Beispiel | Warum er bleibt |
| --- | --- | --- |
| `courses.items[].start_date` | `2026-09-14` | Termin im Format JJJJ-MM-TT. Angezeigt wird er in der Sprache des Lesers – dafür sorgt Abschnitt 6 |
| `news.items[].hide_from` | `2026-08-31` | Tag, ab dem eine Bekanntmachung verschwindet |
| `therapist.image` | `therapeut.jpg` | Dateiname |
| `practice.slides[].image` | `praxis-1.jpg` | Dateiname |
| `funding.logos[].image` | `foerderer-1.png` | Dateiname |
| `seo.og_image` | `og-bild.png` | Dateiname – hier ist ein **eigener** sinnvoll, siehe Schritt 4 |
| `contact.email` | `praxis@…` | Adresse |
| `contact.phone` | `+49 30 …` | Rufnummer |
| `seo.latitude`, `seo.longitude` | Zahlen | Koordinaten |

> **Bilder brauchen Sie nicht zu wiederholen.** Bei der Diashow und den
> Förderlogos holt sich der Build die Dateinamen immer aus der deutschen
> Datei. Übersetzt werden nur `alt` und `caption` – also die
> Beschreibung für Menschen, die das Bild nicht sehen können, und die
> Bildunterschrift. Ändern Sie einen Dateinamen nur in `de.json`.

---

## 6. Datumsangaben und Monatsnamen

Ein Datum steht als `2026-09-14` in der Datei und erscheint auf der Seite
als „14. September". Wie daraus im Englischen „September 14" wird, steht
im Block `formats`:

```json
"formats": {
  "months": ["Januar", "Februar", "März", "April", "Mai", "Juni",
             "Juli", "August", "September", "Oktober", "November", "Dezember"],
  "date": "{day}. {month}",
  "date_with_year": "{day}. {month} {year}"
}
```

Für Englisch:

```json
"formats": {
  "months": ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"],
  "date": "{month} {day}",
  "date_with_year": "{month} {day}, {year}"
}
```

**Drei Dinge sind wichtig:**

1. `months` muss **genau zwölf** Einträge haben, in der richtigen
   Reihenfolge. Sind es mehr oder weniger, erscheint statt des Namens die
   Zahl des Monats.
2. `{day}`, `{month}` und `{year}` sind Platzhalter und bleiben **genau
   so** stehen – auch die geschweiften Klammern. Alles andere darum herum
   dürfen Sie umstellen: Reihenfolge, Punkte, Kommas.
3. `date_with_year` wird nur benutzt, wenn der Termin in einem anderen
   Jahr liegt als heute. So steht bei einem Kurs im selben Jahr keine
   überflüssige Jahreszahl.

---

## 7. Schritt 3 – Die Sprache anmelden

Damit der Umschalter erscheint, muss die Sprache in **beiden**
Python-Dateien stehen: `build.py` erzeugt die veröffentlichte Seite,
`app.py` die Vorschau am eigenen Rechner.

Suchen Sie in beiden Dateien nach `LANGUAGES` und ergänzen Sie eine
Zeile:

```python
LANGUAGES = {
    "de": {"label": "Deutsch", "short": "DE", "locale": "de_DE"},
    "en": {"label": "English", "short": "EN", "locale": "en_GB"},
}
```

| Feld | Wofür | Beispiel |
| --- | --- | --- |
| Schlüssel links | Dateiname, Ordner (`/en/`) und `hreflang` | `"en"` |
| `label` | vollständiger Name, erscheint beim Überfahren | `English` |
| `short` | Kürzel im Umschalter | `EN` |
| `locale` | für `og:locale`, wenn jemand den Link teilt | `en_GB` |

**Der Schlüssel muss dem Dateinamen entsprechen:** `"en"` gehört zu
`translations/en.json`.

**Zum `locale`:** Sprache und Land, verbunden durch einen Unterstrich.
Gängige Werte:

| Sprache | `locale` |
| --- | --- |
| Englisch (britisch) | `en_GB` |
| Englisch (amerikanisch) | `en_US` |
| Französisch | `fr_FR` |
| Italienisch | `it_IT` |
| Türkisch | `tr_TR` |
| Polnisch | `pl_PL` |
| Russisch | `ru_RU` |

> **Die Reihenfolge im Block ist die Reihenfolge der Knöpfe.** Deutsch
> steht vorn, weil es die Standardsprache ist. Diese Rolle steckt in
> `DEFAULT_LANGUAGE` – die deutsche Fassung liegt deshalb direkt unter
> der Adresse der Domain, die englische unter `/en/`.

---

## 8. Schritt 4 – Rechtstexte und Vorschaubild

Beides ist freiwillig. Ohne diese Schritte funktioniert die Seite, es
erscheinen nur die deutschen Fassungen.

### a) Impressum und Datenschutz

Diese beiden Texte stehen nicht in der JSON-Datei, sondern als HTML in
`content/`:

```
content/impressum.de.html
content/datenschutz.de.html
```

Legen Sie daneben `impressum.en.html` und `datenschutz.en.html` an – am
einfachsten wieder als Kopie. **Fehlen sie, erscheint der deutsche
Text.** Eine Seite ohne Impressum gibt es also nie.

> **Rechtlicher Hinweis:** Das Impressum muss den Anforderungen genügen,
> die für Ihre Praxis gelten. Eine Übersetzung ersetzt keine rechtliche
> Prüfung. Lassen Sie beide Fassungen ansehen, bevor die Seite online
> geht.

### b) Vorschaubild für geteilte Links

Teilt jemand die Adresse in einem Messenger, erscheint eine Vorschaukarte
mit Text aus der Sprachdatei. Für eine eigene englische Karte tragen Sie
in `en.json` einen anderen Dateinamen ein:

```json
"seo": {
  "og_image": "og-bild-en.png"
}
```

Dann erzeugen:

```bash
python3 tools/make-og-image.py
```

Das Programm baut für jede Sprache ein Bild, sofern dort ein Dateiname
steht. Gebraucht wird Chromium oder Chrome.

**Lassen Sie den Namen unverändert**, erscheint für beide Sprachen
dasselbe – deutsche – Bild. Das ist kein Fehler, nur eine verpasste
Gelegenheit.

---

## 9. Was der Build daraus macht

```bash
python3 build.py
```

Danach steht in `dist/`:

```
dist/
  index.html            deutsche Startseite
  impressum.html
  datenschutz.html
  en/
    index.html          englische Startseite
    impressum.html
    datenschutz.html
  sitemap.xml           beide Sprachen, alle Seiten
  llms.txt              nennt beide Fassungen
  robots.txt
```

Außerdem geschieht, ohne Ihr Zutun:

* Im Kopfbereich erscheint der Umschalter **DE | EN**, neben der
  Themenwahl.
* Im `<head>` jeder Seite stehen `hreflang`-Verweise auf beide Fassungen
  und ein `x-default` auf die deutsche.
* Die Sitemap führt jede Seite in jeder Sprache.
* `og:locale` trägt den Wert aus `LANGUAGES`.

**Ansehen:**

```bash
python3 build.py --serve
```

Dann <http://127.0.0.1:8000/> für Deutsch und
<http://127.0.0.1:8000/en/> für Englisch.

**Diese Liste durchgehen:**

| Stelle | Worauf achten |
| --- | --- |
| Umschalter oben rechts | Beide Kürzel da, das aktive hervorgehoben |
| Umschalten | Führt auf dieselbe Seite in der anderen Sprache |
| Kursdaten | Erscheinen in der Schreibweise der Sprache (Abschnitt 6) |
| Menü | Alle Punkte übersetzt oder bewusst noch deutsch |
| Fußbereich | Impressum und Datenschutz erreichbar |
| Fenster schmal ziehen | Beide Umschalter passen bis 1200 px nebeneinander |

---

## 10. Kurse und Bekanntmachungen pflegen

**Hier gilt der Rückfall auf Deutsch bewusst nicht.** Kurse und
Bekanntmachungen liest der Build unmittelbar aus der jeweiligen
Sprachdatei.

Der Grund: Ein Kurs, der nur auf Deutsch stattfindet, soll nicht
stillschweigend in der englischen Fassung erscheinen. Und ein Termin, den
jemand in einer Datei streicht, soll nicht aus der anderen
zurückkommen.

**Das heißt für die Pflege:** Ein neuer Kurs muss in **jede**
Sprachdatei, unter `courses.items`:

```json
{
  "title": "Healthy Feet",
  "text": "Arches, rolling and choosing shoes …",
  "start_date": "2026-09-14",
  "scope": "6 × 60 minutes",
  "spots": "3 of 8",
  "price": "240 €"
}
```

**Das `start_date` muss in allen Dateien gleich sein.** Sonst zeigt jede
Sprache einen anderen Termin.

Ist `courses.items` in einer Sprache leer, meldet der Build:

```
Hinweise zu den Sprachdateien:
  · [en] „courses.items“ ist leer – in dieser Sprache erscheint der
    Abschnitt ohne Einträge.
```

Dasselbe gilt für `news.items`. Wie das Ausblenden über `hide_from`
funktioniert, steht in der [README](README.md) unter „Inhalte anpassen".

---

## 11. Welche Sprache ein Besucher sieht

| Fall | Ergebnis |
| --- | --- |
| Aufruf von `/` | Deutsch |
| Aufruf von `/en/` | Englisch |
| Zuvor umgeschaltet | Die zuletzt gewählte Sprache, gemerkt in einem Cookie namens `lang` |

**Die Browsersprache wird nicht ausgewertet** – bewusst. Wer aus einer
Suchmaschine auf die deutsche Seite kommt, soll dort auch landen.

Soll beim allerersten Besuch zusätzlich die Spracheinstellung des
Browsers berücksichtigt werden, setzen Sie in `app.py`:

```python
AUTO_DETECT_BROWSER_LANGUAGE = True
```

> **Das wirkt nur in der Vorschau am eigenen Rechner.** Die
> veröffentlichte Seite besteht aus festen Dateien; dort kann nichts
> abgefragt werden. Eine Weiche auf dem Server ließe sich über die
> `.htaccess` bauen – das ist ein eigenes Thema und für eine Praxisseite
> selten die Mühe wert.

---

## 12. Eine Sprache wieder entfernen

Den Eintrag aus `LANGUAGES` löschen – in **beiden** Dateien, `build.py`
und `app.py`. Das genügt.

Die Textdatei kann liegen bleiben; gebaut wird nur, was in `LANGUAGES`
steht. Der Umschalter verschwindet, sobald nur noch eine Sprache übrig
ist.

**Der Ordner `dist/en/` verschwindet von selbst**, weil der Build `dist/`
jedes Mal neu anlegt. Auf dem Webspace bleibt er allerdings stehen:
Räumen Sie ihn dort einmal von Hand ab, oder laden Sie mit

```bash
python3 deploy.py --delete
```

hoch – das entfernt auf dem Server, was es lokal nicht mehr gibt.

---

## 13. Häufige Stolpersteine

| Symptom | Ursache und Abhilfe |
| --- | --- |
| Der Umschalter erscheint nicht | `LANGUAGES` nur in einer der beiden Dateien ergänzt |
| Der Build hält an: „Der Block … fehlt" | Die Sprachdatei wurde von Hand angelegt statt kopiert – Abschnitt 3 |
| `json.decoder.JSONDecodeError` | Ein Komma zu viel oder zu wenig, oder ein Anführungszeichen im Text ohne Rückstrich – Abschnitt 4 |
| Ein Teil der Seite bleibt deutsch | Das ist der Rückfall und meist Absicht. Fehlt der Block ganz, sagt es der Build |
| Der Abschnitt „Kurse" ist in der neuen Sprache leer | `courses.items` muss in jeder Sprachdatei stehen – Abschnitt 10 |
| Die Kurse zeigen deutsche Monatsnamen | `formats.months` in der neuen Datei nicht übersetzt – Abschnitt 6 |
| Statt des Monats steht eine Zahl | `formats.months` hat nicht genau zwölf Einträge |
| Das Datum steht in falscher Reihenfolge | `formats.date` anpassen, die Platzhalter aber stehen lassen |
| Die Bilder fehlen in der neuen Sprache | Dateinamen nur in `de.json` pflegen – Abschnitt 5 |
| Der Umschalter passt nicht mehr in die Zeile | Ab 1200 px klappt das Menü ohnehin zum Burger zusammen. Bei mehr als zwei Sprachen den Wert in `style.css` prüfen |
| Geteilte Links zeigen das deutsche Bild | `seo.og_image` in der neuen Datei umbenennen – Schritt 4b |

**Wenn gar nichts passt:** `git checkout -- .` verwirft alle Änderungen,
und Sie fangen mit einer frischen Kopie neu an.
