# pyonig Public API - Usage Guide

## Overview

pyonig can be used as both a CLI tool and a Python library. This guide covers the library API.

## Installation

```bash
pip install pyonig
```

## Quick Start

```python
import pyonig

# Highlight JSON
code = '{"name": "test", "value": 123}'
highlighted = pyonig.highlight(code, language='json', theme='monokai')
print(highlighted)
```

## API Reference

### Main Functions

#### `highlight(content, language=None, theme=None, output='ansi', colors=256)`

Highlight source code with syntax highlighting.

**Parameters:**
- `content` (str | bytes): Source code to highlight
- `language` (str, optional): Language/scope name (e.g., 'json', 'yaml', 'source.json')
  - If None, attempts auto-detection from content
- `theme` (str, optional): Theme name, alias, or path to theme file
  - If None, uses default (PYONIG_THEME env var, VS Code settings, or 'dark')
- `output` (str): Output format - 'ansi' for terminal or 'simple' for structured data
- `colors` (int): Number of terminal colors for ANSI output (8, 16, or 256)

**Returns:**
- If `output='ansi'`: String with ANSI escape codes
- If `output='simple'`: List of lists of SimpleLinePart objects

**Raises:**
- `ValueError`: If language cannot be detected or theme not found

**Example:**
```python
import pyonig

# Basic usage
code = '{"key": "value"}'
result = pyonig.highlight(code, language='json', theme='monokai')
print(result)  # Colored JSON

# Auto-detect language
code = '{"key": "value"}'
result = pyonig.highlight(code)  # Detects JSON automatically

# Use VS Code theme
result = pyonig.highlight(code, language='json')  # Uses your VS Code theme

# Different output formats
ansi_output = pyonig.highlight(code, language='json', output='ansi')
simple_output = pyonig.highlight(code, language='json', output='simple')
```

#### `highlight_file(path, language=None, theme=None, output='ansi', colors=256)`

Highlight a source code file.

**Parameters:**
- `path` (str | Path): Path to source code file
- `language` (str, optional): Language/scope name
  - If None, detects from filename and content
- `theme` (str, optional): Theme name, alias, or path
- `output` (str): Output format
- `colors` (int): Number of terminal colors

**Returns:**
- If `output='ansi'`: String with ANSI escape codes
- If `output='simple'`: List of lists of SimpleLinePart objects

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If language cannot be detected or theme not found

**Example:**
```python
import pyonig

# Highlight a file
result = pyonig.highlight_file('config.json', theme='monokai')
print(result)

# Auto-detect from filename
result = pyonig.highlight_file('app.py')  # Detects Python

# Override detection
result = pyonig.highlight_file('data.txt', language='json')
```

#### `detect_language(filename=None, content=None)`

Detect language from filename extension or content.

**Parameters:**
- `filename` (str, optional): Filename to detect from extension
- `content` (bytes, optional): Content bytes for content-based detection

**Returns:**
- `str`: TextMate scope name (e.g., 'source.json')
- `None`: If detection failed

**Example:**
```python
import pyonig

# Detect from filename
scope = pyonig.detect_language(filename='test.json')
print(scope)  # 'source.json'

# Detect from content
scope = pyonig.detect_language(content=b'{"key": "value"}')
print(scope)  # 'source.json'

# Both (filename has priority)
scope = pyonig.detect_language(
    filename='test.json',
    content=b'key: value'  # YAML content but JSON filename
)
print(scope)  # 'source.json' (filename wins)
```

### ThemeManager Class

#### `ThemeManager(theme_dir=None)`

Manages theme detection, resolution, and loading.

**Parameters:**
- `theme_dir` (Path, optional): Directory containing theme files
  - Defaults to package themes/

**Methods:**

##### `get_default() -> str`

Get the default theme name (respects env vars and VS Code settings).

**Returns:**
- `str`: Theme name

**Example:**
```python
from pyonig import ThemeManager

tm = ThemeManager()
default = tm.get_default()
print(f"Default theme: {default}")
```

##### `resolve(theme_name: str) -> str`

Resolve a theme alias to actual filename.

**Parameters:**
- `theme_name` (str): Theme name or alias

**Returns:**
- `str`: Resolved theme filename (without .json)

**Example:**
```python
tm = ThemeManager()
print(tm.resolve('monokai'))  # 'monokai-color-theme'
print(tm.resolve('dark'))     # 'dark_vs'
```

##### `find_path(theme_name: str) -> Path | None`

Find the full path to a theme file.

**Parameters:**
- `theme_name` (str): Theme name, alias, or path

**Returns:**
- `Path`: Path to theme file
- `None`: If not found

**Example:**
```python
tm = ThemeManager()
path = tm.find_path('monokai')
if path:
    print(f"Theme at: {path}")
```

##### `list_themes() -> list[tuple[str, list[str]]]`

List all available themes with their aliases.

**Returns:**
- `list`: List of (theme_filename, [aliases]) tuples

**Example:**
```python
tm = ThemeManager()
for name, aliases in tm.list_themes():
    if aliases:
        print(f"{name}: {', '.join(aliases)}")
    else:
        print(name)
```

## Supported Languages

| Extension | Scope Name | Description |
|-----------|------------|-------------|
| `json` | `source.json` | JSON |
| `yaml`, `yml` | `source.yaml` | YAML |
| `toml` | `source.toml` | TOML |
| `sh`, `bash`, `shell` | `source.shell` | Shell scripts |
| `md`, `markdown` | `text.html.markdown` | Markdown |
| `html`, `htm` | `text.html.basic` | HTML |
| `log` | `text.log` | Log files |

You can also use TextMate scope names directly (e.g., `source.python`, `text.html.basic`).

## Themes

### Built-in Themes

**VS Code Default Themes:**
- `dark_vs` (alias: `dark`) - Visual Studio Dark
- `light_vs` (alias: `light`) - Visual Studio Light
- `dark_plus` (alias: `dark+`) - Dark+
- `light_plus` (alias: `light+`) - Light+
- `hc_black` (alias: `hc-black`) - Dark High Contrast
- `hc_light` (alias: `hc-light`) - Light High Contrast

**Color Themes:**
- `monokai-color-theme` (alias: `monokai`) - Monokai
- `dimmed-monokai-color-theme` (alias: `monokai-dimmed`) - Monokai Dimmed
- `solarized-dark-color-theme` (alias: `solarized-dark`) - Solarized Dark
- `solarized-light-color-theme` (alias: `solarized-light`) - Solarized Light
- `abyss-color-theme` (alias: `abyss`) - Abyss
- `kimbie-dark-color-theme` (alias: `kimbie-dark`) - Kimbie Dark
- `quietlight-color-theme` (alias: `quietlight`) - Quiet Light
- `Red-color-theme` (alias: `red`) - Red
- `tomorrow-night-blue-color-theme` (alias: `tomorrow-night-blue`) - Tomorrow Night Blue

### Theme Auto-Detection

Themes are selected in this priority order:

1. **Explicit `theme` parameter** (highest priority)
2. **`PYONIG_THEME` environment variable**
3. **VS Code user settings** (`workbench.colorTheme`)
4. **'dark' fallback** (lowest priority)

**Example:**
```python
import os
import pyonig

# 1. Explicit theme (highest priority)
result = pyonig.highlight(code, theme='monokai')

# 2. Environment variable
os.environ['PYONIG_THEME'] = 'solarized-dark'
result = pyonig.highlight(code)  # Uses solarized-dark

# 3. VS Code settings (if PYONIG_THEME not set)
# Reads from ~/.config/Code/User/settings.json
result = pyonig.highlight(code)  # Uses your VS Code theme

# 4. Default fallback (if nothing else set)
result = pyonig.highlight(code)  # Uses 'dark'
```

## Output Formats

### ANSI Output (default)

Produces a string with ANSI escape codes for terminal display.

```python
result = pyonig.highlight(code, language='json', output='ansi')
print(result)  # Prints with colors in terminal
```

### Simple Output

Produces structured data (list of lists of `SimpleLinePart` objects) for custom rendering.

```python
result = pyonig.highlight(code, language='json', output='simple')

for line_parts in result:
    for part in line_parts:
        text = part.chars  # The text content
        color = part.color  # RGB tuple (r, g, b) or None
        
        if color:
            r, g, b = color
            print(f"[RGB {r},{g},{b}] {text}", end='')
        else:
            print(text, end='')
    print()  # Newline
```

## Complete Examples

### Example 1: Syntax Highlighting Web Service

```python
from flask import Flask, request, jsonify
import pyonig

app = Flask(__name__)

@app.route('/highlight', methods=['POST'])
def highlight_code():
    data = request.json
    code = data.get('code', '')
    language = data.get('language', None)
    theme = data.get('theme', 'monokai')
    
    try:
        # Get structured output for custom rendering
        highlighted = pyonig.highlight(
            code,
            language=language,
            theme=theme,
            output='simple'
        )
        
        # Convert to JSON-friendly format
        lines = []
        for line_parts in highlighted:
            parts = []
            for part in line_parts:
                parts.append({
                    'text': part.chars,
                    'color': part.color  # (r, g, b) or None
                })
            lines.append(parts)
        
        return jsonify({'success': True, 'lines': lines})
    
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    app.run()
```

### Example 2: Documentation Generator

```python
import pyonig
from pathlib import Path

def generate_highlighted_docs(source_dir, output_dir, theme='monokai'):
    """Generate HTML docs with syntax-highlighted code blocks."""
    
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    for source_file in source_dir.rglob('*.py'):
        # Read source
        code = source_file.read_text()
        
        # Get structured output
        highlighted = pyonig.highlight(
            code,
            language='python',
            theme=theme,
            output='simple'
        )
        
        # Convert to HTML
        html_lines = []
        for line_parts in highlighted:
            line_html = []
            for part in line_parts:
                text = part.chars.replace('<', '&lt;').replace('>', '&gt;')
                if part.color:
                    r, g, b = part.color
                    style = f"color: rgb({r}, {g}, {b});"
                    line_html.append(f'<span style="{style}">{text}</span>')
                else:
                    line_html.append(text)
            html_lines.append(''.join(line_html))
        
        # Write output
        output_file = output_dir / (source_file.stem + '.html')
        output_file.write_text(f'''
<!DOCTYPE html>
<html>
<head>
    <title>{source_file.name}</title>
    <style>
        pre {{ background: #1e1e1e; padding: 1em; overflow: auto; }}
        code {{ font-family: monospace; }}
    </style>
</head>
<body>
    <h1>{source_file.name}</h1>
    <pre><code>{'<br>'.join(html_lines)}</code></pre>
</body>
</html>
''')
        
        print(f"Generated: {output_file}")

# Usage
generate_highlighted_docs('src/', 'docs/html/')
```

### Example 3: Terminal Pager with Syntax Highlighting

```python
import pyonig
import sys
from pathlib import Path

def highlight_and_page(filename, theme='monokai'):
    """Highlight a file and page through it."""
    
    # Highlight the file
    result = pyonig.highlight_file(
        filename,
        theme=theme,
        output='ansi'
    )
    
    # Page through it (requires 'less' command)
    import subprocess
    subprocess.run(['less', '-R'], input=result.encode(), check=False)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python pager.py <file>")
        sys.exit(1)
    
    highlight_and_page(sys.argv[1])
```

### Example 4: Custom Theme Management

```python
import pyonig
from pathlib import Path

# List all themes
tm = pyonig.ThemeManager()

print("Available themes:")
for name, aliases in tm.list_themes():
    if aliases:
        print(f"  {name} (aliases: {', '.join(aliases)})")
    else:
        print(f"  {name}")

# Use custom theme directory
custom_tm = pyonig.ThemeManager(theme_dir=Path('./my-themes'))

# Find a theme
theme_path = custom_tm.find_path('my-custom-theme')
if theme_path:
    print(f"Found theme at: {theme_path}")
    
    # Use it
    code = '{"key": "value"}'
    result = pyonig.highlight(code, language='json', theme=str(theme_path))
    print(result)
```

## Error Handling

```python
import pyonig

try:
    # Invalid UTF-8
    result = pyonig.highlight(b'\x80\x81\x82', language='json')
except ValueError as e:
    print(f"Error: {e}")  # "Content is not valid UTF-8"

try:
    # Language detection failed
    result = pyonig.highlight("some random text")
except ValueError as e:
    print(f"Error: {e}")  # "Could not auto-detect language"

try:
    # Theme not found
    result = pyonig.highlight(code, language='json', theme='nonexistent')
except ValueError as e:
    print(f"Error: {e}")  # "Theme not found: nonexistent"

try:
    # File not found
    result = pyonig.highlight_file('/nonexistent/file.json')
except FileNotFoundError as e:
    print(f"Error: {e}")  # "File not found: /nonexistent/file.json"
```

## Best Practices

1. **Always specify language when known** - it's faster than auto-detection
2. **Use PYONIG_THEME env var** for project/session defaults
3. **Use `output='simple'`** for custom rendering (HTML, RTF, etc.)
4. **Cache ThemeManager instances** if loading many themes
5. **Handle errors gracefully** - especially for user-provided input

## Performance Tips

- Language detection from filename is faster than content-based detection
- Reuse `ThemeManager` instances instead of creating new ones
- For large files, consider streaming or chunking
- ANSI output is faster than simple output for terminal display

## See Also

- [CLI Usage](README.md#cli-usage)
- [Theme Auto-Detection](THEME_AUTO_DETECTION.md)
- [Theme Aliases](THEME_ALIASES.md)
- [Content Detection](CONTENT_DETECTION.md)

