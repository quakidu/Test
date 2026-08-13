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
import sys
from pathlib import Path

from png import read_png, write_png

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

    width, height, channels, rows = read_png(SOURCE)
    if channels != 4:
        sys.exit(f"{SOURCE} braucht einen Alphakanal (RGBA) für die Transparenz.")
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
