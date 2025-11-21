# Theme Auto-Detection - VS Code Integration

## Overview

pyonig automatically detects your VS Code theme preference and uses it by default! No need to specify `--theme` every time.

## Priority Order

Themes are selected in this priority order (highest to lowest):

1. **CLI `--theme` flag** (always wins)
2. **`PYONIG_THEME` environment variable**
3. **VS Code user settings** (`workbench.colorTheme`)
4. **"dark" fallback** (if none of the above are available)

## Usage Examples

### Default (Auto-Detection)
```bash
# Uses your VS Code theme automatically
cat file.json | pyonig

# If you have "workbench.colorTheme": "Monokai" in VS Code settings,
# pyonig will use Monokai theme automatically!
```

### Environment Variable
```bash
# Set default theme for the session
export PYONIG_THEME=solarized-dark
cat file.json | pyonig  # Uses Solarized Dark

# Or set for just one command
PYONIG_THEME=quietlight cat config.yaml | pyonig
```

### CLI Override (Highest Priority)
```bash
# Always use Monokai, regardless of env var or VS Code settings
cat file.json | pyonig --theme monokai

# CLI flag always wins
PYONIG_THEME=dark+ pyonig --theme abyss file.json  # Uses Abyss
```

## VS Code Settings Integration

### Settings File Locations

**Linux:**
```
~/.config/Code/User/settings.json
```

**macOS:**
```
~/Library/Application Support/Code/User/settings.json
```

**Windows:**
```
%APPDATA%\Code\User\settings.json
```

### Example VS Code Settings

If your VS Code `settings.json` contains:
```json
{
  "workbench.colorTheme": "Monokai",
  "editor.fontSize": 14
}
```

Then pyonig will automatically use **Monokai** theme!

### Supported VS Code Theme Names

All official VS Code theme names are supported as aliases:

| VS Code Setting | pyonig Theme |
|----------------|--------------|
| `"Visual Studio Dark"` | `dark_vs` |
| `"Visual Studio Light"` | `light_vs` |
| `"Dark+"` | `dark_plus` |
| `"Light+"` | `light_plus` |
| `"Dark (Visual Studio)"` | `dark_vs` |
| `"Light (Visual Studio)"` | `light_vs` |
| `"Dark High Contrast"` | `hc_black` |
| `"Light High Contrast"` | `hc_light` |
| `"Monokai"` | `monokai-color-theme` |
| `"Monokai Dimmed"` | `dimmed-monokai-color-theme` |
| `"Solarized Dark"` | `solarized-dark-color-theme` |
| `"Solarized Light"` | `solarized-light-color-theme` |
| `"Solarized (dark)"` | `solarized-dark-color-theme` |
| `"Solarized (light)"` | `solarized-light-color-theme` |
| `"Abyss"` | `abyss-color-theme` |
| `"Kimbie Dark"` | `kimbie-dark-color-theme` |
| `"Quiet Light"` | `quietlight-color-theme` |
| `"Red"` | `Red-color-theme` |
| `"Tomorrow Night Blue"` | `tomorrow-night-blue-color-theme` |

## Environment Variable (`PYONIG_THEME`)

### Persistent Default
```bash
# Add to ~/.bashrc or ~/.zshrc for permanent default
export PYONIG_THEME=monokai

# Now all pyonig commands use Monokai by default
cat file.json | pyonig
pyonig script.py
```

### Per-Project Defaults
```bash
# In project directory
echo "export PYONIG_THEME=solarized-dark" >> .envrc

# Or use direnv for automatic loading
# https://direnv.net/
```

### Temporary Override
```bash
# Just for this command
PYONIG_THEME=quietlight cat README.md | pyonig
```

## Complete Examples

### Example 1: VS Code User
```bash
# Your VS Code settings.json:
# { "workbench.colorTheme": "Monokai" }

# Just use pyonig - it picks up your VS Code theme!
cat app.py | pyonig          # Uses Monokai automatically ✨

# Override if needed
cat app.py | pyonig --theme dark+   # Uses Dark+ instead
```

### Example 2: Environment Variable User
```bash
# Set your preferred theme
export PYONIG_THEME=solarized-dark

# Use it everywhere
cat config.yaml | pyonig
pyonig script.sh
cat data.json | pyonig

# Override when needed
pyonig --theme monokai special.json
```

### Example 3: No Configuration
```bash
# No VS Code settings, no env var
cat file.json | pyonig       # Uses "dark" (default fallback)

# Specify explicitly
cat file.json | pyonig --theme monokai
```

## Error Messages

If a theme can't be found, pyonig shows you where it came from:

```bash
$ PYONIG_THEME=nonexistent cat file.json | pyonig
Error: Theme not found: nonexistent
  (from PYONIG_THEME environment variable: 'nonexistent')
Use --list-themes to see available themes
```

```bash
# If your VS Code has an unsupported theme
$ cat file.json | pyonig
Error: Theme not found: Some Custom Theme
  (from VS Code settings: 'Some Custom Theme')
Use --list-themes to see available themes
```

## Implementation Details

### Theme Resolution Algorithm

```python
def get_default_theme():
    # 1. Check environment variable
    if PYONIG_THEME is set:
        return PYONIG_THEME
    
    # 2. Check VS Code settings
    vscode_theme = read_vscode_settings()
    if vscode_theme:
        return vscode_theme
    
    # 3. Fallback to "dark"
    return "dark"

# At CLI invocation:
if --theme provided:
    use --theme              # Highest priority
else:
    use get_default_theme()  # Auto-detect
```

### VS Code Settings Parsing

- Reads `settings.json` from standard locations
- Handles JSON with comments (`//`)
- Extracts `workbench.colorTheme` value
- Gracefully handles missing/invalid files

## Benefits

### For VS Code Users
✅ **Zero configuration** - Just works with your VS Code theme  
✅ **Consistent experience** - Same colors in terminal as in editor  
✅ **Automatic updates** - Change VS Code theme, pyonig follows

### For CLI Users
✅ **Environment variable** - Set once, use everywhere  
✅ **Project-specific** - Different themes per project  
✅ **Always overrideable** - CLI flag always wins

### For Everyone
✅ **Smart defaults** - No need to specify theme every time  
✅ **Flexible** - Three ways to set default, plus CLI override  
✅ **Discoverable** - Clear error messages show where theme came from

## Migration from Previous Versions

### Before (v0.1.0)
```bash
# Had to specify theme every time
pyonig --theme dark_vs file.json
pyonig --theme dark_vs script.py
pyonig --theme dark_vs config.yaml
```

### After (v0.2.0+)
```bash
# Set once (or let it detect from VS Code)
export PYONIG_THEME=dark

# Just use pyonig
pyonig file.json
pyonig script.py
pyonig config.yaml
```

## FAQ

**Q: What if my VS Code theme isn't supported?**  
A: Set `PYONIG_THEME` or use `--theme` flag. We support all official VS Code themes.

**Q: Does this work with VS Code Insiders?**  
A: Not currently. It reads from stable VS Code settings only.

**Q: Can I use a custom theme?**  
A: Yes! Provide a path to your theme JSON file: `--theme /path/to/theme.json`

**Q: Does this slow down pyonig?**  
A: No. VS Code settings are read only once at startup (~1ms overhead).

**Q: What if I don't have VS Code installed?**  
A: No problem! It falls back to "dark" theme automatically.

## See Also

- [THEME_ALIASES.md](THEME_ALIASES.md) - Complete alias reference
- [VSCODE_THEMES_INTEGRATION.md](VSCODE_THEMES_INTEGRATION.md) - Theme implementation details
- [README.md](README.md) - Main documentation

