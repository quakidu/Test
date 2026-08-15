@echo off
rem ==========================================================================
rem  Taeglich bauen und hochladen - fuer die Aufgabenplanung von Windows.
rem
rem  Warum taeglich? Abgelaufene Kurstermine und Bekanntmachungen
rem  verschwinden beim *Bauen*, nicht im Browser des Besuchers. Ohne
rem  regelmaessigen Lauf steht am 1. September noch die Sommerpause auf
rem  der Seite.
rem
rem  Vor dem ersten Einsatz die vier Einstellungen unten anpassen, dann
rem  einmal von Hand ausprobieren (Doppelklick oder in der
rem  Eingabeaufforderung aufrufen).
rem
rem  Diese Datei ist bewusst in ASCII geschrieben: Die Eingabeaufforderung
rem  stellt Umlaute je nach Codepage falsch dar.
rem ==========================================================================

setlocal

rem -- Anpassen ------------------------------------------------------------
rem Ordner mit diesem Projekt (dort liegen build.py und deploy.py).
set "PROJEKT=C:\Praxis\site"

rem Python mit installiertem Jinja2. Einmalig anlegen mit:
rem   py -3 -m venv C:\Praxis\venv
rem   C:\Praxis\venv\Scripts\pip install jinja2
set "PYTHON=C:\Praxis\venv\Scripts\python.exe"

rem Datei, die in der ersten Zeile nur das FTP-Passwort enthaelt.
rem Keine Leerzeichen am Zeilenende - sie zaehlten zum Passwort.
set "PASSWORTDATEI=C:\Praxis\ftp-passwort.txt"

rem Auf 1 setzen, wenn die Inhalte per Git gepflegt werden.
set "MIT_GIT=0"
rem ------------------------------------------------------------------------

cd /d "%PROJEKT%" || exit /b 1

if "%MIT_GIT%"=="1" (
  git pull --ff-only || exit /b 1
)

if not exist "%PASSWORTDATEI%" (
  echo Passwortdatei nicht gefunden: %PASSWORTDATEI% 1>&2
  exit /b 1
)

rem Liest die erste Zeile der Datei in die Umgebungsvariable.
set /p DEPLOY_FTP_PASSWORD=<"%PASSWORTDATEI%"

rem deploy.py baut selbst und uebertraegt nur, was sich geaendert hat. An
rem den meisten Tagen aendert sich nichts - dann wird gar keine Verbindung
rem aufgebaut und die Ausgabe bleibt eine Zeile.
rem Weitere Schalter werden durchgereicht, etwa fuer einen Probelauf:
rem   deploy-taeglich.cmd --dry-run
"%PYTHON%" deploy.py %*
exit /b %ERRORLEVEL%
