#!/usr/bin/env python3
"""CLI utility for syntax highlighting with pyonig."""
from __future__ import annotations

import argparse
import sys

import pyonig
from pyonig.api import highlight, highlight_file
from pyonig.theme import ThemeManager


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Syntax highlight files using pyonig and TextMate grammars",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Highlight a JSON file
  pyonig file.json
  
  # Highlight from stdin
  cat file.yaml | pyonig --language yaml
  
  # Use a specific theme
  pyonig --theme monokai file.py
  
  # Override language detection
  pyonig --language json file.txt
  
  # Specify terminal color support
  pyonig --colors 256 file.json
  
Supported languages:
  json, yaml, toml, shell/bash, markdown, html, log
        """,
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        help="File to highlight (reads from stdin if not provided)",
    )
    
    parser.add_argument(
        "-l", "--language",
        help="Language/scope to use (overrides auto-detection)",
    )
    
    parser.add_argument(
        '-t', '--theme',
        default=None,
        help='Theme name or path (default: auto-detect from VS Code settings or PYONIG_THEME env var)'
    )
    
    parser.add_argument(
        "-c", "--colors",
        type=int,
        choices=[8, 16, 256],
        default=256,
        help="Number of terminal colors to use (default: 256)",
    )
    
    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List supported languages and exit",
    )
    
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List available themes and exit",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"pyonig {pyonig.__version__} (oniguruma {pyonig.__onig_version__})",
    )
    
    args = parser.parse_args()
    
    # Handle list commands
    if args.list_languages:
        from pyonig.api import LANG_TO_SCOPE
        print("Supported languages (extension -> scope):")
        for ext, scope in sorted(LANG_TO_SCOPE.items()):
            print(f"  {ext:10} -> {scope}")
        return 0
    
    if args.list_themes:
        theme_manager = ThemeManager()
        themes = theme_manager.list_themes()
        
        print(f"Available themes ({len(themes)} total):\n")
        
        # Group by category
        vs_themes = [(t, a) for t, a in themes if any(x in t for x in ['dark_vs', 'light_vs', 'dark_plus', 'light_plus', 'hc_'])]
        color_themes = [(t, a) for t, a in themes if 'color-theme' in t]
        other_themes = [(t, a) for t, a in themes if (t, a) not in vs_themes and (t, a) not in color_themes]
        
        if vs_themes:
            print("VS Code Default Themes:")
            for theme_name, aliases in vs_themes:
                if aliases:
                    alias_str = ", ".join(sorted(aliases))
                    print(f"  • {theme_name:25} (aliases: {alias_str})")
                else:
                    print(f"  • {theme_name}")
            print()
        
        if color_themes:
            print("Color Themes:")
            for theme_name, aliases in color_themes:
                if aliases:
                    alias_str = ", ".join(sorted(aliases))
                    print(f"  • {theme_name:40} (alias: {alias_str})")
                else:
                    print(f"  • {theme_name}")
            print()
        
        if other_themes:
            print("Other Themes:")
            for theme_name, aliases in other_themes:
                if aliases:
                    alias_str = ", ".join(sorted(aliases))
                    print(f"  • {theme_name:25} (aliases: {alias_str})")
                else:
                    print(f"  • {theme_name}")
        
        print("\nUsage: pyonig --theme <name> <file>")
        print("Example: pyonig --theme monokai file.json")
        print("         pyonig --theme solarized-dark config.yaml")
        return 0
    
    # Highlight file or stdin
    try:
        if args.file:
            # Highlight file
            result = highlight_file(
                path=args.file,
                language=args.language,
                theme=args.theme,
                output='ansi',
                colors=args.colors,
            )
            print(result)
        else:
            # Highlight stdin
            content = sys.stdin.buffer.read()
            result = highlight(
                content=content,
                language=args.language,
                theme=args.theme,
                output='ansi',
                colors=args.colors,
            )
            print(result)
        
        return 0
    
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
