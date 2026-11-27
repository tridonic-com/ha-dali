<img src="https://raw.githubusercontent.com/tridonic-com/ha-dali/main/icon.png" alt="Tridonic DALI" width="128" align="right" />

# Tridonic DALI

[![HACS](https://github.com/tridonic-com/ha-dali/actions/workflows/hacs.yml/badge.svg)](https://github.com/tridonic-com/ha-dali/actions/workflows/hacs.yml)
[![Hassfest](https://github.com/tridonic-com/ha-dali/actions/workflows/hassfest.yml/badge.svg)](https://github.com/tridonic-com/ha-dali/actions/workflows/hassfest.yml)
[![Release](https://img.shields.io/github/v/release/tridonic-com/ha-dali?sort=semver)](https://github.com/tridonic-com/ha-dali/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/tridonic-com/ha-dali#readme)
[![License](https://img.shields.io/github/license/tridonic-com/ha-dali)](LICENSE)

Pre-release distribution of the **Tridonic DALI** Home Assistant integration for
early testers, before it is available in Home Assistant core. It supports the
Lunatone DALI2-USB serial dongle (USB `17B5:0201`) and the Tridonic/Lunatone
DALI-USB (HID) interface (USB `17B5:0020`; see [DALI-USB (HID) interface](#dali-usb-hid-interface)).

> This is a temporary channel. Work to integrate DALI into Home Assistant core is
> under way; once it ships there, install it from core and remove this custom
> repository.

## Requirements

- A running Home Assistant instance (OS, Container, or Supervised recommended).
- The Home Assistant Marketplace ([HACS](https://hacs.xyz)), available under
  **Settings > Marketplace**.
- Network access on the Home Assistant host (first setup installs `python-dali`
  from PyPI via pip).

## Install

This integration is **not** in the HACS default marketplace, so add it as a
custom repository:

1. In the Home Assistant Marketplace (**Settings > Marketplace**), open the
   three-dot menu → **Custom repositories**, add this repository's URL with
   category **Integration**, or use the button below:

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tridonic-com&repository=ha-dali&category=integration)

2. Search for **Tridonic DALI**, install it, then **restart Home Assistant**.
3. Plug in the DALI-USB dongle. Go to **Settings → Devices & Services → Add
   Integration → Tridonic DALI** and follow the config flow.

On first setup Home Assistant installs the released
[`python-dali`](https://pypi.org/project/python-dali/) dependency from PyPI via
pip; this can take a minute and requires network access.

## DALI-USB (HID) interface

The serial DALI2-USB (`17B5:0201`) appears as `/dev/ttyACM*` and works without
extra setup. The Tridonic/Lunatone **DALI-USB (HID)** interface (`17B5:0020`) is
different: Linux exposes it as a root-only `/dev/hidraw*` node, so Home
Assistant cannot open it until you grant access with a udev rule.

Run this once on the Linux host the dongle is plugged into (Home Assistant
Core/venv, Container, or Supervised, including WSL2):

```bash
sudo ./scripts/install-udev.sh
```

The script installs `/etc/udev/rules.d/50-dali-hid.rules`, which makes the
device readable by the `dialout` group and creates a stable
`/dev/dali/daliusb-<serial>` symlink. Make sure the Home Assistant user is in
the `dialout` group, then replug the dongle.

> For a Container install, run the script on the host, then pass the device into
> the container (for example `--device=/dev/dali/daliusb-<serial>`).
>
> Home Assistant OS is the exception: you cannot add a host udev rule there, so
> the DALI-USB (HID) interface is not supported. Use the serial DALI2-USB
> interface instead.

## Updating

HACS offers updates when a new release is published here. Update from HACS, then
restart Home Assistant.

## For maintainers

The integration under `custom_components/dali/` is a generated copy of
`homeassistant/components/dali/` from a local Home Assistant core checkout. Do
not edit it by hand — change it in core, then re-sync:

```bash
python scripts/sync.py                 # uses ../core and ../brands, keeps version
python scripts/sync.py --version 0.4.0 # bump the integration version
```

The sync also copies the DALI brand images (`icon.png`, `icon@2x.png`) from a
local [home-assistant/brands](https://github.com/home-assistant/brands) checkout
(`../brands` by default, override with `--brands-path`) into
`custom_components/dali/brand/`, since core itself ships no brand assets. Pass
`--skip-brands` to leave them out.

Versus the core manifest, the sync applies the changes a HACS custom
integration needs: it adds a `version` field and points `documentation` and
`issue_tracker` at this GitHub repo (hassfest rejects the home-assistant.io URL
for custom integrations). The `python-dali==1.0a3` and
`dali-drivers[driver-serial]==1.0a5` PyPI pins are copied verbatim; `serialx`
is pulled in transitively by the `driver-serial` extra. Translations
(`translations/en.json`) are generated in the core checkout
(`python3 -m script.translations develop --integration dali`) before syncing,
since core does not commit them. After syncing, commit, tag with the matching
version, and push to the GitHub remote so the Marketplace picks up the release.
