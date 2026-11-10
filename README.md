<img src="https://raw.githubusercontent.com/tridonic-com/ha-dali/main/icon.png" alt="Tridonic DALI" width="128" align="right" />

# Tridonic DALI

[![HACS](https://github.com/tridonic-com/ha-dali/actions/workflows/hacs.yml/badge.svg)](https://github.com/tridonic-com/ha-dali/actions/workflows/hacs.yml)
[![Hassfest](https://github.com/tridonic-com/ha-dali/actions/workflows/hassfest.yml/badge.svg)](https://github.com/tridonic-com/ha-dali/actions/workflows/hassfest.yml)
[![Release](https://img.shields.io/github/v/release/tridonic-com/ha-dali?sort=semver)](https://github.com/tridonic-com/ha-dali/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/tridonic-com/ha-dali#readme)
[![License](https://img.shields.io/github/license/tridonic-com/ha-dali)](LICENSE)

Pre-release distribution of the **Tridonic DALI** Home Assistant integration for
early testers, before it is available in Home Assistant core. It supports the
Lunatone DALI2-USB dongle (USB `17B5:0201`).

> This is a temporary channel. Once the integration ships in Home Assistant core,
> install it from there and remove this custom repository.

## Requirements

- A running Home Assistant instance (OS, Container, or Supervised recommended).
- The Home Assistant Marketplace ([HACS](https://hacs.xyz)), available under
  **Settings > Marketplace**.
- Network access on the Home Assistant host (first setup installs `python-dali`
  from PyPI via pip).

## Install

This integration is available in the Home Assistant Marketplace
(**Settings > Marketplace**).

1. In **Settings > Marketplace**, search for **Tridonic DALI**, install it, then
   **restart Home Assistant**.
2. Plug in the DALI-USB dongle. Go to **Settings → Devices & Services → Add
   Integration → Tridonic DALI** and follow the config flow.

If it does not appear yet, add it as a custom repository as a fallback — in
**Settings > Marketplace**, open the three-dot menu → **Custom repositories**,
add this repository's URL with category **Integration** (or use the button
below), then install as above:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tridonic-com&repository=ha-dali&category=integration)

On first setup Home Assistant installs the released
[`python-dali`](https://pypi.org/project/python-dali/) dependency from PyPI via
pip; this can take a minute and requires network access.

## Updating

HACS offers updates when a new release is published here. Update from HACS, then
restart Home Assistant.

## For maintainers

The integration under `custom_components/dali/` is a generated copy of
`homeassistant/components/dali/` from a local Home Assistant core checkout. Do
not edit it by hand — change it in core, then re-sync:

```bash
python scripts/sync.py                 # uses ../core, keeps the current version
python scripts/sync.py --version 0.2.0 # bump the integration version
```

Versus the core manifest, the sync applies the changes a HACS custom
integration needs: it adds a `version` field, points `documentation` and
`issue_tracker` at this GitHub repo (hassfest rejects the home-assistant.io URL
for custom integrations), and loosens the `serialx` pin to `>=` (Home Assistant
ships it). The `python-dali==0.16` PyPI pin is copied verbatim. Translations
(`translations/en.json`) are generated in the core checkout
(`python3 -m script.translations develop --integration dali`) before syncing,
since core does not commit them. After syncing, commit, tag with the matching
version, and push to the GitHub remote so the Marketplace picks up the release.
