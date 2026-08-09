"""Leitet die Logo-Varianten der Seite aus dem Original ab.

Quelle ist ``static/img/logo.png`` – das gelieferte Logo mit transparentem
Hintergrund. Daraus entstehen:

    static/img/logo-dark.png       aufgehellte Fassung für das dunkle Farbschema
    static/img/logo-mark.png       quadratisch beschnittenes Signet (Favicon)
    static/img/logo-mark-dark.png  Signet für das dunkle Farbschema

Für die dunkle Fassung wird je Pixel nur die Helligkeit gespiegelt, Farbton
und Sättigung bleiben erhalten. Der dunkle Schriftzug wird dadurch hell,
das Stahlblau der Unterzeile bleibt als Blau erkennbar.

Das Skript nutzt ausschließlich die Standardbibliothek:

    python3 tools/prepare-logo.py

Nach dem Austausch von ``static/img/logo.png`` einmal ausführen.
"""

from __future__ import annotations

import colorsys
import struct
import sys
import zlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = BASE_DIR / "static" / "img"
SOURCE = IMG_DIR / "logo.png"

# Ab diesem Alphawert gilt ein Pixel als sichtbar (für Zuschnitt und Lücke).
VISIBLE = 20
# Mindestbreite einer Lücke, die Signet und Schriftzug trennt.
GAP = 4
# Freiraum um das Signet im quadratischen Ausschnitt, in Pixeln.
MARK_PADDING = 1


# ---------------------------------------------------------------------------
# PNG lesen und schreiben
# ---------------------------------------------------------------------------
def read_png(path: Path) -> tuple[int, int, list[bytearray]]:
    """Liest ein PNG und gibt Breite, Höhe und die RGBA-Zeilen zurück."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} ist keine PNG-Datei")

    width, height, depth, color_type = struct.unpack(">IIBB", data[16:26])
    if depth != 8 or color_type != 6:
        raise ValueError(
            f"{path}: erwartet werden 8 Bit RGBA (Farbtyp 6), gefunden "
            f"Bittiefe {depth}, Farbtyp {color_type}"
        )

    compressed = b""
    offset = 8
    while offset < len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        if chunk_type == b"IDAT":
            compressed += data[offset + 8:offset + 8 + length]
        offset += 12 + length

    raw = zlib.decompress(compressed)
    return width, height, unfilter(raw, width, height)


def unfilter(raw: bytes, width: int, height: int) -> list[bytearray]:
    """Macht die zeilenweisen PNG-Filter rückgängig."""
    bpp = 4
    stride = width * bpp
    previous = bytearray(stride)
    rows: list[bytearray] = []
    pos = 0

    for _ in range(height):
        filter_type = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride

        for x in range(stride):
            left = line[x - bpp] if x >= bpp else 0
            up = previous[x]
            up_left = previous[x - bpp] if x >= bpp else 0

            if filter_type == 1:
                line[x] = (line[x] + left) & 0xFF
            elif filter_type == 2:
                line[x] = (line[x] + up) & 0xFF
            elif filter_type == 3:
                line[x] = (line[x] + ((left + up) >> 1)) & 0xFF
            elif filter_type == 4:
                predictor = left + up - up_left
                d_left = abs(predictor - left)
                d_up = abs(predictor - up)
                d_up_left = abs(predictor - up_left)
                if d_left <= d_up and d_left <= d_up_left:
                    line[x] = (line[x] + left) & 0xFF
                elif d_up <= d_up_left:
                    line[x] = (line[x] + up) & 0xFF
                else:
                    line[x] = (line[x] + up_left) & 0xFF
            elif filter_type != 0:
                raise ValueError(f"unbekannter PNG-Filter: {filter_type}")

        rows.append(line)
        previous = line

    return rows


def write_png(path: Path, rows: list[bytearray]) -> None:
    """Schreibt RGBA-Zeilen als PNG (Filtertyp 0)."""
    raw = b"".join(b"\x00" + bytes(row) for row in rows)
    width = len(rows[0]) // 4
    height = len(rows)

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------------------
# Bildoperationen
# ---------------------------------------------------------------------------
def lighten(rows: list[bytearray]) -> list[bytearray]:
    """Spiegelt die Helligkeit jedes Pixels, Farbton und Sättigung bleiben."""
    cache: dict[tuple[int, int, int], tuple[int, int, int]] = {}
    result = []

    for row in rows:
        line = bytearray(row)
        for x in range(0, len(line), 4):
            if line[x + 3] == 0:
                continue
            key = (line[x], line[x + 1], line[x + 2])
            if key not in cache:
                hue, lightness, saturation = colorsys.rgb_to_hls(
                    key[0] / 255, key[1] / 255, key[2] / 255
                )
                red, green, blue = colorsys.hls_to_rgb(hue, 1.0 - lightness, saturation)
                cache[key] = (round(red * 255), round(green * 255), round(blue * 255))
            line[x], line[x + 1], line[x + 2] = cache[key]
        result.append(line)

    return result


def signet_bounds(rows: list[bytearray], width: int) -> tuple[int, int, int, int]:
    """Findet den Kasten um das Signet – alles links der ersten breiten Lücke."""
    visible_columns = [
        any(row[x * 4 + 3] > VISIBLE for row in rows) for x in range(width)
    ]

    try:
        start = visible_columns.index(True)
    except ValueError as error:
        raise ValueError("Das Logo enthält keine sichtbaren Pixel") from error

    end = width
    run = 0
    for x in range(start, width):
        if visible_columns[x]:
            run = 0
            continue
        run += 1
        if run >= GAP:
            end = x - run + 1
            break

    rows_visible = [
        y for y, row in enumerate(rows)
        if any(row[x * 4 + 3] > VISIBLE for x in range(start, end))
    ]
    return start, end, rows_visible[0], rows_visible[-1] + 1


def crop_square(rows: list[bytearray], box: tuple[int, int, int, int]) -> list[bytearray]:
    """Schneidet den Kasten aus und zentriert ihn auf quadratischer Fläche."""
    left, right, top, bottom = box
    size = max(right - left, bottom - top) + 2 * MARK_PADDING
    offset_x = (size - (right - left)) // 2
    offset_y = (size - (bottom - top)) // 2

    square = [bytearray(size * 4) for _ in range(size)]
    for y in range(top, bottom):
        target = square[y - top + offset_y]
        source = rows[y]
        start = (offset_x) * 4
        target[start:start + (right - left) * 4] = source[left * 4:right * 4]

    return square


def main() -> None:
    if not SOURCE.exists():
        sys.exit(f"Quelle fehlt: {SOURCE}")

    width, height, rows = read_png(SOURCE)
    print(f"Quelle: {SOURCE.relative_to(BASE_DIR)} ({width}x{height})")

    write_png(IMG_DIR / "logo-dark.png", lighten(rows))
    print("  ✓ static/img/logo-dark.png")

    box = signet_bounds(rows, width)
    mark = crop_square(rows, box)
    write_png(IMG_DIR / "logo-mark.png", mark)
    print(f"  ✓ static/img/logo-mark.png ({len(mark)}x{len(mark)})")

    write_png(IMG_DIR / "logo-mark-dark.png", lighten(mark))
    print("  ✓ static/img/logo-mark-dark.png")


if __name__ == "__main__":
    main()
