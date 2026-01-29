#!/usr/bin/env python3
"""
PPK DOCUMENT FACTORY - Icon Downloader
======================================
Script untuk download SVG icons dari Feather Icons.

Usage:
    python scripts/download_icons.py

Icons akan disimpan di assets/icons/
"""

import os
import sys
import urllib.request
import urllib.error
import ssl
import time
from pathlib import Path


# Base URL untuk Feather Icons di unpkg
FEATHER_BASE_URL = "https://unpkg.com/feather-icons/dist/icons"

# Mapping: nama yang kita gunakan -> nama file di Feather Icons
ICONS_TO_DOWNLOAD = {
    # Navigation
    "home": "home",
    "dashboard": "layout",  # Feather uses 'layout' for dashboard-like icon
    "arrow-left": "arrow-left",
    "arrow-right": "arrow-right",

    # Finance/Money
    "wallet": "credit-card",  # Feather doesn't have wallet, use credit-card
    "money": "dollar-sign",
    "send": "send",

    # Actions
    "plus-circle": "plus-circle",
    "plus": "plus",
    "edit": "edit-2",
    "delete": "trash-2",
    "view": "eye",
    "save": "save",
    "print": "printer",
    "export": "external-link",
    "download": "download",
    "upload": "upload",
    "refresh": "refresh-cw",
    "search": "search",

    # Objects
    "package": "package",
    "users": "users",
    "user": "user",
    "box": "box",
    "building": "home",  # Feather doesn't have building, use home as fallback
    "file-text": "file-text",
    "folder": "folder",
    "document": "file",

    # Status/Feedback
    "check": "check",
    "check-circle": "check-circle",
    "x": "x",
    "x-circle": "x-circle",
    "warning": "alert-triangle",
    "info": "info",
    "error": "alert-circle",

    # UI
    "settings": "settings",
    "menu": "menu",
    "close": "x",
    "minimize": "minus",
    "maximize": "maximize-2",

    # Misc
    "calendar": "calendar",
    "clock": "clock",
    "filter": "filter",
    "sort": "bar-chart-2",
}


def create_ssl_context():
    """Create SSL context that doesn't verify certificates (for corporate proxies)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def download_icon(icon_name: str, feather_name: str, output_dir: Path) -> bool:
    """
    Download single icon from Feather Icons.

    Args:
        icon_name: Nama file output (tanpa .svg)
        feather_name: Nama icon di Feather Icons
        output_dir: Directory untuk menyimpan file

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    url = f"{FEATHER_BASE_URL}/{feather_name}.svg"
    output_path = output_dir / f"{icon_name}.svg"

    try:
        # Create request with headers
        request = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )

        # Try with SSL verification first
        try:
            response = urllib.request.urlopen(request, timeout=10)
        except urllib.error.URLError:
            # If SSL error, try without verification
            ctx = create_ssl_context()
            response = urllib.request.urlopen(request, timeout=10, context=ctx)

        svg_content = response.read().decode('utf-8')

        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        return True

    except Exception as e:
        print(f"  Error downloading {icon_name}: {e}")
        return False


def create_placeholder_svg(icon_name: str, output_dir: Path) -> None:
    """
    Create placeholder SVG when download fails.

    Args:
        icon_name: Nama icon
        output_dir: Directory untuk menyimpan file
    """
    # Get first letter for placeholder
    letter = icon_name[0].upper() if icon_name else "?"

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10" stroke-opacity="0.3"/>
  <text x="12" y="16" text-anchor="middle" font-size="10" font-family="Arial" fill="currentColor" stroke="none">{letter}</text>
</svg>'''

    output_path = output_dir / f"{icon_name}.svg"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)


def main():
    """Main function to download all icons."""
    # Get script directory and calculate output path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / "assets" / "icons"

    # Create output directory if not exists
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("PPK DOCUMENT FACTORY - Icon Downloader")
    print("=" * 60)
    print(f"\nOutput directory: {output_dir}")
    print(f"Total icons to download: {len(ICONS_TO_DOWNLOAD)}")
    print("-" * 60)

    success_count = 0
    failed_count = 0
    placeholder_count = 0

    for icon_name, feather_name in ICONS_TO_DOWNLOAD.items():
        print(f"Downloading: {icon_name} <- {feather_name}...", end=" ")

        if download_icon(icon_name, feather_name, output_dir):
            print("OK")
            success_count += 1
        else:
            print("FAILED - Creating placeholder...")
            create_placeholder_svg(icon_name, output_dir)
            failed_count += 1
            placeholder_count += 1

        # Small delay to avoid rate limiting
        time.sleep(0.1)

    print("-" * 60)
    print(f"\nSummary:")
    print(f"  Downloaded: {success_count}")
    print(f"  Failed (placeholders created): {failed_count}")
    print(f"  Total icons: {success_count + placeholder_count}")
    print("\nDone!")

    # List all created files
    print(f"\nFiles in {output_dir}:")
    for f in sorted(output_dir.glob("*.svg")):
        size = f.stat().st_size
        print(f"  {f.name} ({size} bytes)")


if __name__ == "__main__":
    main()
