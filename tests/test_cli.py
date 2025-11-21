"""Tests for pyonig CLI utility."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


# Path to the CLI module
CLI_MODULE = "pyonig.cli"


class TestCLIBasic:
    """Test basic CLI functionality."""

    def test_cli_help(self):
        """Test that --help works."""
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
        assert "pyonig" in result.stdout or "cli" in result.stdout

    def test_cli_version_implicit(self):
        """Test that CLI can be invoked."""
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestCLIFileInput:
    """Test CLI with file input."""

    def test_highlight_json_file(self, tmp_path):
        """Test highlighting a JSON file."""
        # Create test file
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}\n')
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, str(json_file)],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        # Should contain ANSI codes or the content
        assert "key" in result.stdout
        assert "value" in result.stdout

    def test_highlight_yaml_file(self, tmp_path):
        """Test highlighting a YAML file."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("key: value\n")
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, str(yaml_file)],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        assert "key" in result.stdout
        assert "value" in result.stdout

    def test_highlight_toml_file(self, tmp_path):
        """Test highlighting a TOML file."""
        toml_file = tmp_path / "test.toml"
        toml_file.write_text('[section]\nkey = "value"\n')
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, str(toml_file)],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        assert "section" in result.stdout
        assert "key" in result.stdout

    def test_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "/nonexistent/file.json"],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "not found" in result.stderr.lower()


class TestCLIStdin:
    """Test CLI with stdin input."""

    def test_highlight_json_stdin(self):
        """Test highlighting JSON from stdin with language flag."""
        json_input = '{"test": "data"}\n'
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "-l", "json"],
            input=json_input,
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        assert "test" in result.stdout
        assert "data" in result.stdout

    def test_highlight_yaml_stdin(self):
        """Test highlighting YAML from stdin with language flag."""
        yaml_input = "key: value\n"
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "-l", "yaml"],
            input=yaml_input,
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        assert "key" in result.stdout
        assert "value" in result.stdout

    def test_highlight_toml_stdin(self):
        """Test highlighting TOML from stdin with language flag."""
        toml_input = '[section]\nkey = "value"\n'
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "-l", "toml"],
            input=toml_input,
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        assert "section" in result.stdout

    def test_stdin_without_language(self):
        """Test stdin without language flag shows warning."""
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE],
            input='{"test": "data"}\n',
            capture_output=True,
            text=True,
        )
        
        # Should either warn about no detection or output plain text
        assert result.returncode == 0
        assert "test" in result.stdout


class TestCLIOptions:
    """Test CLI options and flags."""

    def test_language_flag(self, tmp_path):
        """Test explicit language flag."""
        # Create file with wrong extension
        test_file = tmp_path / "test.txt"
        test_file.write_text('{"key": "value"}\n')
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "-l", "json", str(test_file)],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        assert "key" in result.stdout

    def test_theme_selection(self, tmp_path):
        """Test theme selection."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}\n')
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "--theme", "dark_vs", str(json_file)],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0

    def test_invalid_theme(self, tmp_path):
        """Test error handling for invalid theme."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}\n')
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "--theme", "nonexistent", str(json_file)],
            capture_output=True,
            text=True,
        )
        
        # Should error out
        assert result.returncode != 0


class TestCLILanguageDetection:
    """Test language auto-detection."""

    def test_detect_json(self, tmp_path):
        """Test JSON auto-detection by extension."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}\n')
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, str(json_file)],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0

    def test_detect_yaml(self, tmp_path):
        """Test YAML auto-detection by extension."""
        yaml_file = tmp_path / "test.yml"
        yaml_file.write_text("key: value\n")
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, str(yaml_file)],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0

    def test_detect_toml(self, tmp_path):
        """Test TOML auto-detection by extension."""
        toml_file = tmp_path / "pyproject.toml"
        toml_file.write_text('[project]\nname = "test"\n')
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, str(toml_file)],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0

    def test_detect_markdown(self, tmp_path):
        """Test Markdown auto-detection by extension."""
        md_file = tmp_path / "README.md"
        md_file.write_text("# Header\n\nContent\n")
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, str(md_file)],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0

    def test_detect_shell(self, tmp_path):
        """Test shell script auto-detection by extension."""
        sh_file = tmp_path / "script.sh"
        sh_file.write_text("#!/bin/bash\necho 'hello'\n")
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, str(sh_file)],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_pipe_through_cat(self, tmp_path):
        """Test piping file through cat (simulates real usage)."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}\n')
        
        # Simulate: cat test.json | pyonig -l json
        cat_process = subprocess.Popen(
            ["cat", str(json_file)],
            stdout=subprocess.PIPE,
        )
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "-l", "json"],
            stdin=cat_process.stdout,
            capture_output=True,
            text=True,
        )
        cat_process.stdout.close()
        cat_process.wait()
        
        assert result.returncode == 0
        assert "key" in result.stdout

    def test_multiline_content(self, tmp_path):
        """Test highlighting multiline content."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{\n  "key1": "value1",\n  "key2": "value2"\n}\n')
        
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE, str(json_file)],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        assert "key1" in result.stdout
        assert "key2" in result.stdout
        assert "value1" in result.stdout
        assert "value2" in result.stdout

