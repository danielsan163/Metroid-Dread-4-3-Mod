#!/usr/bin/env python3
"""Disassemble a range of a flat NSO image. Usage: dis.py main.bin ADDR [before] [after]"""
import sys

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs

image = open(sys.argv[1], "rb").read()
addr = int(sys.argv[2], 16)
before = int(sys.argv[3]) if len(sys.argv) > 3 else 16
after = int(sys.argv[4]) if len(sys.argv) > 4 else 32
start = max(0, addr - before * 4)
md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
for ins in md.disasm(image[start:addr + after * 4], start):
    mark = ">>" if ins.address == addr else "  "
    print(f"{mark}{ins.address:08X}: {ins.mnemonic:8} {ins.op_str}")
