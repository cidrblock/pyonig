#!/usr/bin/env bash
# pyonig Demo Script - Showcase all features with asciinema
# This script demonstrates syntax highlighting for all supported file types

set -euo pipefail

# Configuration
readonly DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ASCIINEMA_FILE="${DEMO_DIR}/pyonig-demo.cast"
readonly ASCIINEMA_UPLOAD="${ASCIINEMA_UPLOAD:-true}"

# Colors for non-recorded output
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Typing delay for realistic demo
readonly TYPE_DELAY=0.03
readonly COMMAND_DELAY=1.5
readonly SECTION_DELAY=2.5

# Simulate typing effect
type_command() {
    local cmd="$1"
    for ((i=0; i<${#cmd}; i++)); do
        echo -n "${cmd:$i:1}"
        sleep "$TYPE_DELAY"
    done
    echo
    sleep "$COMMAND_DELAY"
}

# Print a fancy header
print_header() {
    echo
    echo "═══════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════════"
    echo
    sleep 1
}

# Print a section divider
print_section() {
    echo
    echo "───────────────────────────────────────────────────────────────"
    echo "  $1"
    echo "───────────────────────────────────────────────────────────────"
    echo
    sleep 1
}

# Main demo function
run_demo() {
    cd "$DEMO_DIR"
    
    clear
    
    # Welcome
    print_header "pyonig - Syntax Highlighting Demo"
    echo "A self-contained Oniguruma regex engine with TextMate grammar"
    echo "support for Python. Fast, beautiful, zero dependencies."
    echo
    sleep 2
    
    # Show help
    print_section "Getting Started - Help & Version"
    type_command "po --version"
    po --version
    echo
    sleep 1
    
    type_command "po --help"
    po --help | head -20
    echo
    sleep "$SECTION_DELAY"
    
    # List themes
    print_section "Available Themes"
    type_command "po --list-themes"
    po --list-themes | head -25
    echo
    sleep "$SECTION_DELAY"
    
    # List languages
    print_section "Supported Languages"
    type_command "po --list-languages"
    po --list-languages
    echo
    sleep "$SECTION_DELAY"
    
    # JSON highlighting
    print_section "[1] JSON Highlighting"
    echo "Theme: Dark+"
    sleep 1
    type_command "po --theme dark+ sample.json"
    po --theme dark+ sample.json 2>/dev/null | head -20
    echo
    sleep "$SECTION_DELAY"
    
    # YAML highlighting  
    print_section "[2] YAML Highlighting (Ansible Playbook)"
    echo "Theme: Solarized Dark"
    sleep 1
    type_command "po --theme solarized-dark sample.yaml"
    po --theme solarized-dark sample.yaml 2>/dev/null | head -25
    echo
    sleep "$SECTION_DELAY"
    
    # TOML highlighting
    print_section "[3] TOML Highlighting (pyproject.toml)"
    echo "Theme: Dark+"
    sleep 1
    type_command "po --theme dark+ sample.toml"
    po --theme dark+ sample.toml 2>/dev/null | head -25
    echo
    sleep "$SECTION_DELAY"
    
    # Shell script highlighting
    print_section "[4] Shell Script Highlighting"
    echo "Theme: Abyss"
    sleep 1
    type_command "po --theme abyss sample.sh"
    po --theme abyss sample.sh 2>/dev/null | head -30
    echo
    sleep "$SECTION_DELAY"
    
    # Markdown highlighting
    print_section "[5] Markdown Highlighting"
    echo "Theme: Quiet Light (light theme!)"
    sleep 1
    type_command "po --theme quietlight sample.md"
    po --theme quietlight sample.md 2>/dev/null | head -30
    echo
    sleep "$SECTION_DELAY"
    
    # HTML highlighting
    print_section "[6] HTML Highlighting"
    echo "Theme: Kimbie Dark"
    sleep 1
    type_command "po --theme kimbie-dark sample.html"
    po --theme kimbie-dark sample.html 2>/dev/null | head -30
    echo
    sleep "$SECTION_DELAY"
    
    # CSS highlighting
    print_section "[7] CSS Highlighting"
    echo "Theme: Abyss"
    sleep 1
    type_command "po --theme abyss sample.css"
    po --theme abyss sample.css 2>/dev/null | head -25
    echo
    sleep "$SECTION_DELAY"
    
    # JavaScript highlighting
    print_section "[8] JavaScript Highlighting"
    echo "Theme: Monokai"
    sleep 1
    type_command "po --theme monokai sample.js"
    po --theme monokai sample.js 2>/dev/null | head -25
    echo
    sleep "$SECTION_DELAY"
    
    # TypeScript highlighting
    print_section "[9] TypeScript Highlighting"
    echo "Theme: Dark+"
    sleep 1
    type_command "po --theme dark+ sample.ts"
    po --theme dark+ sample.ts 2>/dev/null | head -25
    echo
    sleep "$SECTION_DELAY"
    
    # Python API usage example
    print_section "[10] Python - pyonig API Usage"
    echo "Theme: Solarized Dark"
    sleep 1
    type_command "po --theme solarized-dark sample.py"
    po --theme solarized-dark sample.py 2>/dev/null | head -30
    echo
    sleep "$SECTION_DELAY"
    
    # Pipe examples
    print_section "Pipe Support (cat | po)"
    echo "Works seamlessly with pipes!"
    sleep 1
    
    echo "Example 1: JSON from curl"
    type_command "cat sample.json | po --theme dark+"
    cat sample.json | po --theme dark+ 2>/dev/null | head -15
    echo
    sleep 2
    
    echo "Example 2: YAML with different theme"
    type_command "cat sample.yaml | po --theme tomorrow-night-blue"
    cat sample.yaml | po --theme tomorrow-night-blue 2>/dev/null | head -15
    echo
    sleep "$SECTION_DELAY"
    
    # Auto-detection
    print_section "Auto-Detection (no language flag needed)"
    echo "Smart content-based detection!"
    sleep 1
    
    type_command "cat sample.toml | po"
    cat sample.toml | po 2>/dev/null | head -15
    echo
    sleep "$SECTION_DELAY"
    
    # VS Code theme integration
    print_section "VS Code Theme Integration"
    echo "pyonig automatically detects your VS Code theme!"
    echo
    echo "Priority order:"
    echo "  1. CLI --theme flag (explicit)"
    echo "  2. PYONIG_THEME environment variable"
    echo "  3. VS Code settings.json"
    echo "  4. 'dark' fallback"
    echo
    echo "Try: export PYONIG_THEME=monokai"
    sleep "$SECTION_DELAY"
    
    # Performance showcase
    print_section "Performance"
    echo "Lightning fast with self-contained Oniguruma C extension"
    sleep 1
    type_command "time po sample.json > /dev/null"
    time po sample.json > /dev/null
    echo
    sleep 2
    
    # Finale
    print_header "That's pyonig!"
    echo
    echo "Features:"
    echo "  [*] Self-contained (bundles Oniguruma C library)"
    echo "  [*] Zero runtime dependencies"
    echo "  [*] 17 beautiful themes (VS Code themes included)"
    echo "  [*] 7+ language grammars (JSON, YAML, TOML, Shell, Markdown, HTML, Log)"
    echo "  [*] Content-based auto-detection"
    echo "  [*] VS Code theme integration"
    echo "  [*] Public Python API for library use"
    echo "  [*] Fast C extension (Oniguruma 6.9.10)"
    echo
    echo "Installation:"
    echo "  pip install pyonig"
    echo
    echo "Usage:"
    echo "  po file.json              # Direct file"
    echo "  cat file.yaml | po        # Pipe input"
    echo "  po --theme monokai app.py # Custom theme"
    echo
    echo "GitHub: https://github.com/ansible/pyonig"
    echo
    echo "Thanks for watching!"
    echo
    sleep 3
}

# Check prerequisites
check_prerequisites() {
    if ! command -v po &> /dev/null; then
        echo -e "${YELLOW}Warning: 'po' command not found. Installing pyonig...${NC}"
        pip install -e "$(dirname "$DEMO_DIR")" > /dev/null 2>&1
    fi
    
    if ! command -v asciinema &> /dev/null; then
        echo -e "${YELLOW}Warning: asciinema not found.${NC}"
        echo "Install with: pip install asciinema"
        echo "Or continue without recording (demo will still run)"
        echo
        read -p "Continue without recording? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        return 1
    fi
    
    return 0
}

# Main script
main() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  pyonig Demo Script${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo
    
    if check_prerequisites; then
        echo -e "${GREEN}[OK] All prerequisites found${NC}"
        echo
        echo "Starting asciinema recording..."
        echo "The demo will be recorded and uploaded automatically."
        echo
        sleep 2
        
        # Record with asciinema
        # Export functions and variables so they're available in the subshell
        export -f run_demo print_header print_section type_command
        export TYPE_DELAY COMMAND_DELAY SECTION_DELAY DEMO_DIR
        
        asciinema rec "$ASCIINEMA_FILE" \
            --overwrite \
            --title "pyonig - Syntax Highlighting Demo" \
            --command "bash -c 'run_demo'"
        
        echo
        echo -e "${GREEN}[OK] Recording saved to: $ASCIINEMA_FILE${NC}"
        
        # Upload to asciinema
        if [[ "$ASCIINEMA_UPLOAD" == "true" ]]; then
            echo
            echo "Uploading to asciinema.org..."
            asciinema upload "$ASCIINEMA_FILE"
        fi
    else
        echo -e "${CYAN}Running demo without recording...${NC}"
        echo
        sleep 2
        run_demo
    fi
    
    echo
    echo -e "${GREEN}Demo complete!${NC}"
}

# Run the demo
main "$@"

