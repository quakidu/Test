# Bild für den täglichen Lauf im Container – gedacht für den Container
# Manager einer Synology-DiskStation oder für Docker auf dem eigenen
# Rechner. Es enthält nur, was zum Bauen und Hochladen nötig ist:
#
#   * Python mit Jinja2  – build.py rendert damit die Vorlagen
#   * git                – nur für die Variante „Inhalte per Git pflegen“
#
# Das Projekt selbst steckt nicht im Bild. Es wird beim Start als
# Verzeichnis hineingereicht (-v …:/app), damit Änderungen an den Texten
# sofort wirken, ohne das Bild neu zu bauen.
#
#   docker build -t praxis-deploy .
#   docker run --rm -v /pfad/zum/projekt:/app -v /pfad/zur/passwortdatei:/pw:ro praxis-deploy
#
# Ausführliche Anleitung: Abschnitt „Täglich automatisch veröffentlichen“
# in der README.

FROM python:3.12-slim

RUN pip install --no-cache-dir "jinja2>=3.1" \
 && apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Die Einstellungen des Skripts zeigen standardmäßig auf ein NAS. Im
# Container gelten andere Pfade – sie stehen deshalb hier.
ENV PROJEKT=/app \
    PYTHON=python \
    PASSWORTDATEI=/pw \
    MIT_GIT=0

CMD ["sh", "tools/deploy-taeglich.sh"]
