# Theme Aliases - User-Friendly Names

## Overview

To make themes easier to use, pyonig supports **short, friendly aliases** for theme names. Users can type `monokai` instead of `monokai-color-theme`.

## All Theme Aliases

### VS Code Default Themes
| Alias | Full Theme Name | Description |
|-------|----------------|-------------|
| `dark` | `dark_vs` | Classic dark theme |
| `light` | `light_vs` | Classic light theme |
| `dark+` | `dark_plus` | VS Code's default dark (enhanced) |
| `light+` | `light_plus` | VS Code's default light (enhanced) |
| `hc-black` | `hc_black` | High contrast black |
| `hc-light` | `hc_light` | High contrast light |

### Color Themes
| Alias | Full Theme Name | Description |
|-------|----------------|-------------|
| `monokai` | `monokai-color-theme` | Classic Monokai |
| `monokai-dimmed` | `dimmed-monokai-color-theme` | Softer Monokai |
| `solarized-dark` | `solarized-dark-color-theme` | Solarized Dark |
| `solarized-light` | `solarized-light-color-theme` | Solarized Light |
| `abyss` | `abyss-color-theme` | Deep blue theme |
| `kimbie-dark` | `kimbie-dark-color-theme` | Warm & earthy |
| `quietlight` | `quietlight-color-theme` | Gentle light |
| `red` | `Red-color-theme` | Red-tinted |
| `tomorrow-night-blue` | `tomorrow-night-blue-color-theme` | Tomorrow Night Blue |

## Usage Examples

### Short Aliases (Recommended)
```bash
# Use short, friendly names
pyonig --theme monokai file.json
pyonig --theme solarized-dark config.yaml
pyonig --theme dark+ app.py
pyonig --theme quietlight README.md

# Pipe with aliases
cat data.json | pyonig --theme monokai
echo '{"test": true}' | pyonig --theme dark+
```

### Full Theme Names (Also Work)
```bash
# Full names still work
pyonig --theme monokai-color-theme file.json
pyonig --theme solarized-dark-color-theme config.yaml
pyonig --theme dark_plus app.py
```

## Listing Themes

The `--list-themes` command shows both full names and aliases:

```bash
$ pyonig --list-themes
Available themes (17 total):

VS Code Default Themes:
  • dark_plus                 (aliases: dark+)
  • dark_vs                   (aliases: dark)
  • hc_black                  (aliases: hc-black)
  • hc_light                  (aliases: hc-light)
  • light_plus                (aliases: light+)
  • light_vs                  (aliases: light)

Color Themes:
  • Red-color-theme                          (alias: red)
  • abyss-color-theme                        (alias: abyss)
  • dimmed-monokai-color-theme               (alias: monokai-dimmed)
  • kimbie-dark-color-theme                  (alias: kimbie-dark)
  • monokai-color-theme                      (alias: monokai)
  • quietlight-color-theme                   (alias: quietlight)
  • solarized-dark-color-theme               (alias: solarized-dark)
  • solarized-light-color-theme              (alias: solarized-light)
  • tomorrow-night-blue-color-theme          (alias: tomorrow-night-blue)

Usage: pyonig --theme <name> <file>
Example: pyonig --theme monokai file.json
         pyonig --theme solarized-dark config.yaml
```

## Implementation

Aliases are defined in `src/pyonig/cli.py`:

```python
THEME_ALIASES = {
    # VS Code defaults
    "dark": "dark_vs",
    "light": "light_vs",
    "dark+": "dark_plus",
    "light+": "light_plus",
    
    # Color themes (short names)
    "monokai": "monokai-color-theme",
    "solarized-dark": "solarized-dark-color-theme",
    # ... etc
}
```

When a user specifies `--theme monokai`, the CLI:
1. Checks if "monokai" is an alias
2. Resolves to "monokai-color-theme"
3. Loads `src/pyonig/themes/monokai-color-theme.json`

## Benefits

### User Experience
✅ **Shorter commands**: `monokai` vs `monokai-color-theme`  
✅ **Easier to remember**: No need to remember `-color-theme` suffix  
✅ **Natural naming**: `dark+` instead of `dark_plus`  
✅ **Backward compatible**: Full names still work

### Examples

**Before (verbose):**
```bash
pyonig --theme monokai-color-theme file.json
pyonig --theme solarized-dark-color-theme config.yaml
```

**After (concise):**
```bash
pyonig --theme monokai file.json
pyonig --theme solarized-dark config.yaml
```

## Adding New Aliases

To add a new alias, edit `THEME_ALIASES` in `src/pyonig/cli.py`:

```python
THEME_ALIASES = {
    # ... existing aliases ...
    "my-theme": "my-custom-theme-color-theme",
}
```

## Recommendation

**Use short aliases for daily work:**
- They're easier to type
- They're easier to remember
- They look cleaner in documentation

**Full names are auto-discovered:**
- List themes with `--list-themes`
- See which alias maps to which file
- Full names always work too

## Technical Notes

- Aliases are case-sensitive
- Aliases must be unique
- Full theme names always work (even if not listed as aliases)
- The `--list-themes` command shows all mappings
- Alias resolution happens before file path checking

## Testing

All aliases tested and working:

```bash
✓ monokai              → monokai-color-theme
✓ solarized-dark       → solarized-dark-color-theme  
✓ dark+                → dark_plus
✓ quietlight           → quietlight-color-theme
✓ abyss                → abyss-color-theme
✓ All 9 aliases tested and verified
```

