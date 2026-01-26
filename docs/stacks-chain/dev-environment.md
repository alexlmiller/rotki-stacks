# Development Environment Setup

Quick guide for running the full Rotki dev stack on this fork.

---

## Prerequisites

- **Node.js** 22+ (warning shown but works with 25.x)
- **pnpm** 10+
- **Python** 3.11+
- **Rust** stable toolchain (cargo in PATH)
- **uv** package manager

---

## Initial Setup

```bash
# Clone and enter worktree
cd /path/to/rotki/.worktrees/feat-add-stacks-chain

# Install JS dependencies
pnpm install

# Sync Python virtual environment
uv sync
```

---

## Running the Dev Stack

The dev script requires both the Python venv activated AND cargo in PATH:

```bash
# From repo root
cd frontend
export PATH="$HOME/.cargo/bin:$PATH"
source ../.venv/bin/activate
pnpm dev:web
```

This starts all three services:
- **Frontend** (Vite): http://localhost:8080
- **Backend** (Flask): http://localhost:4242
- **Colibri** (Rust): http://localhost:4343

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "No python virtual environment detected" | venv not activated | `source ../.venv/bin/activate` |
| "Cargo is not installed" | cargo not in PATH | `export PATH="$HOME/.cargo/bin:$PATH"` |
| Port 8080 in use | Previous instance | Kill processes or use assigned port |

---

## Verifying Services

```bash
# Backend
curl http://localhost:4242/api/1/ping
# Expected: {"result": true, "message": ""}

# Colibri (check logs)
tail -5 frontend/logs/colibri.log
# Expected: "Colibri api listens on 127.0.0.1:4343"
```

---

## Alternative: Run Services Individually

```bash
# Backend only
uv run python -m rotkehlchen --api-port 4242 --websockets-port 4333

# Colibri only
cd colibri && cargo run -- --port 4343

# Frontend only (needs backend running)
cd frontend/app && pnpm run dev
```

---

## Stopping Everything

```bash
pkill -f "rotkehlchen|colibri|vite|tsx"
```
