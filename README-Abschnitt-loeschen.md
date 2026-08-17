# Einen Abschnitt von der Seite entfernen

Schritt-für-Schritt-Anleitung, um einen ganzen Abschnitt der Startseite
loszuwerden – etwa die Rückmeldungen, solange noch keine vorliegen, oder
den Förderhinweis nach Ablauf der Förderung.

Geschrieben für Leute ohne Vorkenntnisse: Jeder Handgriff steht
vollständig da, jeder Codeblock lässt sich kopieren.

> **Lesen Sie zuerst Abschnitt 2.** Für einige Abschnitte müssen Sie gar
> nichts löschen – es genügt, ihre Inhalte zu leeren. Das ist der
> sicherere Weg und jederzeit umkehrbar.

---

## Inhalt

1. [Welche Abschnitte es gibt](#1-welche-abschnitte-es-gibt)
2. [Der einfache Weg: Inhalte leeren](#2-der-einfache-weg-inhalte-leeren)
3. [Der zweite Weg: ausblenden](#3-der-zweite-weg-ausblenden)
4. [Der vollständige Weg: löschen](#4-der-vollständige-weg-löschen)
5. [Schritt 1 – Den Abschnitt entfernen](#5-schritt-1--den-abschnitt-entfernen)
6. [Schritt 2 – Die Menüpunkte entfernen](#6-schritt-2--die-menüpunkte-entfernen)
7. [Schritt 3 – Die Texte entfernen](#7-schritt-3--die-texte-entfernen)
8. [Schritt 4 – Die Gestaltung aufräumen](#8-schritt-4--die-gestaltung-aufräumen)
9. [Was sich von selbst regelt](#9-was-sich-von-selbst-regelt)
10. [Abschnitte, die besser bleiben](#10-abschnitte-die-besser-bleiben)
11. [Prüfen](#11-prüfen)
12. [Rückgängig machen](#12-rückgängig-machen)
13. [Häufige Stolpersteine](#13-häufige-stolpersteine)

---

## 1. Welche Abschnitte es gibt

Die Startseite besteht von oben nach unten aus diesen Abschnitten. Der
**Anker** ist der Name, unter dem der Abschnitt überall auftaucht – im
Menü als `#kurse`, in der Datei als `id="courses"`.

| Anker | Auf der Seite | Löschbar? |
| --- | --- | --- |
| `hero` | Kopfbereich mit der großen Überschrift | besser nicht, siehe Abschnitt 10 |
| `news` | Bekanntmachungen | verschwindet von selbst |
| `concept` | Das Konzept der Spiraldynamik | ja |
| `courses` | Kurse | ja |
| `offer` | Therapie im Einzeltermin | ja |
| `approach` | So arbeiten wir zusammen | ja |
| `therapist` | Wer Sie behandelt | ja |
| `practice` | Ein Ort zum Ankommen | ja |
| `testimonials` | Rückmeldungen | ja |
| `contact` | Termin vereinbaren | besser nicht, siehe Abschnitt 10 |
| `funding` | Gefördert durch | verschwindet von selbst |

---

## 2. Der einfache Weg: Inhalte leeren

**Zwei Abschnitte verschwinden vollständig, sobald sie nichts mehr zu
zeigen haben.** Sie brauchen dafür keine Datei zu verändern außer der
Textdatei – und Sie können es jederzeit rückgängig machen, indem Sie die
Einträge wieder hineinschreiben.

### Förderhinweis

In `translations/de.json` die Liste leeren:

```json
"funding": {
  "logos": []
}
```

Der ganze Abschnitt „Gefördert durch" ist damit weg.

### Bekanntmachungen

Hier hängen **zwei** Listen zusammen: der Abschnitt zeigt sowohl die
Hinweise als auch einen Verweis auf den nächsten Kurs. Er verschwindet
erst, wenn beides leer ist:

```json
"news": {
  "items": []
},
"courses": {
  "items": []
}
```

> **Nachgemessen:** Nur `news.items` zu leeren genügt **nicht** – der
> Kurshinweis hält den Abschnitt am Leben. Erst ohne kommende Kurse ist
> er ganz fort. Das ist Absicht: Ein freier Kursplatz soll oben stehen,
> auch wenn es gerade keine Bekanntmachung gibt.

Dasselbe geschieht übrigens von allein, sobald alle Hinweise abgelaufen
und alle Kurstermine vergangen sind. Der Build sagt Ihnen jedes Mal, wann
das sein wird:

```
Nächste Änderung durch Zeitablauf: 31.08.2026 (in 14 Tagen) –
Bekanntmachung „Sommerpause“ endet
```

### Bei den übrigen Abschnitten geht das nicht

Leeren Sie `testimonials.items` oder `practice.slides`, **bleibt die
Überschrift stehen** und darunter erscheint ein Hinweistext. Das ist
gewollt – bei den Rückmeldungen etwa eine Einladung, welche zu schreiben.
Wollen Sie diese Abschnitte wirklich los, führt der Weg über Abschnitt 4.

---

## 3. Der zweite Weg: ausblenden

Sie möchten einen Abschnitt vorerst nicht zeigen, aber später vielleicht
wieder? Dann löschen Sie ihn nicht, sondern **stellen ihn still**.

Öffnen Sie `templates/index.html`, suchen Sie den Abschnitt und setzen
Sie eine Jinja-Bedingung darum, die nie zutrifft:

```jinja
{% if false %}
<section class="section" id="testimonials">
  …
</section>
{% endif %}
```

Die geschweiften Klammern mit Prozentzeichen sind Anweisungen an das
Bauprogramm; `false` heißt „niemals". Der Abschnitt wird dann nicht mehr
gebaut und erscheint in keiner Datei.

**Den Menüpunkt müssen Sie trotzdem entfernen** – sonst führt er ins
Leere. Wie, steht in Abschnitt 6.

**Zum Zurückholen** die beiden Zeilen wieder löschen.

> **Wann lohnt sich das?** Wenn der Abschnitt inhaltlich fertig ist und
> nur der Anlass fehlt – etwa die Rückmeldungen, solange die erste
> Zuschrift aussteht. Alle Texte bleiben erhalten, nichts geht verloren.

---

## 4. Der vollständige Weg: löschen

Wenn ein Abschnitt endgültig weg soll, sind es **vier Handgriffe**:

| Schritt | Datei | Pflicht? |
| --- | --- | --- |
| 1. Abschnitt entfernen | `templates/index.html` | ja |
| 2. Menüpunkte entfernen | `templates/partials/header.html`, `footer.html` | ja |
| 3. Texte entfernen | `translations/de.json` (jede Sprachdatei) | ja |
| 4. Gestaltung aufräumen | `static/css/style.css` | nein, aber sauber |

**Die Reihenfolge ist wichtig.** Löschen Sie die Texte zuerst und den
Abschnitt danach, hält der Build dazwischen an:

```
jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'offer'
```

Das ist kein Schaden – machen Sie einfach mit Schritt 1 weiter, dann
läuft es wieder. Aber es verwirrt unnötig.

Als durchgehendes Beispiel dient hier der Abschnitt **`offer`**
(„Behandlung im Einzeltermin").

---

## 5. Schritt 1 – Den Abschnitt entfernen

Öffnen Sie `templates/index.html`. Jeder Abschnitt beginnt mit einer
Kommentarzeile und endet mit `</section>`:

```html
<!-- ── Therapie ───────────────────────────────────────────────────── -->
<section class="section" id="offer">
  <div class="container">
    …
  </div>
</section>
```

**Löschen Sie alles** von der Kommentarzeile bis einschließlich
`</section>`.

**So finden Sie die richtige Stelle:** Suchen Sie im Editor nach
`id="offer"` – meist mit **Strg + F**. Von dort gehen Sie ein paar Zeilen
nach oben bis zur Kommentarzeile mit den langen Strichen und markieren
bis zum nächsten `</section>`.

> **Aufpassen bei geschachtelten Enden.** Innerhalb eines Abschnitts
> stehen viele `</div>`, aber nur **ein** `</section>` – und zwar am
> Ende. Wenn Sie unsicher sind: Das nächste `<!-- ──` markiert bereits
> den folgenden Abschnitt. Bis dorthin (ausschließlich) muss alles weg.

---

## 6. Schritt 2 – Die Menüpunkte entfernen

Der Anker steht an **zwei** Stellen im Menü. Beide müssen weg, sonst
führt ein Klick ins Leere: Die Seite springt nicht, es passiert einfach
nichts.

**Kopfbereich** – `templates/partials/header.html`:

```html
<li><a class="nav__link" href="{{ anchor_base }}#offer">{{ t('nav.offer') }}</a></li>
```

**Fußbereich** – `templates/partials/footer.html`:

```html
<li><a href="{{ anchor_base }}#offer">{{ t('nav.offer') }}</a></li>
```

Jeweils die ganze Zeile löschen.

> **Nachgemessen:** Vergisst man das, läuft der Build ohne Fehlermeldung
> durch – der tote Verweis fällt erst beim Klicken auf. Es gibt keine
> Warnung. Prüfen Sie deshalb nach Abschnitt 11.

**Weniger Menüpunkte sind übrigens gut.** Das Menü klappt erst ab 1200
Pixel Fensterbreite zum Burger-Menü zusammen, weil sieben Punkte plus
Sprach- und Themenwahl viel Platz brauchen. Mit einem Punkt weniger wird
es luftiger.

---

## 7. Schritt 3 – Die Texte entfernen

In `translations/de.json` steht zu jedem Abschnitt ein Block. Löschen Sie
ihn samt Inhalt:

```json
  "offer": {
    "eyebrow": "Therapie",
    "title": "Behandlung im Einzeltermin",
    …
  },
```

**Achten Sie auf die Kommas.** JSON verlangt zwischen zwei Einträgen ein
Komma, nach dem letzten aber keins. Löschen Sie den letzten Block einer
Klammer, muss das Komma beim vorletzten weg.

Danach prüfen:

```bash
python3 -m json.tool translations/de.json > /dev/null
```

Keine Meldung heißt: Die Datei ist in Ordnung. Andernfalls nennt sie
Zeile und Spalte.

**Gibt es weitere Sprachen**, muss der Block aus **jeder** Sprachdatei
verschwinden. Bleibt er in einer stehen, schadet das nichts – er wird nur
nirgends mehr gebraucht.

**Den Menüeintrag** unter `nav` dürfen Sie ebenfalls löschen:

```json
"nav": {
  "offer": "Angebot",      ← diese Zeile
}
```

---

## 8. Schritt 4 – Die Gestaltung aufräumen

Die Gestaltungsregeln des Abschnitts stehen in `static/css/style.css`.
**Sie müssen sie nicht löschen** – ungenutzte Regeln stören niemanden und
machen die Datei nur unwesentlich größer. Wer aufräumen möchte, findet
sie so:

| Abschnitt | Klassen, die nur dort vorkommen |
| --- | --- |
| `news` | `.notices`, `.notice*` |
| `concept` | `.concept*`, `.features`, `.feature*`, `.regions`, `.region*` |
| `courses` | `.benefits*`, `.courses`, `.course*` |
| `offer` | `.cards`, `.card`, `.card__title`, `.card__text`, `.card__meta` |
| `approach` | `.steps`, `.step*` |
| `therapist` | `.therapist*`, `.stats*` |
| `practice` | `.slideshow*` |
| `testimonials` | `.voices*`, `.voice*` |
| `contact` | `.contact*`, `.map*` |
| `funding` | `.funding*` |

**Diese Klassen benutzen mehrere Abschnitte – nicht anfassen:**

| Klasse | Wird gebraucht von |
| --- | --- |
| `.section__title`, `.section__lead`, `.section__head` | fast allen |
| `.eyebrow` | allen |
| `.btn`, `.btn--primary` | Kurse, Therapeut, Stimmen, Kontakt |
| `.mail-hint` | Kurse, Stimmen, Kontakt |
| `.card__link` | Angebot **und** Kontakt |

> **`.card__link` ist die heimtückischste.** Sie sieht nach „gehört zum
> Angebot" aus, wird aber auch im Kontaktbereich verwendet. Löschen Sie
> sie mit, verliert dort ein Verweis seine Gestaltung.

**Im Zweifel lassen Sie das CSS stehen.** Es ist der einzige Schritt
dieser Anleitung, bei dem man etwas kaputt machen kann, ohne dass es eine
Fehlermeldung gibt.

---

## 9. Was sich von selbst regelt

Um diese Dinge müssen Sie sich **nicht** kümmern – sie stimmen nach dem
Löschen von allein:

| Was | Warum |
| --- | --- |
| **Der Wechsel heller und abgesetzter Flächen** | Die Abschnitte wechseln sich ab. Welche Fläche ein Abschnitt bekommt, ergibt sich aus seiner Stellung, nicht aus einer Klasse – nach dem Löschen rückt alles nach und der Wechsel bleibt |
| **Die maschinenlesbaren Angaben** (JSON-LD) | Fehlt ein Block, entfällt der zugehörige Eintrag. Nachgemessen: bleibt gültiges JSON |
| **`llms.txt`** | Wird bei jedem Bauen neu aus den vorhandenen Texten erzeugt |
| **Die Sitemap** | Zählt Seiten, nicht Abschnitte – bleibt unverändert |
| **Das Vorschaubild** | Nur wenn Sie einen Block gelöscht haben, der darin vorkommt (`brand`, `hero`, `offer`, `courses`, `seo`), einmal `python3 tools/make-og-image.py` aufrufen |
| **Das JavaScript** | Sucht seine Bauteile und findet sie einfach nicht mehr. Nur die Diashow (`practice`) hat eigenen Code – auch der bleibt still |

> **Eine Kleinigkeit am Fuß der Seite.** Löschen Sie eine **ungerade**
> Zahl von Abschnitten, endet die Seite auf einer abgesetzten Fläche –
> und der Fußbereich ist ebenfalls abgesetzt. Die beiden stoßen dann
> farblich aneinander. Sichtbar bleibt die Grenze trotzdem: Der
> Fußbereich zieht seit jeher einen eigenen Trennstrich. Sie müssen
> nichts unternehmen.

---

## 10. Abschnitte, die besser bleiben

**`contact` – Termin vereinbaren.** Daran hängt mehr als der Abschnitt
selbst:

* Der Knopf „Termin vereinbaren" oben rechts zeigt dorthin.
* Anschrift, Telefon und Öffnungszeiten stehen in den maschinenlesbaren
  Angaben für Suchmaschinen und in `llms.txt`.
* Die E-Mail-Adresse speist die Anmeldeknöpfe bei den Kursen und den
  Hinweis „Kein E-Mail-Programm zur Hand?".

Wollen Sie ihn dennoch loswerden, entfernen Sie zusätzlich den Knopf im
Kopfbereich (`header.html`, die Zeile mit `btn--primary`).

**`hero` – der Kopfbereich.** Er trägt die Hauptüberschrift der Seite.
Ohne ihn beginnt die Seite unvermittelt, und Suchmaschinen fehlt die
wichtigste Überschrift. Wenn er stört, ändern Sie lieber seinen Text.

---

## 11. Prüfen

```bash
python3 build.py --serve
```

Dann <http://127.0.0.1:8000/> öffnen.

| Prüfung | Worauf achten |
| --- | --- |
| Der Abschnitt ist weg | Durchscrollen |
| Das Menü stimmt | Jeden Punkt anklicken – jeder muss springen |
| Der Fußbereich stimmt | Dasselbe dort |
| Die Flächen wechseln sich ab | Von oben nach unten: hell, abgesetzt, hell … nirgends zwei gleiche nebeneinander |
| Keine Lücke | Zwischen den Nachbarn des gelöschten Abschnitts sitzt kein doppelter Abstand |
| Dunkles Thema | Rechts oben auf ☾ schalten und noch einmal ansehen |

**Tote Verweise finden**, ohne jeden Punkt anzuklicken:

```bash
python3 - <<'ENDE'
import re
from pathlib import Path
html = Path("dist/index.html").read_text(encoding="utf-8")
anker = set(re.findall(r'id="([a-z-]+)"', html))
verweise = set(re.findall(r'href="#([a-z-]+)"', html))
tot = sorted(verweise - anker)
print("Verweise ins Leere:", tot or "keine")
ENDE
```

Steht dort `keine`, ist das Menü in Ordnung.

Danach **auf dem Telefon ansehen**: siehe
[README-Android-Test.md](README-Android-Test.md).

---

## 12. Rückgängig machen

Solange Sie noch nichts eingecheckt haben, zeigt

```bash
git diff
```

alle Änderungen, und

```bash
git checkout -- .
```

verwirft sie wieder – der Abschnitt ist zurück.

**Ist schon eingecheckt worden**, holt

```bash
git log --oneline
git checkout <kennung> -- templates/index.html
```

eine einzelne Datei aus einem früheren Stand zurück. `<kennung>` ist die
Zeichenfolge links in der Liste.

> **Deshalb lohnt sich Abschnitt 3.** Wer nur ausblendet, braucht Git
> gar nicht erst zu bemühen.

---

## 13. Häufige Stolpersteine

| Symptom | Ursache und Abhilfe |
| --- | --- |
| `UndefinedError: 'dict object' has no attribute …` | Der Textblock ist gelöscht, der Abschnitt steht noch. Schritt 1 nachholen |
| `json.decoder.JSONDecodeError` | Ein Komma zu viel oder zu wenig in der Sprachdatei – Abschnitt 7 |
| Ein Menüpunkt tut nichts mehr | Der Anker fehlt, der Verweis steht noch. Schritt 2 nachholen, in **beiden** Dateien |
| Der Abschnitt ist weg, aber es klafft eine Lücke | Ein `</section>` zu viel oder zu wenig gelöscht. Die Datei mit `git diff` ansehen |
| Zwei gleiche Flächen nebeneinander | Sollte nicht vorkommen – der Wechsel ergibt sich aus der Stellung. Prüfen Sie, ob versehentlich zwei Abschnitte ineinander gerutscht sind |
| Im Kontaktbereich sieht ein Verweis anders aus | `.card__link` wurde mitgelöscht – Abschnitt 8 |
| Der Abschnitt „Stimmen" ist leer, aber die Überschrift steht noch | Das ist Absicht. Leeren genügt hier nicht, siehe Abschnitt 2 |
| Der Förderhinweis kommt immer wieder | In `funding.logos` steht noch ein Eintrag |
| Die Bekanntmachungen bleiben trotz leerer Liste | Ein kommender Kurs hält den Abschnitt – siehe Abschnitt 2 |
| Geteilte Links zeigen alten Text | `python3 tools/make-og-image.py` aufrufen. Messenger merken sich die Vorschau oft tagelang |

**Wenn gar nichts passt:** `git checkout -- .` setzt alles zurück, und
Sie fangen in Ruhe neu an.
