#!/usr/bin/env python3
"""Read selected init/config files from a gzip-compressed Android newc ramdisk.

The script reads locally and prints selected text entries; it never extracts
files to disk or modifies the input image.
"""
from __future__ import annotations
import argparse
import gzip
import re
from pathlib import Path

MAGIC = (b"070701", b"070702")
INTEREST = re.compile(
    r"(^|/)(init(\.mahimahi)?\.rc|.*(wpa|wifi|audio|ril|dhcp|bluetooth|hciattach).*\.conf)$",
    re.I,
)
TEXT_HINT = re.compile(
    r"wpa_supplicant|hciattach|bcm4329|eth0|wlan0|dhcpcd|rmnet|qmi|rild|"
    r"msm_pcm|msm_audio|msm_snd|acoustic|firmware|service .*wifi|service .*ril",
    re.I,
)

def align4(n: int) -> int:
    return (n + 3) & ~3

def parse_newc(data: bytes):
    pos = 0
    while pos + 110 <= len(data):
        magic = data[pos:pos + 6]
        if magic not in MAGIC:
            raise ValueError(f"newc archive marker missing at offset 0x{pos:x}")
        header = data[pos + 6:pos + 110]
        try:
            fields = [int(header[i:i + 8], 16) for i in range(0, 104, 8)]
            filesize = fields[6]
            namesize = fields[11]
        except (ValueError, IndexError) as exc:
            raise ValueError(f"invalid newc header at offset 0x{pos:x}") from exc
        pos += 110
        if namesize < 1 or pos + namesize > len(data):
            raise ValueError("invalid name size in newc archive")
        name = data[pos:pos + namesize - 1].decode("utf-8", "replace")
        pos = align4(pos + namesize)
        if name == "TRAILER!!!":
            return
        if pos + filesize > len(data):
            raise ValueError(f"entry data exceeds archive for {name}")
        payload = data[pos:pos + filesize]
        yield name, payload
        pos = align4(pos + filesize)

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ramdisk", type=Path)
    p.add_argument("--max-bytes", type=int, default=24000,
                   help="Maximum bytes printed for each file")
    p.add_argument("--full", action="store_true",
                   help="Print complete selected .rc files instead of matching context")
    args = p.parse_args()
    raw = args.ramdisk.read_bytes()
    if raw.startswith(b"\x1f\x8b"):
        raw = gzip.decompress(raw)
    entries = list(parse_newc(raw))
    selected = [(name, payload) for name, payload in entries
                if INTEREST.search(name) and payload and b"\0" not in payload[:512]]
    print(f"Entries in archive: {len(entries)}")
    print("Selected configuration files:")
    for name, payload in selected:
        print(f"\n===== {name} ({len(payload)} bytes) =====")
        text = payload.decode("utf-8", "replace")
        lines = text.splitlines()
        matching = [i for i, line in enumerate(lines) if TEXT_HINT.search(line)]
        if name.lower().endswith(".rc") and matching and not args.full:
            wanted = set()
            for i in matching:
                wanted.update(range(max(0, i - 2), min(len(lines), i + 3)))
            output = "\n".join(f"{i+1}: {lines[i]}" for i in sorted(wanted))
        else:
            output = text
        print(output[:max(0, args.max_bytes)])
        if len(output.encode("utf-8", "replace")) > args.max_bytes:
            print("[output truncated]")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
