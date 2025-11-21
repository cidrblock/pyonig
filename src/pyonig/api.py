"""Public API for pyonig library - syntax highlighting for Python applications."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal, Optional, Union

from pyonig.colorize import Colorize, rgb_to_ansi
from pyonig.detect import detect_scope
from pyonig.theme import ThemeManager


# Language to scope mapping
LANG_TO_SCOPE = {
    "json": "source.json",
    "yaml": "source.yaml",
    "yml": "source.yaml",
    "toml": "source.toml",
    "sh": "source.shell",
    "bash": "source.shell",
    "shell": "source.shell",
    "md": "text.html.markdown",
    "markdown": "text.html.markdown",
    "html": "text.html.basic",
    "htm": "text.html.basic",
    "log": "text.log",
    "css": "source.css",
    "js": "source.js",
    "javascript": "source.js",
    "ts": "source.ts",
    "typescript": "source.ts",
    "py": "source.python",
    "python": "source.python",
}


def detect_language(filename: Optional[str] = None, content: Optional[bytes] = None) -> Optional[str]:
    """Detect language from filename extension or content.
    
    Args:
        filename: Optional filename to detect from extension
        content: Optional content bytes for content-based detection
    
    Returns:
        TextMate scope name or None if detection failed
    """
    # Try filename-based detection first (most reliable)
    if filename:
        ext = Path(filename).suffix.lstrip('.')
        scope = LANG_TO_SCOPE.get(ext.lower())
        if scope:
            return scope
    
    # Fall back to content-based detection
    if content:
        return detect_scope(content)
    
    return None


def render_to_ansi(colorized: list[list], colors: int = 256) -> str:
    """Convert colorized output to ANSI escape sequences.
    
    Args:
        colorized: Output from Colorize.render()
        colors: Number of terminal colors (8, 16, or 256)
    
    Returns:
        String with ANSI color codes
    """
    lines = []
    for line_parts in colorized:
        line = ""
        for part in line_parts:
            text = part.chars
            if part.color:
                # Convert RGB to ANSI
                r, g, b = part.color
                ansi_color = rgb_to_ansi(r, g, b, colors)
                line += f"\033[38;5;{ansi_color}m{text}\033[0m"
            else:
                line += text
        lines.append(line.rstrip('\n'))
    return '\n'.join(lines)


def highlight(
    content: Union[str, bytes],
    language: Optional[str] = None,
    theme: Optional[str] = None,
    output: Literal['simple', 'ansi'] = 'ansi',
    colors: int = 256,
) -> Union[str, list]:
    """Highlight source code with syntax highlighting.
    
    This is the main public API for highlighting code as a library.
    
    Args:
        content: Source code as string or bytes
        language: Language/scope name (e.g., 'json', 'python', 'source.yaml')
                 If None, attempts auto-detection from content
        theme: Theme name, alias, or path to theme file
              If None, uses default (PYONIG_THEME env var, VS Code settings, or 'dark')
        output: Output format - 'ansi' for terminal or 'simple' for structured data
        colors: Number of terminal colors for ANSI output (8, 16, or 256)
    
    Returns:
        - If output='ansi': String with ANSI escape codes
        - If output='simple': List of lists of SimpleLinePart objects
    
    Raises:
        ValueError: If language cannot be detected or theme not found
        
    Example:
        >>> import pyonig
        >>> code = '{"key": "value"}'
        >>> highlighted = pyonig.highlight(code, language='json', theme='monokai')
        >>> print(highlighted)  # Prints with ANSI colors
        
        >>> # Auto-detect language
        >>> highlighted = pyonig.highlight(code)  # Detects JSON
        
        >>> # Use VS Code theme automatically
        >>> highlighted = pyonig.highlight(code)  # Uses your VS Code theme
        
        >>> # Get structured output instead of ANSI
        >>> result = pyonig.highlight(code, output='simple')
        >>> # result is list of lists of SimpleLinePart objects
    """
    # Convert bytes to string if needed
    if isinstance(content, bytes):
        content_bytes = content
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError as e:
            raise ValueError(f"Content is not valid UTF-8: {e}")
    else:
        text = content
        content_bytes = content.encode('utf-8')
    
    # Detect language if not provided
    if language is None:
        language = detect_language(content=content_bytes)
        if not language:
            raise ValueError(
                "Could not auto-detect language. "
                "Please specify language explicitly via the 'language' parameter."
            )
    
    # Resolve language alias to scope
    if language in LANG_TO_SCOPE:
        scope = LANG_TO_SCOPE[language]
    else:
        # Assume it's already a scope name
        scope = language
    
    # Get theme
    theme_manager = ThemeManager()
    if theme is None:
        theme = theme_manager.get_default()
    
    # Find theme path
    theme_path = theme_manager.find_path(theme)
    if theme_path is None:
        raise ValueError(
            f"Theme not found: {theme}\n"
            f"Available themes: {[t[0] for t in theme_manager.list_themes()]}"
        )
    
    # Get grammar directory
    grammar_dir = os.path.join(os.path.dirname(__file__), 'grammars')
    
    # Create colorizer and render
    try:
        colorizer = Colorize(grammar_dir=grammar_dir, theme_path=str(theme_path))
        colorized = colorizer.render(text, scope)
    except Exception as e:
        raise ValueError(f"Error highlighting content: {e}")
    
    # Return in requested format
    if output == 'simple':
        return colorized
    else:  # output == 'ansi'
        return render_to_ansi(colorized, colors)


def highlight_file(
    path: Union[str, Path],
    language: Optional[str] = None,
    theme: Optional[str] = None,
    output: Literal['simple', 'ansi'] = 'ansi',
    colors: int = 256,
) -> Union[str, list]:
    """Highlight a source code file with syntax highlighting.
    
    Convenience wrapper around highlight() that reads a file.
    
    Args:
        path: Path to source code file
        language: Language/scope name (if None, detects from filename and content)
        theme: Theme name, alias, or path to theme file
        output: Output format - 'ansi' for terminal or 'simple' for structured data
        colors: Number of terminal colors for ANSI output (8, 16, or 256)
    
    Returns:
        - If output='ansi': String with ANSI escape codes
        - If output='simple': List of lists of SimpleLinePart objects
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If language cannot be detected or theme not found
        
    Example:
        >>> import pyonig
        >>> highlighted = pyonig.highlight_file('config.json', theme='monokai')
        >>> print(highlighted)  # Prints with ANSI colors
        
        >>> # Auto-detect from filename
        >>> highlighted = pyonig.highlight_file('app.py')  # Detects Python
    """
    path = Path(path)
    
    # Read file
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    try:
        with open(path, 'rb') as f:
            content_bytes = f.read()
    except OSError as e:
        raise ValueError(f"Error reading file: {e}")
    
    # Detect language from filename if not provided
    if language is None:
        language = detect_language(filename=str(path), content=content_bytes)
    
    # Use highlight() with the content
    return highlight(
        content=content_bytes,
        language=language,
        theme=theme,
        output=output,
        colors=colors,
    )


# Convenience: Export at package level for easy import
__all__ = ['highlight', 'highlight_file', 'detect_language', 'ThemeManager']

