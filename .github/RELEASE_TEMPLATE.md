# rotki-stacks {VERSION}

Stacks-enabled fork of rotki based on upstream v{UPSTREAM_VERSION}.

---

## What's New

### Stacks Integration

- [List major Stacks features added or improved]
- Example: Added support for new DeFi protocol
- Example: Improved transaction decoding accuracy
- Example: Enhanced balance query performance

### Upstream Sync

- Based on rotki v{UPSTREAM_VERSION}
- Synced {N} commits from upstream develop
- Notable upstream changes:
  - [List important upstream improvements]
  - Example: Performance optimization for large portfolios
  - Example: New exchange integration (Binance, Kraken, etc.)
  - Example: UI/UX improvements

### Bug Fixes

- [List bugs fixed in this release]
- Example: Fixed Stacks token icon loading issue
- Example: Resolved balance refresh timing problem
- Example: Corrected transaction fee calculations

### Known Issues

- [List any known issues or limitations]
- [Link to GitHub issues if applicable]
- Example: Some third-party token icons may not load
- Example: Large transaction history may take time to sync

---

## Installation

### Docker (Recommended)

```bash
# Pull the specific version
docker pull alexlmiller/rotki-stacks:{VERSION}

# Run with persistent data
docker run -d \
  --name rotki-stacks \
  -p 80:80 \
  -v rotki-data:/data \
  -v rotki-logs:/logs \
  alexlmiller/rotki-stacks:{VERSION}
```

**Access**: http://localhost

**Stop**: `docker stop rotki-stacks`
**Start**: `docker start rotki-stacks`
**Logs**: `docker logs rotki-stacks`

### From Source

See [dev-environment.md](https://github.com/alexlmiller/rotki-stacks/blob/main/docs/stacks-chain/dev-environment.md) for build instructions.

---

## Upgrading

### From Previous Version

**Docker:**
```bash
# Stop current container
docker stop rotki-stacks
docker rm rotki-stacks

# Pull new version
docker pull alexlmiller/rotki-stacks:{VERSION}

# Run new version (data persists in volumes)
docker run -d \
  --name rotki-stacks \
  -p 80:80 \
  -v rotki-data:/data \
  -v rotki-logs:/logs \
  alexlmiller/rotki-stacks:{VERSION}
```

**Database migrations** (if any):
- Automatic on first startup
- Backup recommended before upgrading: `docker cp rotki-stacks:/data ./backup`

---

## Documentation

- **Stacks Integration PRD**: [stacks-integration-prd.md](https://github.com/alexlmiller/rotki-stacks/blob/main/docs/stacks-chain/stacks-integration-prd.md)
- **Fork Maintenance**: [fork-maintenance-plan.md](https://github.com/alexlmiller/rotki-stacks/blob/main/docs/stacks-chain/fork-maintenance-plan.md)
- **Development Environment**: [dev-environment.md](https://github.com/alexlmiller/rotki-stacks/blob/main/docs/stacks-chain/dev-environment.md)
- **Release Process**: [release-process.md](https://github.com/alexlmiller/rotki-stacks/blob/main/docs/stacks-chain/release-process.md)

---

## Supported Platforms

### Docker Images

- **linux/amd64** - Intel/AMD 64-bit systems
- **linux/arm64** - ARM 64-bit systems (Apple Silicon, Raspberry Pi 4+, etc.)

### Tested On

- macOS 13+ (Intel & Apple Silicon)
- Ubuntu 22.04 LTS
- Debian 12
- Raspberry Pi 4 (8GB RAM recommended)

---

## Support

- **Issues**: https://github.com/alexlmiller/rotki-stacks/issues
- **Discussions**: https://github.com/alexlmiller/rotki-stacks/discussions
- **Upstream rotki**: https://github.com/rotki/rotki

---

## Checksums

Docker image digests:
```
linux/amd64: sha256:[digest will be in workflow output]
linux/arm64: sha256:[digest will be in workflow output]
```

Verify with:
```bash
docker manifest inspect alexlmiller/rotki-stacks:{VERSION}
```

---

## Credits

- **Upstream rotki**: https://github.com/rotki/rotki
- **Stacks blockchain**: https://www.stacks.co/
- **Contributors**: [List any contributors if applicable]

---

## License

Same as upstream rotki: AGPL-3.0
