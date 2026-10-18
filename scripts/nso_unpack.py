#!/usr/bin/env python3
"""Decompress a Switch NSO (e.g. exefs/main) into a flat memory image.

Usage: nso_unpack.py main main.bin
Prints the build ID and segment layout. Addresses in the output image match
the module's in-memory offsets, which is what .pchtxt patches use (with
`@flag offset_shift 0x100`).
"""
import struct
import sys

import lz4.block


def unpack(path):
    data = open(path, "rb").read()
    if data[:4] != b"NSO0":
        sys.exit("not an NSO file")
    flags = struct.unpack_from("<I", data, 0xC)[0]
    build_id = data[0x40:0x60].hex().upper()
    comp_sizes = struct.unpack_from("<3I", data, 0x60)
    segs = []
    for i, name in enumerate(("text", "ro", "data")):
        file_off, mem_off, size = struct.unpack_from("<3I", data, 0x10 + i * 0x10)
        raw = data[file_off:file_off + comp_sizes[i]]
        if flags & (1 << i):
            raw = lz4.block.decompress(raw, uncompressed_size=size)
        segs.append((name, mem_off, size, raw))
    bss = struct.unpack_from("<I", data, 0x3C)[0]
    end = max(m + s for _, m, s, _ in segs)
    image = bytearray(end)
    for _, mem_off, size, raw in segs:
        image[mem_off:mem_off + size] = raw
    return build_id, segs, bss, bytes(image)


if __name__ == "__main__":
    build_id, segs, bss, image = unpack(sys.argv[1])
    print("build id:", build_id)
    for name, mem_off, size, _ in segs:
        print(f"{name:5} 0x{mem_off:08X}-0x{mem_off + size:08X} (0x{size:X})")
    print(f"bss   size 0x{bss:X}")
    if len(sys.argv) > 2:
        open(sys.argv[2], "wb").write(image)
