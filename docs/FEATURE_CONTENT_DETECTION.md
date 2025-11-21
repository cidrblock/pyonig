# Feature: Content-Based File Type Detection

## Summary

Added intelligent content-based file type detection to pyonig, enabling accurate language detection when filenames are not available (e.g., piping via stdin).

## Implementation

### New Module: `src/pyonig/detect.py`
- **Lines**: 270
- **Functions**: `detect_type()`, `detect_scope()`
- **Supported Types**: JSON, TOML, YAML, Markdown, HTML, Shell, Log, Text, Binary

### Detection Strategy
1. **High-Confidence Checks First** (Shell shebang, JSON structure validation)
2. **Priority Ordering** (Log → TOML → Markdown → YAML to resolve ambiguities)
3. **Indicator Accumulation** (Point system with dynamic thresholds)
4. **Ambiguity Resolution** (Cross-checks between similar formats)

### CLI Integration
Updated `src/pyonig/cli.py` to use content detection as fallback when filename-based detection fails.

## Test Coverage

### New Test Suite: `tests/test_detect.py`
- **Total Tests**: 56 (100% passing)
- **Lines**: 380+
- **Categories**:
  - JSON Detection: 4 tests
  - TOML Detection: 5 tests  
  - YAML Detection: 6 tests
  - Markdown Detection: 10 tests
  - Shell Detection: 3 tests
  - HTML Detection: 2 tests
  - Log Detection: 5 tests
  - Text/Binary: 4 tests
  - Scope Detection: 4 tests
  - Ambiguous Cases: 3 tests
  - Large Input: 2 tests
  - Real-World Examples: 4 tests
  - Edge Cases: 4 tests

### Test Quality
- Comprehensive coverage of common formats
- Edge case handling (empty input, binary data, short content)
- Ambiguous content scenarios (YAML vs Markdown, TOML vs Markdown)
- Real-world data (package.json, Cargo.toml, GitHub workflows, README.md)

## Documentation

### New Files
1. **CONTENT_DETECTION.md** (450+ lines)
   - Overview and usage examples
   - Supported types table
   - Detection algorithm explanation
   - Edge cases and ambiguity handling
   - Performance characteristics
   - Testing guide
   
2. **FEATURE_CONTENT_DETECTION.md** (this file)
   - Implementation summary
   - Test coverage breakdown

### Updated Files
1. **README.md**
   - Added "Smart Detection" to features list
   - Added content detection API examples
   - Updated CLI examples to show content detection

## Usage Examples

### Python API
```python
from pyonig.detect import detect_type, detect_scope

# Detect from content
content = b'[database]\nserver = "localhost"'
assert detect_type(content) == "toml"
assert detect_scope(content) == "source.toml"
```

### CLI (Automatic)
```bash
# Works without filename
cat Cargo.toml | pyonig

# Detects from piped content
echo '{"test": true}' | pyonig

# Even works with complex YAML
kubectl get pods -o yaml | pyonig
```

## Detection Accuracy

### Strengths
- **High accuracy for structured formats** (JSON, TOML with sections)
- **Robust ambiguity resolution** (prioritizes more specific indicators)
- **Fast detection** (only reads first 4KB)

### Limitations
- **Heuristic-based** (not parser-based, can have false positives)
- **Ambiguous edge cases** (e.g., YAML list vs Markdown list)
- **Requires content** (minimum 1-2 lines for reliable detection)

## Performance

- **Fast**: O(n) where n = lines examined (max 50)
- **Efficient**: Only reads first 4KB of content
- **No dependencies**: Uses only stdlib (json, re)

## Future Enhancements (Not Implemented)

Potential improvements for consideration:
- XML/SVG detection
- SQL detection
- More programming languages (Python, JavaScript, Go, Rust)
- Confidence scores
- User-configurable detection rules

## Technical Decisions

### Why heuristics over parsing?
- **Performance**: Parsing every format is expensive
- **Simplicity**: Single, maintainable detection module
- **Speed**: Quick checks without full grammar loading

### Why this detection order?
1. **Shell** (shebang is unique and high-confidence)
2. **JSON** (validates with parser)
3. **Log** (timestamps would confuse YAML)
4. **TOML** (sections would confuse Markdown)
5. **Markdown** (lists would confuse YAML)
6. **YAML** (most flexible, checked last)

### Why indicator thresholds?
- **Flexibility**: Different formats need different confidence levels
- **Short content handling**: Lower thresholds for <5 lines
- **Ambiguity resolution**: Multiple indicators prevent false positives

## Integration Points

### Modules Using Detection
- `cli.py`: Falls back to content detection when filename detection fails
- Future: Could be used by `colorize.py` for scope inference

### API Stability
- **Public API**: `detect_type()`, `detect_scope()`
- **Return types**: `str | None` for type, `str | None` for scope
- **No breaking changes**: Pure addition, no modifications to existing APIs

## Test Results

```bash
$ PYTHONPATH=src pytest tests/test_detect.py -v
============================== 56 passed in 0.13s ==============================
```

All tests passing, including:
- ✅ Format-specific detection (JSON, TOML, YAML, etc.)
- ✅ Ambiguous content resolution
- ✅ Edge cases (empty, binary, whitespace-only)
- ✅ Real-world examples
- ✅ Large input handling

## Comparison with Similar Tools

| Tool | Approach | Languages | Speed | Accuracy |
|------|----------|-----------|-------|----------|
| **pyonig.detect** | Heuristics | 9 types | Very Fast | Good |
| GitHub Linguist | ML + heuristics | 500+ | Medium | Excellent |
| file(1) magic | Magic bytes + patterns | 1000s | Fast | Excellent |
| pygments | Lexer-based | 500+ | Slow | Excellent |

**pyonig.detect** trades comprehensive language support for:
- **Zero dependencies** (no ML models, no external files)
- **Blazing speed** (simple regex checks)
- **Targeted use case** (just the formats pyonig supports)

## Credits

Detection logic inspired by:
- [GitHub Linguist](https://github.com/github/linguist) - Detection strategies
- [file(1) magic database](https://www.darwinsys.com/file/) - Magic byte patterns
- User feedback on real-world use cases

## Conclusion

Content-based detection makes pyonig significantly more user-friendly for CLI use, especially when piping content. The implementation is:
- ✅ **Well-tested** (56 tests, 100% passing)
- ✅ **Well-documented** (450+ lines of docs)
- ✅ **Fast** (heuristics, not parsing)
- ✅ **Accurate** (for targeted use cases)
- ✅ **Maintainable** (single module, clear logic)

The feature is **production-ready** and ready to merge.

