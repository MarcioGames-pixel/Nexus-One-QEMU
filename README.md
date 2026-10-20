# Nexus One QEMU

Research and development project to investigate emulation of the HTC/Google Nexus One (codename `passion`, board `mahimahi`) and its Android 2.1-update1 EPE54B firmware.

**Status: early research/prototype.** This project does not yet boot the original Nexus One firmware and does not yet produce a working Android APK. Wi-Fi, microphone, camera, 3G, battery, and audio are planned, not implemented.

## Goals

- Analyze a locally extracted Nexus One boot image and `build.prop`.
- Build a reproducible QEMU ARM development binary using GitHub Actions.
- Identify the hardware devices the original kernel expects.
- Prototype missing device models with tests and trace logging.
- Design safe Android host bridges for selected real phone resources.
- Package an Android app only after the emulator core can boot a useful guest.

## Build from GitHub

1. Open the **Actions** tab.
2. Select **Build QEMU ARM prototype**.
3. Press **Run workflow** on the `main` branch.
4. When it completes, open the run and download the `qemu-system-arm-linux-x86_64` artifact.

That artifact is a Linux x86_64 development binary, not an Android APK and not directly runnable on Android.

## Analyze firmware locally

Do not commit proprietary firmware images to this repository. After extracting the firmware on your own device, run:

```sh
python3 tools/analyze_firmware.py /path/to/boot.img --system-dir /path/to/extracted/system
```

The script prints the classic Android boot header fields, SHA-256, and selected properties from `build.prop`. It does not modify firmware.

## Current hardware work

The companion [QEMU fork](https://github.com/MarcioGames-pixel/qemu) has an initial `-M nexus-one` bring-up scaffold. It maps RAM at `0x20000000` and uses legacy machine ID `2304`, but it does **not** yet emulate the Qualcomm QSD8x50 peripherals and cannot be considered bootable.

- [Hardware bring-up plan](docs/NEXUS_ONE_HARDWARE.md)
- [Peripheral support plan](docs/PERIPHERALS.md)
- [Nexus One visual skin specification](docs/SKIN.md)
- [Technical roadmap](docs/ROADMAP.md)

## Planned peripheral modes

- **Wi-Fi/network:** virtual guest network first; optional NAT/host internet sharing later.
- **Microphone and camera:** optional Android host capture only after runtime permission and explicit user action, plus deterministic test sources.
- **3G:** virtual modem/RIL research; sharing host internet alone is not 3G emulation.
- **Battery:** configurable guest-visible virtual battery.
- **Audio:** guest PCM output to Android audio APIs, with optional microphone input.

These are planned modes, not features already working. See [docs/PERIPHERALS.md](docs/PERIPHERALS.md) for dependencies and acceptance tests.
