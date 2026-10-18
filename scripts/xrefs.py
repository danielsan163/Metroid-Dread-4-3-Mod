#!/usr/bin/env python3
"""Find code references (ADRP + ADD/LDR/STR) to an address in a flat NSO image.

Usage: xrefs.py main.bin text_end TARGET
"""
import array
import sys


def adrp_target(w, pc):
    immlo = (w >> 29) & 3
    immhi = (w >> 5) & 0x7FFFF
    imm = (immhi << 2) | immlo
    if imm & (1 << 20):
        imm -= 1 << 21
    return (pc & ~0xFFF) + (imm << 12)


def lo12_use(w, rn):
    """Return the low-12 offset if w is ADD imm / LDR / STR (unsigned offset) on rn."""
    if ((w >> 5) & 0x1F) != rn:
        return None
    if (w & 0x7F800000) == 0x11000000:  # add (imm), 32/64-bit, no shift
        return (w >> 10) & 0xFFF
    if (w & 0x3B000000) == 0x39000000:  # ldr/str (imm, unsigned offset), int+fp
        size = (w >> 30) & 3
        opc = (w >> 22) & 3
        v = (w >> 26) & 1
        scale = 4 if (v and size == 0 and opc & 2) else size
        return ((w >> 10) & 0xFFF) << scale
    return None


if __name__ == "__main__":
    image = open(sys.argv[1], "rb").read()
    text_end = int(sys.argv[2], 0)
    target = int(sys.argv[3], 16)
    words = array.array("I", image[: text_end // 4 * 4])
    for i, w in enumerate(words):
        if (w & 0x9F000000) != 0x90000000:  # adrp
            continue
        pc = i * 4
        if adrp_target(w, pc) != target & ~0xFFF:
            continue
        rd = w & 0x1F
        for j in range(i + 1, min(i + 24, len(words))):
            off = lo12_use(words[j], rd)
            if off is not None and off == target & 0xFFF:
                print(f"{pc:08X} adrp -> use at {j * 4:08X}")
                break
