# PyOnig

**Self-contained Oniguruma regex engine with TextMate grammar support for Python**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

[![asciicast](https://asciinema.org/a/k7fAcnGAqgkWnxvN0KMrhLY0n.svg)](https://asciinema.org/a/k7fAcnGAqgkWnxvN0KMrhLY0n)

PyOnig bundles the Oniguruma C regex library with TextMate grammar tokenization for high-performance syntax highlighting in Python. No system dependencies required.

**Documentation:** [docs/README.md](docs/README.md) | [API Usage](docs/API_USAGE.md) | [Building](docs/BUILDING.md) | [Testing](docs/TESTING.md)

## Features

- **Self-Contained** - Statically links Oniguruma (no libonig dependency)
- **Fast** - Direct CPython extension (not CFFI)
- **Syntax Highlighting** - Battle-tested colorization from ansible-navigator
- **Unicode** - Full UTF-8 support with character offsets
- **TextMate Grammars** - JSON, YAML, TOML, Shell, Markdown, HTML, CSS, JavaScript, TypeScript, Python
- **Smart Detection** - Auto-detects file types from content
- **VS Code Themes** - 17 built-in themes with auto-detection from VS Code settings
- **Drop-in Replacement** - Compatible with onigurumacffi API
- **CLI Tool** - Command-line syntax highlighting utility (`pyonig` or `po`)

## Quick Start

### Installation

```bash
# From source
git clone https://github.com/cidrblock/pyonig.git
cd pyonig
git submodule update --init --recursive

# Configure oniguruma (one-time)
cd deps/oniguruma
autoreconf -vfi
./configure --disable-shared --enable-static
cd ../..

# Install
pip install -e .
```

For pre-built wheels, see [Building Distribution Wheels](#building-distribution-wheels) below.

### Usage

**Basic Regex:**
```python
import pyonig

# Compile and search
pattern = pyonig.compile(r'(\d+):(\w+)')
match = pattern.search('  123:hello  ')
print(match.group(0))  # '123:hello'
print(match.span())    # (2, 11)
```

**Multiple Patterns (RegSet):**
```python
# Efficient multi-pattern matching
regset = pyonig.compile_regset(r'\d+', r'[a-z]+', r'[A-Z]+')
idx, match = regset.search('hello world')
print(f"Pattern {idx} matched: {match.group()}")  # Pattern 1 matched: hello
```

**Syntax Highlighting:**
```python
import pyonig

# High-level API
output = pyonig.highlight('{"key": "value"}', language='json', theme='monokai')
print(output)

# Or use the file helper
output = pyonig.highlight_file('data.json', theme='dark_plus')
```

**CLI:**
```bash
# Highlight a file (auto-detect language and theme from VS Code)
pyonig file.json
po file.json  # Short alias

# From stdin with custom theme
cat data.yaml | po --theme monokai

# List available themes
po --list-themes

# Override theme via environment
export PYONIG_THEME=dark_plus
cat data.json | po
```

## API Reference

### High-Level API

- `highlight(content, language=None, theme=None, output_format='ansi')` - Highlight text with syntax coloring
- `highlight_file(filepath, theme=None, output_format='ansi')` - Highlight a file with auto-detection
- `ThemeManager()` - Manage themes, aliases, and VS Code settings detection

See [docs/API_USAGE.md](docs/API_USAGE.md) for detailed examples.

### Core Regex Functions

- `compile(pattern)` → `Pattern` - Compile regex pattern
- `compile_regset(*patterns)` → `RegSet` - Compile multiple patterns

### Pattern Methods

- `Pattern.match(string, start=0, flags=0)` - Match at start
- `Pattern.search(string, start=0, flags=0)` - Search anywhere
- `Pattern.number_of_captures()` - Get capture count

### Match Methods

- `Match.group(n=0)` - Get matched text
- `Match.start(n=0)` / `Match.end(n=0)` - Get position (character offsets)
- `Match.span(n=0)` - Get (start, end) tuple

### RegSet Methods

- `RegSet.search(string, start=0, flags=0)` → `(index, Match | None)`

### Constants

- `ONIG_OPTION_NONE`
- `ONIG_OPTION_NOT_BEGIN_STRING`
- `ONIG_OPTION_NOT_BEGIN_POSITION`
- `ONIG_OPTION_NOT_END_STRING`

## Supported Languages

| Extension | Scope | Grammar |
|-----------|-------|---------|
| `.json` | `source.json` | JSON |
| `.yaml`, `.yml` | `source.yaml` | YAML |
| `.toml` | `source.toml` | TOML |
| `.sh`, `.bash` | `source.shell` | Shell/Bash |
| `.md` | `text.html.markdown` | Markdown |
| `.html`, `.htm` | `text.html.basic` | HTML |
| `.css` | `source.css` | CSS |
| `.js` | `source.js` | JavaScript |
| `.ts` | `source.ts` | TypeScript |
| `.py` | `source.python` | Python (MagicPython) |
| `.log` | `text.log` | Log files |

Content-based detection is supported when no filename is available. See [docs/CONTENT_DETECTION.md](docs/CONTENT_DETECTION.md) for details.

## Architecture

```
pyonig/
├── src/pyonig/
│   ├── _pyonigmodule.c       # CPython extension (~900 lines)
│   ├── __init__.py            # Python API
│   ├── api.py                 # High-level public API
│   ├── theme.py               # Theme management and VS Code integration
│   ├── cli.py                 # CLI utility
│   ├── detect.py              # Content-based language detection
│   ├── colorize.py            # Syntax highlighting (from ansible-navigator)
│   ├── tm_tokenize/           # TextMate tokenizer (from asottile)
│   ├── grammars/              # TextMate grammar files
│   └── themes/                # Color themes (17 VS Code themes)
├── deps/oniguruma/            # Oniguruma submodule (v6.9.10)
├── setup.py                   # Build configuration
├── pyproject.toml             # Project metadata
└── tox.ini                    # Multi-platform build automation
```

## Bug Fixes

PyOnig fixes several critical bugs found during development:

1. **RegSet Dangling Pointers** - Fixed lifetime management of regex objects
2. **RegSet Double-Free** - Fixed cleanup to prevent segfaults
3. **Tokenizer Infinite Loop** - Fixed end-of-string search behavior

See [docs/PROGRESS.md](docs/PROGRESS.md) for detailed bug analysis.

## Credits

PyOnig builds upon excellent open-source work:

- **Oniguruma** - K.Kosako (BSD-2-Clause)
- **tm_tokenize** - Anthony Sottile (MIT)
- **colorize module** - Red Hat / ansible-navigator (Apache-2.0)
- **TextMate grammars** - VS Code and community (MIT/Apache-2.0)
- **VS Code themes** - Microsoft (MIT)

See [docs/CREDITS.md](docs/CREDITS.md) for complete attribution.

## License

MIT License - see [LICENSE](LICENSE) for details

## Development

```bash
# Build extension
python setup.py build_ext --inplace

# Run tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=pyonig --cov-report=html
```

See [docs/TESTING.md](docs/TESTING.md) for detailed test documentation (119 tests, 100% coverage for critical modules).

### Building Distribution Wheels

PyOnig uses a portable, CI-agnostic build system based on [tox](https://tox.wiki/) and [manylinux](https://github.com/pypa/manylinux) containers:

```bash
# Install tox
pip install tox

# Build Linux wheels for all Python versions (x86_64)
tox -e build-wheels-linux-x86_64

# Build Linux wheels for ARM64 (requires qemu or native ARM64)
tox -e build-wheels-linux-aarch64

# Build all Linux wheels (x86_64 + ARM64)
tox -e build-wheels-linux-all

# Build macOS wheels (requires macOS)
tox -e build-wheels-macos

# Wheels output to dist/
ls -lh dist/*.whl
```

**Architecture:**
- Uses official [manylinux2014](https://github.com/pypa/manylinux) Docker images (no custom containers)
- Self-contained builds (Oniguruma compiles from source)
- Supports x86_64 and aarch64 (ARM64) architectures
- Platform-independent (works on any CI: GitHub, GitLab, Jenkins, etc.)

**GitHub Actions workflows:**
- **Tests** - Multi-platform testing (Linux, macOS x86_64, macOS ARM64)
- **Wheel builds** - Automated multi-platform wheel generation
- **Releases** - Publish to PyPI on tag push

**Documentation:**
- [docs/BUILDING.md](docs/BUILDING.md) - Complete build documentation
- [docs/WHEEL_BUILD_STATUS.md](docs/WHEEL_BUILD_STATUS.md) - Build status and results
- [.github/workflows/README.md](.github/workflows/README.md) - CI/CD workflow details
- [tox.ini](tox.ini) - Build environment configuration

## Status

**Version:** 0.1.0  
**Oniguruma:** 6.9.10  
**Python:** >=3.10  
**Status:** Functional and tested

### Test Coverage
- 119 tests passing, 9 skipped
- Core regex: 100% coverage
- Colorization: 100% coverage
- CLI: Full integration tests
- Memory: No leaks or segfaults detected

See [docs/TESTING.md](docs/TESTING.md) for complete test documentation.

## Contributing

Contributions welcome. Areas for improvement:

- Additional TextMate grammars
- More color themes
- Windows wheel support
- Performance optimizations
- Documentation and examples

## Related Projects

- [onigurumacffi](https://github.com/asottile/onigurumacffi) - CFFI bindings (requires system libonig)
- [ansible-navigator](https://github.com/ansible/ansible-navigator) - TUI for Ansible
- [babi](https://github.com/asottile/babi) - Text editor with tm_tokenize
