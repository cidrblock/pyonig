# PyOnig Development Status

## ✅ Completed

### 1. Project Structure
- Created proper project structure with `src/pyonig/` layout
- Configured `pyproject.toml` for modern Python packaging
- Set up `setup.py` for C extension compilation

### 2. Oniguruma Integration
- Added oniguruma as git submodule (`deps/oniguruma`)
- Configured and built oniguruma from source
- Successfully statically links oniguruma into Python extension

### 3. C Extension (`_pyonig`)
- ✅ **Working**: `compile(pattern)` - Compiles regex patterns
- ✅ **Working**: `Pattern.match(string, start=0, flags=0)` - Match at start of string
- ✅ **Working**: `Pattern.search(string, start=0, flags=0)` - Search anywhere in string  
- ✅ **Working**: `Pattern.number_of_captures()` - Returns capture group count
- ✅ **Working**: `Match.group(n)` - Get matched group text
- ✅ **Working**: `Match.start(n)`, `Match.end(n)`, `Match.span(n)` - Get positions
- ✅ **Working**: Unicode support (UTF-8 byte↔character offset conversion)
- ✅ **Working**: Search options (ONIG_OPTION_NOT_BEGIN_STRING, etc.)
- ⚠️  **Bug**: `compile_regset()` - RegSet functionality has a memory/logic bug
- ⚠️  **Missing**: `Match.expand()` - Backreference expansion not implemented

### 4. Module copied from ansible-navigator  
- ✅ Copied `tm_tokenize/` module (tokenization engine)
- ✅ Copied TextMate grammars (JSON, YAML, Shell, Markdown, HTML, Log)
- ✅ Copied themes (dark_vs.json, terminal_colors.json)
- ✅ Updated imports to use `pyonig` instead of `onigurumacffi`
- ⚠️  **Blocked**: Cannot test tm_tokenize until RegSet bug is fixed

### 5. Build System
- ✅ Compiles on Linux (Fedora 42, gcc)
- ✅ Proper config.h generation via autoconf
- ✅ All required oniguruma source files identified and included
- ✅ Extension builds with `python setup.py build_ext --inplace`

## 🔧 Known Issues

### Critical: RegSet Bug
The `compile_regset()` function and `_RegSet.search()` are not working correctly:
- Returns `(-1, None)` even when patterns should match
- Likely issue in how regset is created or how individual regexes are managed
- This blocks tm_tokenize which heavily uses RegSet for performance

**Impact**: Blocks syntax highlighting functionality

### Minor: Match.expand()
The `Match.expand()` method is stubbed but not implemented:
- Should expand backreferences like `\\1`, `\\2` in template strings
- Not critical for tm_tokenize functionality

## 📋 TODO

### High Priority
1. **Fix RegSet bug** - Debug and fix compile_regset/RegSet.search
2. **Test tm_tokenize** - Once RegSet works, verify tokenization
3. **Create Python wrapper** - Add context managers and convenience functions
4. **CLI utility** - Create `pyonig` command for syntax highlighting

### Medium Priority  
5. **Port unit tests** - Copy and adapt tests from onigurumacffi and ansible-navigator
6. **Implement Match.expand()** - Add backreference expansion
7. **Package for PyPI** - Create wheels with cibuildwheel

### Low Priority
8. **Documentation** - API docs, usage examples
9. **Performance testing** - Compare with onigurumacffi
10. **Windows/macOS support** - Test and fix platform-specific issues

## 🧪 Testing

### Manual Test Results
```python
import pyonig

# ✅ Basic compilation and matching
p = pyonig.compile('^foo')
m = p.match('food')
assert m.group(0) == 'foo'
assert m.start() == 0
assert m.end() == 3

# ✅ Search with capture groups
p2 = pyonig.compile('(a+)B+(c+)')
m2 = p2.search('zzzaaaBccczzz')
assert m2.group(0) == 'aaaBccc'
assert m2.group(1) == 'aaa'
assert m2.group(2) == 'ccc'
assert m2.start() == 3

# ✅ Unicode support
p3 = pyonig.compile('🙃+')
m3 = p3.search('hello🙃🙃🙃world')
assert m3.group(0) == '🙃🙃🙃'

# ❌ RegSet broken
regset = pyonig.compile_regset('a+', 'b+', 'c+')
idx, match = regset.search('zzzaaa')
# Returns (-1, None) instead of (0, <match>)
```

## 📦 Files

```
pyonig/
├── deps/
│   └── oniguruma/          # Git submodule (oniguruma C sources)
├── src/
│   └── pyonig/
│       ├── __init__.py       # Python API exports
│       ├── _pyonigmodule.c   # C extension implementation
│       ├── tm_tokenize/      # Tokenization engine (from ansible-navigator)
│       ├── grammars/         # TextMate grammar files (*.json)
│       └── themes/           # Color themes (*.json)
├── pyproject.toml          # Python packaging config
├── setup.py                # C extension build config
└── STATUS.md              # This file
```

## 🎯 Next Steps

The immediate priority is fixing the RegSet bug. Once that's resolved, the full syntax highlighting pipeline (pyonig → tm_tokenize → CLI) should work end-to-end.

