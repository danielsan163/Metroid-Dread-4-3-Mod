#!/usr/bin/env python3
"""Convert a .pchtxt into an IPS file for Atmosphère / Eden / yuzu forks.

Usage: pchtxt_to_ips.py patch.pchtxt OUT_DIR
Writes OUT_DIR/<build id>.ips (trailing zeros of the build ID trimmed).
Uses classic IPS, or IPS32 if any offset needs more than 24 bits.
"""
import os
import re
import struct
import sys

text = open(sys.argv[1]).read()
build_id = re.search(r"@nsobid-([0-9A-Fa-f]+)", text)[1].upper().rstrip("0")
shift = int((re.search(r"@flag\s+offset_shift\s+(0x[0-9A-Fa-f]+|\d+)", text) or [0, "0"])[1], 0)

records = []
enabled = False
for line in text.splitlines():
    line = line.split("//")[0].strip()
    if line.startswith("@enabled"):
        enabled = True
    elif line.startswith("@stop"):
        enabled = False
    elif enabled and (m := re.fullmatch(r"([0-9A-Fa-f]{8})\s+([0-9A-Fa-f]+)", line)):
        records.append((int(m[1], 16) + shift, bytes.fromhex(m[2])))

ips32 = any(off + len(val) > 0xFFFFFF for off, val in records)
out = bytearray(b"IPS32" if ips32 else b"PATCH")
for off, val in records:
    out += off.to_bytes(4 if ips32 else 3, "big") + struct.pack(">H", len(val)) + val
out += b"EEOF" if ips32 else b"EOF"

path = os.path.join(sys.argv[2], build_id + ".ips")
open(path, "wb").write(out)
print(path, f"({'IPS32' if ips32 else 'IPS'}, {len(records)} records)")
