# Content-Based File Type Detection

## Overview

The `pyonig.detect` module provides intelligent, heuristic-based file type detection from raw content. This is essential for scenarios where filenames are not available, such as piping content through the CLI.

## Usage

### Python API

```python
from pyonig.detect import detect_type, detect_scope

# Detect general content type
content = b'{"key": "value"}'
file_type = detect_type(content)  # Returns: "json"

# Detect TextMate scope name (ready for syntax highlighting)
scope = detect_scope(content)  # Returns: "source.json"
```

### CLI Integration

The CLI automatically uses content detection when:
1. Reading from stdin without a filename
2. Filename-based detection fails

```bash
# Automatic content detection
cat config.toml | pyonig

# Works even without filename
echo '{"test": true}' | pyonig
```

## Supported Types

| Type | Indicators | Priority | Scope Name |
|------|-----------|----------|------------|
| **JSON** | `{` or `[` at start, validates with parser | 1 | `source.json` |
| **Log** | Timestamps, log levels (`[INFO]`, `[ERROR]`) | 2 | `text.log` |
| **TOML** | `[section]` headers, `key = value` pairs | 3 | `source.toml` |
| **Markdown** | Headers (`#`), lists (`-`, `*`), code blocks | 4 | `text.html.markdown` |
| **YAML** | `---`, `key: value`, list items | 5 | `source.yaml` |
| **HTML** | `<html>`, `<!DOCTYPE>`, tags | 6 | `text.html.basic` |
| **Shell** | Shebang `#!/bin/bash` | 7 | `source.shell` |
| **Text** | Valid UTF-8, fallback | 8 | `text.plain` |
| **Binary** | Non-UTF-8 data | 9 | `None` |

## Detection Algorithm

### 1. **Early Checks** (High Confidence)
- **Shebang**: `#!/bin/bash` → Shell
- **JSON Structure**: Starts with `{` or `[` and validates → JSON

### 2. **Priority Detection** (Ambiguity Resolution)
Detection order matters for ambiguous cases:
1. **Log files** (checked early to avoid YAML confusion due to colons)
2. **TOML** (checked before Markdown due to `#` comments)
3. **Markdown** (checked before YAML due to `-` lists)
4. **YAML** (most flexible format)

### 3. **Indicator Accumulation**
Each format accumulates "indicators" (confidence points):
- Strong indicators: +2 or +3 points (e.g., `[section]` for TOML)
- Weak indicators: +1 point (e.g., single `key = value`)
- Threshold: Usually 2+ points, lower for short content

### 4. **Ambiguity Handling**
Special logic for confusing patterns:
- **Markdown vs YAML**: If `key: value` patterns found → skip Markdown
- **TOML vs Markdown**: If `[section]` found → TOML takes precedence
- **Short content**: Lower thresholds (1 indicator for <5 lines)

## Examples

### JSON Detection
```python
assert detect_type(b'{"key": "value"}') == "json"
assert detect_type(b'[1, 2, 3]') == "json"
```

### TOML Detection
```python
assert detect_type(b'[database]\nserver = "192.168.1.1"') == "toml"
assert detect_type(b'key = "value"') == "toml"
```

### YAML Detection
```python
assert detect_type(b'---\nkey: value') == "yaml"
assert detect_type(b'- item1\n- item2') == "yaml"
```

### Markdown Detection
```python
assert detect_type(b'# Header\n\nParagraph') == "markdown"
assert detect_type(b'- List item\n- Another') == "markdown"
```

### Log Detection
```python
assert detect_type(b'2024-01-01 10:00:00 [INFO] Starting...') == "log"
assert detect_type(b'[ERROR] Failed to connect') == "log"
```

## Edge Cases

### Ambiguous Content
```python
# Markdown wins (has header)
detect_type(b'# Title\n- item')  # → "markdown"

# YAML wins (has key:value)
detect_type(b'key: value\n- item')  # → "yaml"

# TOML wins (has [section])
detect_type(b'# Comment\n[section]')  # → "toml"
```

### Short Content
For content with <5 lines, detection uses lower thresholds:
```python
detect_type(b'key = "value"')  # → "toml" (1 indicator)
detect_type(b'key: value')     # → "yaml" (1 indicator)
detect_type(b'# Header')       # → "markdown" (1 indicator)
```

### Binary Content
```python
detect_type(b'\x80\x81\x82')  # → "binary"
detect_scope(b'\x80\x81\x82')  # → None
```

## Testing

The detection module has comprehensive test coverage (56 tests):

```bash
# Run detection tests
pytest tests/test_detect.py -v

# Test categories
pytest tests/test_detect.py::TestDetectJSON -v      # 4 tests
pytest tests/test_detect.py::TestDetectTOML -v      # 5 tests
pytest tests/test_detect.py::TestDetectYAML -v      # 6 tests
pytest tests/test_detect.py::TestDetectMarkdown -v  # 10 tests
pytest tests/test_detect.py::TestDetectLog -v       # 5 tests
pytest tests/test_detect.py::TestAmbiguousCases -v  # 3 tests
pytest tests/test_detect.py::TestRealWorldExamples -v  # 4 tests
```

### Real-World Test Data
```python
# package.json detection
package_json = b'{\n  "name": "test",\n  "version": "1.0.0"\n}'
assert detect_type(package_json) == "json"

# Cargo.toml detection
cargo_toml = b'[package]\nname = "test"\nversion = "0.1.0"'
assert detect_type(cargo_toml) == "toml"

# GitHub Actions YAML
workflow = b'name: CI\non: [push, pull_request]'
assert detect_type(workflow) == "yaml"

# README.md
readme = b'# Project\n\n## Features\n\n- Feature 1'
assert detect_type(readme) == "markdown"
```

## Performance

- **Efficient**: Only examines first 4KB of content
- **Fast**: Uses compiled regex patterns
- **Scalable**: O(n) complexity where n = number of lines examined

## Limitations

1. **Not 100% Accurate**: Heuristic-based, not parsing-based
2. **Ambiguous Cases**: Some content is genuinely ambiguous
3. **Short Content**: May need more context for accurate detection
4. **Custom Formats**: Only detects common, standard formats

## Future Enhancements

Potential improvements (not currently planned):
- Machine learning-based detection
- Language-specific tokenizers
- User-configurable detection rules
- Confidence scores in addition to type
- Support for more formats (XML, SQL, etc.)

## Credits

Detection logic inspired by:
- [GitHub Linguist](https://github.com/github/linguist)
- [file(1) magic database](https://www.darwinsys.com/file/)
- Best practices from various language parsers

## License

This detection logic is part of the pyonig project and is licensed under the MIT License.

