#!/usr/bin/env bash
# Smoke-test the reusable network/audio models on QEMU's reference board.
# This is not a claim that Nexus One guest drivers are compatible.
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

# RealView PB-A8 already wires its LAN9118 and PL041 devices to a functioning
# interrupt controller. Use it to test device creation; do not attach devices
# at speculative Nexus One addresses or pretend these are its original chips.
"$QEMU_BIN" -M realview-pb-a8,audiodev=audio0 \
  -display none -nodefaults \
  -nic user,model=lan9118 \
  -audiodev none,id=audio0 \
  -S -monitor none -serial none -parallel none \
  -qmp stdio <<'QMP' >/dev/null
{"execute":"qmp_capabilities"}
{"execute":"quit"}
QMP

echo "PASS: nexus-one is registered; LAN9118 and PL041 models instantiate on RealView PB-A8."
echo "LIMIT: this validates reusable QEMU models only, not Nexus One Android networking/audio."
