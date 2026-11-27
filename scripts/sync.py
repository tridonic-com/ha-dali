#!/usr/bin/env python3
"""Sync the DALI integration from Home Assistant core into this HACS repo.

Copies ``homeassistant/components/dali/`` from a local Home Assistant core
checkout into ``custom_components/dali/`` and rewrites the manifest so it passes
HACS and hassfest validation as a custom integration (see ``patch_manifest``).
Everything else is copied verbatim. Re-run after any change in core.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DST = REPO_ROOT / "custom_components" / "dali"
# Brand assets live in the separate home-assistant/brands repo, not in core, so
# the rmtree+copytree below leaves none behind; copy_brand() restores them here.
BRAND_DST = DST / "brand"

DEFAULT_VERSION = "0.3.2"

# Where the DALI brand images sit inside a brands checkout, most specific first.
BRAND_SUBDIRS = ("core_integrations/dali", "custom_integrations/dali")
# Brand image filenames to mirror when present (icon/logo, light and dark).
BRAND_FILES = (
    "icon.png",
    "icon@2x.png",
    "logo.png",
    "logo@2x.png",
    "dark_icon.png",
    "dark_icon@2x.png",
    "dark_logo.png",
    "dark_logo@2x.png",
)

GITHUB_REPO = "tridonic-com/ha-dali"

# Packages Home Assistant ships as direct dependencies must not be listed at all
# by a custom integration.
DROP_REQUIREMENTS: frozenset[str] = frozenset()
# Packages Home Assistant only constrains must be loosened from "==" to ">=" so
# they follow core instead of pinning against it.
LOOSEN_REQUIREMENTS: frozenset[str] = frozenset({"serialx"})
# Categories to add only when core defines none (HACS wants categories).
DEFAULT_CATEGORIES: list[str] = []

EXCLUDE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")


def _package_name(requirement: str) -> str:
    """Return the distribution name from a requirement like ``serialx==1.0``."""
    return re.split(r"[=<>!~ ]", requirement, maxsplit=1)[0].strip()


def _patch_requirements(requirements: list[str]) -> list[str]:
    patched: list[str] = []
    for req in requirements:
        name = _package_name(req)
        if name in DROP_REQUIREMENTS:
            continue
        if name in LOOSEN_REQUIREMENTS:
            req = req.replace("==", ">=")
        patched.append(req)
    return patched


def patch_manifest(path: Path, version: str) -> None:
    """Rewrite the core manifest into a HACS-custom one.

    Versus the core manifest this:
    - adds a ``version`` field (required for custom integrations),
    - points ``documentation``/``issue_tracker`` at this GitHub repo (hassfest
      rejects the home-assistant.io URL for custom integrations),
    - drops/loosens requirements Home Assistant itself ships,
    - adds fallback ``categories`` when core defines none, and
    - sorts keys as hassfest expects (``domain``, ``name``, then alphabetical).
    """
    manifest = json.loads(path.read_text(encoding="utf-8"))

    manifest["version"] = version
    manifest["documentation"] = f"https://github.com/{GITHUB_REPO}"
    manifest["issue_tracker"] = f"https://github.com/{GITHUB_REPO}/issues"
    if "requirements" in manifest:
        manifest["requirements"] = _patch_requirements(manifest["requirements"])
    if DEFAULT_CATEGORIES and not manifest.get("categories"):
        manifest["categories"] = DEFAULT_CATEGORIES

    rest = sorted(key for key in manifest if key not in ("domain", "name"))
    ordered = {key: manifest[key] for key in ("domain", "name", *rest)}

    path.write_text(
        json.dumps(ordered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def copy_brand(brands_path: Path) -> int:
    """Copy the DALI brand images from the brands repo into ``brand/``.

    Core ships no brand assets (they live in the separate home-assistant/brands
    repo), so the copytree from core leaves none behind. Mirror whatever brand
    images exist for the DALI domain into ``custom_components/dali/brand/`` so the
    custom integration ships them in-repo. Returns the number of files copied.
    """
    source = next(
        (brands_path / sub for sub in BRAND_SUBDIRS if (brands_path / sub).is_dir()),
        None,
    )
    if source is None:
        raise SystemExit(
            f"DALI brand assets not found under {brands_path} "
            f"({' or '.join(BRAND_SUBDIRS)}); pass --brands-path or --skip-brands."
        )

    BRAND_DST.mkdir(parents=True, exist_ok=True)
    copied = [name for name in BRAND_FILES if (source / name).is_file()]
    for name in copied:
        shutil.copy2(source / name, BRAND_DST / name)
    if not copied:
        raise SystemExit(f"No brand images found in {source}")
    return len(copied)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--core-path",
        type=Path,
        default=REPO_ROOT.parent / "core",
        help="Path to the Home Assistant core checkout (default: ../core).",
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Integration version for the manifest (default: keep existing or "
        f"{DEFAULT_VERSION}).",
    )
    parser.add_argument(
        "--brands-path",
        type=Path,
        default=REPO_ROOT.parent / "brands",
        help="Path to the home-assistant/brands checkout (default: ../brands).",
    )
    parser.add_argument(
        "--skip-brands",
        action="store_true",
        help="Do not copy brand images (leaves the brand/ folder absent).",
    )
    args = parser.parse_args()

    src = args.core_path / "homeassistant" / "components" / "dali"
    if not src.is_dir():
        raise SystemExit(f"DALI integration not found at {src}")

    # Preserve the existing version unless explicitly overridden.
    version = args.version
    if version is None:
        existing = DST / "manifest.json"
        if existing.is_file():
            version = json.loads(existing.read_text(encoding="utf-8")).get(
                "version", DEFAULT_VERSION
            )
        else:
            version = DEFAULT_VERSION

    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(src, DST, ignore=EXCLUDE)

    patch_manifest(DST / "manifest.json", version)

    print(f"Synced {src} -> {DST}")
    print(f"  version: {version}")
    if args.skip_brands:
        print("  brand assets: skipped")
    else:
        count = copy_brand(args.brands_path)
        print(f"  brand assets: {count} file(s) from {args.brands_path}")
    print("Remember to bump the version and cut a matching release tag.")


if __name__ == "__main__":
    main()
