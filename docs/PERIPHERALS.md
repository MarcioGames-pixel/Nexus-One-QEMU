# Peripheral support plan: Nexus One on Android

This document defines the host/guest boundary for Wi-Fi, microphone, camera, cellular data, battery, and audio. It is an implementation plan, not a claim that these devices are already emulated.

## Two different kinds of support

- **Guest emulation**: the virtual Nexus One sees a modeled device and its guest driver can communicate with it. This is required for hardware-specific Android features.
- **Host sharing**: the Android app uses an Android API and exposes a controlled service to the emulator. This can provide real audio/camera/network data, but does not automatically make the guest's original Qualcomm driver work.

The current `nexus-one` machine is only a registration scaffold. These peripherals cannot work until the machine model, guest-facing devices, and Android host bridge are implemented and tested.

## Feature matrix

| Feature | Proposed initial mode | Guest-facing work still required | Android permission / limitation |
|---|---|---|---|
| Wi-Fi | Virtual Ethernet backed by a user-mode network/NAT service; optional host internet sharing | Emulated network adapter, link state, DHCP/DNS and a guest-compatible driver; original Qualcomm Wi-Fi chipset is not yet modeled | Use Android's normal network access; no need to toggle or control the host's Wi-Fi radio |
| Microphone | Optional live input from Android's `AudioRecord`, with a synthetic silence/test source for tests | Route captured PCM into an emulated audio input endpoint understood by the guest | Request `RECORD_AUDIO` at runtime; only capture while the user enables it |
| Camera | Camera2/CameraX host capture, plus a virtual test pattern fallback | Expose frames through a guest camera device/protocol that the guest camera HAL can use; this is not implemented | Request `CAMERA`; start only after explicit user action and show clear capture state |
| 3G / mobile data | Virtual cellular status/modem for tests; network access can optionally use the host's existing internet connection | A modem/RIL interface and guest-compatible radio implementation are required for cellular bars, SIM state, SMS and mobile-data behavior. NAT alone is not a 3G modem | Do not manipulate the host SIM or mobile radio. Android may restrict tethering/radio details |
| Battery | Configurable virtual battery (level, charging/discharging, temperature) | Emulate the guest-visible battery/power-supply interface and notify the guest of changes | Reading host battery level is optional; virtual battery should remain independent by default |
| Audio output | Guest PCM output mixed by Android audio APIs | Emulated audio device and guest driver/route; choose a simple documented guest audio interface before implementing | Use normal Android audio output; respect mute/volume and audio focus |
| Audio input | Android microphone or generated PCM test source | Same guest audio input path as microphone above | Microphone permission, explicit opt-in, no background recording |

## Implementation order

1. Keep the QEMU machine registration and smoke test passing.
2. Add a host-neutral peripheral interface and deterministic test devices (fake battery, test audio samples, camera color bars, network loopback).
3. Implement an initial guest-visible network device and validate packet exchange before internet/NAT sharing.
4. Implement guest-visible audio output, then optional microphone capture.
5. Implement camera frame transport and permission/lifecycle handling.
6. Add battery notifications and configurable charging state.
7. Research and implement a minimal modem/RIL path only after the Android guest can boot and its radio stack can be observed.
8. Build/package the Android ARM64 app and verify permissions and resource cleanup on a real device.

## Acceptance tests

- Each peripheral can be disabled and the guest remains stable.
- Network loopback works before NAT/internet forwarding is enabled.
- Microphone and camera remain off until enabled, and stop immediately when disabled or permission is revoked.
- Audio uses a test source in automated builds; no physical microphone/camera is accessed in CI.
- Virtual battery values are deterministic in tests and never silently track the host.
- A feature is marked supported only after a guest-side test demonstrates it. A successful QEMU compilation alone is insufficient.

## Security and compatibility

The Android app must request only permissions it uses, explain why they are needed, handle denial/revocation, and avoid recording or transmitting camera/microphone data without an explicit user action. Do not promise original Nexus One 3G/Wi-Fi driver compatibility until the relevant QSD8x50-era hardware and Android 2.1 interfaces have been reproduced.


## Current first-stage work (network and audio)

The CI now runs `tools/check_network_audio_models.sh` against the compiled development binary. It checks that QEMU exposes the reusable LAN9118 Ethernet model and PL041 audio model, verifies that `nexus-one` is registered, and starts the models on QEMU's `versatilepb` reference board, whose IRQ wiring is already implemented.

**Scope boundary:** this is a model/CLI smoke test, not yet a working Nexus One guest network or sound path. The Nexus One machine does not yet have a modeled interrupt controller, a proven guest-compatible NIC/audio register map, or an Android host bridge. The test intentionally uses `versatilepb` for model instantiation instead of attaching devices at invented Nexus One addresses. The next implementation step is to establish the guest-visible interrupt/device wiring and test it with a guest kernel before calling either feature supported.

## Firmware evidence from local EPE54B scan (2026-10-20)

A read-only printable-string scan of the user's local `system.img` and gzip ramdisk produced the following leads. These are observations from strings, not proof that the guest can boot or that the listed hardware has been emulated.

- The ramdisk contains an `hciattach`-style command with `--patchram /etc/firmware/bcm4329.hcd /dev/ttyHS0`. Treat this first as evidence for a firmware-loaded UART HCI device (likely Bluetooth), **not** as proof that `bcm4329.hcd` is the Wi-Fi firmware. The BCM4329 is a combo-chip family, so Wi-Fi and Bluetooth paths must be distinguished.
- The ramdisk contains a `wpa_supplicant` command using `-Dwext` and `-ieth0`, along with `dhcpcd -ABKL eth0` and Wi-Fi DHCP properties. The interface name and exact startup ordering should be confirmed from the complete `init.mahimahi.rc` and any Wi-Fi config files before choosing a virtual NIC or Android bridge.
- The ramdisk and system image reference Qualcomm-style audio endpoints including `/dev/msm_pcm_out`, `/dev/msm_pcm_in`, `/dev/msm_pcm_ctl`, `/dev/msm_audio_ctl`, `/dev/msm_snd`, `/dev/adsp/`, and `/dev/htc-acoustic`. This points to a Qualcomm MSM audio driver/HAL contract, not automatically to ARM PrimeCell PL041.
- The ramdisk includes `/dev/msm_camera/`, `/dev/pmem_camera`, and camera service strings, suggesting a legacy MSM camera HAL path that would need its expected kernel driver and memory interfaces.
- The ramdisk mentions `/dev/qmi*`, `net.rmnet0`, `rild`, and a property `ro.radio.use-ppp no`. These are cellular/RIL clues; forwarding the host's internet is still not equivalent to emulating the radio protocol.
- The ramdisk contains fake battery properties, while system strings mention `/sys/class/power_supply`. These alone do not identify the precise guest-visible battery driver contract.

### Next evidence to collect

Inspect the full `init.mahimahi.rc`, relevant `init.rc` service definitions, Wi-Fi configuration files, and audio HAL library names from the local firmware. Keep proprietary images local. Do not add a guest NIC/audio device at speculative addresses until the machine's interrupt controller, memory map, and guest driver interface have been established.
