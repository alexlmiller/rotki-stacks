# Release Process: rotki-stacks

Guide for creating and publishing releases of the rotki-stacks fork.

---

## Prerequisites

### 1. Repository Access
- Write access to alexlmiller/rotki-stacks
- Permission to create tags and releases

### 2. Docker Hub Account
- Account: `alexlmiller` (or your username)
- Access token generated: https://hub.docker.com/settings/security

### 3. GitHub Secrets Configuration

Add these secrets in GitHub Settings → Secrets and variables → Actions:

| Secret | Value | Purpose |
|--------|-------|---------|
| `DOCKERHUB_USER` | Your Docker Hub username | Docker login |
| `DOCKERHUB_TOKEN` | Docker Hub access token | Docker authentication |

**How to configure:**
1. Go to https://github.com/alexlmiller/rotki-stacks/settings/secrets/actions
2. Click "New repository secret"
3. Add each secret above

### 4. Docker Environment

In GitHub Settings → Environments, create environment named `docker`:
1. Go to https://github.com/alexlmiller/rotki-stacks/settings/environments
2. Click "New environment"
3. Name it: `docker`
4. Add the secrets to this environment

---

## Versioning Strategy

### Format

`v{upstream}-stacks.{suffix}`

**Examples:**
- `v1.41.3-stacks.1` - First release based on rotki v1.41.3
- `v1.41.3-stacks.2` - Second release (upstream sync or bug fixes)
- `v1.42.0-stacks.1` - First release based on rotki v1.42.0

### When to Increment

**Increment suffix** (`-stacks.1` → `-stacks.2`):
- Syncing upstream commits within same upstream version
- Bug fixes
- Stacks-specific improvements
- Documentation updates

**New upstream version** (`v1.41.3-stacks.N` → `v1.42.0-stacks.1`):
- Upstream releases new version (v1.42.0)
- Merge upstream release tag
- Reset suffix to .1

---

## Cutting a Release

### Step 1: Prepare develop Branch

Ensure develop branch is ready:
```bash
git checkout develop
git pull origin develop

# Run tests
uv run python pytestgeventwrapper.py -k stacks
cd frontend && pnpm run test:unit

# Run linters
uv run make lint
cd frontend && pnpm run lint
```

### Step 2: Merge to main

```bash
git checkout main
git merge develop --no-edit
git push origin main
```

### Step 3: Tag Release

```bash
# Determine version (increment from last release)
git tag | grep stacks | sort -V | tail -1  # Shows last tag

# Create new tag
git tag v1.41.3-stacks.2 -m "Release: upstream sync + bug fixes"

# Push tag (triggers CI)
git push origin v1.41.3-stacks.2
```

**Tag message template:**
- "Release: Initial Stacks integration"
- "Release: Upstream sync with bug fixes"
- "Release: Based on rotki v1.42.0"

### Step 4: Monitor Workflow

1. Go to https://github.com/alexlmiller/rotki-stacks/actions
2. Find "Rotki-Stacks Release" workflow
3. Monitor jobs:
   - extract-version (should complete in <1min)
   - create-release (should complete in <1min)
   - build-docker (15-30 minutes per platform)
   - docker-merge (should complete in <2min)

**Typical timeline:** 20-35 minutes total

### Step 5: Verify Docker Hub

Check images published:
```bash
# Check version tag exists
docker pull alexlmiller/rotki-stacks:v1.41.3-stacks.2

# Check latest tag updated
docker pull alexlmiller/rotki-stacks:latest

# Verify multi-arch
docker manifest inspect alexlmiller/rotki-stacks:latest
```

Should show both:
- `linux/amd64`
- `linux/arm64`

### Step 6: Test Release

Run the Docker image:
```bash
docker run -p 8080:80 \
  -v rotki-data:/data \
  -v rotki-logs:/logs \
  alexlmiller/rotki-stacks:v1.41.3-stacks.2
```

Verify:
- Navigate to http://localhost:8080
- Backend API responds
- Colibri service running
- Can add Stacks address
- Balance queries work

### Step 7: Update Release Notes

GitHub Release is created automatically with basic template. Edit to add:

```bash
gh release edit v1.41.3-stacks.2
```

**What to include:**
- New features since last release
- Bug fixes
- Upstream sync details (commits synced, notable changes)
- Known issues
- Breaking changes (if any)

---

## Release Notes Template

```markdown
# rotki-stacks {VERSION}

## What's New

### Stacks Integration
- [List major Stacks features added/improved]
- Example: Added support for Velar DEX swaps
- Example: Improved STX stacking reward tracking

### Upstream Sync
- Based on rotki v{UPSTREAM_VERSION}
- Synced {N} commits from upstream
- Notable upstream changes:
  - [List important upstream improvements]
  - Example: Performance improvements for large portfolios
  - Example: New exchange integrations

### Bug Fixes
- [List bugs fixed]
- Example: Fixed Stacks token icon loading
- Example: Resolved balance refresh issue

### Known Issues
- [List any known issues]
- [Link to GitHub issues if applicable]

## Installation

### Docker (Recommended)
\`\`\`bash
docker pull alexlmiller/rotki-stacks:{VERSION}
docker run -p 80:80 -v rotki-data:/data alexlmiller/rotki-stacks:{VERSION}
\`\`\`

Access at: http://localhost

### From Source
See [dev-environment.md](https://github.com/alexlmiller/rotki-stacks/blob/main/docs/stacks-chain/dev-environment.md)

## Documentation
- [Stacks Integration PRD](https://github.com/alexlmiller/rotki-stacks/blob/main/docs/stacks-chain/stacks-integration-prd.md)
- [Fork Maintenance](https://github.com/alexlmiller/rotki-stacks/blob/main/docs/stacks-chain/fork-maintenance-plan.md)
```

---

## Troubleshooting

### Docker Build Fails

**Problem:** Build fails with "no space left on device"
**Solution:**
```bash
docker system prune -a  # Clean up Docker cache
```

**Problem:** ARM64 build fails or times out
**Solution:**
- ARM64 uses QEMU emulation (slower)
- Check GitHub Actions runner availability
- If persistent, build arm64 locally and push manually

### Authentication Issues

**Problem:** "unauthorized: incorrect username or password"
**Solution:**
1. Verify `DOCKERHUB_USER` matches your username exactly
2. Regenerate Docker Hub access token
3. Update `DOCKERHUB_TOKEN` secret in GitHub
4. Ensure secrets are in `docker` environment

### Release Already Exists

**Problem:** "Release v1.41.3-stacks.2 already exists"
**Solution:**
```bash
# Delete existing release
gh release delete v1.41.3-stacks.2 --yes

# Delete tag locally and remotely
git tag -d v1.41.3-stacks.2
git push origin :refs/tags/v1.41.3-stacks.2

# Re-create and push tag
git tag v1.41.3-stacks.2 -m "Release message"
git push origin v1.41.3-stacks.2
```

### Multi-Arch Manifest Issues

**Problem:** Only one platform shows in manifest
**Solution:**
- Check both platform builds completed successfully
- Verify digests were uploaded as artifacts
- Re-run docker-merge job if needed

---

## Rollback Procedure

If a release is broken and needs rollback:

### 1. Delete Bad Release
```bash
gh release delete v1.41.3-stacks.2 --yes
git tag -d v1.41.3-stacks.2
git push origin :refs/tags/v1.41.3-stacks.2
```

### 2. Update latest Tag on Docker Hub

Docker Hub `latest` tag will still point to bad release. Options:

**Option A: Re-tag previous good version as latest**
```bash
docker pull alexlmiller/rotki-stacks:v1.41.3-stacks.1
docker tag alexlmiller/rotki-stacks:v1.41.3-stacks.1 alexlmiller/rotki-stacks:latest
docker push alexlmiller/rotki-stacks:latest
```

**Option B: Create hotfix release**
- Fix the issue on main branch
- Tag v1.41.3-stacks.3 (increment suffix)
- Push tag (triggers new build)

### 3. Communicate

If users may have pulled the bad release:
- Update GitHub Release of good version with warning
- Post notice in discussions/issues
- Document the issue for future reference

---

## Post-Release Checklist

- [ ] GitHub Release created and visible
- [ ] Release notes updated with accurate information
- [ ] Docker images pulled and tested
- [ ] Multi-arch manifest verified
- [ ] Documentation links work (PRD, dev-environment, etc.)
- [ ] `latest` tag points to new release
- [ ] main branch updated with release tag

---

## Automated vs Manual Steps

**Automated by CI:**
- ✅ GitHub Release creation
- ✅ Docker image builds (amd64 + arm64)
- ✅ Docker Hub push
- ✅ Manifest merge
- ✅ latest tag update

**Manual steps:**
- Create and push git tag
- Update release notes (CI creates template)
- Test release
- Communicate to users (if significant)

---

## Questions?

- Check [fork-maintenance-plan.md](fork-maintenance-plan.md) for general fork operations
- Review [dev-environment.md](dev-environment.md) for build issues
- See `.github/workflows/release.yml` for CI implementation details
