"""PNG lesen und schreiben – nur mit der Standardbibliothek.

Gemeinsame Grundlage von ``prepare-logo.py`` (Logo-Varianten) und
``make-og-image.py`` (Vorschaubild). Unterstützt werden 8 Bit je Kanal mit
Farbtyp 2 (RGB) und 6 (RGBA); mehr braucht die Seite nicht, und alles
Weitere würde nur unbemerkt falsche Ergebnisse liefern.

Ein Bild ist hier eine Liste von Zeilen (``bytearray``) mit ``channels``
Bytes je Pixel.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

# Farbtyp aus dem PNG-Kopf → Anzahl der Kanäle je Pixel.
CHANNELS = {2: 3, 6: 4}


def unfilter(raw: bytes, width: int, height: int, channels: int) -> list[bytearray]:
    """Macht die zeilenweisen PNG-Filter rückgängig."""
    stride = width * channels
    previous = bytearray(stride)
    rows: list[bytearray] = []
    pos = 0

    for _ in range(height):
        filter_type = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride

        for x in range(stride):
            left = line[x - channels] if x >= channels else 0
            up = previous[x]
            up_left = previous[x - channels] if x >= channels else 0

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


def read_png(path: Path) -> tuple[int, int, int, list[bytearray]]:
    """Liest ein PNG und gibt Breite, Höhe, Kanalzahl und die Zeilen zurück."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} ist keine PNG-Datei")

    width, height, depth, color_type = struct.unpack(">IIBB", data[16:26])
    if depth != 8 or color_type not in CHANNELS:
        raise ValueError(
            f"{path}: erwartet werden 8 Bit RGB oder RGBA (Farbtyp 2 oder 6), "
            f"gefunden Bittiefe {depth}, Farbtyp {color_type}"
        )
    channels = CHANNELS[color_type]

    compressed = b""
    offset = 8
    while offset < len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        if chunk_type == b"IDAT":
            compressed += data[offset + 8:offset + 8 + length]
        offset += 12 + length

    raw = zlib.decompress(compressed)
    return width, height, channels, unfilter(raw, width, height, channels)


def write_png(path: Path, rows: list[bytearray], channels: int = 4) -> None:
    """Schreibt Bildzeilen als PNG (Filtertyp 0)."""
    color_type = next(key for key, value in CHANNELS.items() if value == channels)
    raw = b"".join(b"\x00" + bytes(row) for row in rows)
    width = len(rows[0]) // channels
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
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def crop(rows: list[bytearray], width: int, height: int, channels: int) -> list[bytearray]:
    """Schneidet oben links einen Ausschnitt der gewünschten Größe heraus."""
    if len(rows) < height or len(rows[0]) < width * channels:
        raise ValueError("Das Bild ist kleiner als der gewünschte Ausschnitt")
    return [bytearray(row[:width * channels]) for row in rows[:height]]
