# CI/CD Pipeline Quick Setup Guide

## 🚀 Quick Start

Your CI/CD pipeline is ready! Just set up the GitHub secrets and you're good to go.

## 📋 Setup Checklist

### Step 1: Create PyPI API Token
1. Go to https://pypi.org/manage/account/
2. Scroll to "API tokens" → "Add API token"
3. Name: "GitHub Actions - heracless"
4. Scope: "Project: heracless" (or "Entire account")
5. **Copy the token** (starts with `pypi-`)

### Step 2: Add GitHub Secret
1. Go to https://github.com/felixscode/heracless/settings/secrets/actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Paste the token from Step 1
5. Click "Add secret"

### Step 3: (Optional) Setup Codecov
1. Go to https://codecov.io/
2. Sign in with GitHub
3. Add repository "felixscode/heracless"
4. Copy the upload token
5. Add as GitHub secret: `CODECOV_TOKEN`

### Step 4: (Optional) Setup TestPyPI
1. Go to https://test.pypi.org/manage/account/
2. Create API token (same process as PyPI)
3. Add as GitHub secret: `TEST_PYPI_API_TOKEN`
4. Add repository variable: `PUBLISH_TO_TESTPYPI` = `true`

## 🎯 How to Release

### Quick Release Process:
```bash
# 1. Update version in pyproject.toml
vim pyproject.toml  # Change version to "0.3.3"

# 2. Commit changes
git add pyproject.toml
git commit -m "Bump version to 0.3.3"
git push origin main

# 3. Create and push tag
git tag v0.3.3
git push origin v0.3.3

# 4. Watch the magic happen!
# Go to: https://github.com/felixscode/heracless/actions
```

The pipeline will automatically:
- ✅ Validate version matches tag
- ✅ Run all tests (Python 3.10, 3.11, 3.12)
- ✅ Check with mypy
- ✅ Build package
- ✅ Publish to PyPI
- ✅ Create GitHub Release

## 📊 Badges in README

These badges are now live in your README:
- **Tests**: Shows test status for all Python versions
- **Publish**: Shows deployment status
- **Coverage**: Shows code coverage percentage
- **Python Version**: Shows supported Python versions
- **PyPI Version**: Shows latest published version

## 🔍 What Gets Tested

### On Every Push/PR:
- ✅ Full pytest suite (156 tests)
- ✅ mypy type checking (strict mode)
- ✅ Code coverage report
- ✅ Python 3.10, 3.11, 3.12, 3.13, 3.14
- ✅ Package build validation

### On Version Tag:
- ✅ Everything above, plus:
- ✅ Version validation (tag matches pyproject.toml)
- ✅ Package integrity check
- ✅ PyPI publication
- ✅ GitHub Release creation

## 🛡️ Safety Features

1. **Version validation**: Prevents accidental mismatched versions
2. **Test gates**: Must pass all tests before deploying
3. **Type checking**: mypy must pass
4. **Package validation**: twine check must pass
5. **Protected environments**: Can require manual approval

## 📁 File Structure

```
.github/
├── workflows/
│   ├── test.yml         # CI: Run tests on push/PR
│   └── publish.yml      # CD: Deploy on version tags
└── PIPELINE_SETUP.md    # This file

DEPLOYMENT.md            # Detailed deployment guide
README.md                # Updated with badges
pyproject.toml          # Updated with test/coverage config
```

## 🆘 Troubleshooting

### Pipeline fails on tag push?
Check the Actions tab for detailed logs:
https://github.com/felixscode/heracless/actions

### Common issues:
1. **Version mismatch**: Tag (v0.3.3) must match pyproject.toml (0.3.3)
2. **Tests fail**: Run `pytest tests/` locally first
3. **Invalid token**: Regenerate and update GitHub secret
4. **Package exists**: Can't overwrite; bump version number

### Get help:
- View logs in GitHub Actions
- Check DEPLOYMENT.md for detailed guide
- Open issue: https://github.com/felixscode/heracless/issues

## ✅ Verification

After setting up secrets, test the pipeline:

1. **Test CI** (optional):
   ```bash
   # Create a test branch
   git checkout -b test-ci
   git push origin test-ci
   # Open PR and check if tests run
   ```

2. **Test CD** (when ready):
   ```bash
   # Bump version and create tag as shown above
   # Monitor: https://github.com/felixscode/heracless/actions
   ```

3. **Verify deployment**:
   - Check PyPI: https://pypi.org/project/heracless/
   - Test install: `pip install --upgrade heracless`
   - Check release: https://github.com/felixscode/heracless/releases

## 🎉 You're Done!

Your pipeline is production-ready. Just add the `PYPI_API_TOKEN` secret and you can start releasing with confidence!

**Next tag push will automatically deploy to PyPI! 🚀**
