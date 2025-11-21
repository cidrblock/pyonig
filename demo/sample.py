#!/usr/bin/env python3
"""
Sample Python Application - Using pyonig API
Demonstrates syntax highlighting as a library
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import sys

import pyonig


def highlight_file_example():
    """Example 1: Highlight a file with pyonig."""
    print("=== Example 1: Highlighting Files ===\n")
    
    # Highlight a JSON file
    result = pyonig.highlight_file(
        'config.json',
        theme='monokai',
        output='ansi'
    )
    print(result)
    
    # Auto-detect language from filename
    result = pyonig.highlight_file('app.py')
    print(result)


def highlight_string_example():
    """Example 2: Highlight strings directly."""
    print("\n=== Example 2: Highlighting Strings ===\n")
    
    code = '''
def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
    
    # Highlight Python code
    result = pyonig.highlight(
        code,
        language='python',
        theme='solarized-dark',
        output='ansi'
    )
    print(result)


def theme_management_example():
    """Example 3: Working with themes."""
    print("\n=== Example 3: Theme Management ===\n")
    
    # Create theme manager
    tm = pyonig.ThemeManager()
    
    # Get default theme (respects VS Code settings)
    default = tm.get_default()
    print(f"Default theme: {default}")
    
    # Resolve theme aliases
    print(f"'monokai' resolves to: {tm.resolve('monokai')}")
    print(f"'dark+' resolves to: {tm.resolve('dark+')}")
    
    # List all available themes
    themes = tm.list_themes()
    print(f"\nAvailable themes: {len(themes)}")
    for name, aliases in themes[:5]:
        if aliases:
            print(f"  - {name} (aliases: {', '.join(aliases)})")
        else:
            print(f"  - {name}")


def structured_output_example():
    """Example 4: Get structured output for custom rendering."""
    print("\n=== Example 4: Structured Output ===\n")
    
    code = '{"name": "pyonig", "version": "1.0.0"}'
    
    # Get structured output instead of ANSI
    result = pyonig.highlight(
        code,
        language='json',
        theme='dark',
        output='simple'  # Returns list of SimpleLinePart objects
    )
    
    # Process structured data
    for line_num, line_parts in enumerate(result, 1):
        print(f"Line {line_num}:")
        for part in line_parts:
            if part.color:
                r, g, b = part.color
                print(f"  Text: {part.chars!r}, RGB: ({r}, {g}, {b})")
            else:
                print(f"  Text: {part.chars!r}, No color")


def batch_processing_example():
    """Example 5: Batch processing multiple files."""
    print("\n=== Example 5: Batch Processing ===\n")
    
    files = ['config.yaml', 'app.py', 'styles.css', 'script.js']
    
    for filepath in files:
        try:
            result = pyonig.highlight_file(
                filepath,
                theme='abyss',
                output='ansi'
            )
            print(f"\n--- {filepath} ---")
            print(result[:200] + "...")  # Show first 200 chars
        except FileNotFoundError:
            print(f"File not found: {filepath}")
        except ValueError as e:
            print(f"Error processing {filepath}: {e}")


def custom_colors_example():
    """Example 6: Extract colors for custom rendering."""
    print("\n=== Example 6: Color Extraction ===\n")
    
    code = 'const greeting = "Hello, World!";'
    result = pyonig.highlight(
        code,
        language='javascript',
        theme='monokai',
        output='simple'
    )
    
    # Extract unique colors used
    colors = set()
    for line_parts in result:
        for part in line_parts:
            if part.color:
                colors.add(part.color)
    
    print(f"Found {len(colors)} unique colors:")
    for r, g, b in sorted(colors):
        print(f"  RGB({r:3d}, {g:3d}, {b:3d}) - #{r:02x}{g:02x}{b:02x}")


def error_handling_example():
    """Example 7: Proper error handling."""
    print("\n=== Example 7: Error Handling ===\n")
    
    # Handle invalid UTF-8
    try:
        pyonig.highlight(b'\x80\x81\x82', language='json')
    except ValueError as e:
        print(f"Caught error: {e}")
    
    # Handle language detection failure
    try:
        pyonig.highlight("random text with no clear format")
    except ValueError as e:
        print(f"Caught error: {e}")
    
    # Handle invalid theme
    try:
        pyonig.highlight('{"key": "value"}', language='json', theme='nonexistent')
    except ValueError as e:
        print(f"Caught error: {e}")


def web_service_example():
    """Example 8: Using pyonig in a web service."""
    print("\n=== Example 8: Web Service Integration ===\n")
    
    # Simulate a Flask/FastAPI endpoint
    def highlight_endpoint(code: str, language: str, theme: str = 'dark') -> Dict[str, Any]:
        """API endpoint that returns highlighted code."""
        try:
            result = pyonig.highlight(
                code,
                language=language,
                theme=theme,
                output='simple'
            )
            
            # Convert to JSON-friendly format
            lines = []
            for line_parts in result:
                parts = []
                for part in line_parts:
                    parts.append({
                        'text': part.chars,
                        'color': part.color  # RGB tuple or None
                    })
                lines.append(parts)
            
            return {
                'success': True,
                'language': language,
                'theme': theme,
                'lines': lines
            }
        except ValueError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # Test the endpoint
    response = highlight_endpoint(
        code='print("Hello, World!")',
        language='python',
        theme='monokai'
    )
    
    print(f"API Response:")
    print(f"  Success: {response['success']}")
    print(f"  Lines: {len(response.get('lines', []))}")


class CodeHighlighter:
    """Example 9: OOP wrapper around pyonig."""
    
    def __init__(self, default_theme: str = 'dark'):
        self.theme_manager = pyonig.ThemeManager()
        self.default_theme = default_theme
        self.cache: Dict[str, str] = {}
    
    def highlight(self, code: str, language: Optional[str] = None) -> str:
        """Highlight code with caching."""
        cache_key = f"{language}:{hash(code)}:{self.default_theme}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = pyonig.highlight(
            code,
            language=language,
            theme=self.default_theme,
            output='ansi'
        )
        
        self.cache[cache_key] = result
        return result
    
    def highlight_file(self, path: Path) -> str:
        """Highlight file with caching."""
        code = path.read_text()
        return self.highlight(code, language=path.suffix.lstrip('.'))
    
    def set_theme(self, theme: str) -> None:
        """Change default theme and clear cache."""
        self.default_theme = theme
        self.cache.clear()
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return [name for name, _ in self.theme_manager.list_themes()]


def oop_example():
    """Example 10: Object-oriented usage."""
    print("\n=== Example 10: OOP Wrapper ===\n")
    
    # Create highlighter instance
    highlighter = CodeHighlighter(default_theme='solarized-dark')
    
    # Highlight code
    result = highlighter.highlight('SELECT * FROM users;', language='sql')
    print("Highlighted SQL (cached)")
    
    # Change theme
    highlighter.set_theme('monokai')
    print(f"Changed theme to: {highlighter.default_theme}")
    
    # List themes
    themes = highlighter.get_available_themes()
    print(f"Available themes: {len(themes)}")


def main():
    """Run all examples."""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║           pyonig API Examples - Python Usage               ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    examples = [
        ("File Highlighting", highlight_file_example),
        ("String Highlighting", highlight_string_example),
        ("Theme Management", theme_management_example),
        ("Structured Output", structured_output_example),
        ("Batch Processing", batch_processing_example),
        ("Color Extraction", custom_colors_example),
        ("Error Handling", error_handling_example),
        ("Web Service", web_service_example),
        ("OOP Usage", oop_example),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{'='*60}")
        print(f"Example {i}: {name}")
        print('='*60)
        try:
            func()
        except Exception as e:
            print(f"Error in example: {e}")
        
        if i < len(examples):
            input("\nPress Enter to continue...")
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == '__main__':
    main()

