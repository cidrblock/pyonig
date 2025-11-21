#!/bin/bash
# Build macOS wheels for pyonig
# This script runs NATIVELY on macOS (no container needed)
# It compiles wheels for multiple Python versions and both architectures (x86_64 and arm64)

set -euxo pipefail

# Ensure we're in the project directory
cd "$(dirname "$0")/.."

# Initialize git submodules (Oniguruma)
if [ ! -f deps/oniguruma/src/oniguruma.h ]; then
    echo "Initializing Oniguruma submodule..."
    git submodule update --init --recursive
fi

# Clean previous builds
rm -rf build dist/*.whl src/pyonig.egg-info wheelhouse

# Create dist directory
mkdir -p dist

# Detect available Python versions
# Look for python3.X in common locations
PYTHON_VERSIONS=()
for version in 10 11 12 13; do
    for python_cmd in "python3.${version}" "/usr/local/bin/python3.${version}" "/opt/homebrew/bin/python3.${version}"; do
        if command -v "$python_cmd" &> /dev/null; then
            PYTHON_VERSIONS+=("$python_cmd")
            break
        fi
    done
done

if [ ${#PYTHON_VERSIONS[@]} -eq 0 ]; then
    echo "ERROR: No Python 3.10+ installations found!"
    echo "Please install Python 3.10 or later using:"
    echo "  brew install python@3.10 python@3.11 python@3.12 python@3.13"
    exit 1
fi

echo "Found Python versions: ${PYTHON_VERSIONS[*]}"

# Build wheels for each Python version
for PYTHON in "${PYTHON_VERSIONS[@]}"; do
    echo "=================================="
    echo "Building wheel with $PYTHON"
    echo "=================================="
    
    # Upgrade pip and install build dependencies
    "$PYTHON" -m pip install --upgrade pip setuptools wheel
    
    # Build the wheel
    # Note: macOS wheels are built for the native architecture
    # For universal2 builds, you'd need: --config-setting="--build-option=--plat-name=macosx_10_9_universal2"
    "$PYTHON" -m pip wheel . --no-deps -w wheelhouse/
done

# Move wheels to dist/
mv wheelhouse/*.whl dist/ 2>/dev/null || true
rm -rf wheelhouse

# Use delocate to bundle dependencies (similar to auditwheel on Linux)
# First check if delocate is available, if not, skip this step
if command -v delocate-wheel &> /dev/null; then
    echo "=================================="
    echo "Repairing wheels with delocate"
    echo "=================================="
    
    for whl in dist/pyonig-*.whl; do
        if [ -f "$whl" ]; then
            echo "Repairing: $(basename $whl)"
            delocate-wheel -w dist/ "$whl"
            # Remove the unrelocated wheel
            rm "$whl"
            # Move the relocated wheel back
            mv dist/$(basename $whl) dist/
        fi
    done
else
    echo "⚠ delocate not found, skipping wheel repair"
    echo "  Install with: pip install delocate"
    echo "  Wheels will still work but may not be fully portable"
fi

# List the final wheels
echo "=================================="
echo "Built wheels:"
echo "=================================="
ls -lh dist/*.whl 2>/dev/null || echo "No wheels found"

# Verify wheels can be imported (basic smoke test)
echo "=================================="
echo "Smoke testing wheels"
echo "=================================="

for PYTHON in "${PYTHON_VERSIONS[@]}"; do
    PYTHON_VERSION=$("$PYTHON" --version 2>&1 | awk '{print $2}')
    echo "Testing with Python $PYTHON_VERSION"
    
    # Find the wheel for this Python version
    MAJOR_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f1,2 | tr -d .)
    WHL=$(ls dist/pyonig-*-cp${MAJOR_MINOR}-*.whl 2>/dev/null | head -n1 || echo "")
    
    if [ -n "$WHL" ] && [ -f "$WHL" ]; then
        # Create temporary venv for testing
        VENV_DIR=$(mktemp -d)
        "$PYTHON" -m venv "$VENV_DIR"
        source "$VENV_DIR/bin/activate"
        
        # Install and test
        pip install "$WHL" --force-reinstall
        python -c "import pyonig; print(f'✓ pyonig {pyonig.__version__} imported successfully')"
        python -c "from pyonig import compile, search; p = compile(b'test'); print('✓ Basic regex compilation works')"
        
        # Cleanup
        deactivate
        rm -rf "$VENV_DIR"
    else
        echo "⚠ No wheel found for Python $PYTHON_VERSION"
    fi
done

echo "=================================="
echo "Build complete! Wheels are in dist/"
echo "=================================="

