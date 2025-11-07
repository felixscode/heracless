# Deployment Guide

This document explains how to set up and use the CI/CD pipeline for Heracless.

## Overview

The project uses GitHub Actions for:
- **Continuous Integration (CI)**: Automated testing on every push and pull request
- **Continuous Deployment (CD)**: Automated publishing to PyPI when a new version tag is created

## CI Pipeline (Testing)

### Workflow: `.github/workflows/test.yml`

**Triggers:**
- Push to `main`, `master`, or `develop` branches
- Pull requests to `main`, `master`, or `develop` branches

**What it does:**
1. Runs tests on Python 3.10, 3.11, 3.12 (stable)
2. Tests Python 3.13, 3.14 (experimental, allowed to fail)
3. Runs mypy type checking
4. Generates code coverage report
5. Uploads coverage to Codecov
6. Tests package building

**Status:** View the badge in README.md

## CD Pipeline (Publishing to PyPI)

### Workflow: `.github/workflows/publish.yml`

**Triggers:**
- Push of a tag matching pattern `v*.*.*` (e.g., `v0.3.3`)

**What it does:**
1. **Validates** that the tag version matches `pyproject.toml` version
2. **Tests** the code on Python 3.10, 3.11, 3.12
3. **Builds** source distribution (sdist) and wheel
4. **Publishes** to TestPyPI (optional, if enabled)
5. **Publishes** to PyPI
6. **Creates** a GitHub Release with auto-generated notes

## Setup Instructions

### 1. PyPI API Token

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Scroll to "API tokens" and click "Add API token"
3. Set scope to "Entire account" or limit to "heracless" project
4. Copy the token (starts with `pypi-`)

### 2. GitHub Secrets Setup

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:

#### Required Secrets:

**`PYPI_API_TOKEN`**
- Value: Your PyPI API token from step 1
- Used for: Publishing to PyPI

**`CODECOV_TOKEN`** (optional but recommended)
- Get from: https://codecov.io/ (sign up with GitHub)
- Used for: Coverage reporting
- Steps:
  1. Go to https://codecov.io/
  2. Sign in with GitHub
  3. Add your repository
  4. Copy the upload token
  5. Add as GitHub secret

#### Optional Secrets:

**`TEST_PYPI_API_TOKEN`**
- Get from: https://test.pypi.org/manage/account/
- Used for: Testing deployment on TestPyPI before production
- Only needed if you want to test on TestPyPI first

### 3. GitHub Environments (Recommended)

For extra safety, set up environments with protection rules:

1. Go to **Settings** → **Environments**
2. Create two environments:
   - `testpypi` (optional)
   - `pypi` (required)

3. For the `pypi` environment, add protection rules:
   - ✅ Required reviewers (yourself)
   - ✅ Deployment branches: Only protected branches and tags

4. Add secrets to each environment:
   - In `pypi` environment: Add `PYPI_API_TOKEN`
   - In `testpypi` environment: Add `TEST_PYPI_API_TOKEN`

### 4. Enable TestPyPI (Optional)

To enable TestPyPI deployment before production:

1. Go to **Settings** → **Secrets and variables** → **Actions** → **Variables**
2. Add a repository variable:
   - Name: `PUBLISH_TO_TESTPYPI`
   - Value: `true`

## How to Release a New Version

### Step 1: Update Version

Edit `pyproject.toml`:

```toml
[project]
name = "heracless"
version = "0.3.3"  # Update this
```

### Step 2: Commit and Push

```bash
git add pyproject.toml
git commit -m "Bump version to 0.3.3"
git push origin main
```

### Step 3: Create and Push Tag

```bash
# Create tag (must match version in pyproject.toml)
git tag v0.3.3

# Push tag to trigger deployment
git push origin v0.3.3
```

### Step 4: Monitor Pipeline

1. Go to **Actions** tab on GitHub
2. Watch the "Publish to PyPI" workflow run
3. Check each step:
   - ✅ Version validation
   - ✅ Tests pass
   - ✅ Build succeeds
   - ✅ TestPyPI publish (if enabled)
   - ✅ PyPI publish
   - ✅ GitHub Release created

### Step 5: Verify Release

1. Check PyPI: https://pypi.org/project/heracless/
2. Check GitHub Releases: https://github.com/felixscode/heracless/releases
3. Test installation:
   ```bash
   pip install --upgrade heracless
   ```

## Troubleshooting

### "Version mismatch" Error

**Problem:** Tag version doesn't match `pyproject.toml` version

**Solution:**
```bash
# Delete incorrect tag
git tag -d v0.3.3
git push origin :refs/tags/v0.3.3

# Update pyproject.toml to match
# Create correct tag
git tag v0.3.3
git push origin v0.3.3
```

### "401 Unauthorized" Error

**Problem:** Invalid or missing PyPI API token

**Solution:**
1. Verify secret name is exactly `PYPI_API_TOKEN`
2. Generate new token on PyPI
3. Update secret in GitHub

### Tests Failing

**Problem:** Tests fail during deployment

**Solution:**
1. Run tests locally first:
   ```bash
   pytest tests/ -v
   mypy heracless/
   ```
2. Fix issues before creating tag
3. Delete tag and recreate after fixes

### Package Already Exists

**Problem:** Version already published to PyPI

**Solution:**
- Cannot overwrite existing versions on PyPI
- Must bump version number
- Delete tag, update version, create new tag

## Manual Deployment (Fallback)

If the pipeline fails, you can deploy manually:

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI
twine upload dist/*
# Enter PyPI credentials when prompted
```

## Best Practices

1. **Always test locally first**
   ```bash
   pytest tests/ -v
   mypy heracless/
   python -m build
   ```

2. **Use semantic versioning**
   - Major: Breaking changes (1.0.0 → 2.0.0)
   - Minor: New features (0.3.0 → 0.4.0)
   - Patch: Bug fixes (0.3.2 → 0.3.3)

3. **Keep version in sync**
   - Update `pyproject.toml` version
   - Create matching tag (v0.3.3)

4. **Review before merge**
   - All tests pass
   - Coverage maintained
   - Documentation updated

5. **Monitor deployments**
   - Watch Actions tab
   - Verify on PyPI
   - Test installation

## Support

If you encounter issues:
1. Check workflow logs in GitHub Actions
2. Review this deployment guide
3. Open an issue: https://github.com/felixscode/heracless/issues
