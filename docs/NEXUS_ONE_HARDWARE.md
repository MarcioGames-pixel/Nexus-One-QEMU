# Nexus One hardware bring-up

## Target identity

- Product: HTC/Google Nexus One
- Board codename: `mahimahi` / `passion`
- SoC family: Qualcomm QSD8x50 (QSD8K / Scorpion-era)
- Firmware target: Android 2.1-update1 EPE54B
- Physical RAM base used by the legacy board support: `0x20000000`
- Legacy ARM machine ID: `2304` (`MACH_MAHIMAHI`)
- Display target for the Android guest: portrait, 480 x 800 logical pixels

The board identity, memory base and machine ID are grounded in historical Linux ARM/MSM board support. See the linked source material in the project README and the legacy kernel references.

## Implemented first milestone

The QEMU fork now contains an initial `nexus-one` machine registration in:

- `hw/arm/nexus-one.c`
- `hw/arm/Kconfig`
- `hw/arm/meson.build`

The current scaffold sets up one Cortex-A8 CPU, maps RAM beginning at `0x20000000`, and uses QEMU's ARM Linux kernel loader with machine ID 2304.

**This is not full Nexus One hardware support.** The CPU model is a starting approximation for the ARMv7/Scorpion generation; it is not a cycle-accurate Scorpion implementation. The machine currently does not model the QSD8x50 interrupt controller, timers, UART, clocks, GPIO, NAND controller, flash partitions, display controller, touchscreen, USB, audio, Wi-Fi, Bluetooth, sensors, or modem.

The original EPE54B kernel is therefore expected to stop early or fail until the required hardware and boot handoff are implemented. Do not treat the presence of `-M nexus-one` as proof that Android boots.

## Implementation order

1. **Build and machine registration** — ensure the QEMU ARM build includes `nexus-one` and reports it in `-machine help`.
2. **Boot trace / debug console** — determine the exact QSD8x50 UART base, register semantics and IRQ routing from kernel source or hardware documentation before implementing a model.
3. **Interrupt controller and timer** — implement the MSM VIC/SIRC and required timer blocks with correct MMIO registers and interrupt behavior.
4. **Clock/reset and GPIO** — add only register behavior evidenced by the target kernel and source.
5. **NAND/MTD** — emulate the flash controller/partition interface expected by the legacy kernel. YAFFS2 image bytes alone do not emulate the controller.
6. **Display and input** — implement the Nexus One display path and touchscreen/input path; then connect guest framebuffer output to the Android front end.
7. **Remaining devices** — MMC/SD, USB, audio, sensors, Wi-Fi/Bluetooth and modem are separate milestones.
8. **Boot validation** — capture serial logs and demonstrate kernel progress before claiming Android boot support.

## Useful references

- [Historical Nexus One / mahimahi kernel support patch](https://lkml.iu.edu/1101.2/01838.html)
- [QEMU device emulation documentation](https://www.qemu.org/docs/master/system/device-emulation.html)
- [Android kernel machine-type table containing MACH_MAHIMAHI 2304](https://android.googlesource.com/kernel/mediatek/+/3be93a68c209393cfe24a842e2d5896a17ea37dc/arch/arm/tools/mach-types)

## Firmware handling

Keep personal firmware images local. Do not commit `boot.img`, `system.img`, private keys, or extracted proprietary APKs to the repository unless redistribution rights are clear.
