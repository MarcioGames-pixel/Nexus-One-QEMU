#!/usr/bin/env python3
"""Read-only search of local Nexus One firmware images for peripheral clues.

This is a heuristic triage tool, not a driver-compatibility proof. It does not
modify firmware, mount filesystems, or upload data.
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
from pathlib import Path

PATTERNS = {
    "wifi_wireless": re.compile(
        r"wlan|wireless|wifi|bcm[0-9a-z_-]{2,20}|broadcom|tiwlan|ath[0-9a-z_-]{1,16}|"
        r"cfg80211|mac80211|firmware.*(wifi|wlan)|/etc/wifi",
        re.I,
    ),
    "network_cellular": re.compile(
        r"rmnet|qmi|radiointerface|rild|ril\.so|libreference-ril|"
        r"ppp[0-9]?|dhcp|netd|gsm\.data|ro\.telephony",
        re.I,
    ),
    "audio": re.compile(
        r"msm.*audio|audio.*msm|alsa|snd[_-]|adsp|adie|acoustic|"
        r"libaudio|audio_policy|audio\.primary|tinyalsa|qsd.*audio",
        re.I,
    ),
    "camera": re.compile(r"camera|libcamera|mm-camera|sensor|vfe|jpeg", re.I),
    "battery_power": re.compile(
        r"battery|power_supply|charger|pmic|rpc.*battery|healthd", re.I
    ),
    "device_init": re.compile(
        r"init\.[a-z0-9_-]+\.rc|service[[:space:]]+ril-daemon|"
        r"service[[:space:]]+.*audio|/dev/(msm|smd|tty|sound|radio)",
        re.I,
    ),
}
PRINTABLE = re.compile(rb"[\x20-\x7e]{6,220}")


def scan(path: Path, limit: int) -> dict:
    raw = path.read_bytes()
    candidates = [(m.start(), m.group().decode("ascii", "replace"))
                  for m in PRINTABLE.finditer(raw)]
    decompressed_note = "raw byte scan"
    if raw.startswith(b"\x1f\x8b"):
        try:
            unpacked = gzip.decompress(raw)
            candidates = [(m.start(), m.group().decode("ascii", "replace"))
                          for m in PRINTABLE.finditer(unpacked)]
            decompressed_note = "gzip decompressed in memory"
        except (OSError, EOFError):
            decompressed_note = "gzip header detected; decompression failed; scanned raw bytes"
    result = {
        "file": str(path),
        "size_bytes": len(raw),
        "scan_mode": decompressed_note,
        "categories": {},
    }
    for category, pattern in PATTERNS.items():
        matches = []
        seen = set()
        for offset, value in candidates:
            if pattern.search(value) and value not in seen:
                matches.append({"offset_hex": hex(offset), "string": value})
                seen.add(value)
                if len(matches) >= limit:
                    break
        result["categories"][category] = matches
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path,
                        help="Local system.img, ramdisk.img, or other firmware image")
    parser.add_argument("--max-hits", type=int, default=40)
    args = parser.parse_args()
    reports = []
    for path in args.images:
        if not path.is_file():
            reports.append({"file": str(path), "error": "file not found"})
            continue
        try:
            reports.append(scan(path, max(1, args.max_hits)))
        except OSError as exc:
            reports.append({"file": str(path), "error": str(exc)})
    print(json.dumps({
        "note": "Heuristic string scan only; hits are clues, not proof of working guest drivers.",
        "reports": reports,
    }, indent=2, ensure_ascii=False))
    return 0 if all("error" not in item for item in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
