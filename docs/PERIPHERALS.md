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
