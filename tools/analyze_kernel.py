#!/usr/bin/env python3
"""Read-only scan of a Nexus One kernel image for embedded config and driver clues."""

from __future__ import annotations

import argparse
import gzip
import json
import re
import zlib
from pathlib import Path

KEYWORDS = {
    "board_soc": [
        rb"qsd8k", rb"qsd8x50", rb"msm7", rb"mahimahi", rb"qualcomm",
        rb"machine[_ -]?id", rb"board[_ -]?id",
    ],
    "network_wifi": [
        rb"wlan", rb"wifi", rb"wireless", rb"bcm[0-9a-z_ -]{0,16}",
        rb"libertas", rb"ath[0-9a-z_]{0,12}", rb"cfg80211", rb"mac80211",
        rb"rmnet", rb"smc91", rb"lan9118", rb"msm[_ -]?ether",
    ],
    "audio": [
        rb"alsa", rb"snd[_ -]", rb"audio", rb"msm[_ -]?audio",
        rb"adsp", rb"adie", rb"acoustic", rb"codec",
    ],
    "display_input": [
        rb"framebuffer", rb"msm[_ -]?fb", rb"mddi", rb"mdp",
        rb"touchscreen", rb"synaptics", rb"atmel", rb"tsc200",
    ],
    "power_battery": [
        rb"battery", rb"power[_ -]?supply", rb"pmic", rb"charger",
        rb"rpc[_ -]?battery",
    ],
}

PRINTABLE = re.compile(rb"[\x20-\x7e]{5,160}")


def embedded_config(data: bytes) -> tuple[bytes | None, str]:
    start = data.find(b"IKCFG_ST")
    if start < 0:
        return None, "IKCFG_ST marker not found"
    start += len(b"IKCFG_ST")
    end = data.find(b"IKCFG_ED", start)
    if end < 0:
        return None, "IKCFG_ED marker not found"
    blob = data[start:end]
    for wbits in (zlib.MAX_WBITS, -zlib.MAX_WBITS, zlib.MAX_WBITS | 16):
        try:
            return zlib.decompress(blob, wbits), "embedded kernel config recovered"
        except zlib.error:
            continue
    return None, "config markers found but compressed payload could not be decoded"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kernel", type=Path, help="Path to zImage or kernel binary")
    parser.add_argument("--max-hits", type=int, default=30, help="Maximum matching strings per category")
    args = parser.parse_args()

    data = args.kernel.read_bytes()
    strings = [(m.start(), m.group().decode("ascii", "replace")) for m in PRINTABLE.finditer(data)]
    results = {
        "file": str(args.kernel),
        "size_bytes": len(data),
        "format_note": "Read-only printable-string scan; a lack of hits does not prove a driver is absent.",
        "categories": {},
    }
    for category, patterns in KEYWORDS.items():
        matches = []
        for offset, value in strings:
            if any(re.search(pattern, value.encode("ascii", "ignore"), re.I) for pattern in patterns):
                matches.append({"offset_hex": hex(offset), "string": value})
                if len(matches) >= args.max_hits:
                    break
        results["categories"][category] = matches

    config, note = embedded_config(data)
    results["embedded_config"] = {"status": note}
    if config is not None:
        lines = config.decode("utf-8", "replace").splitlines()
        selected = [line for line in lines if any(
            token in line.upper() for token in (
                "CONFIG_WLAN", "CONFIG_WIFI", "CONFIG_CFG80211", "CONFIG_MAC80211",
                "CONFIG_SND", "CONFIG_AUDIO", "CONFIG_MSM", "CONFIG_BATTERY",
                "CONFIG_POWER_SUPPLY", "CONFIG_MTD", "CONFIG_YAFFS",
            )
        )]
        results["embedded_config"]["selected_options"] = selected[:300]
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
