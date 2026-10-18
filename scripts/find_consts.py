#!/usr/bin/env python3
"""Find float constants in a flat NSO image (from nso_unpack.py).

Looks both for raw 32-bit values in the image (literal pools, .rodata) and for
values built in code with a MOVZ/MOVK pair (`mov wN,#lo; movk wN,#hi,lsl#16`).

Usage: find_consts.py main.bin text_end [name=0xHEX ...]
"""
import array
import sys

DEFAULTS = {
    "16/9": 0x3FE38E39,
    "16/9 (alt)": 0x3FE38E38,
    "9/16": 0x3F100000,
    "1280.0": 0x44A00000,
    "720.0": 0x44340000,
    "1920.0": 0x44F00000,
    "1080.0": 0x44870000,
}


def scan(image, text_end, consts):
    words = array.array("I", image[: len(image) // 4 * 4])
    text_words = text_end // 4
    hits = {name: {"raw": [], "movk": []} for name in consts}
    by_value = {v: n for n, v in consts.items()}
    for i, w in enumerate(words):
        if w in by_value:
            hits[by_value[w]]["raw"].append(i * 4)
    # MOVZ (32-bit) then MOVK lsl16 into the same register within a few instrs
    wanted_hi = {v >> 16: v for v in consts.values()}
    for i in range(text_words):
        w = words[i]
        if (w & 0xFFE00000) != 0x72A00000:  # movk wN, #imm, lsl #16
            continue
        hi = (w >> 5) & 0xFFFF
        if hi not in wanted_hi:
            continue
        rd = w & 0x1F
        for j in range(max(0, i - 6), i):
            p = words[j]
            if (p & 0xFFE00000) == 0x52800000 and (p & 0x1F) == rd:
                val = (hi << 16) | ((p >> 5) & 0xFFFF)
                if val in by_value:
                    hits[by_value[val]]["movk"].append(j * 4)
        # value with low half zero is a single MOVZ lsl16, handled below
    for i in range(text_words):
        w = words[i]
        if (w & 0xFFE00000) == 0x52A00000:  # movz wN, #imm, lsl #16
            val = ((w >> 5) & 0xFFFF) << 16
            if val in by_value:
                hits[by_value[val]]["movk"].append(i * 4)
    return hits


if __name__ == "__main__":
    image = open(sys.argv[1], "rb").read()
    text_end = int(sys.argv[2], 0)
    consts = dict(DEFAULTS)
    for arg in sys.argv[3:]:
        n, v = arg.split("=")
        consts[n] = int(v, 0)
    for name, h in scan(image, text_end, consts).items():
        raw_text = [a for a in h["raw"] if a < text_end]
        raw_data = [a for a in h["raw"] if a >= text_end]
        print(f"{name:12} code-built:{len(h['movk']):5}  raw-in-text:{len(raw_text):4}  raw-in-ro/data:{len(raw_data):5}")
        for label, lst in (("code", h["movk"]), ("text", raw_text), ("rodata", raw_data)):
            if lst and len(lst) <= 40:
                print(f"   {label}: " + " ".join(f"{a:08X}" for a in sorted(lst)))
