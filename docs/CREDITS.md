# Credits and Licenses

## Vendored Code Summary

**Files vendored from ansible-navigator (Apache-2.0):**
- `src/pyonig/tm_tokenize/**/*.py` - All Python files in tm_tokenize directory
- `src/pyonig/colorize.py` - Vendored from ansible-navigator/src/ansible_navigator/ui_framework/colorize.py
- `src/pyonig/curses_defs.py` - Vendored from ansible-navigator/src/ansible_navigator/ui_framework/curses_defs.py
- `src/pyonig/ui_constants.py` - Vendored from ansible-navigator/src/ansible_navigator/ui_framework/ui_constants.py
- `src/pyonig/grammars/*.json` (except `source.toml.json`) - From ansible-navigator/src/ansible_navigator/data/grammar/
- `src/pyonig/themes/terminal_colors.json`, `src/pyonig/themes/hc-black.json`, `src/pyonig/themes/hc-light.json` - From ansible-navigator/src/ansible_navigator/data/themes/

**Files from Visual Studio Code (MIT):**
- 17 VS Code theme files from microsoft/vscode (MIT License)
- See `src/pyonig/themes/VSCODE_THEMES_LICENSE.txt` for full attribution
- Themes include: Dark+, Light+, Monokai, Solarized Dark/Light, and more

**Files from other sources:**
- `src/pyonig/grammars/source.toml.json` - From Taplo (MIT) - https://github.com/tamasfe/taplo
- `deps/oniguruma/` - Git submodule (BSD-2-Clause) - https://github.com/kkos/oniguruma

**Original PyOnig code (MIT):**
- `src/pyonig/_pyonigmodule.c` - CPython extension wrapper
- `src/pyonig/__init__.py`, `src/pyonig/cli.py` - Python wrapper and CLI
- `setup.py`, `pyproject.toml` - Build system integration

## PyOnig Components

PyOnig is built upon several excellent open-source projects:

### Core Components

#### Oniguruma (BSD-2-Clause)
- **Source**: https://github.com/kkos/oniguruma
- **Author**: K.Kosako and contributors
- **License**: BSD-2-Clause
- **Usage**: Regex engine bundled as git submodule, statically linked into PyOnig
- **Location**: `deps/oniguruma/`

#### ansible-navigator Components (Apache-2.0)
- **Source**: https://github.com/ansible/ansible-navigator
- **Organization**: Red Hat
- **License**: Apache-2.0
- **Usage**: TextMate grammar tokenization and syntax highlighting
- **Vendored Files**:
  - `src/pyonig/tm_tokenize/` - **Complete directory** vendored from `ansible-navigator/src/ansible_navigator/tm_tokenize/`
    - TextMate grammar tokenization engine (originally from @asottile/babi, integrated into ansible-navigator)
    - All `.py` files in this directory
  - `src/pyonig/colorize.py` - From `ansible-navigator/src/ansible_navigator/ui_framework/colorize.py`
    - Color scheme handling and tokenization rendering
  - `src/pyonig/curses_defs.py` - From `ansible-navigator/src/ansible_navigator/ui_framework/curses_defs.py`
    - Curses line definitions and color types
  - `src/pyonig/ui_constants.py` - From `ansible-navigator/src/ansible_navigator/ui_framework/ui_constants.py`
    - UI constants for colors and decorations
  - `src/pyonig/grammars/*.json` - From `ansible-navigator/src/ansible_navigator/data/grammar/`
    - TextMate grammar files (except TOML, see below)
  - `src/pyonig/themes/*.json` - From `ansible-navigator/src/ansible_navigator/data/themes/`
    - Color theme files

**Modifications to vendored code**: 
- Updated `tm_tokenize/reg.py` to use `import pyonig` instead of `import onigurumacffi`
- Updated imports in `colorize.py` to use `pyonig.tm_tokenize` and local vendored modules
- All other files vendored without modifications

### TextMate Grammars

The following TextMate grammars are included. Each grammar file contains `information_for_contributors` metadata crediting the original source:

#### From ansible-navigator (Apache-2.0)
- **JSON** - `source.json.json`, `JSON.tmLanguage.json` - From microsoft/vscode-JSON.tmLanguage
- **YAML** - `source.yaml.json`, `yaml.tmLanguage.json` - From textmate/yaml.tmbundle
- **Shell/Bash** - `source.shell.json`, `shell-unix-bash.tmLanguage.json` - From atom/language-shellscript
- **Markdown** - `text.html.markdown.json`, `markdown.tmLanguage.json` - From microsoft/vscode-markdown-tm-grammar
- **HTML** - `text.html.basic.json`, `html.tmLanguage.json`, `html-derivative.tmLanguage.json`, `text.html.derivative.json` - From textmate/html.tmbundle
- **Log** - `text.log.json`, `log.tmLanguage.json` - From emilast/vscode-logfile-highlighter

#### Additional Grammars (MIT)
- **TOML** - `source.toml.json` - From tamasfe/taplo (MIT License)
  - Source: https://github.com/tamasfe/taplo/tree/master/editors/vscode
  - Downloaded separately, not from ansible-navigator

### Color Themes

- **Dark VS** (`dark_vs.json`) - From Visual Studio Code
- **Terminal Colors** (`terminal_colors.json`) - From ansible-navigator

## License Summary

PyOnig itself is released under the **MIT License**.

The bundled/vendored components retain their original licenses:
- **Oniguruma**: BSD-2-Clause (statically linked)
- **ansible-navigator components**: Apache-2.0 (vendored)
  - tm_tokenize module
  - colorize.py, curses_defs.py, ui_constants.py
  - TextMate grammars (except TOML)
  - Color themes
- **TOML grammar** (Taplo): MIT
- **Other TextMate grammars**: Various upstream licenses (MIT/Apache-2.0/BSD) - see individual files for details

## Acknowledgments

Special thanks to:

- **K.Kosako** - For creating and maintaining the excellent Oniguruma regex library
- **Anthony Sottile** (@asottile) - For the original tm_tokenize implementation in babi (later integrated into ansible-navigator)
- **Red Hat** / **ansible-navigator team** - For the robust colorize module, grammar integration, and tm_tokenize maintenance
- **Tamas Feng** (@tamasfe) - For the Taplo TOML language server and TextMate grammar
- **Visual Studio Code team** - For TextMate grammars and themes
- **TextMate contributors** - For creating the TextMate grammar specification

## Full License Texts

See the `licenses/` directory for complete license texts of all components.

## Contributions

PyOnig was created by Bradley A. Thornton (@bthornto) at Red Hat.

The primary contribution of PyOnig is:
1. C extension wrapper (`_pyonigmodule.c`) - wrapping Oniguruma for Python
2. Build system integration - statically linking Oniguruma
3. CLI utility - making syntax highlighting accessible from command line
4. Integration layer - connecting all components into a cohesive package
5. Bug fixes - resolving RegSet and tokenization issues

## Reporting Issues

If you encounter issues with:
- **C extension / RegSet**: Report to PyOnig
- **Tokenization logic**: May be upstream in tm_tokenize
- **Color rendering**: May be upstream in ansible-navigator
- **Grammars**: May be upstream in respective VS Code extensions

When reporting, please specify which component is affected.

