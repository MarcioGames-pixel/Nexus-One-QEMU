#!/usr/bin/env bash
# Smoke-test QEMU's reusable network/audio models in a development build.
# This deliberately does NOT claim the Nexus One guest drivers are compatible.
set -euo pipefail

QEMU_BIN="${1:-./qemu-src/build/qemu-system-arm}"

if [[ ! -x "$QEMU_BIN" ]]; then
  echo "Usage: $0 /path/to/qemu-system-arm" >&2
  exit 2
fi

devices="$("$QEMU_BIN" -device help 2>&1 || true)"
for model in lan9118 pl041; do
  if ! grep -Eiq "name \"?$model\"?([,[:space:]]|$)" <<<"$devices"; then
    echo "Required QEMU model not found: $model" >&2
    exit 1
  fi
done

machines="$("$QEMU_BIN" -machine help)"
grep -Eq '^[[:space:]]*nexus-one([[:space:]]|$)' <<<"$machines" || {
  echo "Machine nexus-one is not registered" >&2
  exit 1
}

# The versatilepb reference board wires LAN9118/PL041 with a real IRQ
# controller. This verifies the model CLI and audio backend without claiming
# those board addresses/drivers are valid for Nexus One.
"$QEMU_BIN" -M versatilepb -display none -nodefaults \
  -nic user,model=lan9118 \
  -audiodev none,id=audio0 \
  -device pl041,audiodev=audio0 \
  -S -monitor none -serial none -parallel none \
  -qmp stdio <<'QMP' >/dev/null
{"execute":"qmp_capabilities"}
{"execute":"quit"}
QMP

echo "PASS: nexus-one registered; LAN9118 and PL041 models instantiate on the reference board."
echo "NOTE: This is a model smoke test, not proof of Nexus One Android driver compatibility."
