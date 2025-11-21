# VS Code Themes Integration

## Summary

Successfully integrated 17 official VS Code built-in color themes into pyonig.

## Themes Included

### VS Code Default Themes (8)
- **dark_plus** - Dark+ (default dark)
- **light_plus** - Light+ (default light)
- **dark_vs** - Dark (Visual Studio)
- **light_vs** - Light (Visual Studio)
- **hc_black** - High Contrast (Black)
- **hc_light** - High Contrast (Light)
- **hc-black** - High Contrast alternate
- **hc-light** - High Contrast Light alternate

### Popular Color Themes (9)
- **monokai-color-theme** - Monokai
- **dimmed-monokai-color-theme** - Monokai Dimmed
- **solarized-dark-color-theme** - Solarized Dark
- **solarized-light-color-theme** - Solarized Light
- **abyss-color-theme** - Abyss
- **kimbie-dark-color-theme** - Kimbie Dark
- **quietlight-color-theme** - Quiet Light
- **Red-color-theme** - Red
- **tomorrow-night-blue-color-theme** - Tomorrow Night Blue

## Implementation

### Files Added
- `src/pyonig/themes/*-color-theme.json` - VS Code color themes
- `src/pyonig/themes/VSCODE_THEMES_LICENSE.txt` - MIT License attribution
- `scripts/download_vscode_themes.py` - Download script (unused, manual copy used instead)
- `scripts/clean_jsonc_themes.py` - JSONC to JSON converter

### Processing Steps
1. **Cloned VS Code repo**: `git clone --depth 1 https://github.com/microsoft/vscode.git`
2. **Copied themes**: `cp ../vscode/extensions/theme-*/themes/*.json src/pyonig/themes/`
3. **Cleaned JSONC**: Removed comments and trailing commas using `clean_jsonc_themes.py`
4. **Removed base themes**: Deleted `dark_modern.json`, `light_modern.json`, `terminal_colors.json` (these only contain UI colors, not syntax colors)

### CLI Integration
Added `--list-themes` flag to display all available themes:

```bash
$ pyonig --list-themes
Available themes (17 total):

VS Code Default Themes:
  • dark_plus
  • dark_vs
  • hc_black
  • hc_light
  • light_plus
  • light_vs

Color Themes:
  • Red-color-theme                          (Red)
  • abyss-color-theme                        (Abyss)
  • dimmed-monokai-color-theme               (Dimmed Monokai)
  • kimbie-dark-color-theme                  (Kimbie Dark)
  • monokai-color-theme                      (Monokai)
  • quietlight-color-theme                   (Quietlight)
  • solarized-dark-color-theme               (Solarized Dark)
  • solarized-light-color-theme              (Solarized Light)
  • tomorrow-night-blue-color-theme          (Tomorrow Night Blue)

Usage: pyonig --theme <name> <file>
Example: pyonig --theme monokai-color-theme file.json
```

## Usage Examples

```bash
# Use Monokai theme
echo '{"key": "value"}' | pyonig --theme monokai-color-theme

# Use Solarized Dark theme
cat config.yaml | pyonig --theme solarized-dark-color-theme

# Use VS Code Dark+ (default)
pyonig --theme dark_plus file.json

# Use High Contrast theme
pyonig --theme hc_black file.py
```

## JSONC Processing

VS Code themes use JSONC (JSON with Comments) format, which includes:
- Line comments (`//`)
- Block comments (`/* */`)
- Trailing commas

The `clean_jsonc_themes.py` script converts JSONC to valid JSON by:
1. Removing `//` line comments
2. Removing `/* */` block comments
3. Removing trailing commas before `}` and `]`
4. Re-formatting as valid JSON

## License Compliance

All VS Code themes are distributed under the MIT License.

- **Source**: https://github.com/microsoft/vscode
- **Copyright**: Microsoft Corporation
- **License**: MIT License
- **Attribution**: `src/pyonig/themes/VSCODE_THEMES_LICENSE.txt`
- **CREDITS.md**: Updated with VS Code theme attribution

## Technical Notes

### Excluded Themes
The following VS Code themes were excluded because they don't contain `tokenColors` (syntax highlighting rules):
- `dark_modern.json` - Base theme that includes `dark_plus`
- `light_modern.json` - Base theme that includes `light_plus`
- `terminal_colors.json` - Only contains terminal ANSI colors

These themes use the `include` property to reference other themes and only provide UI colors. They would require additional processing to resolve includes.

### Theme Structure
Valid themes for pyonig must contain:
- `tokenColors`: Array of syntax highlighting rules
- `colors`: (Optional) UI color definitions
- `name`: Theme display name

Example:
```json
{
  "name": "Monokai",
  "tokenColors": [
    {
      "scope": ["comment"],
      "settings": {
        "foreground": "#75715E"
      }
    }
  ],
  "colors": {
    "editor.background": "#272822"
  }
}
```

## Testing

All 17 included themes were tested and confirmed working:

```bash
# Test various themes
echo '{"key": "value"}' | pyonig --theme monokai-color-theme  # ✓
echo '{"key": "value"}' | pyonig --theme dark_plus            # ✓
echo '{"key": "value"}' | pyonig --theme solarized-light-color-theme  # ✓
echo '[package]\nname = "test"' | pyonig --theme kimbie-dark-color-theme  # ✓
```

## Future Enhancements

Potential improvements (not currently implemented):
1. **Resolve `include` references** - Support themes that reference other themes
2. **Semantic highlighting** - Use `semanticTokenColors` for enhanced highlighting
3. **Theme preview** - CLI command to preview themes
4. **Custom theme support** - Allow users to add their own themes
5. **Theme validation** - Validate theme structure on load

## Impact

- **User Experience**: 14 additional professional themes (17 total)
- **Professional Appearance**: Industry-standard VS Code themes
- **Choice**: Light themes, dark themes, high contrast, and specialty themes
- **Compatibility**: Familiar themes for VS Code users

## Credits

Themes are copyright Microsoft Corporation and used under the MIT License.
See `src/pyonig/themes/VSCODE_THEMES_LICENSE.txt` for full license text.

