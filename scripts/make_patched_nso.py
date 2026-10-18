#!/usr/bin/env python3
"""Build a pre-patched NSO from your own exefs/main and a .pchtxt.

Usage: make_patched_nso.py main patch.pchtxt out_main

Put the output in Eden's load/<title id>/<mod name>/exefs/main. Eden then loads
it through LayeredExeFS like an unmodded file, which avoids PatchNSO. PatchNSO
makes extra copies of Dread's image, which includes a 1.8 GB bss, and that gets
Eden killed for low memory on 8 GB Android devices.

The output is a game file: keep it out of this repo.
"""
import hashlib
import os
import re
import struct
import sys

import lz4.block

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nso_unpack import unpack  # noqa: E402


def read_pchtxt(path):
    """Yield (image offset, bytes) for the @enabled blocks (offset_shift 0x100)."""
    enabled = False
    for line in open(path).read().splitlines():
        line = line.split("//")[0].split("#")[0].strip()
        if line.startswith("@enabled"):
            enabled = True
        elif line.startswith("@stop"):
            enabled = False
        elif enabled and (m := re.fullmatch(r"([0-9A-Fa-f]{8})\s+([0-9A-Fa-f]+)", line)):
            yield int(m[1], 16), bytes.fromhex(m[2])


def main():
    src, pchtxt, out = sys.argv[1:4]
    data = bytearray(open(src, "rb").read())
    build_id, segs, _, _ = unpack(src)
    flags = struct.unpack_from("<I", data, 0xC)[0]

    seg_bytes = [bytearray(raw) for _, _, _, raw in segs]
    for addr, val in read_pchtxt(pchtxt):
        for i, (name, mem_off, size, _) in enumerate(segs):
            if mem_off <= addr and addr + len(val) <= mem_off + size:
                rel = addr - mem_off
                print(f"{addr:08X} ({name}): {seg_bytes[i][rel:rel + len(val)].hex()} -> {val.hex()}")
                seg_bytes[i][rel:rel + len(val)] = val
                break
        else:
            sys.exit(f"{addr:08X} is outside text/ro/data")

    # Keep the header and module name, then re-append the segments in order.
    file_off = struct.unpack_from("<I", data, 0x10)[0]
    body = bytearray(data[:file_off])
    for i, raw in enumerate(seg_bytes):
        stored = lz4.block.compress(bytes(raw), store_size=False) if flags & (1 << i) else bytes(raw)
        struct.pack_into("<I", body, 0x10 + i * 0x10, len(body))
        struct.pack_into("<I", body, 0x60 + i * 4, len(stored))
        body[0xA0 + i * 0x20:0xC0 + i * 0x20] = hashlib.sha256(raw).digest()
        body += stored
    open(out, "wb").write(body)

    # Round trip: the output must unpack to the patched segments.
    out_id, out_segs, _, _ = unpack(out)
    assert out_id == build_id
    assert all(bytes(a) == b[3] for a, b in zip(seg_bytes, out_segs))
    print(f"wrote {out} ({len(body)} bytes), build id {build_id}")


if __name__ == "__main__":
    main()
