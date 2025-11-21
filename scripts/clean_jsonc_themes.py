#!/usr/bin/env python3
"""
Clean JSONC (JSON with Comments) theme files to valid JSON.
Removes comments and trailing commas.
"""
import json
import re
from pathlib import Path


def strip_jsonc_comments(text: str) -> str:
    """Remove // and /* */ comments from JSONC."""
    # Remove // comments (but not in strings)
    text = re.sub(r'(?<!:)//.*?$', '', text, flags=re.MULTILINE)
    
    # Remove /* */ comments
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    return text


def remove_trailing_commas(text: str) -> str:
    """Remove trailing commas before } and ]."""
    # Remove comma before closing brace/bracket (with optional whitespace)
    text = re.sub(r',(\s*[}\]])', r'\1', text)
    return text


def clean_jsonc_file(file_path: Path) -> bool:
    """Clean a JSONC file in-place."""
    print(f"Cleaning {file_path.name}...", end=" ")
    
    try:
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean JSONC
        cleaned = strip_jsonc_comments(content)
        cleaned = remove_trailing_commas(cleaned)
        
        # Parse and re-format as valid JSON
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"FAILED (JSON error: {e})")
            return False
        
        # Write back as properly formatted JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("✓")
        return True
    
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    theme_dir = Path("src/pyonig/themes")
    
    if not theme_dir.exists():
        print(f"Error: {theme_dir} not found")
        return 1
    
    print("=" * 70)
    print("CLEANING JSONC THEME FILES")
    print("=" * 70)
    print()
    
    success_count = 0
    fail_count = 0
    
    for theme_file in sorted(theme_dir.glob('*.json')):
        # Skip license files
        if 'LICENSE' in theme_file.name.upper():
            continue
        
        if clean_jsonc_file(theme_file):
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print("=" * 70)
    print(f"Cleaned: {success_count} files")
    if fail_count > 0:
        print(f"Failed:  {fail_count} files")
    print("=" * 70)
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    exit(main())

