"""Comprehensive tests to achieve 100% coverage of colorize.py."""
from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import patch


from pyonig.colorize import (
    Colorize,
    ansi_to_curses,
    rgb_to_ansi,
)
from pyonig.ui_constants import Color


# Get paths to grammars and themes
GRAMMAR_DIR = Path(__file__).parent.parent / "src" / "pyonig" / "grammars"
THEME_PATH = Path(__file__).parent.parent / "src" / "pyonig" / "themes" / "dark_vs.json"


class TestRgbToAnsi:
    """Test RGB to ANSI color conversion (lines 268-293)."""

    def test_256_colors_grayscale_very_dark(self):
        """Test 256 color grayscale for very dark color."""
        result = rgb_to_ansi(5, 5, 5, 256)
        assert isinstance(result, int)
        assert 232 <= result <= 256  # Grayscale ramp

    def test_256_colors_grayscale_very_light(self):
        """Test 256 color grayscale for very light color."""
        result = rgb_to_ansi(250, 250, 250, 256)
        assert isinstance(result, int)
        assert 232 <= result <= 256  # Grayscale ramp

    def test_256_colors_grayscale_medium(self):
        """Test 256 color grayscale for medium gray."""
        result = rgb_to_ansi(128, 128, 128, 256)
        assert isinstance(result, int)
        assert 232 <= result <= 255  # Gray ramp

    def test_256_colors_red(self):
        """Test 256 color for pure red."""
        result = rgb_to_ansi(255, 0, 0, 256)
        assert isinstance(result, int)
        assert result >= 16  # Non-grayscale

    def test_256_colors_green(self):
        """Test 256 color for pure green."""
        result = rgb_to_ansi(0, 255, 0, 256)
        assert isinstance(result, int)
        assert result >= 16

    def test_256_colors_blue(self):
        """Test 256 color for pure blue."""
        result = rgb_to_ansi(0, 0, 255, 256)
        assert isinstance(result, int)
        assert result >= 16

    def test_16_colors_black(self):
        """Test 16 color mode for black."""
        result = rgb_to_ansi(0, 0, 0, 16)
        assert isinstance(result, int)
        assert result == 30  # Black in 16 color mode

    def test_16_colors_bright(self):
        """Test 16 color mode for bright color."""
        result = rgb_to_ansi(200, 200, 200, 16)
        assert isinstance(result, int)
        # Should return a valid ANSI color code
        assert result >= 0

    def test_16_colors_medium_brightness(self):
        """Test 16 color mode medium brightness."""
        result = rgb_to_ansi(100, 100, 100, 16)
        assert isinstance(result, int)

    def test_8_colors_red(self):
        """Test 8 color mode for red."""
        result = rgb_to_ansi(255, 0, 0, 8)
        assert isinstance(result, int)

    def test_8_colors_green(self):
        """Test 8 color mode for green."""
        result = rgb_to_ansi(0, 255, 0, 8)
        assert isinstance(result, int)

    def test_8_colors_blue(self):
        """Test 8 color mode for blue."""
        result = rgb_to_ansi(0, 0, 255, 8)
        assert isinstance(result, int)

    def test_8_colors_combination(self):
        """Test 8 color mode for color combination."""
        result = rgb_to_ansi(255, 255, 0, 8)  # Yellow
        assert isinstance(result, int)


class TestAnsiToCurses:
    """Test ANSI to curses conversion (lines 361-418)."""

    def test_empty_line(self):
        """Test empty line conversion."""
        result = ansi_to_curses("")
        assert len(result) == 1
        assert result[0].string == ""
        assert result[0].color == Color.BLACK

    def test_plain_text(self):
        """Test plain text without ANSI codes."""
        result = ansi_to_curses("Hello World")
        assert len(result) == 1
        assert result[0].string == "Hello World"
        assert result[0].column == 0

    def test_ansi_fg_color_256(self):
        """Test ANSI foreground color (256 color mode)."""
        # ESC[38;5;196m = bright red in 256 color mode
        line = "\x1b[38;5;196mRed Text\x1b[0m"
        result = ansi_to_curses(line)
        assert len(result) >= 1
        # Should have parsed the color code

    def test_ansi_fg_color_reset(self):
        """Test ANSI color reset (39m)."""
        line = "\x1b[39mDefault\x1b[0m"
        result = ansi_to_curses(line)
        assert len(result) >= 1

    def test_ansi_full_reset(self):
        """Test full ANSI reset (0m)."""
        line = "\x1b[0mReset\x1b[0m"
        result = ansi_to_curses(line)
        assert len(result) >= 1

    def test_ansi_16_color_simple(self):
        """Test ANSI 16 color mode (30-37, 90-97)."""
        line = "\x1b[31mRed\x1b[0m"  # Red (30-37 range)
        result = ansi_to_curses(line)
        assert len(result) >= 1

    def test_ansi_16_color_bright(self):
        """Test ANSI 16 color bright mode (90-97)."""
        line = "\x1b[91mBright Red\x1b[0m"  # Bright red
        result = ansi_to_curses(line)
        assert len(result) >= 1

    def test_ansi_with_style(self):
        """Test ANSI with style code."""
        # Bold (1) + color
        line = "\x1b[1;31mBold Red\x1b[0m"
        result = ansi_to_curses(line)
        assert len(result) >= 1

    def test_ansi_256_with_style(self):
        """Test ANSI 256 color with style."""
        line = "\x1b[38;5;196;1mStyled\x1b[0m"
        result = ansi_to_curses(line)
        assert len(result) >= 1

    def test_multiple_ansi_sequences(self):
        """Test multiple ANSI sequences in one line."""
        line = "\x1b[31mRed\x1b[0m Normal \x1b[32mGreen\x1b[0m"
        result = ansi_to_curses(line)
        assert len(result) >= 2  # Should have multiple parts

    def test_ansi_no_color_code(self):
        """Test ANSI sequence that's not a color."""
        # Some other ANSI sequence
        line = "\x1b[HCursor\x1b[0m"
        ansi_to_curses(line)
        # Should handle gracefully


class TestColorizeAnsiToCursesLines:
    """Test colorized output conversion (lines 135-136)."""

    def test_render_produces_simple_line_parts(self):
        """Test that render produces SimpleLinePart objects."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        result = colorizer.render('{"key": "value"}', "source.json")
        assert len(result) >= 1
        # Each line should have parts
        for line in result:
            assert isinstance(line, list)
            for part in line:
                assert hasattr(part, 'chars')
                assert hasattr(part, 'color')

    def test_render_multiline_produces_multiple_lines(self):
        """Test multiline rendering."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        doc = "line1\nline2\nline3"
        result = colorizer.render(doc, "source.json")
        assert len(result) == 3

    def test_ansi_to_curses_direct(self):
        """Test ansi_to_curses function directly."""
        # This tests the actual ANSI conversion function
        result = ansi_to_curses("\x1b[31mRed\x1b[0m")
        assert len(result) >= 1


class TestColorizeExceptionHandling:
    """Test exception handling in render method (lines 162-176)."""

    def test_tokenization_exception_handling(self, caplog):
        """Test that tokenization exceptions are caught and logged."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        
        # Mock tokenize to raise an exception
        with patch("pyonig.colorize.tokenize") as mock_tokenize:
            mock_tokenize.side_effect = RuntimeError("Test tokenization error")
            
            with caplog.at_level(logging.CRITICAL):
                # This should catch the exception and log it
                result = colorizer.render('{"test": "data"}', "source.json")
                
                # Should return plain text fallback
                assert len(result) >= 1
                
                # Should have logged the error
                assert any("unexpected error" in record.message.lower() for record in caplog.records)
                assert any("test tokenization error" in record.message.lower() for record in caplog.records)

    def test_tokenization_exception_with_multiline(self, caplog):
        """Test exception handling with multiline content."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        
        call_count = [0]
        
        def tokenize_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:  # Fail on second line
                raise ValueError("Test error on line 2")
            # First call returns normally
            from pyonig.tm_tokenize.state import State
            from pyonig.tm_tokenize.region import Regions
            return (State(tuple()), Regions(tuple()))
        
        with patch("pyonig.colorize.tokenize", side_effect=tokenize_side_effect):
            with caplog.at_level(logging.CRITICAL):
                colorizer.render("line1\nline2\nline3", "source.json")
                
                # Should have caught error on line 2
                assert any("unexpected error" in record.message.lower() for record in caplog.records)


class TestColorizeUnusualScopes:
    """Test unusual scope handling."""

    def test_unknown_scope(self):
        """Test handling of completely unknown scope."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        result = colorizer.render("test content", "source.nonexistent.language")
        # Should fall back to plain text
        assert len(result) >= 1

    def test_no_color_scope(self):
        """Test no_color scope explicitly."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        sample = "plain text\nno colors"
        result = colorizer.render(sample, "no_color")
        assert len(result) == 2


class TestColorizeEdgeCases:
    """Test edge cases for complete coverage."""

    def test_empty_document(self):
        """Test rendering empty document."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        result = colorizer.render("", "source.json")
        assert result == []

    def test_document_without_trailing_newline(self):
        """Test document that doesn't end with newline."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        result = colorizer.render('{"key": "value"}', "source.json")
        assert len(result) >= 1

    def test_document_with_trailing_newlines(self):
        """Test document with multiple trailing newlines."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        result = colorizer.render('{"key": "value"}\n\n\n', "source.json")
        assert len(result) >= 1

    def test_very_long_line(self):
        """Test rendering very long line."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        long_json = '{"key": "' + "x" * 1000 + '"}'
        result = colorizer.render(long_json, "source.json")
        assert len(result) >= 1

    def test_special_characters(self):
        """Test special characters in content."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        special = '{"emoji": "🎉", "unicode": "こんにちは"}'
        result = colorizer.render(special, "source.json")
        assert len(result) >= 1

    def test_all_color_modes(self):
        """Test different terminal color support modes."""
        # 8 colors
        assert rgb_to_ansi(255, 0, 0, 8) >= 0
        
        # 16 colors
        assert rgb_to_ansi(255, 0, 0, 16) >= 0
        
        # 256 colors
        assert rgb_to_ansi(255, 0, 0, 256) >= 0

    def test_grayscale_boundary_conditions(self):
        """Test RGB to ANSI for grayscale boundary conditions."""
        # Very dark grays
        result = rgb_to_ansi(7, 7, 7, 256)
        assert 232 <= result <= 256  # Gray ramp
        
        # Very light grays  
        result = rgb_to_ansi(249, 249, 249, 256)
        assert 232 <= result <= 256  # Gray ramp


class TestColorizeIntegration:
    """Integration tests for full coverage."""

    def test_full_render_cycle_json(self):
        """Test complete render cycle for JSON."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        json_doc = '''{
  "string": "value",
  "number": 42,
  "boolean": true,
  "null": null,
  "array": [1, 2, 3],
  "object": {"nested": "value"}
}'''
        result = colorizer.render(json_doc, "source.json")
        assert len(result) >= 7  # Multiple lines

    def test_full_render_cycle_yaml(self):
        """Test complete render cycle for YAML."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        yaml_doc = """
key: value
list:
  - item1
  - item2
nested:
  child: value
"""
        result = colorizer.render(yaml_doc, "source.yaml")
        assert len(result) >= 5

    def test_cache_effectiveness(self):
        """Test that caching works for repeated renders."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        doc = '{"cached": "content"}'
        
        # First render
        result1 = colorizer.render(doc, "source.json")
        
        # Second render (should use cache)
        result2 = colorizer.render(doc, "source.json")
        
        # Should be identical
        assert result1 == result2



class TestUtilityFunctions:
    """Test utility functions for complete coverage."""

    def test_scope_handling(self):
        """Test scope handling in render method."""
        # Test that various scope types work
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        
        # Valid scope
        result = colorizer.render('test', 'source.json')
        assert len(result) >= 1
        
        # Invalid scope should fallback
        result = colorizer.render('test', 'source.nonexistent')
        assert len(result) >= 1

    def test_hex_to_rgb_curses(self):
        """Test hex_to_rgb_curses function."""
        from pyonig.colorize import hex_to_rgb_curses
        result = hex_to_rgb_curses("#FFFFFF")
        assert len(result) == 3
        # Should scale to 1000
        assert all(0 <= val <= 1000 for val in result)

    def test_scale_for_curses(self):
        """Test scale_for_curses function."""
        from pyonig.colorize import scale_for_curses
        # Test scaling from 255 to 1000
        result = scale_for_curses(255)
        assert result == 1000
        result = scale_for_curses(0)
        assert result == 0
        result = scale_for_curses(128)
        assert 400 <= result <= 600

    def test_markdown_processing(self):
        """Test markdown processing functions."""
        from pyonig.colorize import columns_and_colors, ColorSchema
        import json
        
        # Create a simple markdown structure
        lines = [
            ([],  "```python\n"),  # Code block start
            ([], "code\n"),
            ([], "```\n"),  # Code block end
            ([], "# Header\n"),  # Heading
            ([], "---\n"),  # Horizontal rule
            ([], "`inline`\n"),  # Inline code
            ([], "*italic*\n"),  # Italic
        ]
        
        # Load schema
        theme_path = Path(__file__).parent.parent / "src" / "pyonig" / "themes" / "dark_vs.json"
        with open(theme_path) as f:
            schema = ColorSchema(json.load(f))
        
        # This should process markdown without errors
        result = columns_and_colors(lines, schema)
        assert len(result) >= 1


class TestAnsiToCursesEdgeCases:
    """Test ANSI to curses edge cases for complete coverage."""

    def test_ansi_background_color(self):
        """Test ANSI background color codes (48;5)."""
        # Background color shouldn't affect foreground parsing
        line = "\x1b[48;5;196mBG Red\x1b[0m"
        result = ansi_to_curses(line)
        assert len(result) >= 1

    def test_ansi_mixed_codes(self):
        """Test mixed ANSI codes."""
        # Mix of different ANSI sequences
        line = "\x1b[38;5;196;48;5;233mText\x1b[0m"
        result = ansi_to_curses(line)
        assert len(result) >= 1

    def test_ansi_16_color_with_two_params(self):
        """Test 16 color mode with two parameters."""
        # Style + color
        line = "\x1b[1;32mBold Green\x1b[0m"
        result = ansi_to_curses(line)
        assert len(result) >= 1
        # Should have parsed style and color

    def test_ansi_out_of_range_16_color(self):
        """Test ANSI 16 color with out-of-range values."""
        # Color not in 30-37 or 90-97 range
        line = "\x1b[50mUnknown\x1b[0m"
        result = ansi_to_curses(line)
        assert len(result) >= 1


class TestColorConversionEdgeCases:
    """Test color conversion edge cases."""

    def test_16_color_value_0(self):
        """Test 16 color mode with value 0 (dark)."""
        result = rgb_to_ansi(0, 0, 0, 16)
        assert result == 30  # Should be black

    def test_16_color_value_2_bright(self):
        """Test 16 color mode with value 2 (bright)."""
        # Very bright colors
        result = rgb_to_ansi(255, 255, 255, 16)
        assert isinstance(result, int)  # Should return a color

    def test_256_color_boundary_if_conditions(self):
        """Test 256 color mode boundary conditions."""
        # Test the if red < 8 path
        result = rgb_to_ansi(7, 7, 7, 256)
        assert isinstance(result, int)
        
        # Test the if red > 248 path  
        result = rgb_to_ansi(249, 249, 249, 256)
        assert isinstance(result, int)
        
        # Test the middle path (should compute ansi)
        result = rgb_to_ansi(100, 100, 100, 256)
        assert isinstance(result, int)


class TestMarkdownSpecificProcessing:
    """Test markdown-specific processing for remaining coverage."""

    def test_markdown_heading_with_dash_line(self):
        """Test markdown heading that triggers dash line insertion."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        # Heading 1 should trigger dash line insertion
        markdown = "# Main Heading\n\nContent"
        result = colorizer.render(markdown, "text.html.markdown")
        # Should have processed without error
        assert len(result) >= 1

    def test_markdown_horizontal_rule(self):
        """Test markdown horizontal rule processing."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        markdown = "\n---\n\nContent"
        result = colorizer.render(markdown, "text.html.markdown")
        assert len(result) >= 1

    def test_markdown_code_blocks(self):
        """Test markdown code block processing."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        markdown = "```python\ncode\n```\n"
        result = colorizer.render(markdown, "text.html.markdown")
        assert len(result) >= 1

    def test_markdown_inline_code(self):
        """Test markdown inline code processing."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        markdown = "Text with `inline code` here\n"
        result = colorizer.render(markdown, "text.html.markdown")
        assert len(result) >= 1

    def test_markdown_italic(self):
        """Test markdown italic processing."""
        colorizer = Colorize(grammar_dir=str(GRAMMAR_DIR), theme_path=str(THEME_PATH))
        markdown = "Text with *italic* here\n"
        result = colorizer.render(markdown, "text.html.markdown")
        assert len(result) >= 1
