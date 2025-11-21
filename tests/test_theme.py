"""Tests for the theme management module."""
import pytest
from pathlib import Path

from pyonig.theme import (
    THEME_ALIASES,
    get_vscode_theme,
    get_default_theme,
    resolve_theme_alias,
    find_theme_path,
    ThemeManager,
)


class TestThemeAliases:
    """Test the THEME_ALIASES dictionary."""
    
    def test_aliases_exist(self):
        """Test that theme aliases are defined."""
        assert isinstance(THEME_ALIASES, dict)
        assert len(THEME_ALIASES) > 0
    
    def test_common_aliases(self):
        """Test common aliases are present."""
        assert 'monokai' in THEME_ALIASES
        assert 'dark' in THEME_ALIASES
        assert 'light' in THEME_ALIASES
        assert 'solarized-dark' in THEME_ALIASES
    
    def test_vscode_display_names(self):
        """Test VS Code display names are present."""
        assert 'Dark+' in THEME_ALIASES
        assert 'Monokai' in THEME_ALIASES
        assert 'Solarized Dark' in THEME_ALIASES


class TestGetVscodeTheme:
    """Test VS Code theme detection."""
    
    def test_no_vscode_settings(self, monkeypatch):
        """Test when VS Code settings don't exist."""
        # Mock Path.exists to return False
        monkeypatch.setattr(Path, 'exists', lambda self: False)
        
        theme = get_vscode_theme()
        assert theme is None
    
    def test_with_vscode_settings(self, monkeypatch, tmp_path):
        """Test reading VS Code settings."""
        # Create fake settings file
        settings_dir = tmp_path / ".config" / "Code" / "User"
        settings_dir.mkdir(parents=True)
        settings_file = settings_dir / "settings.json"
        settings_file.write_text('{\n  "workbench.colorTheme": "Monokai"\n}')
        
        # Mock Path.home() to return tmp_path
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)
        
        theme = get_vscode_theme()
        assert theme == "Monokai"
    
    def test_vscode_settings_with_comments(self, monkeypatch, tmp_path):
        """Test reading VS Code settings with comments."""
        settings_dir = tmp_path / ".config" / "Code" / "User"
        settings_dir.mkdir(parents=True)
        settings_file = settings_dir / "settings.json"
        settings_file.write_text('''
{
  // This is a comment
  "workbench.colorTheme": "Dark+",
  "editor.fontSize": 14  // Another comment
}
''')
        
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)
        
        theme = get_vscode_theme()
        assert theme == "Dark+"
    
    def test_vscode_settings_invalid_json(self, monkeypatch, tmp_path):
        """Test handling invalid JSON gracefully."""
        settings_dir = tmp_path / ".config" / "Code" / "User"
        settings_dir.mkdir(parents=True)
        settings_file = settings_dir / "settings.json"
        settings_file.write_text('{ invalid json }')
        
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)
        
        theme = get_vscode_theme()
        assert theme is None


class TestGetDefaultTheme:
    """Test default theme resolution."""
    
    def test_env_var_priority(self, monkeypatch):
        """Test that PYONIG_THEME env var takes priority."""
        monkeypatch.setenv("PYONIG_THEME", "monokai")
        monkeypatch.setattr('pyonig.theme.get_vscode_theme', lambda: "Dark+")
        
        theme = get_default_theme()
        assert theme == "monokai"
    
    def test_vscode_fallback(self, monkeypatch):
        """Test fallback to VS Code theme."""
        monkeypatch.delenv("PYONIG_THEME", raising=False)
        monkeypatch.setattr('pyonig.theme.get_vscode_theme', lambda: "Solarized Dark")
        
        theme = get_default_theme()
        assert theme == "Solarized Dark"
    
    def test_dark_fallback(self, monkeypatch):
        """Test final fallback to 'dark'."""
        monkeypatch.delenv("PYONIG_THEME", raising=False)
        monkeypatch.setattr('pyonig.theme.get_vscode_theme', lambda: None)
        
        theme = get_default_theme()
        assert theme == "dark"


class TestResolveThemeAlias:
    """Test theme alias resolution."""
    
    def test_resolve_known_alias(self):
        """Test resolving known aliases."""
        assert resolve_theme_alias('monokai') == 'monokai-color-theme'
        assert resolve_theme_alias('dark') == 'dark_vs'
        assert resolve_theme_alias('solarized-dark') == 'solarized-dark-color-theme'
    
    def test_resolve_vscode_names(self):
        """Test resolving VS Code display names."""
        assert resolve_theme_alias('Dark+') == 'dark_plus'
        assert resolve_theme_alias('Monokai') == 'monokai-color-theme'
    
    def test_resolve_unknown_alias(self):
        """Test that unknown aliases pass through unchanged."""
        assert resolve_theme_alias('unknown') == 'unknown'
        assert resolve_theme_alias('custom-theme') == 'custom-theme'


class TestFindThemePath:
    """Test theme path finding."""
    
    def test_find_existing_theme(self):
        """Test finding an existing theme."""
        path = find_theme_path('dark_vs')
        assert path is not None
        assert path.exists()
        assert path.suffix == '.json'
    
    def test_find_with_alias(self):
        """Test finding theme with alias."""
        path = find_theme_path('monokai')
        assert path is not None
        assert 'monokai-color-theme' in path.name
    
    def test_find_nonexistent(self):
        """Test finding non-existent theme."""
        path = find_theme_path('nonexistent')
        assert path is None
    
    def test_find_with_extension(self):
        """Test finding theme with .json extension."""
        path = find_theme_path('dark_vs.json')
        assert path is not None
        assert path.exists()
    
    def test_find_absolute_path(self, tmp_path):
        """Test finding theme by absolute path."""
        theme_file = tmp_path / "custom.json"
        theme_file.write_text('{"name": "Custom"}')
        
        path = find_theme_path(str(theme_file))
        assert path == theme_file
        assert path.exists()


class TestThemeManagerClass:
    """Test the ThemeManager class."""
    
    def test_initialization(self):
        """Test ThemeManager initialization."""
        tm = ThemeManager()
        assert tm.theme_dir.exists()
        assert tm.theme_dir.is_dir()
    
    def test_custom_theme_dir(self, tmp_path):
        """Test initialization with custom theme directory."""
        tm = ThemeManager(theme_dir=tmp_path)
        assert tm.theme_dir == tmp_path
    
    def test_get_default(self, monkeypatch):
        """Test getting default theme."""
        monkeypatch.setenv("PYONIG_THEME", "test-theme")
        
        tm = ThemeManager()
        assert tm.get_default() == "test-theme"
    
    def test_resolve(self):
        """Test resolving aliases."""
        tm = ThemeManager()
        assert tm.resolve('monokai') == 'monokai-color-theme'
    
    def test_find_path(self):
        """Test finding theme path."""
        tm = ThemeManager()
        path = tm.find_path('dark')
        assert path is not None
        assert path.exists()
    
    def test_list_themes(self):
        """Test listing themes."""
        tm = ThemeManager()
        themes = tm.list_themes()
        
        assert isinstance(themes, list)
        assert len(themes) > 0
        
        # Check structure
        for theme_name, aliases in themes:
            assert isinstance(theme_name, str)
            assert isinstance(aliases, list)
            # Aliases should be strings
            for alias in aliases:
                assert isinstance(alias, str)
    
    def test_list_themes_includes_monokai(self):
        """Test that monokai is in the list."""
        tm = ThemeManager()
        themes = tm.list_themes()
        
        theme_names = [name for name, _ in themes]
        assert 'monokai-color-theme' in theme_names
    
    def test_list_themes_has_aliases(self):
        """Test that themes have aliases in the list."""
        tm = ThemeManager()
        themes = tm.list_themes()
        
        # Find monokai theme
        for theme_name, aliases in themes:
            if theme_name == 'monokai-color-theme':
                assert 'monokai' in aliases
                assert 'Monokai' in aliases
                break
        else:
            pytest.fail("monokai-color-theme not found in themes list")

