# Nexus One visual skin

The Android front end should resemble the real HTC/Google Nexus One shown by the user's Wikimedia Commons reference:

- Reference image: https://thumb.wikimedia.org/wikipedia/commons/thumb/2/22/Nexus_One.png/250px-Nexus_One.png
- Image source page: https://commons.wikimedia.org/wiki/File:Nexus_One.png
- Guest display: portrait 480 x 800 pixels, density target 240 dpi (from the EPE54B system properties).
- The bezel and trackball/buttons belong to the device skin; the emulated guest framebuffer must be rendered only inside the physical screen area.
- Touches inside the screen should be mapped from displayed coordinates to the 480 x 800 guest coordinate space. Hardware buttons/trackball should map to Android key events.
- The device frame must scale proportionally and remain centered; never stretch the phone image to fill the whole app window.

## Asset/licensing note

Before bundling the image into an APK, verify the current Wikimedia Commons file page for the original image's license and attribution requirements. Prefer the full-resolution original over the 250 px thumbnail. The reference link is for visual guidance; the emulator should not depend on a remote image being available at runtime.

## Current status

This document is a visual specification only. The emulator APK and its display/input bridge have not been implemented yet. The first milestone remains the QEMU hardware scaffold and a successful build.
