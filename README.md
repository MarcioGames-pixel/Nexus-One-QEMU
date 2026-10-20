# Nexus One QEMU

Research and development project to investigate emulation of the HTC/Google Nexus One (codename `passion`, board `mahimahi`) and its Android 2.1-update1 EPE54B firmware.

**Status: early research/prototype.** This project does not yet boot the original Nexus One firmware and does not yet produce a working Android APK.

## Goals

- Analyze a locally extracted Nexus One boot image and `build.prop`.
- Build a reproducible QEMU ARM development binary using GitHub Actions.
- Identify the hardware devices the original kernel expects.
- Prototype missing device models with tests and trace logging.
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

## Documentation

See [docs/ROADMAP.md](docs/ROADMAP.md) for the milestones and known limitations.
