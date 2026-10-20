# Technical roadmap

## Known starting point

The target is the HTC/Google Nexus One (codename "passion", board "mahimahi") running Android 2.1-update1 EPE54B. The original kernel expects Qualcomm QSD8K-era hardware and MTD/YAFFS2 partitions.

## Milestones

1. **Repository and repeatable CI** — compile a stock QEMU ARM system-emulator binary and record which machine models it contains.
2. **Firmware analysis** — inspect the boot image header and extracted build properties locally. Do not commit proprietary firmware images or private signing material.
3. **Hardware research** — document the CPU, memory map, interrupt controller, timers, display, input, flash/MTD and boot protocol expected by the Nexus One kernel.
4. **Machine-model prototype** — implement and test missing devices in QEMU only after their interfaces and register behavior are supported by reliable documentation or source evidence.
5. **Boot experiments** — test the kernel with trace logging and minimal devices; a successful QEMU build is not evidence that Android boots.
6. **Android APK** — only after a usable emulator core exists, package the core and a UI using the Android NDK/SDK, then test the APK on ARM64 Android.

## Important current limitations

- The stock QEMU ARM target does not automatically emulate the Nexus One's Qualcomm board.
- A boot image rebuild that preserves the image size is not proof that it boots.
- The CI workflow currently produces a **Linux x86_64 QEMU executable for development/testing**, not an Android APK.
- No Nexus One board model or successful EPE54B boot is claimed at this stage.
- The firmware is not stored in this repository. Keep firmware files local unless you have permission to redistribute them.

## CI artifact

The "Build QEMU ARM prototype" workflow compiles `qemu-system-arm` from the `MarcioGames-pixel/qemu` fork and publishes a short-lived Actions artifact with the machine list. The artifact runs on Linux x86_64; it is not executable directly on the Moto G52.
