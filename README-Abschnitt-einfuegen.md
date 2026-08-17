# Einen neuen Abschnitt einfügen

Schritt-für-Schritt-Anleitung, um der Startseite einen weiteren Abschnitt
hinzuzufügen – etwa häufige Fragen, Preise oder eine Anfahrtsbeschreibung.

Geschrieben für Leute ohne Vorkenntnisse: Jeder Handgriff steht
vollständig da, jeder Codeblock lässt sich kopieren. Als durchgehendes
Beispiel dient ein Abschnitt **„Häufige Fragen"**.

> **Das Gegenstück** – einen Abschnitt wieder loswerden – steht in
> [README-Abschnitt-loeschen.md](README-Abschnitt-loeschen.md).

---

## Inhalt

1. [Woraus ein Abschnitt besteht](#1-woraus-ein-abschnitt-besteht)
2. [Überblick: vier Handgriffe](#2-überblick-vier-handgriffe)
3. [Schritt 1 – Namen und Platz festlegen](#3-schritt-1--namen-und-platz-festlegen)
4. [Schritt 2 – Den Abschnitt schreiben](#4-schritt-2--den-abschnitt-schreiben)
5. [Schritt 3 – Die Texte hinterlegen](#5-schritt-3--die-texte-hinterlegen)
6. [Schritt 4 – In das Menü aufnehmen](#6-schritt-4--in-das-menü-aufnehmen)
7. [Fertige Bausteine zum Kopieren](#7-fertige-bausteine-zum-kopieren)
8. [Die Falle mit dem Namen „items"](#8-die-falle-mit-dem-namen-items)
9. [Wenn es mehrere Sprachen gibt](#9-wenn-es-mehrere-sprachen-gibt)
10. [Was von selbst funktioniert](#10-was-von-selbst-funktioniert)
11. [Prüfen](#11-prüfen)
12. [Rückgängig machen](#12-rückgängig-machen)
13. [Häufige Stolpersteine](#13-häufige-stolpersteine)

---

## 1. Woraus ein Abschnitt besteht

Jeder Abschnitt der Startseite ist nach demselben Muster gebaut. Hier der
Abschnitt „Ablauf", auseinandergenommen:

```html
<!-- ── Ablauf ─────────────────────────────────────────── -->   ← Merkzeile
<section class="section" id="approach">                          ← Hülle mit Anker
  <div class="container">                                        ← hält die Breite
    <header class="section__head">                               ← Kopf
      <p class="eyebrow reveal">{{ t('approach.eyebrow') }}</p>   ← kleine Zeile darüber
      <h2 class="section__title reveal" …>{{ t('approach.title') }}</h2>
      <p class="section__lead reveal" …>{{ t('approach.lead') }}</p>
    </header>

    …hier kommt der eigentliche Inhalt…
  </div>
</section>
```

**Vier Dinge kehren immer wieder:**

| Teil | Wofür |
| --- | --- |
| `class="section"` | Abstand nach oben und unten, Fläche aus dem Wechsel |
| `id="approach"` | der **Anker** – darüber springt das Menü hierher |
| `class="container"` | begrenzt die Breite und hält den Rand |
| `class="reveal"` | lässt das Element beim Scrollen sanft einblenden |

**Und zwei Schreibweisen aus der Vorlagensprache:**

* `{{ t('approach.title') }}` holt **einen** Text aus der Sprachdatei.
  Fehlt er, erscheint der deutsche – und wenn es den auch nicht gibt, der
  Schlüssel selbst.
* `{% for … %}` durchläuft eine **Liste** aus der Sprachdatei. Dafür
  gelten strengere Regeln, siehe Abschnitte 8 und 9.

---

## 2. Überblick: vier Handgriffe

| Schritt | Datei | Dauer |
| --- | --- | --- |
| 1. Namen und Platz festlegen | – | 5 Min. |
| 2. Abschnitt schreiben | `templates/index.html` | 15 Min. |
| 3. Texte hinterlegen | `translations/de.json` | je nach Inhalt |
| 4. In das Menü aufnehmen | `templates/partials/header.html`, `footer.html` | 2 Min. |

**Gestaltung kommt darin nicht vor.** Wenn Sie die fertigen Bausteine aus
Abschnitt 7 verwenden, brauchen Sie das Stylesheet nicht anzufassen – der
neue Abschnitt sieht dann aus wie der Rest der Seite. Das ist ausdrücklich
so gemeint.

---

## 3. Schritt 1 – Namen und Platz festlegen

### Der Anker

Suchen Sie ein kurzes englisches Wort in Kleinbuchstaben: `faq`, `prices`,
`directions`, `team`. Es taucht an drei Stellen auf und muss überall
gleich geschrieben sein:

```
id="faq"          in der Vorlage
href="#faq"       im Menü
"faq": { … }      in der Sprachdatei
```

**Es darf ihn noch nicht geben.** Vergeben sind zurzeit: `hero`, `news`,
`concept`, `courses`, `offer`, `approach`, `therapist`, `practice`,
`testimonials`, `contact`, `funding`.

> **Warum englisch?** Nur der Gleichmäßigkeit halber – alle vorhandenen
> Anker sind es. Deutsch funktioniert genauso. Vermeiden Sie nur Umlaute
> und Leerzeichen: Der Anker steht in der Adresszeile.

### Der Platz

Überlegen Sie, **zwischen welche** vorhandenen Abschnitte der neue gehört.
Die Reihenfolge auf der Seite ist die Reihenfolge in der Datei – mehr
steckt nicht dahinter.

Für „Häufige Fragen" bietet sich der Platz **vor dem Kontakt** an: erst
die offenen Fragen ausräumen, dann zum Termin einladen.

> **Um die Farben müssen Sie sich nicht kümmern.** Helle und abgesetzte
> Flächen wechseln sich ab, und welche ein Abschnitt bekommt, ergibt sich
> aus seiner Stellung. Schieben Sie einen dazwischen, rückt alles
> Folgende nach und der Wechsel stimmt weiterhin. Nachgemessen über alle
> zwölf Abschnitte.

---

## 4. Schritt 2 – Den Abschnitt schreiben

Öffnen Sie `templates/index.html` und suchen Sie die Merkzeile des
Abschnitts, **vor** den Ihrer soll:

```html
<!-- ── Kontakt ────────────────────────────────────────────────────── -->
```

**Direkt davor** fügen Sie ein:

```html
<!-- ── Fragen ─────────────────────────────────────────────────────── -->
<section class="section" id="faq">
  <div class="container">
    <header class="section__head">
      <p class="eyebrow reveal">{{ t('faq.eyebrow') }}</p>
      <h2 class="section__title reveal" data-reveal-delay="1">{{ t('faq.title') }}</h2>
      <p class="section__lead reveal" data-reveal-delay="2">{{ t('faq.lead') }}</p>
    </header>

    <div class="features">
      {% for frage in s.faq.questions %}
      <article class="feature reveal" data-reveal-delay="{{ loop.index0 }}">
        <h3 class="feature__title">{{ frage.question }}</h3>
        <p class="feature__text">{{ frage.answer }}</p>
      </article>
      {% endfor %}
    </div>
  </div>
</section>

```

**Zu `data-reveal-delay`:** Die Zahl verzögert das Einblenden um jeweils
90 Millisekunden. So erscheinen Zeile für Zeile nacheinander statt alles
auf einmal. In einer Schleife nimmt man `{{ loop.index0 }}` – das zählt
von 0 hoch, jede Karte kommt also ein Stückchen später.

**Zur Merkzeile:** Sie ist nur ein Kommentar und für den Browser
unsichtbar. Sie hilft beim Suchen – und die Löschanleitung nimmt sie als
Anfangsmarke. Die Striche dürfen beliebig lang sein.

---

## 5. Schritt 3 – Die Texte hinterlegen

Öffnen Sie `translations/de.json`. Fügen Sie einen neuen Block ein – die
Stelle innerhalb der Datei ist gleichgültig, aber neben den verwandten
Blöcken findet man ihn später leichter:

```json
  "faq": {
    "eyebrow": "Fragen",
    "title": "Häufige Fragen",
    "lead": "Was vor dem ersten Termin oft gefragt wird.",
    "questions": [
      {
        "question": "Brauche ich eine ärztliche Verordnung?",
        "answer": "Nein. Sie dürfen auch ohne Verordnung kommen."
      },
      {
        "question": "Was soll ich anziehen?",
        "answer": "Bequeme Kleidung, in der Sie sich gut bewegen können."
      }
    ]
  },
```

**Die Namen müssen zusammenpassen.** Was in der Vorlage steht, muss in
der Sprachdatei existieren:

| In der Vorlage | In der Sprachdatei |
| --- | --- |
| `t('faq.title')` | `"faq"` → `"title"` |
| `s.faq.questions` | `"faq"` → `"questions"` |
| `frage.question` | in jedem Listeneintrag `"question"` |

**Auf die Kommas achten.** Zwischen zwei Einträgen steht ein Komma, nach
dem letzten in einer Klammer keins. Danach prüfen:

```bash
python3 -m json.tool translations/de.json > /dev/null
```

Keine Meldung heißt: Die Datei ist in Ordnung.

---

## 6. Schritt 4 – In das Menü aufnehmen

Ein Abschnitt ohne Menüpunkt ist erreichbar, aber schwer zu finden. Der
Eintrag gehört an **zwei** Stellen, jeweils an die passende Position in
der Liste.

**Kopfbereich** – `templates/partials/header.html`:

```html
        <li><a class="nav__link" href="{{ anchor_base }}#faq">{{ t('nav.faq') }}</a></li>
```

**Fußbereich** – `templates/partials/footer.html`:

```html
        <li><a href="{{ anchor_base }}#faq">{{ t('nav.faq') }}</a></li>
```

Und die Beschriftung in `translations/de.json` unter `nav`:

```json
"nav": {
  "faq": "Fragen"
}
```

> **`anchor_base` nicht weglassen.** Auf der Startseite ist es leer, auf
> Impressum und Datenschutz enthält es den Weg zurück. Ohne diesen
> Zusatz führt der Menüpunkt von den Rechtsseiten aus ins Leere.

### Denken Sie an die Breite

Das Menü klappt erst ab 1200 Pixel Fensterbreite zum Burger zusammen –
darüber muss alles in eine Zeile passen. Nachgemessen bei 1201 Pixeln,
also im engsten Fall, in dem die Zeile noch gilt:

| Kopfbereich | Platz | gebraucht | Rest |
| --- | --- | --- | --- |
| 7 Punkte, nur Themenwahl (heute) | 1180 | 1007 | **173** |
| **8 Punkte**, nur Themenwahl | 1180 | 1078 | **102** |
| **8 Punkte + Sprachumschalter** | 1180 | 1183 | **−3 → Überlauf** |

**Solange es nur Deutsch gibt, ist ein achter Punkt unproblematisch.**
Über hundert Pixel bleiben frei.

**Kommt eine zweite Sprache dazu, wird es zu eng.** Der Umschalter
braucht den Platz, den der achte Punkt belegt. Drei Auswege:

1. Den neuen Eintrag **nur in den Fußbereich** setzen. Sie müssen ihn
   nicht in beide Listen aufnehmen – im Fußbereich ist ohnehin mehr Platz,
   dort stehen heute nur sechs.
2. Einen anderen Menüpunkt streichen. Nicht jeder Abschnitt braucht
   einen – „Bekanntmachungen" und „Förderung" haben auch keinen.
3. Den Umbruchpunkt anheben: in `static/css/style.css` nach `1200px`
   suchen. Dann klappt das Menü früher zusammen und die Zeile wird nie
   zu eng. Das ist eine Änderung an der Gestaltung, keine große –
   prüfen Sie danach die Breiten dazwischen.

> **So messen Sie selbst nach:** Fenster auf 1201 Pixel ziehen und
> schauen, ob rechts neben dem Knopf „Termin vereinbaren" noch Rand
> bleibt. Läuft etwas über den Rand hinaus oder rutscht der Knopf aus dem
> Bild, ist die Zeile zu voll.

---

## 7. Fertige Bausteine zum Kopieren

Für den Inhalt gibt es fünf vorhandene Muster. Sie sind alle gestaltet,
zum Thema passend und in jedem Thema stimmig – Sie brauchen kein CSS zu
schreiben.

### Karten nebeneinander – für Aufzählungen

```html
    <div class="features">
      {% for eintrag in s.faq.questions %}
      <article class="feature reveal" data-reveal-delay="{{ loop.index0 }}">
        <span class="feature__index" aria-hidden="true">{{ '%02d' % loop.index }}</span>
        <h3 class="feature__title">{{ eintrag.title }}</h3>
        <p class="feature__text">{{ eintrag.text }}</p>
      </article>
      {% endfor %}
    </div>
```

Die Zeile mit `feature__index` setzt eine kleine Nummer darüber (01, 02,
…). Wer sie nicht möchte, lässt sie weg.

### Karten mit Verweis – für Angebote

```html
    <div class="cards">
      {% for eintrag in s.faq['items'] %}
      <article class="card reveal" data-reveal-delay="{{ loop.index0 }}">
        <h3 class="card__title">{{ eintrag.title }}</h3>
        <p class="card__text">{{ eintrag.text }}</p>
        <p class="card__meta">{{ eintrag.meta }}</p>
        <a class="card__link" href="#contact">
          {{ t('faq.detail_link') }}
          <span aria-hidden="true">&rarr;</span>
        </a>
      </article>
      {% endfor %}
    </div>
```

### Nummerierte Schritte – für Abläufe

```html
    <ol class="steps">
      {% for schritt in s.faq.steps %}
      <li class="step reveal" data-reveal-delay="{{ loop.index0 }}">
        <span class="step__dot" aria-hidden="true"></span>
        <span class="step__num">{{ loop.index }}</span>
        <h3 class="step__title">{{ schritt.title }}</h3>
        <p class="step__text">{{ schritt.text }}</p>
      </li>
      {% endfor %}
    </ol>
```

### Hinweiskästen mit farbiger Kante

```html
    <div class="notices">
      {% for hinweis in s.faq.notes %}
      <article class="notice reveal" data-reveal-delay="{{ loop.index0 }}">
        <h3 class="notice__title">{{ hinweis.title }}</h3>
        <p class="notice__text">{{ hinweis.text }}</p>
      </article>
      {% endfor %}
    </div>
```

### Beschriftete Werte – für Zahlen

```html
    <dl class="regions">
      {% for wert in s.faq.prices %}
      <div class="region reveal" data-reveal-delay="{{ loop.index0 }}">
        <dt class="region__title">{{ wert.title }}</dt>
        <dd class="region__text">{{ wert.text }}</dd>
      </div>
      {% endfor %}
    </dl>
```

> Die Liste heißt hier bewusst `prices` und nicht `values` – warum, steht
> im nächsten Abschnitt.

### Nur Fließtext

Ganz ohne Liste geht es auch:

```html
    <p class="section__lead">{{ t('faq.body') }}</p>
```

---

## 8. Die Falle mit dem Namen „items"

**Nennen Sie Ihre Liste nicht `items`, wenn Sie sie mit einem Punkt
ansprechen.** Sonst bricht der Build ab mit:

```
TypeError: 'builtin_function_or_method' object is not iterable
```

Der Grund: `s.faq.items` bedeutet für die Vorlagensprache nicht „der
Eintrag `items`", sondern eine eingebaute Funktion, die jeder Datensatz
ohnehin besitzt. Sie wird gefunden, bevor irgendwer in Ihrer Datei
nachsieht.

**Zwei Auswege, beide ausprobiert:**

```jinja
{% for x in s.faq['items'] %}      ← eckige Klammern statt Punkt
{% for x in s.faq.questions %}     ← oder einfach anders benennen
```

Der Bestand nutzt beide Wege: `s.offer['items']` und
`s.testimonials['items']` mit Klammern, `s.approach.steps` und
`s.therapist.facts` mit sprechenden Namen.

**Dieselbe Falle gilt für** `keys`, `values`, `get`, `copy`, `update`,
`pop` – ausprobiert für `items`, `values`, `keys` und `get`, alle vier
brechen mit derselben Meldung ab.

Am einfachsten umgehen Sie sie, indem Sie Ihrer Liste einen Namen geben,
der zum Inhalt passt: `questions`, `prices`, `notes`, `steps`. Diese
Namen sind unverfänglich, und man liest später, worum es geht.

> **Woran man die Falle erkennt:** Die Meldung nennt weder Ihren Block
> noch Ihren Listennamen. Steht dort `builtin_function_or_method`, ist
> es fast immer dieser Fall.

---

## 9. Wenn es mehrere Sprachen gibt

Solange nur Deutsch eingetragen ist, betrifft Sie dieser Abschnitt nicht.

Bei zwei Sprachen gilt ein **Unterschied**, der leicht überrascht:

| In der Vorlage | Fehlt der Block in der zweiten Sprache |
| --- | --- |
| `{{ t('faq.title') }}` | **kein Problem** – der deutsche Text erscheint |
| `{% for x in s.faq.questions %}` | **Build bricht ab** |

Die Meldung nennt den Block:

```
jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'faq'
```

**Also: Enthält Ihr Abschnitt eine Schleife, muss der Block in jede
Sprachdatei.** Notfalls zunächst mit den deutschen Texten – übersetzen
können Sie später.

> **Die eingebaute Prüfung kennt Ihren neuen Block nicht.** `build.py`
> warnt vor fehlenden Blöcken, aber nur vor denen, die es beim Schreiben
> des Programms schon gab. Für einen selbst hinzugefügten Abschnitt
> bleibt es bei der Meldung oben – die immerhin den Namen nennt.
>
> Wer möchte, trägt seinen Anker in `build.py` bei `TEMPLATE_BLOCKS`
> nach; dann erscheint auch für ihn die freundliche Meldung. Nötig ist
> es nicht.

Wie eine zweite Sprache überhaupt hinzukommt, steht in
[README-Sprachen.md](README-Sprachen.md).

---

## 10. Was von selbst funktioniert

Um diese Dinge müssen Sie sich **nicht** kümmern:

| Was | Warum |
| --- | --- |
| **Die Fläche des Abschnitts** | Hell und abgesetzt wechseln sich nach der Stellung ab. Der neue reiht sich ein, die folgenden rücken nach |
| **Der Abstand nach oben und unten** | Steckt in `class="section"` |
| **Die Breite und der Seitenrand** | Steckt in `class="container"` |
| **Das Einblenden beim Scrollen** | `class="reveal"` genügt |
| **Die Hervorhebung im Menü** | Das Skript baut seine Zuordnung aus den vorhandenen Menüpunkten. Ein neuer Punkt mit passendem Anker wird von allein hervorgehoben, sobald man dort ist |
| **Der Sprung unter die Kopfleiste** | Die Seite hält beim Springen von sich aus Abstand, der Titel verschwindet nicht hinter dem Menü |
| **Dunkles Thema und weitere Themen** | Die Bausteine aus Abschnitt 7 fragen alle die Farb-Tokens ab |
| **Sitemap, `llms.txt`, Vorschaubild** | Zählen Seiten, nicht Abschnitte – bleiben unverändert |

**Nicht automatisch** geschieht dagegen: Ein neuer Abschnitt erscheint
**nicht** in den maschinenlesbaren Angaben für Suchmaschinen (JSON-LD).
Für Fließtext und Karten ist das richtig so. Wollen Sie etwas
Maschinenlesbares hinterlegen – etwa Preise oder Fragen als `FAQPage` –,
ist das ein eigenes Vorhaben in `content.py`.

---

## 11. Prüfen

```bash
python3 build.py --serve
```

Dann <http://127.0.0.1:8000/> öffnen.

| Prüfung | Worauf achten |
| --- | --- |
| Der Abschnitt ist da | An der geplanten Stelle, mit Überschrift und Inhalt |
| Der Menüpunkt springt | Anklicken – der Titel steht danach unterhalb der Kopfleiste, nicht darunter versteckt |
| Die Hervorhebung wandert mit | Beim Scrollen wird der zugehörige Menüpunkt betont |
| Die Flächen wechseln sich ab | Von oben nach unten, nirgends zwei gleiche nebeneinander |
| Das Einblenden | Beim Scrollen erscheinen die Karten nacheinander |
| Schmales Fenster | Ziehen Sie das Fenster zusammen: Die Karten müssen untereinander rutschen |
| Dunkles Thema | Rechts oben auf ☾ schalten und noch einmal ansehen |
| Von den Rechtsseiten | Impressum öffnen, dann den neuen Menüpunkt anklicken – er muss zur Startseite und dort zur richtigen Stelle führen |

**Tote Verweise finden:**

```bash
python3 - <<'ENDE'
import re
from pathlib import Path
html = Path("dist/index.html").read_text(encoding="utf-8")
anker = set(re.findall(r'id="([a-z-]+)"', html))
verweise = set(re.findall(r'href="#([a-z-]+)"', html))
print("Verweise ins Leere:", sorted(verweise - anker) or "keine")
ENDE
```

Danach **auf dem Telefon ansehen**: siehe
[README-Android-Test.md](README-Android-Test.md).

---

## 12. Rückgängig machen

Solange nichts eingecheckt ist:

```bash
git diff             # zeigt alle Änderungen
git checkout -- .    # verwirft sie
```

Möchten Sie den Abschnitt behalten, aber vorerst nicht zeigen, setzen Sie
eine Bedingung darum, die nie zutrifft:

```jinja
{% if false %}
<section class="section" id="faq">
  …
</section>
{% endif %}
```

Den Menüpunkt müssen Sie dann trotzdem herausnehmen. Mehr dazu in
[README-Abschnitt-loeschen.md](README-Abschnitt-loeschen.md).

---

## 13. Häufige Stolpersteine

| Symptom | Ursache und Abhilfe |
| --- | --- |
| `TypeError: 'builtin_function_or_method' object is not iterable` | Die Liste heißt `items` und wird mit einem Punkt angesprochen – Abschnitt 8 |
| `UndefinedError: 'dict object' has no attribute 'faq'` | Der Block fehlt in der Sprachdatei; bei zwei Sprachen in einer davon – Abschnitt 9 |
| `json.decoder.JSONDecodeError` | Komma zu viel oder zu wenig in der Sprachdatei – Abschnitt 5 |
| Statt des Textes steht `faq.title` auf der Seite | Der Schlüssel fehlt oder ist anders geschrieben als in der Vorlage |
| Der Abschnitt ist leer | Die Schleife läuft über eine Liste, die es nicht gibt. Namen in Vorlage und Sprachdatei vergleichen |
| Der Menüpunkt tut nichts | `id` und `href="#…"` stimmen nicht überein – auf Schreibweise achten |
| Der Menüpunkt heißt `nav.faq` | Der Eintrag unter `nav` in der Sprachdatei fehlt |
| Von den Rechtsseiten führt der Punkt ins Leere | `{{ anchor_base }}` vor dem `#` vergessen – Abschnitt 6 |
| Die Überschrift verschwindet hinter dem Menü | Sollte nicht vorkommen. Prüfen Sie, ob die `id` wirklich am `<section>` steht und nicht an einem Element darin |
| Der Abschnitt sieht anders aus als der Rest | `class="section"` oder `class="container"` fehlt |
| Nichts blendet ein | `class="reveal"` fehlt. Ohne JavaScript ist alles sofort sichtbar – das ist Absicht |
| Zwei gleiche Flächen nebeneinander | Sollte nicht vorkommen. Meist ist ein `</section>` verrutscht: Steht Ihr Abschnitt versehentlich **innerhalb** eines anderen? |
| Der Build läuft, die Seite zeigt aber den alten Stand | Im Browser mit **Strg + F5** neu laden |

**Wenn gar nichts passt:** `git checkout -- .` setzt alles zurück, und Sie
fangen mit dem Gerüst aus Abschnitt 4 neu an.
