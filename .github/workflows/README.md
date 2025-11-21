# GitHub Actions Workflows

This directory contains CI/CD workflows for pyonig. All workflows use the **same tox commands** that work locally, ensuring consistency across environments.

## Workflows

### 🧪 `test.yml` - Continuous Testing

**Triggers:** Every push and pull request

**What it does:**
- Runs tests on **3 platforms** (Ubuntu, macOS x86_64, macOS ARM64)
- Tests **4 Python versions** (3.10, 3.11, 3.12, 3.13)
- Runs linters (if configured)
- Tests the CLI tool
- Uploads coverage to Codecov

**Matrix:**
```
Ubuntu:    Python 3.10, 3.11, 3.12, 3.13
macOS x64: Python 3.10, 3.11, 3.12, 3.13
macOS ARM: Python 3.11, 3.12, 3.13 (no 3.10)
```

**Key commands:**
```bash
tox -e py3.10  # Run tests for Python 3.10
tox -e lint    # Run linters
```

### 📦 `build-wheels.yml` - Wheel Building

**Triggers:** Push to main/master, pull requests, manual dispatch

**What it does:**
- Builds source distribution (sdist)
- Builds Linux wheels (x86_64 + aarch64)
- Builds macOS wheels (x86_64 + ARM64)
- Tests all wheels on their respective platforms
- Verifies wheel count and quality

**Artifacts produced:**
```
Linux x86_64:  5 wheels (cp310-cp313, cp313t)
Linux aarch64: 5 wheels (cp310-cp313, cp313t)
macOS x86_64:  4 wheels (cp310-cp313)
macOS ARM64:   3 wheels (cp311-cp313)
Total:         ~17 wheels + 1 sdist
```

**Key commands:**
```bash
tox -e build-sdist                    # Source distribution
tox -e build-wheels-linux-x86_64      # Linux x86_64 wheels
tox -e build-wheels-linux-aarch64     # Linux ARM64 wheels (QEMU)
tox -e build-wheels-macos             # macOS wheels
```

### 🚀 `release.yml` - PyPI Publishing

**Triggers:** 
- Automatic: When a `v*` tag is pushed (e.g., `v0.1.0`)
- Manual: Workflow dispatch (choose TestPyPI or PyPI)

**What it does:**
1. Builds all wheels and sdist
2. Publishes to TestPyPI or PyPI (trusted publishing via OIDC)
3. Creates GitHub Release with artifacts

**Environments:**
- `testpypi` - For testing releases
- `pypi` - For production releases

**How to release:**
```bash
# 1. Tag a release
git tag v0.1.0
git push origin v0.1.0

# 2. Workflow automatically:
#    - Builds all wheels
#    - Publishes to PyPI
#    - Creates GitHub Release

# Or manually:
# - Go to Actions → Release to PyPI → Run workflow
# - Choose testpypi or pypi
```

**Requirements:**
- Set up [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- Configure environments in GitHub repo settings:
  - `testpypi` → test.pypi.org
  - `pypi` → pypi.org

## Architecture Matrix

| Platform | Architecture | Runner | Build Method | Status |
|----------|-------------|---------|--------------|--------|
| Linux | x86_64 | ubuntu-latest | Docker + manylinux2014 | ✅ |
| Linux | aarch64 | ubuntu-latest | Docker + manylinux2014 + QEMU | ✅ |
| macOS | x86_64 | macos-15-intel | Native | ✅ |
| macOS | arm64 | macos-15 | Native | ✅ |
| Windows | x86_64 | - | - | ⚠️ Future |

## Key Features

### 1. **Consistency with Local Development**

Every workflow uses the **same tox commands** you run locally:

```bash
# Local
tox -e build-wheels-linux-x86_64

# CI (in test.yml)
- run: tox -e build-wheels-linux-x86_64
```

No special CI magic, no surprises.

### 2. **CI-Agnostic Design**

These workflows call tox, which calls our build scripts. This means:
- ✅ Easy to port to GitLab CI, Jenkins, etc.
- ✅ Developers can reproduce CI builds locally
- ✅ No vendor lock-in

### 3. **Platform Coverage**

We build on **native runners** for each platform:
- **ubuntu-latest**: For Linux x86_64 and aarch64 (via QEMU)
- **macos-15-intel**: For macOS x86_64 (Intel) on macOS 15 Sequoia
- **macos-15**: For macOS arm64 (Apple Silicon) on macOS 15 Sequoia

### 4. **Trusted Publishing**

Uses PyPI's [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC):
- ✅ No API tokens needed
- ✅ More secure
- ✅ Automatic authentication

## Setup Instructions

### 1. Enable Workflows

Workflows are automatically enabled when pushed to GitHub. No action needed.

### 2. Configure PyPI Trusted Publishing

For the release workflow to work:

1. Go to [PyPI](https://pypi.org/) (or [TestPyPI](https://test.pypi.org/))
2. Create/select your project
3. Go to "Publishing" → "Add a new publisher"
4. Configure:
   - **Repository owner**: Your GitHub username/org
   - **Repository name**: pyonig
   - **Workflow name**: release.yml
   - **Environment name**: pypi (or testpypi)

5. In GitHub repo settings, create environments:
   - Settings → Environments → New environment
   - Name: `pypi` (and `testpypi`)
   - Add protection rules if desired

### 3. Secrets (Optional)

For optional features:

- `CODECOV_TOKEN` - For coverage uploads (optional)

## Workflow Dependencies

```
test.yml
  └─ Runs on every push/PR
  └─ No dependencies

build-wheels.yml
  └─ Runs on push to main/PR
  └─ No dependencies
  └─ Artifacts retained for 7 days

release.yml
  └─ Runs on tag push or manual dispatch
  ├─ Depends on: test.yml (implicitly)
  ├─ Builds all wheels
  ├─ Publishes to PyPI
  └─ Creates GitHub Release
```

## Debugging

### View Workflow Runs

```
https://github.com/YOUR_USERNAME/pyonig/actions
```

### Re-run a Failed Job

1. Go to Actions tab
2. Click on the failed run
3. Click "Re-run jobs" → "Re-run failed jobs"

### Test Locally

Reproduce CI builds locally:

```bash
# Same command CI runs
tox -e build-wheels-linux-x86_64

# Test a specific Python version
tox -e py313

# Run tests like CI does
tox
```

## Cost

**All workflows use free GitHub Actions minutes:**
- Public repos: ✅ Unlimited
- Private repos: 2,000 minutes/month free

**Approximate usage per run:**
- test.yml: ~5-10 minutes × 12 jobs = 60-120 minutes
- build-wheels.yml: ~20-30 minutes total
- release.yml: ~30-40 minutes total

For public repos, this is completely free!

## Maintenance

### Adding a New Python Version

1. Update `tox.ini`:
   ```ini
   envlist = py{310,311,312,313,314}  # Add 314
   ```

2. Update workflow matrices:
   ```yaml
   python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]
   ```

3. Update build scripts (if needed)

### Adding a New Platform

For example, to add Windows:

1. Create `build-scripts/build-windows-wheels.bat`
2. Add to `tox.ini`:
   ```ini
   [testenv:build-wheels-windows]
   platform = win32
   skip_install = true
   commands = build-scripts\build-windows-wheels.bat
   ```
3. Add to workflows:
   ```yaml
   build-wheels-windows:
     runs-on: windows-latest
     steps:
       - run: tox -e build-wheels-windows
   ```

## Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [tox Documentation](https://tox.wiki/)
- [manylinux Wheels](https://github.com/pypa/manylinux)

