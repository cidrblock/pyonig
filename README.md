# PyOnig

**Self-contained Oniguruma regex engine with TextMate grammar support for Python**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

PyOnig bundles the Oniguruma C regex library with TextMate grammar tokenization for high-performance syntax highlighting in Python. **No system dependencies required!**

## ✨ Features

- 🚀 **Self-Contained** - Statically links Oniguruma (no libonig dependency)
- ⚡ **Fast** - Direct CPython extension (not CFFI)
- 🎨 **Syntax Highlighting** - Battle-tested colorization from ansible-navigator
- 🌍 **Unicode** - Full UTF-8 support with character offsets
- 📝 **TextMate Grammars** - JSON, YAML, TOML, Shell, Markdown, HTML, Log
- 🔍 **Smart Detection** - Auto-detects file types from content
- 🎯 **Drop-in Replacement** - Compatible with onigurumacffi API
- 🖥️ **CLI Tool** - Command-line syntax highlighting utility

## 🚀 Quick Start

### Installation

```bash
# Clone and setup
git clone https://github.com/yourusername/pyonig.git
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
from pyonig.colorize import Colorize

colorizer = Colorize(
    grammar_dir='src/pyonig/grammars',
    theme_path='src/pyonig/themes/dark_vs.json'
)
colorized = colorizer.render('{"key": "value"}', 'source.json')
```

**CLI:**
```bash
# Highlight a file (auto-detect language)
pyonig file.json

# From stdin with custom theme
cat data.yaml | pyonig -l yaml --colors 256

# List supported languages
pyonig --list-languages
```

## 📚 API Reference

### Core Functions

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

## 🎨 Supported Languages

| Extension | Scope | Grammar |
|-----------|-------|---------|
| `.json` | `source.json` | JSON |
| `.yaml`, `.yml` | `source.yaml` | YAML |
| `.sh`, `.bash` | `source.shell` | Shell/Bash |
| `.md` | `text.html.markdown` | Markdown |
| `.html`, `.htm` | `text.html.basic` | HTML |
| `.log` | `text.log` | Log files |

## 🏗️ Architecture

```
pyonig/
├── src/pyonig/
│   ├── _pyonigmodule.c       # CPython extension (~900 lines)
│   ├── __init__.py            # Python API
│   ├── cli.py                 # CLI utility
│   ├── colorize.py            # Syntax highlighting (from ansible-navigator)
│   ├── tm_tokenize/           # TextMate tokenizer (from asottile)
│   ├── grammars/              # TextMate grammar files
│   └── themes/                # Color themes
├── deps/oniguruma/            # Oniguruma submodule (v6.9.10)
├── setup.py                   # Build configuration
└── pyproject.toml             # Project metadata
```

## 🐛 Bug Fixes

PyOnig fixes several critical bugs found during development:

1. **RegSet Dangling Pointers** - Fixed lifetime management of regex objects
2. **RegSet Double-Free** - Fixed cleanup to prevent segfaults
3. **Tokenizer Infinite Loop** - Fixed end-of-string search behavior

See [PROGRESS.md](PROGRESS.md) for detailed bug analysis.

## 🙏 Credits

PyOnig builds upon excellent open-source work:

- **Oniguruma** - K.Kosako (BSD-2-Clause)
- **tm_tokenize** - Anthony Sottile (MIT)
- **colorize module** - Red Hat / ansible-navigator (Apache-2.0)
- **TextMate grammars** - VS Code (MIT/Apache-2.0)

See [CREDITS.md](CREDITS.md) for complete attribution.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🔧 Development

```bash
# Build extension
python setup.py build_ext --inplace

# Test
python -m pytest tests/

# See TESTING.md for detailed test documentation
# 110 passing, 9 skipped
```

### Building Distribution Wheels

PyOnig uses a **portable, CI-agnostic build system** based on tox and manylinux containers:

```bash
# Install tox
pip install tox

# Build Linux wheels (x86_64 + ARM64)
tox -e build-wheels-linux-all

# Build macOS wheels (on macOS)
tox -e build-wheels-macos

# Build all wheels
tox -e build-wheels-all

# Wheels appear in dist/
ls -lh dist/*.whl
```

**Key features:**
- ✅ Works on **any CI platform** (GitHub, GitLab, Jenkins, etc.)
- ✅ Uses **official manylinux containers** (no custom images needed)
- ✅ **Self-contained** - Oniguruma compiles from source
- ✅ Builds for **x86_64** and **aarch64** (ARM64)

**GitHub Actions workflows included:**
- 🧪 **Tests** - Every push/PR on Linux, macOS x86_64, macOS ARM64
- 📦 **Wheel builds** - Automatic multi-platform wheel generation
- 🚀 **Releases** - Publish to PyPI on tag push

See [BUILDING.md](BUILDING.md) and [`.github/workflows/README.md`](.github/workflows/README.md) for complete documentation.

## 📊 Status

**Version:** 0.1.0  
**Oniguruma:** 6.9.10  
**Python:** >=3.10  
**Status:** Functional and tested

### Test Results
```
✅ Basic regex (compile, match, search)
✅ Capture groups and offsets  
✅ Unicode/UTF-8 support
✅ RegSet with multiple patterns
✅ End-of-string handling
✅ Memory management (no leaks/segfaults)
✅ JSON/YAML/Shell syntax highlighting
✅ Multiple tokenization calls
✅ CLI with ANSI color output
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional TextMate grammars (Python, JavaScript, etc.)
- More color themes
- Windows wheel support
- Documentation and examples

## 📞 Contact

**Author:** Bradley A. Thornton  
**Email:** bthornto@redhat.com  
**Organization:** Red Hat

## 🔗 Related Projects

- [onigurumacffi](https://github.com/asottile/onigurumacffi) - CFFI bindings (requires system libonig)
- [ansible-navigator](https://github.com/ansible/ansible-navigator) - TUI for Ansible
- [babi](https://github.com/asottile/babi) - Text editor with tm_tokenize
