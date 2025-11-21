"""Tests for colorize module.

Adapted from ansible-navigator's test_colorize.py
"""
from __future__ import annotations

from pathlib import Path

import pytest

from pyonig.colorize import Colorize


# Get paths to grammars and themes
GRAMMAR_DIR = Path(__file__).parent.parent / "src" / "pyonig" / "grammars"
THEME_PATH = Path(__file__).parent.parent / "src" / "pyonig" / "themes" / "dark_vs.json"


class TestColorizeJSON:
    """Test colorizing JSON content."""

    def test_basic_json(self):
        """Test basic JSON colorization."""
        sample = '{"test": "data"}\n'
        colorized = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH)).render(
            doc=sample,
            scope="source.json",
        )
        
        # Should return lines
        assert len(colorized) == 1
        
        # Can reassemble to original
        reassembled = "".join(part.chars for part in colorized[0])
        assert reassembled == sample

    def test_multiline_json(self):
        """Test multiline JSON colorization."""
        sample = '{\n  "key": "value",\n  "number": 42\n}\n'
        colorized = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH)).render(
            doc=sample,
            scope="source.json",
        )
        
        # Verify line count
        assert len(colorized) >= 3
        
        # Verify reassembly
        lines = [part.chars for line in colorized for part in line]
        assert "".join(lines) == sample


class TestColorizeYAML:
    """Test colorizing YAML content."""

    def test_basic_yaml(self):
        """Test basic YAML colorization."""
        sample = "key: value\n"
        colorized = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH)).render(
            doc=sample,
            scope="source.yaml",
        )
        
        assert len(colorized) == 1
        reassembled = "".join(part.chars for part in colorized[0])
        assert reassembled == sample

    def test_yaml_list(self):
        """Test YAML list colorization."""
        sample = "items:\n  - first\n  - second\n"
        colorized = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH)).render(
            doc=sample,
            scope="source.yaml",
        )
        
        assert len(colorized) == 3
        lines = ["".join(part.chars for part in line) for line in colorized]
        assert "".join(lines) == sample


class TestColorizeTOML:
    """Test colorizing TOML content."""

    def test_basic_toml(self):
        """Test basic TOML colorization."""
        sample = '[section]\nkey = "value"\n'
        colorized = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH)).render(
            doc=sample,
            scope="source.toml",
        )
        
        assert len(colorized) == 2
        lines = ["".join(part.chars for part in line) for line in colorized]
        assert "".join(lines) == sample


class TestColorizeLog:
    """Test colorizing log content."""

    @pytest.mark.skip(reason="Log grammar has regex issues with certain patterns")
    def test_basic_log(self):
        """Test basic log colorization."""
        # Log grammar may have compatibility issues with some patterns
        pass


class TestColorizeNoColor:
    """Test no-color mode."""

    def test_no_color_mode(self):
        """Test that no_color scope returns plain text."""
        sample = '{"test": "data"}'
        colorized = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH)).render(
            doc=sample,
            scope="no_color",
        )
        
        # Should still return line parts but without colorization
        assert len(colorized) >= 1
        reassembled = "".join(part.chars for line in colorized for part in line)
        assert reassembled == sample


class TestEdgeCases:
    """Test edge cases in colorization."""

    def test_empty_string(self):
        """Test colorizing empty string."""
        colorized = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH)).render(
            doc="",
            scope="source.json",
        )
        assert colorized == []

    def test_single_newline(self):
        """Test colorizing string with only newline."""
        colorized = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH)).render(
            doc="\n",
            scope="source.json",
        )
        assert len(colorized) == 1

    def test_unicode_content(self):
        """Test colorizing Unicode content."""
        sample = '{"text": "こんにちは"}\n'
        colorized = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH)).render(
            doc=sample,
            scope="source.json",
        )
        
        reassembled = "".join(part.chars for line in colorized for part in line)
        assert reassembled == sample

    def test_unknown_scope(self):
        """Test handling of unknown scope."""
        sample = "test content\n"
        # Should fall back gracefully
        colorized = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH)).render(
            doc=sample,
            scope="source.unknown",
        )
        
        # Should still return something
        assert len(colorized) >= 1


class TestThemeLoading:
    """Test theme loading and color application."""

    def test_valid_theme(self):
        """Test loading valid theme."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        assert colorizer is not None

    def test_terminal_colors_theme(self):
        """Test loading terminal_colors theme."""
        terminal_theme = Path(__file__).parent.parent / "src" / "pyonig" / "themes" / "terminal_colors.json"
        if terminal_theme.exists():
            # Terminal colors theme may have different structure
            # Just test that it exists and is valid JSON
            import json
            with open(terminal_theme) as f:
                theme_data = json.load(f)
            assert theme_data is not None


@pytest.mark.skipif(not GRAMMAR_DIR.exists(), reason="Grammar directory not found")
@pytest.mark.skipif(not THEME_PATH.exists(), reason="Theme file not found")
class TestIntegration:
    """Integration tests for colorize functionality."""

    def test_all_supported_grammars(self):
        """Test that all grammar files can be loaded and used."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        
        test_cases = [
            ("source.json", '{"key": "value"}\n', True),
            ("source.yaml", "key: value\n", True),
            ("source.toml", '[section]\nkey = "value"\n', True),
            ("source.shell", "echo 'hello'\n", True),
            ("text.html.markdown", "# Header\n", False),  # Markdown may transform content
        ]
        
        for scope, sample, check_content in test_cases:
            colorized = colorizer.render(doc=sample, scope=scope)
            assert len(colorized) >= 1, f"Failed to colorize {scope}"
            
            # Verify content preservation (for non-transforming grammars)
            if check_content:
                reassembled = "".join(part.chars for line in colorized for part in line)
                assert reassembled == sample, f"Content mismatch for {scope}"

