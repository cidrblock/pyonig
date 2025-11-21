#!/bin/bash
# Build manylinux wheels for pyonig
# This script runs INSIDE the manylinux container
# It compiles wheels for multiple Python versions and repairs them with auditwheel

set -euxo pipefail

# Ensure we're in the mounted project directory
cd /io

# Get the platform from environment (manylinux2014_x86_64 or manylinux2014_aarch64)
PLAT="${PLAT:-manylinux2014_x86_64}"

# Initialize git submodules (Oniguruma)
# The container may not have git configured, so we check if deps/oniguruma is populated
if [ ! -f /io/deps/oniguruma/src/oniguruma.h ]; then
    echo "ERROR: Oniguruma submodule not initialized!"
    echo "Run 'git submodule update --init' on the host before building wheels."
    exit 1
fi

# Clean previous builds
rm -rf /io/build /io/src/pyonig.egg-info /io/wheelhouse

# Create wheelhouse directory
mkdir -p /io/wheelhouse

# Compile wheels for all supported Python versions
# manylinux containers have Python installations in /opt/python/
for PYBIN in /opt/python/cp{310,311,312,313}*/bin; do
    # Skip if Python binary doesn't exist
    if [ ! -d "$PYBIN" ]; then
        echo "Skipping $PYBIN (not found)"
        continue
    fi
    
    echo "=================================="
    echo "Building wheel with $PYBIN"
    echo "=================================="
    
    # Upgrade pip and install build dependencies
    "${PYBIN}/pip" install --upgrade pip setuptools wheel
    
    # Build the wheel
    "${PYBIN}/pip" wheel /io/ --no-deps -w /io/wheelhouse/
done

# Bundle external shared libraries into the wheels using auditwheel
# This ensures wheels are portable across different Linux distributions
echo "=================================="
echo "Repairing wheels with auditwheel"
echo "=================================="

mkdir -p /io/dist

for whl in /io/wheelhouse/pyonig-*.whl; do
    # Skip if no wheels were built
    if [ ! -f "$whl" ]; then
        echo "No wheels found to repair!"
        continue
    fi
    
    echo "Repairing: $(basename $whl)"
    auditwheel repair "$whl" --plat "$PLAT" -w /io/dist/
done

# List the final wheels
echo "=================================="
echo "Built wheels:"
echo "=================================="
ls -lh /io/dist/

# Verify wheels can be imported (basic smoke test)
echo "=================================="
echo "Smoke testing wheels"
echo "=================================="

for PYBIN in /opt/python/cp{310,311,312,313}*/bin; do
    if [ ! -d "$PYBIN" ]; then
        continue
    fi
    
    PYTHON_VERSION=$("${PYBIN}/python" --version 2>&1 | awk '{print $2}')
    echo "Testing with Python $PYTHON_VERSION"
    
    # Find the wheel for this Python version
    WHL=$(ls /io/dist/pyonig-*-cp${PYTHON_VERSION%%.*}${PYTHON_VERSION#*.}*-*.whl 2>/dev/null | head -n1 || echo "")
    
    if [ -n "$WHL" ] && [ -f "$WHL" ]; then
        # Install and test
        "${PYBIN}/pip" install "$WHL" --force-reinstall --no-deps
        "${PYBIN}/python" -c "import pyonig; print(f'✓ pyonig {pyonig.__version__} imported successfully')"
        "${PYBIN}/python" -c "from pyonig import compile, search; p = compile(b'test'); print('✓ Basic regex compilation works')"
    else
        echo "⚠ No wheel found for Python $PYTHON_VERSION"
    fi
done

echo "=================================="
echo "Build complete! Wheels are in /io/dist/"
echo "=================================="

