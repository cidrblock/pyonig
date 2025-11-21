"""Tests for pyonig C extension (core regex functionality)."""
from __future__ import annotations

import pytest
import pyonig


class TestBasicRegex:
    """Test basic regex compilation and matching."""

    def test_compile_pattern(self):
        """Test basic pattern compilation."""
        pattern = pyonig.compile(b"hello")
        assert pattern is not None

    def test_simple_search(self):
        """Test basic search functionality."""
        pattern = pyonig.compile(b"world")
        match = pattern.search("hello world")
        assert match is not None
        assert match.span() == (6, 11)
        assert match.group() == "world"

    def test_search_not_found(self):
        """Test search returns None when pattern not found."""
        pattern = pyonig.compile(b"xyz")
        match = pattern.search("hello world")
        assert match is None

    def test_simple_match(self):
        """Test match at beginning of string."""
        pattern = pyonig.compile(b"hello")
        match = pattern.match("hello world")
        assert match is not None
        assert match.span() == (0, 5)
        assert match.group() == "hello"

    def test_match_fails_if_not_at_start(self):
        """Test match returns None if pattern not at start."""
        pattern = pyonig.compile(b"world")
        match = pattern.match("hello world")
        assert match is None

    def test_groups(self):
        """Test capture groups."""
        pattern = pyonig.compile(b"(\\w+)@(\\w+)")
        match = pattern.search("email@example.com")
        assert match is not None
        assert match.group(0) == "email@example"
        assert match.group(1) == "email"
        assert match.group(2) == "example"
        # Note: groups() method may not be implemented
        # assert match.groups() == ("email", "example")

    def test_unicode_handling(self):
        """Test Unicode string handling."""
        pattern = pyonig.compile(b"\\p{L}+")
        match = pattern.search("こんにちは world")
        assert match is not None
        assert match.group() == "こんにちは"

    @pytest.mark.skip(reason="Option flags not yet exposed - need ONIG_OPTION_IGNORECASE")
    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        # Would need: pattern = pyonig.compile(b"HELLO", ONIG_OPTION_IGNORECASE)
        pass

    @pytest.mark.skip(reason="Option flags not yet exposed - need ONIG_OPTION_MULTILINE")
    def test_multiline(self):
        """Test multiline mode."""
        # Would need: pattern = pyonig.compile(b"^world", ONIG_OPTION_MULTILINE)
        pass


class TestRegSet:
    """Test RegSet (multiple pattern matching) functionality."""

    def test_empty_regset(self):
        """Test creating empty RegSet."""
        regset = pyonig.compile_regset()
        assert regset is not None
        idx, match = regset.search("hello world")
        assert idx == -1
        assert match is None

    def test_single_pattern_regset(self):
        """Test RegSet with single pattern."""
        regset = pyonig.compile_regset("world")  # String, not bytes
        idx, match = regset.search("hello world")
        assert idx == 0
        assert match is not None
        assert match.span() == (6, 11)

    def test_multiple_patterns(self):
        """Test RegSet with multiple patterns."""
        regset = pyonig.compile_regset("\\d+", "[a-z]+", "[A-Z]+")  # Strings
        
        # Test matching numbers
        idx, match = regset.search("abc 123 XYZ")
        assert idx == 1  # Second pattern ([a-z]+)
        assert match.span() == (0, 3)
        assert match.group() == "abc"

    def test_regset_first_match_wins(self):
        """Test that RegSet returns first matching pattern."""
        regset = pyonig.compile_regset("[a-z]+", "\\w+")  # Strings
        idx, match = regset.search("hello123")
        assert idx == 0  # First pattern matches first
        assert match.group() == "hello"

    def test_regset_search_from_position(self):
        """Test RegSet search from specific position."""
        regset = pyonig.compile_regset("\\d+", "[a-z]+")  # Strings
        idx, match = regset.search("abc123def", 3)
        assert idx == 0  # Number pattern
        assert match.span() == (3, 6)
        assert match.group() == "123"

    def test_regset_no_match(self):
        """Test RegSet when no pattern matches."""
        regset = pyonig.compile_regset("\\d+", "[A-Z]+")  # Strings
        idx, match = regset.search("hello")
        assert idx == -1
        assert match is None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Test searching empty string."""
        pattern = pyonig.compile(b"test")
        match = pattern.search("")
        assert match is None

    def test_empty_pattern(self):
        """Test empty pattern (matches zero-width)."""
        pattern = pyonig.compile(b"")
        match = pattern.search("hello")
        assert match is not None
        assert match.span() == (0, 0)

    def test_search_at_end_of_string(self):
        """Test that search at end of string returns None (regression test)."""
        pattern = pyonig.compile(b"\\d+")
        text = "123"
        match = pattern.search(text, 3)  # Start at end
        assert match is None  # Should not search backward

    def test_regset_at_end_of_string(self):
        """Test RegSet search at end of string returns None (regression test)."""
        regset = pyonig.compile_regset("\\d+")  # String
        text = "123"
        idx, match = regset.search(text, 3)  # Start at end
        assert idx == -1
        assert match is None

    def test_multibyte_character_positions(self):
        """Test position handling with multibyte UTF-8 characters."""
        pattern = pyonig.compile(b"world")
        text = "こんにちは world"  # Japanese chars are 3 bytes each in UTF-8
        match = pattern.search(text)
        assert match is not None
        # Character positions (not byte positions)
        assert match.span() == (6, 11)

    @pytest.mark.skip(reason="Named group access by string name not yet implemented")
    def test_named_groups(self):
        """Test named capture groups."""
        # Named groups work in patterns but can't be accessed by name yet
        # Would need: match.group("user")
        pass


class TestOptions:
    """Test various Oniguruma options."""

    @pytest.mark.skip(reason="Most option flags not yet exposed in Python API")
    def test_option_multiline(self):
        """Test ONIG_OPTION_MULTILINE flag."""
        # Would need ONIG_OPTION_MULTILINE exposed
        pass

    @pytest.mark.skip(reason="Most option flags not yet exposed in Python API")
    def test_option_singleline(self):
        """Test ONIG_OPTION_SINGLELINE (dot matches newline)."""
        # Would need ONIG_OPTION_SINGLELINE exposed
        pass

    @pytest.mark.skip(reason="Most option flags not yet exposed in Python API")
    def test_option_find_longest(self):
        """Test ONIG_OPTION_FIND_LONGEST flag."""
        # Would need ONIG_OPTION_FIND_LONGEST exposed
        pass

    @pytest.mark.skip(reason="Most option flags not yet exposed in Python API")
    def test_combined_options(self):
        """Test combining multiple options."""
        # Would need more option flags exposed
        pass


class TestErrorHandling:
    """Test error handling and invalid inputs."""

    def test_invalid_regex(self):
        """Test that invalid regex raises error."""
        with pytest.raises(Exception):  # Could be ValueError or RuntimeError
            pyonig.compile(b"[invalid")

    def test_invalid_group_index(self):
        """Test accessing invalid group index."""
        pattern = pyonig.compile(b"(\\w+)")
        match = pattern.search("test")
        assert match is not None
        with pytest.raises(IndexError):
            match.group(5)  # Only has groups 0 and 1

    @pytest.mark.skip(reason="Named group access not yet implemented")
    def test_invalid_group_name(self):
        """Test accessing non-existent named group."""
        # Would test named group access errors
        pass

