#!/usr/bin/env python3
"""Apply a .pchtxt to a flat NSO image (from nso_unpack.py) for checking.

Usage: apply_pchtxt.py patch.pchtxt main.bin out.bin
Assumes `offset_shift 0x100`, so patch addresses are image offsets.
"""
import re
import sys

lines = open(sys.argv[1]).read().splitlines()
image = bytearray(open(sys.argv[2], "rb").read())
enabled = False
for line in lines:
    line = line.split("//")[0].strip()
    if line.startswith("@enabled"):
        enabled = True
    elif line.startswith("@stop"):
        enabled = False
    elif enabled and (m := re.fullmatch(r"([0-9A-Fa-f]{8})\s+([0-9A-Fa-f]+)", line)):
        addr, val = int(m[1], 16), bytes.fromhex(m[2])
        print(f"{addr:08X}: {image[addr:addr + len(val)].hex()} -> {val.hex()}")
        image[addr:addr + len(val)] = val
open(sys.argv[3], "wb").write(image)
