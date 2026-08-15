#!/bin/sh
# ==========================================================================
# Täglich bauen und hochladen – gedacht für den Aufgabenplaner einer
# Synology-DiskStation, funktioniert aber ebenso mit cron auf einem Linux-
# Rechner.
#
# Warum überhaupt täglich? Abgelaufene Kurstermine und Bekanntmachungen
# verschwinden beim *Bauen*, nicht im Browser des Besuchers. Ohne
# regelmäßigen Lauf steht am 1. September noch die Sommerpause auf der
# Seite.
#
# Vor dem ersten Einsatz die vier Pfade unten anpassen. Danach:
#
#   chmod +x tools/deploy-taeglich.sh
#   sh tools/deploy-taeglich.sh          # einmal von Hand ausprobieren
#
# Das Skript ist absichtlich in POSIX-sh geschrieben – auf einer
# DiskStation ist bash nicht überall vorhanden.
# ==========================================================================

set -eu

# ── Anpassen ──────────────────────────────────────────────────────────────
# Verzeichnis mit diesem Projekt (dort liegen build.py und deploy.py).
PROJEKT="/volume1/web-praxis/site"

# Python mit installiertem Jinja2. Einmalig anlegen mit:
#   python3 -m venv /volume1/web-praxis/venv
#   /volume1/web-praxis/venv/bin/pip install jinja2
PYTHON="/volume1/web-praxis/venv/bin/python"

# Datei, die nur das FTP-Passwort enthält – sonst nichts, kein Zeilenumbruch
# nötig. Rechte einschränken:  chmod 600 …/ftp-passwort
PASSWORTDATEI="/volume1/web-praxis/ftp-passwort"

# Auf 1 setzen, wenn die Inhalte per Git gepflegt werden und das NAS sich
# vor dem Bauen den neuesten Stand holen soll.
MIT_GIT=0
# ──────────────────────────────────────────────────────────────────────────

cd "$PROJEKT"

if [ "$MIT_GIT" = "1" ]; then
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
"$PYTHON" deploy.py
