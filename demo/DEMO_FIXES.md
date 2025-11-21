# Demo Script Fixes

## Issue

The original demo script failed when running with asciinema due to:
1. Shell syntax errors with Unicode emoji characters (✅, 🎨, etc.)
2. Improper function passing to asciinema subshell

## Error Message

```
sh: -c: line 119: syntax error near unexpected token `('
sh: -c: line 119: `    echo "  ✅ Self-contained (bundles Oniguruma C library)";'
```

## Root Cause

1. **Unicode Emoji Issues**: When bash function definitions containing Unicode emoji were passed as a string to `bash -c`, the shell parser couldn't handle them correctly in certain contexts.

2. **Function Export Method**: Using `$(declare -f ...)` to pass functions inline to asciinema's `--command` was fragile and prone to escaping issues.

## Solutions Applied

### 1. Replaced Unicode Emoji with ASCII

Changed all emoji characters to ASCII equivalents for better shell compatibility:

**Before:**
```bash
echo "  ✅ Self-contained (bundles Oniguruma C library)"
print_header "🎨 pyonig - Syntax Highlighting Demo"
print_section "1️⃣  JSON Highlighting"
```

**After:**
```bash
echo "  [*] Self-contained (bundles Oniguruma C library)"
print_header "pyonig - Syntax Highlighting Demo"
print_section "[1] JSON Highlighting"
```

### 2. Improved Function Export for Asciinema

Changed from inline function declaration to proper `export -f`:

**Before:**
```bash
asciinema rec "$ASCIINEMA_FILE" \
    --command "bash -c '$(declare -f run_demo print_header print_section type_command); run_demo'"
```

**After:**
```bash
# Export functions so they're available in the subshell
export -f run_demo print_header print_section type_command

asciinema rec "$ASCIINEMA_FILE" \
    --command "bash -c 'run_demo'"
```

## Changes Made

### Unicode to ASCII Replacements

| Original | Replacement | Context |
|----------|-------------|---------|
| `🎨` | (removed) | Headers |
| `📚` | (removed) | Section titles |
| `📝` | (removed) | Section titles |
| `1️⃣ 2️⃣ 3️⃣...` | `[1] [2] [3]...` | Numbered sections |
| `🔧` | (removed) | Pipe support |
| `🔍` | (removed) | Auto-detection |
| `💻` | (removed) | VS Code integration |
| `⚡` | (removed) | Performance |
| `✨` | (removed) | Finale |
| `✅` | `[*]` | Feature bullets |
| `🚀` | (removed) | Closing message |

## Testing

After fixes:
```bash
cd demo/
./demo.sh
```

Result: ✓ Script runs successfully and records without errors

## Benefits of Changes

1. **Better Compatibility**: ASCII characters work in all shell environments
2. **Cleaner Code**: Less potential for encoding issues
3. **More Reliable**: `export -f` is the proper way to share functions in bash
4. **Still Readable**: `[1]`, `[2]`, `[*]` are clear and professional

## Additional Notes

- The asciinema recording still looks professional without emoji
- ASCII markers like `[1]`, `[2]`, etc. are actually clearer in terminal recordings
- The recording uploaded successfully to https://asciinema.org/
- No functionality was lost, only visual presentation slightly changed

## Verification Commands

```bash
# Test function export
cd demo/
bash -c 'source demo.sh && export -f print_header && bash -c "print_header Test"'

# Run full demo (local only)
export ASCIINEMA_UPLOAD=false
./demo.sh

# Run with asciinema recording
unset ASCIINEMA_UPLOAD
./demo.sh
```

All tests pass successfully! ✓

