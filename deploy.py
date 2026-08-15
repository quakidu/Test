"""Lädt die gebaute Seite per FTPS auf den Webspace (Alfahosting).

Ablauf: erst ``build.py`` ausführen, dann den Inhalt von ``dist/`` in das
konfigurierte Verzeichnis auf dem Server spiegeln.

    cp deploy.ini.example deploy.ini    # einmalig, dann ausfüllen
    python3 deploy.py --dry-run         # zeigt nur, was passieren würde
    python3 deploy.py                   # lädt hoch

Übertragen wird nur, was sich seit dem letzten Lauf geändert hat. Wie der
zuletzt hochgeladene Stand aussah, merkt sich ``.deploy-state.json`` –
eine Liste von Prüfsummen. Ändert sich nichts, geht das Skript gar nicht
erst online. ``--all`` überträgt wieder alles.

Das Passwort steht bewusst nicht in der Konfiguration. Es kommt aus der
Umgebungsvariable ``DEPLOY_FTP_PASSWORD`` oder wird abgefragt.

Die Verbindung läuft verschlüsselt (FTP über TLS). Nur wenn der Server das
nicht unterstützt, hilft ``--plain-ftp`` – dabei gehen Zugangsdaten
allerdings unverschlüsselt über die Leitung.

Benötigt nur die Standardbibliothek.
"""

from __future__ import annotations

import argparse
import configparser
import ftplib
import hashlib
import json
import os
import ssl
import sys
from getpass import getpass
from pathlib import Path

import build as builder

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
CONFIG_FILE = BASE_DIR / "deploy.ini"
STATE_FILE = BASE_DIR / ".deploy-state.json"
PASSWORD_ENV = "DEPLOY_FTP_PASSWORD"

# Dateien, die nie hochgeladen werden.
SKIP_NAMES = {".DS_Store", "Thumbs.db"}


# --------------------------------------------------------------------------
# Konfiguration
# --------------------------------------------------------------------------
def load_config() -> configparser.ConfigParser:
    if not CONFIG_FILE.exists():
        sys.exit(
            f"{CONFIG_FILE.name} fehlt.\n"
            "Vorlage kopieren und ausfüllen:  cp deploy.ini.example deploy.ini"
        )
    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE, encoding="utf-8")

    for section, key in (("ftp", "host"), ("ftp", "user"), ("site", "url")):
        if not parser.has_option(section, key) or not parser.get(section, key).strip():
            sys.exit(f"In {CONFIG_FILE.name} fehlt der Eintrag [{section}] {key}.")
    return parser


def get_password() -> str:
    password = os.environ.get(PASSWORD_ENV)
    if password:
        return password
    return getpass("FTP-Passwort: ")


# --------------------------------------------------------------------------
# Dateien einsammeln
# --------------------------------------------------------------------------
def local_files() -> list[Path]:
    """Alle Dateien in dist/, relativ zum Wurzelverzeichnis, sortiert."""
    files = [
        path.relative_to(DIST_DIR)
        for path in sorted(DIST_DIR.rglob("*"))
        if path.is_file() and path.name not in SKIP_NAMES
    ]
    # Verzeichnisse zuerst anlegen: nach Tiefe sortieren hält die Ausgabe ruhig.
    return sorted(files, key=lambda p: (len(p.parts), str(p)))


# --------------------------------------------------------------------------
# Was hat sich geändert?
# --------------------------------------------------------------------------
# Der Build erzeugt jedes Mal alle Dateien neu, auch wenn sich nichts
# geändert hat. Statt sie täglich erneut hochzuladen, vergleichen wir
# Prüfsummen mit dem Stand des letzten erfolgreichen Laufs.
#
# Der Stand steht lokal in .deploy-state.json, nicht auf dem Server: Ein
# Webspace beantwortet Fragen nach Prüfsummen nicht, und Zeitstempel über
# FTP sind zu unzuverlässig, um daran eine Entscheidung zu knüpfen.


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_state(host: str, remote_dir: str) -> dict[str, str]:
    """Prüfsummen des letzten Laufs – nur für dasselbe Ziel.

    Zeigt die Konfiguration auf einen anderen Server oder ein anderes
    Verzeichnis, ist der gemerkte Stand wertlos: Dort liegt die Seite noch
    gar nicht. Dann wird alles übertragen.
    """
    if not STATE_FILE.exists():
        return {}
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}  # beschädigt oder unlesbar: lieber alles neu laden
    if data.get("host") != host or data.get("remote_dir") != remote_dir:
        return {}
    files = data.get("files")
    return files if isinstance(files, dict) else {}


def save_state(host: str, remote_dir: str, hashes: dict[str, str]) -> None:
    STATE_FILE.write_text(
        json.dumps(
            {"host": host, "remote_dir": remote_dir, "files": hashes},
            ensure_ascii=False, indent=2, sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


# --------------------------------------------------------------------------
# FTP
# --------------------------------------------------------------------------
def connect(config: configparser.ConfigParser, password: str, plain: bool) -> ftplib.FTP:
    host = config.get("ftp", "host")
    user = config.get("ftp", "user")
    port = config.getint("ftp", "port", fallback=21)

    if plain:
        print("Achtung: unverschlüsselte FTP-Verbindung.")
        session: ftplib.FTP = ftplib.FTP()
        session.connect(host, port, timeout=30)
        session.login(user, password)
    else:
        session = ftplib.FTP_TLS(context=ssl.create_default_context())
        session.connect(host, port, timeout=30)
        session.login(user, password)
        session.prot_p()  # auch die Datenverbindung verschlüsseln

    session.set_pasv(config.getboolean("ftp", "passive", fallback=True))
    return session


def ensure_remote_dir(session: ftplib.FTP, path: str, known: set[str]) -> None:
    """Legt ein Verzeichnis samt Elternverzeichnissen an, falls nötig."""
    if not path or path in known:
        return

    parts = path.strip("/").split("/")
    current = ""
    for part in parts:
        current = f"{current}/{part}" if current else part
        if current in known:
            continue
        try:
            session.mkd(current)
        except ftplib.error_perm as error:
            # 550 heißt hier in aller Regel: gibt es schon.
            if not str(error).startswith("550"):
                raise
        known.add(current)


def remote_listing(session: ftplib.FTP, directory: str = "") -> list[str]:
    """Listet alle Dateien unterhalb von ``directory`` rekursiv auf."""
    found: list[str] = []
    try:
        entries = list(session.mlsd(directory or "."))
    except (ftplib.error_perm, ftplib.error_proto):
        return found  # Server kann MLSD nicht – dann eben kein Aufräumen

    for name, facts in entries:
        if name in (".", ".."):
            continue
        path = f"{directory}/{name}" if directory else name
        if facts.get("type") == "dir":
            found.extend(remote_listing(session, path))
        elif facts.get("type") == "file":
            found.append(path)
    return found


# --------------------------------------------------------------------------
# Ablauf
# --------------------------------------------------------------------------
def upload(session: ftplib.FTP, files: list[Path], dry_run: bool,
           done: set[str] | None = None) -> int:
    """Überträgt die übergebenen Dateien.

    Jede erfolgreich übertragene Datei landet in ``done``. Bricht der Lauf
    in der Mitte ab, ist damit trotzdem festgehalten, was schon oben ist –
    der nächste Lauf macht dort weiter.
    """
    known_dirs: set[str] = set()
    count = 0

    for relative in files:
        remote = relative.as_posix()
        parent = relative.parent.as_posix()
        if parent == ".":
            parent = ""

        if dry_run:
            print(f"  würde laden  {remote}")
            count += 1
            continue

        ensure_remote_dir(session, parent, known_dirs)
        with (DIST_DIR / relative).open("rb") as fh:
            session.storbinary(f"STOR {remote}", fh)
        print(f"  geladen  {remote}")
        if done is not None:
            done.add(remote)
        count += 1

    return count


def remove_stale(session: ftplib.FTP, files: list[Path], dry_run: bool) -> int:
    wanted = {path.as_posix() for path in files}
    stale = [name for name in remote_listing(session) if name not in wanted]

    for name in stale:
        if dry_run:
            print(f"  würde löschen  {name}")
            continue
        try:
            session.delete(name)
            print(f"  gelöscht  {name}")
        except ftplib.error_perm as error:
            print(f"  übersprungen  {name} ({error})")

    return len(stale)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seite auf den Webspace laden.")
    parser.add_argument("--dry-run", action="store_true",
                        help="nichts übertragen, nur anzeigen")
    parser.add_argument("--no-build", action="store_true",
                        help="vorhandenes dist/ verwenden, nicht neu bauen")
    parser.add_argument("--delete", action="store_true",
                        help="Dateien auf dem Server löschen, die es lokal nicht mehr gibt")
    parser.add_argument("--plain-ftp", action="store_true",
                        help="unverschlüsseltes FTP, nur wenn FTPS nicht geht")
    parser.add_argument("--all", action="store_true",
                        help="alle Dateien übertragen, auch unveränderte")
    args = parser.parse_args()

    config = load_config()
    site_url = config.get("site", "url")
    base_path = config.get("site", "base_path", fallback="/")
    remote_dir = config.get("ftp", "remote_dir", fallback="/").strip() or "/"

    if not args.no_build:
        print(f"Baue Startseite für {site_url} …")
        builder.build(site_url, base_path)

    if not DIST_DIR.exists():
        sys.exit("dist/ fehlt – bitte zuerst python3 build.py ausführen.")

    host = config.get("ftp", "host")
    files = local_files()
    hashes = {path.as_posix(): file_hash(DIST_DIR / path) for path in files}

    previous = {} if args.all else load_state(host, remote_dir)
    pending = [path for path in files if hashes[path.as_posix()]
               != previous.get(path.as_posix())]

    print(f"\n{len(files)} Dateien in dist/, davon {len(pending)} geändert")
    print(f"Ziel: {host}:{remote_dir}\n")

    if args.dry_run:
        print("Testlauf – es wird nichts übertragen.\n")
        upload(None, files if args.all else pending, dry_run=True)  # type: ignore[arg-type]
        if args.delete:
            print("\n(Aufräumen lässt sich nur mit Verbindung ermitteln.)")
        return

    # Gibt es nichts zu übertragen und soll auch nicht aufgeräumt werden,
    # ist eine Verbindung überflüssig – dann wird auch kein Passwort
    # gebraucht. Das ist der Normalfall bei einem täglichen Lauf.
    if not pending and not args.delete:
        print("Nichts zu tun – der Server hat bereits diesen Stand.")
        return

    # Was schon oben liegt, bleibt vermerkt, auch wenn der Lauf abbricht.
    uploaded: set[str] = set()
    session = connect(config, get_password(), args.plain_ftp)
    try:
        if remote_dir not in ("", "/"):
            try:
                session.cwd(remote_dir)
            except ftplib.error_perm:
                sys.exit(
                    f"Verzeichnis {remote_dir} nicht gefunden. "
                    "Bitte den Pfad im Kundenmenü von Alfahosting prüfen."
                )

        count = upload(session, pending, dry_run=False, done=uploaded)
        removed = remove_stale(session, files, dry_run=False) if args.delete else 0

        print(f"\nFertig: {count} Dateien übertragen"
              + (f", {removed} entfernt" if args.delete else "")
              + (f", {len(files) - count} unverändert" if count < len(files) else ""))
        print(f"Die Seite ist erreichbar unter {site_url}")
    finally:
        # Nur Dateien vermerken, die es lokal noch gibt – sonst wüchse die
        # Liste mit jeder umbenannten Datei weiter.
        state = {name: value for name, value in previous.items() if name in hashes}
        state.update({name: hashes[name] for name in uploaded})
        save_state(host, remote_dir, state)
        try:
            session.quit()
        except Exception:
            session.close()


if __name__ == "__main__":
    main()
