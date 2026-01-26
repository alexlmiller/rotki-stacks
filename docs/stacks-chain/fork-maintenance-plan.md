# Fork Maintenance Guide: rotki-stacks

Guide for maintaining alexlmiller/rotki-stacks as a long-lived fork of rotki/rotki.

This document provides the strategy and workflows for keeping the fork in sync with upstream while maintaining Stacks-specific additions.

---

## 1. Repository Identity

The fork is named `alexlmiller/rotki-stacks` to:
- Establish clear identity as a specialized fork
- Avoid confusion with upstream
- Signal this is a maintained variant, not just a contributor fork

GitHub automatically redirects old URLs if renamed. Update local remotes:
```bash
git remote set-url origin https://github.com/alexlmiller/rotki-stacks.git
gh repo set-default alexlmiller/rotki-stacks
```

---

## 2. Branch Strategy

### Branches to Keep

| Branch | Purpose | Tracks |
|--------|---------|--------|
| `main` | Stable releases | Tagged releases |
| `develop` | Active development | Your work + upstream merges |
| `upstream-sync` | Clean upstream mirror | `upstream/develop` exactly |

### Branches to Delete

```bash
# Old/stale branches (from upstream, not needed)
git push origin --delete alexandria
git push origin --delete future
git push origin --delete messaging-fix
git push origin --delete tests
git push origin --delete feature/remove-usd-value

# After merging feature branch to develop
git push origin --delete feat/add-stacks-chain

# Keep for now (may be useful)
# bugfixes - if you track upstream bugfixes
# build - if you have custom CI
# master - legacy, can delete after confirming main works
```

### Recommended Flow

```
upstream/develop ──merge──> upstream-sync ──merge──> develop ──release──> main
                                                         │
                                                    feature branches
```

---

## 3. Upstream Sync Workflow

### Regular Sync (Weekly/Bi-weekly)

```bash
# 1. Update upstream-sync to match upstream exactly
git checkout upstream-sync
git fetch upstream
git reset --hard upstream/develop
git push origin upstream-sync --force

# 2. Merge into develop
git checkout develop
git merge upstream-sync

# 3. Resolve conflicts (see section 5)
# 4. Test thoroughly
# 5. Push
git push origin develop
```

### Why upstream-sync Branch?

- Keeps a clean reference of upstream state
- Makes it easy to see what upstream changed
- Allows `git diff upstream-sync develop` to see your modifications
- Useful for creating PRs back to upstream

---

## 4. Conflict Zones

Files most likely to conflict during upstream merges:

### High Risk (Core Integration Points)
```
rotkehlchen/types.py              # StacksAddress type
rotkehlchen/rotkehlchen.py        # Chain initialization
rotkehlchen/db/dbhandler.py       # DB handler methods
rotkehlchen/db/schema.py          # Database schema
rotkehlchen/globaldb/handler.py   # Global DB queries
frontend/common/src/blockchain/   # Chain definitions
```

### Medium Risk (Feature Integration)
```
rotkehlchen/api/v1/schemas.py     # API schemas
frontend/app/src/composables/     # Vue composables
frontend/app/src/types/           # TypeScript types
frontend/app/src/locales/en.json  # i18n strings
```

### Low Risk (Additive)
```
rotkehlchen/chain/stacks/         # Entirely new
frontend/app/src/.../stacks/      # Entirely new
docs/stacks-chain/                # Entirely new
```

### Conflict Resolution Strategy

1. **For high-risk files**: Review upstream changes carefully, reapply your additions
2. **For medium-risk files**: Usually append/merge, rarely true conflicts
3. **For low-risk files**: Your changes should survive untouched

---

## 5. Release Strategy

### Versioning

Follow upstream version with suffix:
- Upstream: `v1.41.3`
- Your release: `v1.41.3-stacks.1`

```bash
git tag v1.41.3-stacks.1
git push origin v1.41.3-stacks.1
```

### Release Workflow

1. Sync with upstream release tag
2. Test thoroughly
3. Tag your release
4. Create GitHub Release with notes

### GitHub Releases

For each release, document:
- Which upstream version it's based on
- What Stacks features are included
- Any known issues or limitations

---

## 6. Contributing Back to Upstream

### What to PR Upstream

1. **Bug fixes** you discover
2. **Generic improvements** (not Stacks-specific)
3. **Foundational changes** that make Stacks integration cleaner

### How to Create Upstream PRs

```bash
# From upstream-sync (clean upstream base)
git checkout upstream-sync
git checkout -b upstream-pr/fix-xyz

# Make changes
git commit -m "Fix XYZ"

# Push to your fork, PR to upstream
git push origin upstream-pr/fix-xyz
# Then create PR: rotki/rotki ← alexlmiller/rotki-stacks:upstream-pr/fix-xyz
```

### What NOT to PR Upstream (Initially)

- Full Stacks integration (too large)
- Changes that only make sense with Stacks

### Long-term: Propose Stacks Integration

If the integration matures and you want it upstream:
1. Open an issue first to discuss
2. Break into smaller PRs (types, DB schema, API, chain module, frontend)
3. Ensure comprehensive tests
4. Be prepared for feedback/changes

---

## 7. Making It Easy for Users

### Documentation

- Clear README explaining this is a Stacks-enabled fork
- Installation instructions
- Link to upstream for non-Stacks users

### Distribution Options

1. **Docker images**: `alexlmiller/rotki-stacks:latest`
2. **GitHub Releases**: Downloadable binaries
3. **Build instructions**: For those who want to compile

### README Updates

```markdown
# Rotki with Stacks Support

This is a fork of [Rotki](https://github.com/rotki/rotki) with
first-class Stacks blockchain support.

## What's Different

- Native STX balance tracking
- SIP-10 token support (sBTC, stSTX, etc.)
- Full transaction history and decoding
- Stacking protocol support

## Upstream Compatibility

Based on Rotki v1.41.3. We sync regularly with upstream releases.

## Installation

[Download latest release](https://github.com/alexlmiller/rotki-stacks/releases)
```

---

## 8. Commands Reference

```bash
# Check divergence from upstream
git log --oneline upstream/develop..develop

# See what you've changed vs upstream
git diff upstream-sync develop --stat

# Find conflicts before merging
git merge upstream-sync --no-commit --no-ff
git merge --abort  # if you want to inspect first

# Sync with specific upstream tag
git fetch upstream --tags
git checkout -b release/v1.42.0-stacks upstream/v1.42.0
git merge develop
```
