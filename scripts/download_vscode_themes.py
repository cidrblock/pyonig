#!/usr/bin/env python3
"""
Download all built-in VS Code themes.
"""
import os
import json
import requests
from pathlib import Path

# VS Code GitHub raw content base URL
RAW_BASE = "https://raw.githubusercontent.com/microsoft/vscode/main/extensions"

# Known theme extensions and their theme files
THEMES = {
    "theme-abyss": ["themes/abyss-color-theme.json"],
    "theme-defaults": [
        "themes/dark_plus.json",
        "themes/dark_vs.json",
        "themes/light_plus.json",
        "themes/light_vs.json",
        "themes/dark_modern.json",
        "themes/hc_black.json",
        "themes/hc_light.json",
    ],
    "theme-kimbie-dark": ["themes/kimbie-dark-color-theme.json"],
    "theme-monokai": ["themes/monokai-color-theme.json"],
    "theme-monokai-dimmed": ["themes/dimmed-monokai-color-theme.json"],
    "theme-quietlight": ["themes/quietlight-color-theme.json"],
    "theme-red": ["themes/Red-color-theme.json"],
    "theme-solarized-dark": ["themes/solarized-dark-color-theme.json"],
    "theme-solarized-light": ["themes/solarized-light-color-theme.json"],
    "theme-tomorrow-night-blue": ["themes/tomorrow-night-blue-color-theme.json"],
}


def download_theme(extension, theme_path, out_dir):
    """Download a single theme file."""
    url = f"{RAW_BASE}/{extension}/{theme_path}"
    filename = os.path.basename(theme_path)
    
    # Normalize filename
    filename = filename.replace("_", "-")
    out_path = os.path.join(out_dir, filename)
    
    print(f"Downloading {filename}...", end=" ")
    
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"FAILED (HTTP {r.status_code})")
            return None
        
        # Validate it's valid JSON
        theme_data = r.json()
        
        # Write formatted JSON
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(theme_data, f, indent=2, ensure_ascii=False)
        
        print("✓")
        return filename
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def write_license(theme_files, out_dir):
    """Write MIT license file with attribution."""
    MIT_LICENSE = """MIT License

Copyright (c) Microsoft Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
    
    license_path = os.path.join(out_dir, "VSCODE_THEMES_LICENSE.txt")
    
    with open(license_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("VS CODE BUILT-IN THEMES\n")
        f.write("=" * 70 + "\n\n")
        f.write("Source: https://github.com/microsoft/vscode\n")
        f.write("Downloaded from: microsoft/vscode main branch\n\n")
        f.write("These themes are the official built-in color themes from\n")
        f.write("Visual Studio Code, used under the MIT License.\n\n")
        f.write("Included theme files:\n")
        for theme in sorted(theme_files):
            f.write(f"  • {theme}\n")
        f.write("\n")
        f.write("=" * 70 + "\n\n")
        f.write(MIT_LICENSE)
    
    print(f"\nLicense written to: {license_path}")


def main():
    # Output to src/pyonig/themes/
    out_dir = Path("src/pyonig/themes")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("DOWNLOADING VS CODE THEMES")
    print("=" * 70)
    print(f"Output directory: {out_dir}\n")
    
    downloaded = []
    
    for extension, theme_paths in THEMES.items():
        for theme_path in theme_paths:
            filename = download_theme(extension, theme_path, out_dir)
            if filename:
                downloaded.append(filename)
    
    print(f"\n{'=' * 70}")
    print(f"SUCCESS: Downloaded {len(downloaded)} themes")
    print(f"{'=' * 70}")
    
    # Write license file
    write_license(downloaded, out_dir)
    
    # List all downloaded themes
    print("\nDownloaded themes:")
    for theme in sorted(downloaded):
        theme_name = theme.replace("-color-theme.json", "").replace(".json", "")
        print(f"  • {theme_name:30} ({theme})")
    
    print(f"\nAll themes saved to: {out_dir}/")


if __name__ == "__main__":
    main()
