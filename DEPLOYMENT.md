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
1. **Rust job:** checks formatting (`cargo fmt --check`), runs clippy with `-D warnings` (with and without the `python` feature) and runs `cargo test`
2. **Python jobs:** installs the package with `pip install -e ".[dev]"` (builds the Rust extension) and runs pytest and mypy on Python 3.10, 3.11, 3.12, 3.13 and 3.14 (all required)
3. Generates code coverage report
4. Uploads coverage to Codecov (from the Python 3.12 job)
5. **Package build job:** builds a wheel and an sdist with maturin and checks them with `twine check`

**Status:** View the badge in README.md

## CD Pipeline (Publishing to PyPI)

### Workflow: `.github/workflows/publish.yml`

**Triggers:**
- Push of a tag matching pattern `v*.*.*` (e.g., `v0.3.3`)

**What it does:**
1. **Validates** that the tag version matches the version in `Cargo.toml`
2. **Tests** the code (`cargo test`, pytest, mypy) on Python 3.10 - 3.14
3. **Builds** wheels with maturin for Linux (x86_64, aarch64, manylinux), Windows (x64) and macOS (universal2), plus a source distribution (sdist). The wheels use the stable ABI (abi3), so one wheel per platform covers Python 3.10 and newer.
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

The version lives only in `Cargo.toml`; `pyproject.toml` declares `dynamic = ["version"]` and maturin takes the version from `Cargo.toml`. Edit `Cargo.toml`:

```toml
[package]
name = "heracless"
version = "0.3.3"  # Update this
```

Then refresh `Cargo.lock` (e.g. by running `cargo build` or `cargo test`).

### Step 2: Commit and Push

```bash
git add Cargo.toml Cargo.lock
git commit -m "Bump version to 0.3.3"
git push origin main
```

### Step 3: Create and Push Tag

```bash
# Create tag (must match version in Cargo.toml)
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

**Problem:** Tag version doesn't match the `Cargo.toml` version

**Solution:**
```bash
# Delete incorrect tag
git tag -d v0.3.3
git push origin :refs/tags/v0.3.3

# Update Cargo.toml to match
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
   pip install -e ".[dev]"   # rebuilds the Rust extension
   cargo test
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

Building needs a Rust toolchain. Note that this builds a wheel only for your own platform; the other platforms' wheels come from the CI pipeline.

```bash
# Install build tools
pip install maturin twine

# Build wheel and sdist
maturin build --release --sdist --out dist

# Check package
twine check dist/*

# Upload to PyPI
twine upload dist/*
# Enter PyPI credentials when prompted
```

## Best Practices

1. **Always test locally first**
   ```bash
   cargo fmt --check
   cargo clippy --all-targets --features python -- -D warnings
   cargo test
   pytest tests/ -v
   mypy heracless/
   maturin build --release --sdist --out dist
   ```

2. **Use semantic versioning**
   - Major: Breaking changes (1.0.0 → 2.0.0)
   - Minor: New features (0.3.0 → 0.4.0)
   - Patch: Bug fixes (0.3.2 → 0.3.3)

3. **Keep version in sync**
   - Update the version in `Cargo.toml` (the only place it is set)
   - Create matching tag (v0.3.3)

4. **Review before merge**
   - All tests pass
   - Coverage maintained
   - Documentation updated

5. **Monitor deployments**
   - Watch Actions tab
   - Verify on PyPI
   - Test installation

## Documentation Deployment

### Automatic Deployment to Hetzner VM

Documentation is automatically built and deployed to your Hetzner VM when changes are pushed to the `main` branch.

#### Required GitHub Secrets

Configure these secrets in your GitHub repository settings:

1. **`SSH_PRIVATE_KEY`** - Your SSH private key for authentication
   ```bash
   # Generate if needed
   ssh-keygen -t ed25519 -C "github-actions-heracless"
   # Add public key to server: ~/.ssh/authorized_keys
   # Copy private key and add to GitHub Secrets
   cat ~/.ssh/id_ed25519
   ```

2. **`SSH_HOST`** - Your Hetzner VM hostname or IP
   ```
   Example: heracless-py.com or 123.456.789.0
   ```

3. **`SSH_USER`** - SSH username
   ```
   Example: root or www-data
   ```

4. **`DEPLOY_PATH`** - Deployment path on server
   ```
   Example: /var/www/heracless/ or /var/www/html/
   ```

#### Workflow Triggers

Docs will rebuild and deploy when:
- Changes pushed to `main` branch affecting: `docs/**`, `mkdocs.yml`, or `.github/workflows/docs.yml`
- Manual trigger via **Actions** tab → **Documentation** → **Run workflow**

#### Testing Locally

```bash
# Build docs
mkdocs build

# Serve locally
mkdocs serve

# Manual deploy
rsync -avz --delete site/ user@your-server:/var/www/heracless/
```

#### Server Setup

Ensure your Hetzner VM has:
- SSH access configured
- Web server (nginx/apache) serving the deployment path
- Proper permissions for deployment user

Example nginx config:
```nginx
server {
    listen 80;
    server_name heracless-py.com www.heracless-py.com;
    root /var/www/heracless;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

---

## Support

If you encounter issues:
1. Check workflow logs in GitHub Actions
2. Review this deployment guide
3. Open an issue: https://github.com/felixscode/heracless/issues
