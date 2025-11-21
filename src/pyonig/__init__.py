"""pyonig - Self-contained oniguruma regex engine with TextMate grammar support."""

from __future__ import annotations

__version__ = "0.1.0"

# Re-export main API from C extension
from pyonig._pyonig import (
    OnigError,
    compile,
    compile_regset,
    ONIG_OPTION_NONE,
    ONIG_OPTION_NOT_BEGIN_STRING,
    ONIG_OPTION_NOT_BEGIN_POSITION,
    ONIG_OPTION_NOT_END_STRING,
    __onig_version__,
)

# Public API for syntax highlighting
from pyonig.api import highlight, highlight_file, detect_language
from pyonig.theme import ThemeManager

__all__ = [
    # Core regex API
    "OnigError",
    "compile",
    "compile_regset",
    "ONIG_OPTION_NONE",
    "ONIG_OPTION_NOT_BEGIN_STRING",
    "ONIG_OPTION_NOT_BEGIN_POSITION",
    "ONIG_OPTION_NOT_END_STRING",
    "__onig_version__",
    "__version__",
    # Syntax highlighting API
    "highlight",
    "highlight_file",
    "detect_language",
    "ThemeManager",
]
