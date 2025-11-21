# PyOnig Progress Report

## ✅ MAJOR SUCCESS: RegSet Fixed!

The RegSet implementation was fixed! There were two critical bugs:

### Bug 1: Dangling Pointers (FIXED)
**Problem**: We were freeing the individual `regex_t*` objects immediately after creating the regset, but `onig_regset_new()` doesn't copy them - it just stores pointers. This left the regset with dangling pointers.

**Solution**: Keep the `regex_t**` array alive for the lifetime of the RegSet object.

### Bug 2: Double-Free (FIXED)  
**Problem**: `onig_regset_free()` already frees the individual regex objects, so we were double-freeing them in our dealloc method, causing segfaults.

**Solution**: Only free the array pointer in dealloc, not the regex objects themselves.

### RegSet Test Results
```python
✅ Basic RegSet matching works
✅ Multiple patterns work (returns correct index)
✅ Empty regsets work (return -1, None)
✅ No more segfaults
✅ Memory management is clean
```

## ⚠️ Current Issue: Tokenizer Hangs

### Symptoms
- First tokenization call works perfectly
- Second tokenization call hangs indefinitely
- Happens even with fresh state for each call

### What We Know
- ✅ The regex patterns themselves work fine in isolation
- ✅ RegSet works correctly when called directly
- ✅ Grammar loading works
- ✅ Compiler creation works
- ❌ Second call to `tokenize.tokenize()` hangs

### Test Results
```
Test 1 ('x'): Works fine → 1 region
Test 2 ('123'): Hangs during tokenization
```

### Next Steps
1. Add debug logging to tm_tokenize module to find infinite loop
2. Check if there's a circular reference or infinite recursion
3. Investigate regset caching in compiler
4. May need to review how `_Reg` objects are managed

## What's Working

### C Extension (`_pyonig`)
- ✅ `compile(pattern)` - Compiles regex patterns
- ✅ `Pattern.match()` / `Pattern.search()` - All working
- ✅ `Pattern.number_of_captures()` - Returns capture count
- ✅ `Match.group()`, `Match.start()`, `Match.end()`, `Match.span()` - All working
- ✅ Unicode/UTF-8 support with proper character offset conversion
- ✅ `compile_regset(*patterns)` - **NOW WORKING!**
- ✅ `RegSet.search()` - **NOW WORKING!**
- ✅ Empty regsets - **NOW WORKING!**
- ✅ Memory management - **NO MORE SEGFAULTS!**

### Project Structure
- ✅ Oniguruma submodule configured and building
- ✅ Static linking works (no system dependencies)
- ✅ pyproject.toml configured
- ✅ tm_tokenize module copied from ansible-navigator
- ✅ All TextMate grammars copied (JSON, YAML, Shell, Markdown, HTML, Log)
- ✅ Theme files copied

## Files Created/Modified

### New Files
- `src/pyonig/_pyonigmodule.c` - CPython extension (823 lines)
- `src/pyonig/__init__.py` - Python API
- `src/pyonig/tm_tokenize/` - Copied from ansible-navigator
- `src/pyonig/grammars/*.json` - TextMate grammars
- `src/pyonig/themes/*.json` - Color themes
- `setup.py` - Build configuration
- `deps/oniguruma/` - Git submodule

### Modified
- `pyproject.toml` - Updated for C extension build
- `src/pyonig/tm_tokenize/reg.py` - Updated imports to use pyonig

## Build Commands

```bash
# One-time setup
cd deps/oniguruma && autoreconf -vfi && ./configure

# Build extension
python setup.py build_ext --inplace

# Test
PYTHONPATH=src python3 -c "import pyonig; print(pyonig.__onig_version__)"
```

## Test Results Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Basic regex | ✅ | Compile, match, search all work |
| Unicode/UTF-8 | ✅ | Character offsets correct |
| Capture groups | ✅ | All group methods work |
| RegSet | ✅ | **FIXED!** Works perfectly |
| Empty RegSet | ✅ | Correctly returns no match |
| Memory safety | ✅ | **FIXED!** No segfaults |
| Grammar loading | ✅ | All grammars load |
| First tokenization | ✅ | Works correctly |
| Multiple tokenizations | ❌ | **Hangs on second call** |

## Performance Notes

The C extension is very fast:
- Direct CPython API (not CFFI overhead)
- Statically linked oniguruma
- No dynamic library loading
- UTF-8 native throughout

Once the tokenizer hang is fixed, this will be a high-performance drop-in replacement for onigurumacffi.

