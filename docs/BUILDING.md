# Building Wheels for pyonig

This document describes how to build platform wheels for `pyonig` using the portable, CI-agnostic build system based on tox and manylinux containers.

## Overview

The build system is designed to work **anywhere**:
- ✅ Local development machines
- ✅ GitHub Actions
- ✅ GitLab CI
- ✅ Jenkins
- ✅ Any CI platform

It uses standard tools:
- **tox** for orchestration
- **Official manylinux containers** for Linux wheels
- **Native builds** for macOS wheels

## Prerequisites

### For Linux Wheel Builds

- Docker or Podman
- tox (`pip install tox`)

### For macOS Wheel Builds

- macOS machine
- Multiple Python versions (3.10, 3.11, 3.12, 3.13)
- Install with: `brew install python@3.10 python@3.11 python@3.12 python@3.13`
- (Optional) delocate: `pip install delocate`

## Quick Start

```bash
# Clone the repository
git clone https://github.com/ansible/pyonig.git
cd pyonig

# Initialize Oniguruma submodule
git submodule update --init --recursive

# Install tox
pip install tox

# Build Linux wheels (requires Docker)
tox -e build-wheels-linux-all

# Or build for specific architecture
tox -e build-wheels-linux-x86_64    # x86_64 only
tox -e build-wheels-linux-aarch64   # ARM64 only

# Build macOS wheels (on macOS only)
tox -e build-wheels-macos

# Build all wheels
tox -e build-wheels-all

# Wheels will be in dist/
ls -lh dist/*.whl
```

## Available tox Environments

### Testing

- `tox` - Run tests on all Python versions (3.10, 3.11, 3.12, 3.13)
- `tox -e py310` - Test on Python 3.10 specifically
- `tox -e coverage` - Generate HTML coverage report

### Building

- `tox -e build-sdist` - Build source distribution
- `tox -e build-wheels-linux-x86_64` - Build manylinux x86_64 wheels
- `tox -e build-wheels-linux-aarch64` - Build manylinux aarch64 wheels
- `tox -e build-wheels-linux-all` - Build all Linux wheels
- `tox -e build-wheels-macos` - Build macOS wheels (macOS only)
- `tox -e build-wheels-all` - Build all wheels (Linux + macOS if available)

### Publishing

- `tox -e publish-test` - Publish to TestPyPI
- `tox -e publish` - Publish to PyPI (production)

## How It Works

### Linux Wheels

The Linux build process uses official PyPA manylinux containers:

1. **tox** mounts the project directory into the container
2. The container runs `build-scripts/build-linux-wheels.sh`
3. The script:
   - Verifies Oniguruma submodule is initialized
   - Compiles wheels for Python 3.10, 3.11, 3.12, 3.13
   - Repairs wheels with `auditwheel` (bundles dependencies)
   - Smoke tests each wheel
4. Final wheels are written to `dist/`

**No custom container images needed!** Since Oniguruma is bundled as a git submodule and compiles from source, standard manylinux containers work perfectly.

### macOS Wheels

The macOS build process runs natively:

1. **tox** runs `build-scripts/build-macos-wheels.sh`
2. The script:
   - Detects available Python versions
   - Builds wheels for each version
   - (Optional) Uses `delocate` to bundle dependencies
   - Smoke tests each wheel
3. Final wheels are written to `dist/`

## Architecture Support

| Platform | Architecture | Status |
|----------|-------------|---------|
| Linux | x86_64 | ✅ Supported |
| Linux | aarch64 (ARM64) | ✅ Supported (via QEMU) |
| macOS | x86_64 | ✅ Supported |
| macOS | arm64 (Apple Silicon) | ✅ Supported |
| Windows | x86_64 | ⚠️ Not yet implemented |

## Local Development

### Build and Test Locally

```bash
# Build Linux wheels locally
tox -e build-wheels-linux-x86_64

# Install the built wheel
pip install dist/pyonig-*.whl --force-reinstall

# Test it
python -c "import pyonig; print(pyonig.__version__)"
pyonig sample.json
```

### Testing ARM64 Wheels on x86_64

Docker can emulate ARM64 using QEMU:

```bash
# Enable QEMU (one-time setup)
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

# Build ARM64 wheels
tox -e build-wheels-linux-aarch64

# This will be slower due to emulation
```

## CI Integration Examples

### GitHub Actions

**pyonig includes complete GitHub Actions workflows!** See `.github/workflows/`:

- **`test.yml`** - Runs tests on every push/PR (Linux, macOS x86_64, macOS ARM64)
- **`build-wheels.yml`** - Builds wheels for all platforms
- **`release.yml`** - Publishes to PyPI on tag push

**Example workflow (simplified):**

```yaml
name: Build Wheels

on: [push, pull_request]

jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      
      - name: Install tox
        run: pip install tox
      
      - name: Build wheels
        run: tox -e build-wheels-linux-all
      
      - uses: actions/upload-artifact@v4
        with:
          name: wheels
          path: dist/*.whl
```

See [`.github/workflows/README.md`](.github/workflows/README.md) for complete documentation.

### GitLab CI

```yaml
build-wheels:
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - apk add --no-cache python3 py3-pip
    - pip3 install tox
  script:
    - git submodule update --init --recursive
    - tox -e build-wheels-linux-all
  artifacts:
    paths:
      - dist/*.whl
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Build Wheels') {
            steps {
                sh '''
                    git submodule update --init --recursive
                    pip install tox
                    tox -e build-wheels-linux-all
                '''
            }
        }
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'dist/*.whl', fingerprint: true
            }
        }
    }
}
```

## Publishing Wheels

### To TestPyPI

```bash
# Set credentials
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...  # Your TestPyPI token

# Build all wheels
tox -e build-wheels-all

# Build source distribution
tox -e build-sdist

# Publish
tox -e publish-test
```

### To PyPI (Production)

```bash
# Set credentials
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...  # Your PyPI token

# Build all wheels
tox -e build-wheels-all

# Build source distribution
tox -e build-sdist

# Publish
tox -e publish
```

## Troubleshooting

### "Oniguruma submodule not initialized"

```bash
git submodule update --init --recursive
```

### "docker: command not found"

Install Docker:
- Linux: `sudo apt install docker.io` or `sudo dnf install docker`
- macOS: Install Docker Desktop
- Or use Podman as a drop-in replacement

### "Permission denied" when running Docker

Add your user to the docker group:
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

Or use Podman (no root required):
```bash
# Install podman
sudo apt install podman  # or: brew install podman

# Create alias
alias docker=podman

# Run tox as normal
tox -e build-wheels-linux-all
```

### ARM64 builds are very slow

ARM64 builds on x86_64 use QEMU emulation and will be slower. This is normal. Options:
- Build on native ARM64 hardware (faster)
- Build only x86_64 for development: `tox -e build-wheels-linux-x86_64`
- Use GitHub Actions with ARM64 runners for CI

### macOS: "No Python 3.10+ installations found"

```bash
# Install multiple Python versions
brew install python@3.10 python@3.11 python@3.12 python@3.13
```

## Advanced: Custom manylinux Images

If you need newer manylinux versions (e.g., manylinux_2_28):

1. Edit `tox.ini`
2. Change `manylinux2014_x86_64` to `manylinux_2_28_x86_64`
3. Update the image: `quay.io/pypa/manylinux_2_28_x86_64`

Example:
```ini
[testenv:build-wheels-linux-x86_64]
commands =
    bash -c "docker run --rm \
        -v {toxinidir}:/io:Z \
        -e PLAT=manylinux_2_28_x86_64 \
        quay.io/pypa/manylinux_2_28_x86_64 \
        /io/build-scripts/build-linux-wheels.sh"
```

## Why This Approach?

**Portability**: Works on any platform with Docker/Podman and tox
**Self-Contained**: No external C library dependencies to manage
**Simple**: Uses standard Python tools (tox) and official containers
**Flexible**: Easy to customize for your CI platform
**Maintainable**: No vendor lock-in, no custom infrastructure

The key advantage of `pyonig` is that **Oniguruma is bundled** via git submodule. This means:
- No need for custom container images (unlike pylibssh which needs libssh pre-built)
- No need to install system packages
- Standard manylinux containers "just work"
- Builds are reproducible anywhere

## Reference

- [PEP 427 - The Wheel Binary Package Format](https://www.python.org/dev/peps/pep-0427/)
- [manylinux GitHub](https://github.com/pypa/manylinux)
- [auditwheel Documentation](https://github.com/pypa/auditwheel)
- [tox Documentation](https://tox.wiki/)

