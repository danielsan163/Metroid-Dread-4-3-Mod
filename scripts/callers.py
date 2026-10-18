#!/usr/bin/env python3
"""List BL/B call sites targeting an address. Usage: callers.py main.bin text_end TARGET"""
import array
import sys

image = open(sys.argv[1], "rb").read()
text_end = int(sys.argv[2], 0)
target = int(sys.argv[3], 16)
words = array.array("I", image[: text_end // 4 * 4])
for i, w in enumerate(words):
    if (w & 0x7C000000) == 0x14000000:  # b / bl
        imm = w & 0x3FFFFFF
        if imm & (1 << 25):
            imm -= 1 << 26
        if i * 4 + imm * 4 == target:
            print(f"{i * 4:08X} {'bl' if w >> 31 else 'b '}")
