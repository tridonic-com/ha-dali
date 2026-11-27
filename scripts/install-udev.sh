#!/usr/bin/env bash
#
# install-udev.sh — grant Home Assistant access to the Tridonic/Lunatone
# DALI-USB (HID) interface.
#
# The HID DALI-USB (USB 17B5:0020) is exposed by Linux as a root-only
# /dev/hidraw* node, so Home Assistant cannot open it out of the box. This
# installs a udev rule that makes the device readable by the "dialout" group
# and creates a stable /dev/dali/daliusb-<serial> symlink.
#
# Only needed for the HID interface. The serial DALI2-USB (17B5:0201) appears
# as /dev/ttyACM* and needs no rule.
#
# Run on the host that the dongle is plugged into:
#   sudo ./install-udev.sh
#
# Supported: Home Assistant Core/venv, Container, and Supervised installs on a
# normal Linux host (including WSL2). For a Container install, run this on the
# host, then pass the device into the container (--device=/dev/dali/daliusb-...).
# Home Assistant OS is out of scope: you cannot add a host udev rule there, so
# the HID interface is unsupported; use the serial DALI2-USB interface instead.

set -euo pipefail

VENDOR_ID="17b5"
PRODUCT_ID="0020"
RULE_PATH="/etc/udev/rules.d/50-dali-hid.rules"
GROUP="dialout"

if [[ "${EUID}" -ne 0 ]]; then
  echo "This script needs root to write ${RULE_PATH}." >&2
  echo "Re-run it with: sudo $0" >&2
  exit 1
fi

if [[ ! -d /etc/udev/rules.d ]]; then
  echo "No /etc/udev/rules.d on this system; udev is not in use here." >&2
  echo "Run this on the Linux host, not inside the container; then pass the" >&2
  echo "device into the container with --device=/dev/dali/daliusb-<serial>." >&2
  echo "Home Assistant OS does not support the HID interface; use the serial" >&2
  echo "DALI2-USB interface there instead." >&2
  exit 1
fi

echo "Writing udev rule to ${RULE_PATH} ..."
cat > "${RULE_PATH}" <<EOF
# Tridonic/Lunatone DALI-USB (HID). Installed by hacs-dali install-udev.sh.
# Makes the hidraw node group-accessible and adds a stable /dev/dali symlink.
SUBSYSTEMS=="usb", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="${VENDOR_ID}", ATTRS{idProduct}=="${PRODUCT_ID}", MODE="660", GROUP="${GROUP}", SYMLINK+="dali/daliusb-%s{serial}"
EOF

echo "Reloading udev rules ..."
udevadm control --reload
udevadm trigger --subsystem-match=hidraw

echo
echo "Done. The Home Assistant user must be in the '${GROUP}' group:"
echo "    sudo usermod -aG ${GROUP} <home-assistant-user>"
echo "Replug the dongle (or reboot) so the new permissions take effect."
echo

shopt -s nullglob
links=(/dev/dali/daliusb-*)
if [[ ${#links[@]} -gt 0 ]]; then
  echo "Detected DALI-USB interface(s):"
  for link in "${links[@]}"; do
    echo "    ${link} -> $(readlink -f "${link}")"
  done
else
  echo "No DALI-USB HID interface detected yet. Plug it in and re-run; the"
  echo "symlink appears under /dev/dali/ once the rule matches."
fi
