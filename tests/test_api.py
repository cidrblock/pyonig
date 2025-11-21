"""Tests for the public pyonig API."""
import pytest
from pathlib import Path
import tempfile

import pyonig


class TestHighlight:
    """Test the highlight() function."""
    
    def test_highlight_json_with_theme(self):
        """Test highlighting JSON with explicit theme."""
        code = '{"key": "value"}'
        result = pyonig.highlight(code, language='json', theme='monokai')
        
        assert isinstance(result, str)
        assert '\033[' in result  # Has ANSI codes
        assert 'key' in result
        assert 'value' in result
    
    def test_highlight_auto_detect_language(self):
        """Test auto-detection of language from content."""
        code = b'{"key": "value"}'
        result = pyonig.highlight(code)  # No language specified
        
        assert isinstance(result, str)
        assert '\033[' in result
    
    def test_highlight_bytes_input(self):
        """Test highlighting with bytes input."""
        code = b'{"key": "value"}'
        result = pyonig.highlight(code, language='json', theme='dark')
        
        assert isinstance(result, str)
        assert '\033[' in result
    
    def test_highlight_str_input(self):
        """Test highlighting with string input."""
        code = '{"key": "value"}'
        result = pyonig.highlight(code, language='json', theme='light')
        
        assert isinstance(result, str)
        assert '\033[' in result
    
    def test_highlight_simple_output(self):
        """Test simple output format (structured data)."""
        code = '{"key": "value"}'
        result = pyonig.highlight(code, language='json', theme='monokai', output='simple')
        
        assert isinstance(result, list)
        assert len(result) > 0
        # Each line is a list of parts
        assert isinstance(result[0], list)
    
    def test_highlight_with_alias(self):
        """Test using theme alias."""
        code = '{"key": "value"}'
        result = pyonig.highlight(code, language='json', theme='solarized-dark')
        
        assert isinstance(result, str)
        assert '\033[' in result
    
    def test_highlight_different_colors(self):
        """Test different color depths."""
        code = '{"key": "value"}'
        
        result_8 = pyonig.highlight(code, language='json', theme='dark', colors=8)
        result_256 = pyonig.highlight(code, language='json', theme='dark', colors=256)
        
        assert isinstance(result_8, str)
        assert isinstance(result_256, str)
        # Both should have ANSI codes
        assert '\033[' in result_8
        assert '\033[' in result_256
    
    def test_highlight_toml(self):
        """Test highlighting TOML."""
        code = '[package]\nname = "test"'
        result = pyonig.highlight(code, language='toml', theme='monokai')
        
        assert isinstance(result, str)
        assert 'package' in result
        assert 'name' in result
    
    def test_highlight_yaml(self):
        """Test highlighting YAML."""
        code = 'key: value\nlist:\n  - item1'
        result = pyonig.highlight(code, language='yaml', theme='monokai')
        
        assert isinstance(result, str)
        assert 'key' in result
    
    def test_highlight_invalid_utf8(self):
        """Test error handling for invalid UTF-8."""
        code = b'\x80\x81\x82'
        
        with pytest.raises(ValueError, match="not valid UTF-8"):
            pyonig.highlight(code, language='json')
    
    def test_highlight_no_language_detection(self):
        """Test error when language cannot be detected."""
        code = "some random text"
        
        with pytest.raises(ValueError, match="Could not auto-detect language"):
            pyonig.highlight(code)  # No language, can't detect from content
    
    def test_highlight_invalid_theme(self):
        """Test error for invalid theme."""
        code = '{"key": "value"}'
        
        with pytest.raises(ValueError, match="Theme not found"):
            pyonig.highlight(code, language='json', theme='nonexistent')


class TestHighlightFile:
    """Test the highlight_file() function."""
    
    def test_highlight_file_json(self):
        """Test highlighting a JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"key": "value"}')
            f.flush()
            filepath = f.name
        
        try:
            result = pyonig.highlight_file(filepath, theme='monokai')
            assert isinstance(result, str)
            assert '\033[' in result
            assert 'key' in result
        finally:
            Path(filepath).unlink()
    
    def test_highlight_file_auto_detect(self):
        """Test auto-detection from filename."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('key: value')
            f.flush()
            filepath = f.name
        
        try:
            result = pyonig.highlight_file(filepath)  # No language specified
            assert isinstance(result, str)
            assert '\033[' in result
        finally:
            Path(filepath).unlink()
    
    def test_highlight_file_explicit_language(self):
        """Test with explicit language override."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('{"key": "value"}')
            f.flush()
            filepath = f.name
        
        try:
            result = pyonig.highlight_file(filepath, language='json', theme='dark')
            assert isinstance(result, str)
            assert '\033[' in result
        finally:
            Path(filepath).unlink()
    
    def test_highlight_file_not_found(self):
        """Test error for non-existent file."""
        with pytest.raises(FileNotFoundError):
            pyonig.highlight_file('/nonexistent/file.json')
    
    def test_highlight_file_simple_output(self):
        """Test simple output format for files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"key": "value"}')
            f.flush()
            filepath = f.name
        
        try:
            result = pyonig.highlight_file(filepath, output='simple', theme='monokai')
            assert isinstance(result, list)
        finally:
            Path(filepath).unlink()


class TestDetectLanguage:
    """Test the detect_language() function."""
    
    def test_detect_from_filename(self):
        """Test detection from filename extension."""
        scope = pyonig.detect_language(filename='test.json')
        assert scope == 'source.json'
        
        scope = pyonig.detect_language(filename='test.yaml')
        assert scope == 'source.yaml'
        
        scope = pyonig.detect_language(filename='test.toml')
        assert scope == 'source.toml'
    
    def test_detect_from_content(self):
        """Test detection from content."""
        scope = pyonig.detect_language(content=b'{"key": "value"}')
        assert scope == 'source.json'
        
        scope = pyonig.detect_language(content=b'[package]\nname = "test"')
        assert scope == 'source.toml'
    
    def test_detect_filename_priority(self):
        """Test that filename takes priority over content."""
        # YAML content but JSON filename
        scope = pyonig.detect_language(
            filename='test.json',
            content=b'key: value'
        )
        assert scope == 'source.json'  # Filename wins
    
    def test_detect_nothing(self):
        """Test when nothing can be detected."""
        scope = pyonig.detect_language()
        assert scope is None


class TestThemeManager:
    """Test the ThemeManager class."""
    
    def test_get_default(self):
        """Test getting default theme."""
        tm = pyonig.ThemeManager()
        default = tm.get_default()
        assert isinstance(default, str)
        assert len(default) > 0
    
    def test_resolve_alias(self):
        """Test resolving theme aliases."""
        tm = pyonig.ThemeManager()
        
        assert tm.resolve('monokai') == 'monokai-color-theme'
        assert tm.resolve('dark') == 'dark_vs'
        assert tm.resolve('solarized-dark') == 'solarized-dark-color-theme'
    
    def test_resolve_full_name(self):
        """Test that full names pass through unchanged."""
        tm = pyonig.ThemeManager()
        
        assert tm.resolve('dark_vs') == 'dark_vs'
        assert tm.resolve('monokai-color-theme') == 'monokai-color-theme'
    
    def test_find_path(self):
        """Test finding theme file path."""
        tm = pyonig.ThemeManager()
        
        path = tm.find_path('monokai')
        assert path is not None
        assert path.exists()
        assert path.suffix == '.json'
    
    def test_find_path_alias(self):
        """Test finding path with alias."""
        tm = pyonig.ThemeManager()
        
        path = tm.find_path('dark')
        assert path is not None
        assert 'dark_vs' in path.name
    
    def test_find_path_invalid(self):
        """Test finding invalid theme."""
        tm = pyonig.ThemeManager()
        
        path = tm.find_path('nonexistent')
        assert path is None
    
    def test_list_themes(self):
        """Test listing all themes."""
        tm = pyonig.ThemeManager()
        
        themes = tm.list_themes()
        assert isinstance(themes, list)
        assert len(themes) > 0
        
        # Each item is (theme_name, [aliases])
        theme_name, aliases = themes[0]
        assert isinstance(theme_name, str)
        assert isinstance(aliases, list)

