#!/usr/bin/env python3
"""Inspect a classic Android boot.img header without modifying the image."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

MAGIC = b"ANDROID!"
HEADER_V0_MIN = 608


def inspect_boot(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < HEADER_V0_MIN or data[:8] != MAGIC:
        raise ValueError("Not a supported classic Android boot image (ANDROID! header missing).")

    (
        kernel_size, kernel_addr, ramdisk_size, ramdisk_addr,
        second_size, second_addr, tags_addr, page_size, dt_size, unused,
    ) = struct.unpack_from("<10I", data, 8)

    if page_size == 0 or page_size & (page_size - 1):
        raise ValueError(f"Unexpected page size: {page_size}")

    def page_align(value: int) -> int:
        return (value + page_size - 1) // page_size * page_size

    name = data[48:64].split(b"\0", 1)[0].decode("ascii", errors="replace")
    cmdline = data[64:576].split(b"\0", 1)[0].decode("ascii", errors="replace")
    expected_minimum = page_size + page_align(kernel_size) + page_align(ramdisk_size)
    return {
        "file": str(path),
        "file_size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "format": "classic Android boot image, header v0-style",
        "board_name": name,
        "page_size": page_size,
        "kernel_size": kernel_size,
        "kernel_addr_hex": f"0x{kernel_addr:08x}",
        "ramdisk_size": ramdisk_size,
        "ramdisk_addr_hex": f"0x{ramdisk_addr:08x}",
        "second_size": second_size,
        "second_addr_hex": f"0x{second_addr:08x}",
        "tags_addr_hex": f"0x{tags_addr:08x}",
        "dt_size": dt_size,
        "unused_header_word": unused,
        "cmdline": cmdline,
        "minimum_expected_image_size": expected_minimum,
        "image_size_sufficient_for_declared_sections": len(data) >= expected_minimum,
    }


def read_build_prop(system_dir: Path) -> dict:
    prop = system_dir / "build.prop"
    if not prop.is_file():
        raise FileNotFoundError(f"Could not find {prop}")
    wanted = {
        "ro.product.model", "ro.product.device", "ro.product.board",
        "ro.product.cpu.abi", "ro.build.description", "ro.build.fingerprint",
        "ro.sf.lcd_density", "ro.board.platform",
    }
    result = {}
    for line in prop.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in wanted:
            result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("boot_img", type=Path, help="Path to boot.img")
    parser.add_argument("--system-dir", type=Path, help="Optional extracted system directory containing build.prop")
    args = parser.parse_args()

    report = {"boot_image": inspect_boot(args.boot_img)}
    if args.system_dir:
        report["system_properties"] = read_build_prop(args.system_dir)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
