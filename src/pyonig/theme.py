"""Theme management for pyonig - detection, aliases, and resolution."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional


# Theme name aliases (friendly name -> actual filename)
THEME_ALIASES = {
    # VS Code defaults (short names)
    "dark": "dark_vs",
    "light": "light_vs",
    "dark+": "dark_plus",
    "light+": "light_plus",
    "hc-black": "hc_black",
    "hc-light": "hc_light",
    
    # VS Code display names (from settings.json "workbench.colorTheme")
    "Dark (Visual Studio)": "dark_vs",
    "Light (Visual Studio)": "light_vs",
    "Visual Studio Dark": "dark_vs",  # Alternative name
    "Visual Studio Light": "light_vs",  # Alternative name
    "Dark+": "dark_plus",
    "Light+": "light_plus",
    "Dark High Contrast": "hc_black",
    "Light High Contrast": "hc_light",
    
    # Color themes (short names)
    "monokai": "monokai-color-theme",
    "monokai-dimmed": "dimmed-monokai-color-theme",
    "solarized-dark": "solarized-dark-color-theme",
    "solarized-light": "solarized-light-color-theme",
    "abyss": "abyss-color-theme",
    "kimbie-dark": "kimbie-dark-color-theme",
    "quietlight": "quietlight-color-theme",
    "red": "Red-color-theme",
    "tomorrow-night-blue": "tomorrow-night-blue-color-theme",
    
    # VS Code display names for color themes
    "Abyss": "abyss-color-theme",
    "Kimbie Dark": "kimbie-dark-color-theme",
    "Monokai": "monokai-color-theme",
    "Monokai Dimmed": "dimmed-monokai-color-theme",
    "Quiet Light": "quietlight-color-theme",
    "Red": "Red-color-theme",
    "Solarized Dark": "solarized-dark-color-theme",
    "Solarized Light": "solarized-light-color-theme",
    "Solarized (dark)": "solarized-dark-color-theme",
    "Solarized (light)": "solarized-light-color-theme",
    "Tomorrow Night Blue": "tomorrow-night-blue-color-theme",
}


def get_vscode_theme() -> Optional[str]:
    """Get the current VS Code theme from user settings.
    
    Checks the standard VS Code settings locations:
    - Linux: ~/.config/Code/User/settings.json
    - macOS: ~/Library/Application Support/Code/User/settings.json
    - Windows: %APPDATA%/Code/User/settings.json
    
    Returns:
        Theme name from "workbench.colorTheme" or None if not found
    """
    # Determine settings path based on platform
    home = Path.home()
    
    if sys.platform == "darwin":
        settings_path = home / "Library/Application Support/Code/User/settings.json"
    elif sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            settings_path = Path(appdata) / "Code/User/settings.json"
        else:
            return None
    else:  # Linux and other Unix-like
        settings_path = home / ".config/Code/User/settings.json"
    
    # Try to read the settings
    if not settings_path.exists():
        return None
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            # VS Code settings.json allows comments, so we need to handle that
            content = f.read()
            # Simple comment removal (not perfect but good enough)
            lines = []
            for line in content.splitlines():
                # Remove // comments
                if '//' in line:
                    line = line.split('//')[0]
                lines.append(line)
            clean_content = '\n'.join(lines)
            
            settings = json.loads(clean_content)
            return settings.get("workbench.colorTheme")
    except (json.JSONDecodeError, OSError):
        return None


def get_default_theme() -> str:
    """Get the default theme to use.
    
    Priority order:
    1. PYONIG_THEME environment variable
    2. VS Code user settings (workbench.colorTheme)
    3. "dark" as fallback
    
    Returns:
        Theme name (may be an alias or full theme name)
    """
    # Check environment variable first
    env_theme = os.environ.get("PYONIG_THEME")
    if env_theme:
        return env_theme
    
    # Try to get VS Code theme
    vscode_theme = get_vscode_theme()
    if vscode_theme:
        return vscode_theme
    
    # Final fallback
    return "dark"


def resolve_theme_alias(theme_name: str) -> str:
    """Resolve a theme alias to the actual theme filename (without .json).
    
    Args:
        theme_name: Theme name or alias
    
    Returns:
        Resolved theme filename (without .json extension)
    """
    return THEME_ALIASES.get(theme_name, theme_name)


def find_theme_path(theme_name: str, theme_dir: Optional[Path] = None) -> Optional[Path]:
    """Find the full path to a theme file.
    
    Args:
        theme_name: Theme name, alias, or path
        theme_dir: Directory containing theme files (defaults to package themes/)
    
    Returns:
        Path to theme file or None if not found
    """
    # If it's already a path and exists, use it
    theme_path = Path(theme_name)
    if theme_path.exists():
        return theme_path
    
    # Resolve alias
    resolved_name = resolve_theme_alias(theme_name)
    
    # Determine theme directory
    if theme_dir is None:
        # Default to package themes directory
        theme_dir = Path(__file__).parent / 'themes'
    
    # Try with resolved name
    if resolved_name.endswith('.json'):
        theme_path = theme_dir / resolved_name
    else:
        theme_path = theme_dir / f"{resolved_name}.json"
    
    if theme_path.exists():
        return theme_path
    
    return None


class ThemeManager:
    """Manages theme detection, resolution, and loading."""
    
    def __init__(self, theme_dir: Optional[Path] = None):
        """Initialize theme manager.
        
        Args:
            theme_dir: Directory containing theme files (defaults to package themes/)
        """
        self.theme_dir = theme_dir or (Path(__file__).parent / 'themes')
    
    def get_default(self) -> str:
        """Get the default theme name (respects env vars and VS Code settings)."""
        return get_default_theme()
    
    def resolve(self, theme_name: str) -> str:
        """Resolve a theme alias to actual filename."""
        return resolve_theme_alias(theme_name)
    
    def find_path(self, theme_name: str) -> Optional[Path]:
        """Find the full path to a theme file."""
        return find_theme_path(theme_name, self.theme_dir)
    
    def list_themes(self) -> list[tuple[str, list[str]]]:
        """List all available themes with their aliases.
        
        Returns:
            List of (theme_filename, [aliases]) tuples
        """
        if not self.theme_dir.exists():
            return []
        
        # Build reverse mapping (filename -> aliases)
        filename_to_aliases = {}
        for alias, filename in THEME_ALIASES.items():
            if filename not in filename_to_aliases:
                filename_to_aliases[filename] = []
            filename_to_aliases[filename].append(alias)
        
        # List all theme files
        themes = []
        for theme_file in sorted(self.theme_dir.glob('*.json')):
            # Skip license files
            if 'LICENSE' in theme_file.name.upper():
                continue
            
            theme_name = theme_file.stem
            aliases = filename_to_aliases.get(theme_name, [])
            themes.append((theme_name, aliases))
        
        return themes

