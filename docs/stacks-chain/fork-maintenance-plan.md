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
# 4. Test thoroughly (see testing checklist below)
# 5. Push and update main
git push origin develop
git checkout main
git merge develop --no-edit
git push origin main

# 6. Tag release if significant changes
git tag v1.41.3-stacks.N -m "Upstream sync: <summary>"
git push origin v1.41.3-stacks.N
```

**Reality Check**: Our first upstream sync (4 commits) had zero conflicts. The Stacks integration is mostly additive, so conflicts may be rarer than expected. Most upstream changes won't touch Stacks-specific code.

### Testing Checklist After Sync

Minimal validation before releasing:
1. **Backend starts**: `uv run python -m rotkehlchen --api-port 4242`
2. **Colibri starts**: Check logs for errors
3. **Frontend builds**: `cd frontend && pnpm run build`
4. **Stacks queries work**: Add a Stacks address, check balance loads
5. **Run linters**: `uv run make lint` (backend), `pnpm run lint` (frontend)

Full validation (if time permits):
6. **Backend tests**: `uv run python pytestgeventwrapper.py` (Stacks tests only: `-k stacks`)
7. **Frontend tests**: `cd frontend && pnpm run test:unit`
8. **Smoke test**: Create new user, add accounts, verify transaction history

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

### When Conflicts Happen

**Preparation:**
```bash
# Before merging, preview what changed upstream
git log develop..upstream-sync --oneline
git diff develop..upstream-sync --stat

# Try merge without committing to see conflicts
git merge upstream-sync --no-commit --no-ff
# Review conflicts
git merge --abort  # abort to prepare
```

**Resolution Process:**
```bash
# Do the actual merge
git merge upstream-sync

# For each conflicted file:
# 1. Understand what upstream changed and why
# 2. Understand what your fork changed
# 3. Keep both changes if possible (additive)
# 4. If truly conflicting, prefer upstream's approach + adapt your code

git add <resolved-files>
git commit
```

**Common Conflict Patterns:**

| Conflict Type | Resolution Strategy |
|--------------|---------------------|
| Enum additions (ChainID, etc.) | Keep both, your addition at end of list |
| New function signatures | Update your Stacks code to match new signature |
| Schema changes | Merge both schema changes, ensure consistency |
| Import reordering | Accept upstream's imports, add yours |
| Type changes | Update Stacks types to match new patterns |

**After Resolution:**
```bash
# Always test after conflict resolution
uv run python pytestgeventwrapper.py -k stacks
cd frontend && pnpm run test:unit
```

---

## 5. Release Strategy

### Versioning

Follow upstream version with suffix:
- Upstream: `v1.41.3`
- Your release: `v1.41.3-stacks.1`

**When to increment the suffix:**
- `v1.41.3-stacks.1` → `v1.41.3-stacks.2`: After syncing upstream commits (same base version)
- `v1.41.3-stacks.2` → `v1.42.0-stacks.1`: When upstream releases a new version

```bash
# Same upstream base, different fork commits
git tag v1.41.3-stacks.2 -m "Upstream sync: bug fixes"
git push origin v1.41.3-stacks.2

# New upstream version
git tag v1.42.0-stacks.1 -m "Based on upstream v1.42.0"
git push origin v1.42.0-stacks.1
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

## 8. Working with Git Worktrees

Git worktrees allow multiple branches checked out simultaneously - useful for parallel work.

### Why Use Worktrees?
- Test changes without switching branches
- Run different versions side-by-side
- Keep development environment running while working on fixes

### Setup Worktrees

```bash
# Create worktree in .worktrees/ subdirectory
git worktree add .worktrees/fix-issue-42 -b fix/issue-42

# Work in the worktree
cd .worktrees/fix-issue-42
# Make changes, commit, push

# Back to main repo
cd ../..
```

### Cleanup After Merge

```bash
# Remove worktree
git worktree remove .worktrees/fix-issue-42

# Delete branch
git branch -d fix/issue-42
```

### List Active Worktrees

```bash
git worktree list
```

---

## 9. Branch Cleanup Cadence

**Clean up regularly** to avoid branch clutter:

### After Every Merge
```bash
# Delete merged feature branches immediately
git branch -d feat/my-feature
git push origin --delete feat/my-feature
```

### Monthly Review
```bash
# List branches not updated in 30+ days
git for-each-ref --sort=-committerdate refs/heads/ --format='%(refname:short) %(committerdate:relative)'

# Delete if no longer needed
```

### Keep These Branches
- `main` - Stable releases
- `develop` - Active development
- `upstream-sync` - Upstream mirror
- Active feature branches

---

## 10. Tracking Sync Work with Issues

Create a GitHub issue for each significant upstream sync:

```markdown
# Upstream Sync: v1.42.0

Syncing with upstream rotki v1.42.0 release.

**Upstream commits:** 23 commits
**Changes:**
- New Avalanche subnet support
- Performance improvements
- Bug fixes

**Conflicts to resolve:** TBD
**Testing:** Full test suite + Stacks integration tests
**Target release:** v1.42.0-stacks.1
```

Benefits:
- Track what was synced when
- Document conflict resolution decisions
- Link to release tags
- Reference for future syncs

---

## 11. Fork Health Monitoring

### Check if You're Falling Behind

```bash
# How many commits behind upstream?
git fetch upstream
git log --oneline develop..upstream/develop | wc -l

# What changed upstream?
git log --oneline develop..upstream/develop

# How different is your fork?
git diff upstream-sync develop --shortstat
```

**Guidelines:**
- **< 10 commits behind**: Sync when convenient
- **10-50 commits behind**: Sync soon (weekly/bi-weekly)
- **> 50 commits behind**: Priority sync - technical debt accumulating

### Measure Fork Complexity

```bash
# Count lines changed vs upstream
git diff upstream-sync develop --numstat | awk '{added+=$1; removed+=$2} END {print "Added:", added, "Removed:", removed}'

# List files with most changes
git diff upstream-sync develop --numstat | sort -rn | head -20
```

**Interpretation:**
- **< 5,000 lines**: Clean additive fork (good)
- **5,000-20,000 lines**: Moderate divergence (manageable)
- **> 20,000 lines**: Consider splitting features or upstreaming

### Track Merge Difficulty Over Time

After each sync, document:
```markdown
| Date | Upstream Commits | Conflicts | Resolution Time | Notes |
|------|-----------------|-----------|-----------------|-------|
| 2026-01-26 | 4 | 0 | 10 min | Clean merge |
| 2026-02-10 | 12 | 2 | 30 min | Schema conflicts |
```

If merge difficulty increases, consider:
1. More frequent syncs (reduce batch size)
2. Contributing changes back upstream
3. Refactoring fork to be less invasive

---

## 12. Commands Reference

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

# Count commits in each direction
git rev-list --left-right --count upstream/develop...develop
# Output: X Y (X=upstream ahead, Y=you ahead)
```
