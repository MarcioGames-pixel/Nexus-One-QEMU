# Technical roadmap

## Known starting point

The target is the HTC/Google Nexus One (codename "passion", board "mahimahi") running Android 2.1-update1 EPE54B. The original kernel expects Qualcomm QSD8K-era hardware and MTD/YAFFS2 partitions.

## Milestones

1. **Repository and repeatable CI** — compile a QEMU ARM system-emulator binary and record which machine models it contains. An initial `nexus-one` machine scaffold has been added to the companion QEMU fork; the current CI build is being validated.
2. **Firmware analysis** — inspect the boot image header and extracted build properties locally. Do not commit proprietary firmware images or private signing material.
3. **Hardware research** — document the CPU, memory map, interrupt controller, timers, display, input, flash/MTD and boot protocol expected by the Nexus One kernel.
4. **Machine-model prototype** — the initial machine registration is only a scaffold. Implement and test missing QSD8x50 devices in QEMU only after their interfaces and register behavior are supported by reliable documentation or source evidence.
5. **Boot experiments** — test the kernel with trace logging and minimal devices; a successful QEMU build is not evidence that Android boots.
6. **Deterministic peripheral tests** — establish test devices and interfaces for virtual network, audio test PCM, camera test frames, and configurable battery before using host resources.
7. **Guest-visible peripherals** — implement and test guest-facing devices and drivers/protocols. Planned modes are documented in [PERIPHERALS.md](PERIPHERALS.md).
8. **Android host bridge** — only after a stable guest interface exists, add opt-in Android audio/camera capture and host network forwarding with runtime permissions and lifecycle cleanup.
9. **Cellular modem/RIL** — investigate the guest radio interface after Android boots; host internet forwarding is not equivalent to emulating 3G, SIM, or cellular signaling.
10. **Android APK** — package a compatible ARM64 emulator core and UI using the Android NDK/SDK, then test on Android. Add the user-provided skin as an asset independently of the hardware model.

## Important current limitations

- The stock QEMU ARM target does not automatically emulate the Nexus One's Qualcomm board.
- A boot image rebuild that preserves the image size is not proof that it boots.
- The CI workflow currently produces a **Linux x86_64 QEMU executable for development/testing**, not an Android APK.
- Wi-Fi, microphone, camera, 3G, battery, and audio are **planned only**; they are not currently implemented or verified.
- No Nexus One board model or successful EPE54B boot is claimed at this stage.
- The firmware is not stored in this repository. Keep firmware files local unless you have permission to redistribute them.
- Host camera and microphone access must be opt-in and permission-gated. Never access the host SIM/radio as though it were a guest modem without a dedicated, reviewed design.

## CI artifact

The "Build QEMU ARM prototype" workflow compiles `qemu-system-arm` from the `MarcioGames-pixel/qemu` fork and publishes an Actions artifact with the machine list. The artifact runs on Linux x86_64; it is not executable directly on the Moto G52.
