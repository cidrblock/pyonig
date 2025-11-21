# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Content-based file type detection for pyonig.

This module provides heuristics for detecting file types from content when
no filename is available (e.g., when reading from stdin).
"""

import json
import re
from typing import Optional


def detect_type(data: bytes, *, max_probe: int = 2048) -> Optional[str]:
    """Detect file type from content.
    
    Args:
        data: The content to analyze (typically from stdin or a file)
        max_probe: Maximum number of bytes to examine (default: 2048)
    
    Returns:
        A file type string suitable for use with pyonig.cli LANG_TO_SCOPE,
        or None if type cannot be determined.
        
        Possible return values:
        - "json"
        - "toml"
        - "yaml"
        - "html"
        - "shell"
        - "markdown"
        - "log"
        - "text" (fallback for valid UTF-8)
        - None (binary or unrecognizable)
    
    Examples:
        >>> detect_type(b'{"key": "value"}')
        'json'
        >>> detect_type(b'---\\nkey: value')
        'yaml'
        >>> detect_type(b'[package]\\nname = "test"')
        'toml'
    """
    if not data:
        return None
    
    # Only examine the first max_probe bytes for efficiency
    head = data[:max_probe]
    head_lines = head.splitlines()
    
    # Try to decode as UTF-8 early (many checks need this)
    try:
        head_str = head.decode("utf-8")
    except UnicodeDecodeError:
        # Binary data
        return None
    
    # ========== Shell Script ==========
    # Check FIRST - shebang is very specific and should take precedence
    # Shebang line: #!/bin/bash, #!/bin/sh, etc.
    if head_str.startswith("#!"):
        shebang = head_lines[0].lower() if head_lines else b""
        if any(shell in shebang for shell in [b"sh", b"bash", b"zsh", b"fish", b"ksh"]):
            return "shell"
    
    # ========== JSON ==========
    # JSON must start with { or [ (after whitespace)
    stripped = head_str.lstrip()
    if stripped.startswith(("{", "[")):
        try:
            # Validate it's actually valid JSON
            json.loads(data.decode("utf-8"))
            return "json"
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Looks like JSON but isn't valid - fall through
            pass
    
    # ========== Log Files ==========
    # Check logs EARLY to avoid confusion with YAML (timestamps have colons)
    # Log patterns:
    # 1. Timestamps: 2024-01-01 12:00:00 or similar
    # 2. Log levels: [INFO], [ERROR], [WARN], [DEBUG]
    # 3. Common log formats
    log_indicators = 0
    
    if head_lines:
        first_line = head_lines[0]
        # ISO 8601 timestamp at start
        if re.match(rb"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", first_line):
            log_indicators += 2
        
        # Common log timestamp formats
        if re.match(rb"^\[\d{4}-\d{2}-\d{2}|\d{4}/\d{2}/\d{2}", first_line):
            log_indicators += 2
    
    # Check for log level indicators in first few KB
    log_patterns = [
        rb"\[INFO\]", rb"\[ERROR\]", rb"\[WARN\]", rb"\[DEBUG\]",
        rb"\sINFO\s", rb"\sERROR\s", rb"\sWARN\s", rb"\sDEBUG\s",
        rb" INFO:", rb" ERROR:", rb" WARN:", rb" DEBUG:",
    ]
    for pattern in log_patterns:
        if re.search(pattern, head):
            log_indicators += 2  # Increased weight for log levels
            break
    
    if log_indicators >= 2:
        return "log"
    
    # ========== TOML ==========
    # Check TOML BEFORE Markdown (both use # for comments, but TOML has [sections])
    # TOML patterns:
    # 1. [section] headers
    # 2. key = value pairs
    # 3. key.subkey = value (dotted keys)
    toml_indicators = 0
    markdown_like = False
    for line in head_lines[:50]:  # Check first 50 lines
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith(b"#"):
            continue
        
        # Table headers: [section] or [[array]]
        # This is a STRONG TOML indicator
        if re.match(rb"^\[\[?[^\]]+\]\]?$", line_stripped):
            toml_indicators += 3  # Increased weight
        
        # Key-value pairs with optional dots: key = value or key.sub = value
        elif re.match(rb"^[A-Za-z0-9_\-]+(\.?[A-Za-z0-9_\-]+)*\s*=", line_stripped):
            toml_indicators += 1
        
        # Strong indicator: triple-quoted strings
        if b'"""' in line or b"'''" in line:
            toml_indicators += 1
        
        # Check if it looks like markdown (headers)
        if re.match(rb"^#{1,6}\s+\S", line_stripped):
            markdown_like = True
    
    # TOML [section] headers are very specific - if we found them, it's TOML
    if toml_indicators >= 3:  # Means we found a [section] header
        return "toml"
    
    # Lower threshold for short content (but not if it looks like markdown)
    if not markdown_like:
        if toml_indicators >= 1 and len(head_lines) < 5:
            return "toml"
        if toml_indicators >= 2:
            return "toml"
    
    # ========== Markdown ==========
    # Check markdown BEFORE YAML (both use `-` for lists, but markdown has headers)
    # Markdown patterns:
    # 1. Headers: #, ##, ###
    # 2. Lists: -, *, +
    # 3. Blockquotes: >
    # 4. Code blocks: ```
    # 5. Links: [text](url) or [text][ref]
    # BUT: Don't confuse with YAML (which has key: value patterns)
    markdown_indicators = 0
    yaml_indicators = 0
    for line in head_lines[:30]:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Headers (must have text after the #, not just a comment)
        if re.match(rb"^#{1,6}\s+\S", line_stripped):
            markdown_indicators += 2
        
        # Lists
        if re.match(rb"^[-*+]\s+", line_stripped):
            markdown_indicators += 1
        
        # Blockquotes
        if line_stripped.startswith(b">"):
            markdown_indicators += 1
        
        # Code fences
        if line_stripped.startswith(b"```"):
            markdown_indicators += 2
        
        # Links: [text](url)
        if re.search(rb"\[.+?\]\(.+?\)", line):
            markdown_indicators += 1
        
        # But check for YAML patterns too
        if re.match(rb"^[A-Za-z0-9_\-]+\s*:\s*", line_stripped):
            yaml_indicators += 1
    
    # If we see YAML key:value patterns, it's probably YAML not Markdown
    if yaml_indicators >= 1:
        # Skip markdown detection, let YAML handle it
        pass
    else:
        # Lower threshold for short content
        if markdown_indicators >= 1 and len(head_lines) < 5:
            return "markdown"
        if markdown_indicators >= 2:
            return "markdown"
    
    # ========== YAML ==========
    # YAML patterns:
    # 1. Document start: ---
    # 2. key: value patterns
    # 3. List items: - item
    yaml_indicators = 0
    
    if head_str.startswith("---"):
        yaml_indicators += 2
    
    for line in head_lines[:50]:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith(b"#"):
            continue
        
        # key: value pattern (with optional spaces)
        if re.match(rb"^[A-Za-z0-9_\-]+\s*:\s*", line_stripped):
            yaml_indicators += 1
        
        # List items
        if re.match(rb"^-\s+", line_stripped):
            yaml_indicators += 1
        
        # Document end
        if line_stripped == b"...":
            yaml_indicators += 1
        
        # Lower threshold for short content
        if yaml_indicators >= 1 and len(head_lines) < 5:
            return "yaml"
        if yaml_indicators >= 2:
            return "yaml"
    
    # ========== HTML ==========
    # HTML patterns (case-insensitive)
    head_lower = head_str[:2000].lower()
    if any(pattern in head_lower for pattern in [
        "<!doctype html",
        "<html",
        "<head>",
        "<body>",
        "<div",
        "<span",
    ]):
        return "html"
    
    
    # ========== Plain Text ==========
    # If we got here and it's valid UTF-8, call it text
    # (already validated at the top)
    return "text"


def detect_scope(data: bytes, *, max_probe: int = 2048) -> Optional[str]:
    """Detect TextMate scope from content.
    
    This is a convenience wrapper that maps detect_type() results to
    TextMate scope names used by pyonig.
    
    Args:
        data: The content to analyze
        max_probe: Maximum number of bytes to examine
    
    Returns:
        A TextMate scope name (e.g., "source.json") or None
    
    Examples:
        >>> detect_scope(b'{"key": "value"}')
        'source.json'
    """
    from pyonig.api import LANG_TO_SCOPE
    
    file_type = detect_type(data, max_probe=max_probe)
    if not file_type:
        return None
    
    return LANG_TO_SCOPE.get(file_type)

