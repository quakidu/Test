#!/bin/sh
# ==========================================================================
# Täglich bauen und hochladen.
#
# Gedacht für den Aufgabenplaner einer Synology-DiskStation, funktioniert
# ebenso mit cron auf einem Linux-Rechner und innerhalb eines Docker-
# Containers.
#
# Warum überhaupt täglich? Abgelaufene Kurstermine und Bekanntmachungen
# verschwinden beim *Bauen*, nicht im Browser des Besuchers. Ohne
# regelmäßigen Lauf steht am 1. September noch die Sommerpause auf der
# Seite.
#
# Vor dem ersten Einsatz die vier Einstellungen unten anpassen. Danach:
#
#   chmod +x tools/deploy-taeglich.sh
#   sh tools/deploy-taeglich.sh          # einmal von Hand ausprobieren
#
# Jede Einstellung lässt sich auch von außen setzen, ohne die Datei zu
# ändern – praktisch im Container:
#
#   PROJEKT=/app PYTHON=python sh tools/deploy-taeglich.sh
#
# Das Skript ist absichtlich in POSIX-sh geschrieben – auf einer
# DiskStation ist bash nicht überall vorhanden.
# ==========================================================================

set -eu

# ── Anpassen ──────────────────────────────────────────────────────────────
# Verzeichnis mit diesem Projekt (dort liegen build.py und deploy.py).
PROJEKT="${PROJEKT:-/volume1/web-praxis/site}"

# Python mit installiertem Jinja2. Einmalig anlegen mit:
#   python3 -m venv /volume1/web-praxis/venv
#   /volume1/web-praxis/venv/bin/pip install jinja2
PYTHON="${PYTHON:-/volume1/web-praxis/venv/bin/python}"

# Datei, die nur das FTP-Passwort enthält – sonst nichts. Rechte
# einschränken:  chmod 600 …/ftp-passwort
PASSWORTDATEI="${PASSWORTDATEI:-/volume1/web-praxis/ftp-passwort}"

# Auf 1 setzen, wenn die Inhalte per Git gepflegt werden und der Rechner
# sich vor dem Bauen den neuesten Stand holen soll.
MIT_GIT="${MIT_GIT:-0}"
# ──────────────────────────────────────────────────────────────────────────

cd "$PROJEKT"

if [ "$MIT_GIT" = "1" ]; then
  # Gehört der Ordner einem anderen Benutzer als dem, der das Skript
  # ausführt, verweigert Git die Arbeit. Im Container ist das der
  # Normalfall, deshalb der Eintrag – er betrifft nur dieses Verzeichnis.
  git config --global --add safe.directory "$PROJEKT" 2>/dev/null || true
  git pull --ff-only
fi

if [ ! -r "$PASSWORTDATEI" ]; then
  echo "Passwortdatei nicht lesbar: $PASSWORTDATEI" >&2
  exit 1
fi

DEPLOY_FTP_PASSWORD="$(cat "$PASSWORTDATEI")"
export DEPLOY_FTP_PASSWORD

# deploy.py baut selbst und überträgt nur, was sich geändert hat. An den
# meisten Tagen ändert sich nichts – dann wird gar keine Verbindung
# aufgebaut und die Ausgabe bleibt eine Zeile.
#
# Weitere Schalter werden durchgereicht, etwa für einen Probelauf:
#   sh tools/deploy-taeglich.sh --dry-run
"$PYTHON" deploy.py "$@"
