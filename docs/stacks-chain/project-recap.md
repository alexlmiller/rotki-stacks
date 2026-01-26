# Stacks Integration for Rotki - Project Recap

**Project**: First-class Stacks blockchain support for Rotki
**Timeline**: Weekend hackathon (Saturday evening setup + Sunday full implementation)
**Branch**: `feat/add-stacks-chain`
**Status**: Complete (100 tests passing)

---

## Executive Summary

This project adds full Stacks blockchain support to Rotki, an open-source, privacy-focused crypto portfolio manager and tax calculator. The integration enables Stacks users to track STX holdings, SIP-10 tokens, transaction history, and DeFi protocol interactions for tax preparation and portfolio analysis.

**Key Stats**:
- 30 commits
- 126 files changed
- ~8,900 lines added
- 52 new Python files
- 14 protocol decoder modules
- 100 unit tests

---

## 1. The Problem

### Gap in the Stacks Ecosystem

- Limited options for Stacks tax tracking exist today
- Cross-chain users have fragmented portfolios (STX in one tool, ETH in another)
- No self-custody, offline-first solution exists for Stacks

### The Opportunity

Rotki is an open-source portfolio tracker supporting 40+ chains - but not Stacks. This integration fills that gap.

### Primary Job-to-be-Done

> "I need to file my taxes with accurate cost basis and complete transaction history for all my STX-affiliated transactions, including native STX, SIP-10 tokens like sBTC, stacking rewards, and cross-chain bridge operations."

---

## 2. What is Rotki?

For those unfamiliar:

- **Open-source** crypto portfolio manager & tax calculator
- **Self-custody data** - your financial data stays on your machine (SQLite + SQLCipher encryption)
- **Python backend**, Vue.js frontend, runs as desktop app or web
- Already supports: Ethereum, Bitcoin, Solana, 40+ exchanges
- Established patterns for adding new chains

**Why this matters**: It's not a SaaS that holds your data - it's software you run locally.

---

## 3. What We Built

### Feature Summary

| Feature | Status |
|---------|--------|
| STX balance tracking | Complete |
| 13 SIP-10 tokens (sBTC, stSTX, ALEX, USDA...) | Complete |
| Complete transaction history | Complete |
| Human-readable event decoding | Complete |
| 14 protocol decoders | Complete |
| Frontend integration | Complete |
| 100 tests passing | Complete |

### Supported Tokens (13 curated)

| Token | Contract | Type |
|-------|----------|------|
| STX | Native | Native |
| sBTC | `SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-token` | Bridge |
| stSTX | `SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.ststx-token` | Liquid Staking |
| stSTXBTC | `SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.ststxbtc-token-v2` | Liquid Staking |
| USDCx | `SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx` | Stablecoin |
| aeUSDC | `SP3Y2ZSH8P7D50B0VBTSX11S7XSG24M1VB9YFQA4K.token-aeusdc` | Stablecoin |
| ALEX | `SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.token-alex` | DEX |
| VELAR | `SP1Y5YSTAHZ88XYK1VPDH24GY0HPX5J4JECTMY4A1.velar-token` | DEX |
| USDA | `SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.usda-token` | Stablecoin |
| xBTC | `SP3DX3H4FEYZJZ586MFBS25ZW3HZDMEW92260R2PR.Wrapped-Bitcoin` | Wrapped |
| zstSTX | `SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.zststx-token` | Zest |
| zstSTXBTC | `SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.zststxbtc-v2-token` | Zest |
| zsBTC | `SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.zsbtc-token` | Zest |

### Protocol Decoder Coverage (14 modules)

| Category | Protocols |
|----------|-----------|
| **Bridges** | sBTC, Allbridge (aeUSDC/aeETH), USDCx |
| **Stacking** | Native PoX, StackingDAO, Third-party pools (Fastpool, Xverse, etc.) |
| **DEXes** | ALEX, Velar, Bitflow |
| **Lending** | Zest Protocol |
| **CDPs** | Arkadiko |
| **Synthetics** | Hermetica |
| **Utilities** | Send-many (batch transfers) |

---

## 4. Development Process

### Timeline

**Saturday evening**: Setup
- Forked Rotki repository
- Configured development environment
- Initial codebase exploration

**Sunday morning** (~2 hours): Planning & Documentation
- Product exploration with Claude Code
- Built comprehensive `CLAUDE.md` (project instructions for AI)
- Created architecture reference docs
- Wrote detailed PRD with 7 phased implementation plan

**Sunday afternoon/evening**: Implementation
- 7 implementation phases executed sequentially
- Claude Code for all primary coding
- Cursor + Gemini for code review and feedback
- 30 commits total

### AI-Assisted Development Workflow

The upfront investment in documentation (~2 hours) enabled efficient autonomous implementation:

| Document | Purpose |
|----------|---------|
| `CLAUDE.md` | Project conventions, coding rules |
| `stacks-integration-prd.md` | Scope, phases, acceptance criteria |
| `architecture/quick-reference.md` | Patterns to follow |
| `architecture/*.md` | Detailed implementation guides |

**Key insight**: Claude Code could work autonomously through phases because it had clear scope boundaries, architecture patterns, and coding conventions documented upfront.

---

## 5. Technical Implementation

### 5.1 Component Overview

**52 new Python files** across these components:

| Component | Files | Lines | Purpose |
|-----------|-------|-------|---------|
| Core module | 8 | ~1,200 | Manager, inquirer, API client, validation |
| Transaction handling | 3 | ~600 | Fetcher, DB handler, types |
| Clarity parser | 1 | 462 | Parse Clarity repr strings from Hiro API |
| Base decoder | 3 | ~700 | Transaction to human-readable events |
| Protocol decoders | 14 modules | ~2,500 | Protocol-specific event interpretation |
| Database | 3 | ~400 | Schema, migrations, filter queries |
| Tests | 2 | ~1,000 | Unit tests for validation + Clarity parser |

**33 frontend files** modified/created:
- New accounts page (`/accounts/stacks`)
- Event form component (345 lines)
- Address/txId validation functions
- Navigation, routing, localization
- Hiro API key settings page

### 5.2 Type System Integration

Adding a new blockchain to Rotki requires touching the type system in many places:

```python
# New types added to rotkehlchen/types.py
T_StacksAddress = str
StacksAddress = NewType('StacksAddress', T_StacksAddress)

class SupportedBlockchain(SerializableEnumValueMixin):
    STACKS = 'STX'  # Added

class ChainType(SerializableEnumNameMixin):
    STACKS = auto()  # Added

# Location enum for database
Location.STACKS = 57

# External services for API key management
class ExternalService(SerializableEnumNameMixin):
    HIRO = auto()
```

Every union type that includes blockchain addresses needed updating:
```python
BlockchainAddress = BTCAddress | ChecksumEvmAddress | SubstrateAddress | SolanaAddress | StacksAddress
```

### 5.3 The Clarity Parser

**The problem**: Hiro API returns function arguments as Clarity repr strings, not JSON:

```
# What Hiro returns:
"(tuple (to 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7) (ustx u1000000))"

# What we need:
{"to": "SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7", "ustx": 1000000}
```

**The solution**: Built a full lexer + parser (462 lines):

```python
class ClarityLexer:
    """Tokenizes: (, ), u123, -123, 'SP..., 0x..., "str", true/false, symbols"""

class ClarityParser:
    """Parses token stream into Python values"""
```

**Supported Clarity types**:
- Primitives: `uint`, `int`, `bool`
- Principals: `'SP...`, `SP...contract.name`
- Buffers: `0x1234...`
- Strings: `"ascii"`, `u"utf8"`
- Containers: `(some val)`, `none`, `(ok val)`, `(err val)`
- Structures: `(tuple (k1 v1) (k2 v2))`, `(list v1 v2 v3)`
- Nested combinations of all the above

**60 unit tests** cover edge cases, nested structures, and error handling.

### 5.4 Database Schema

New tables added via migration v51 to v52:

```sql
CREATE TABLE stacks_transactions (
    identifier INTEGER PRIMARY KEY,
    tx_id TEXT NOT NULL UNIQUE,
    block_height INTEGER NOT NULL,
    block_time INTEGER NOT NULL,
    tx_type TEXT NOT NULL,
    sender_address TEXT NOT NULL,
    fee_rate TEXT NOT NULL,        -- TEXT not INTEGER (overflow fix)
    nonce INTEGER NOT NULL,
    tx_status TEXT NOT NULL,
    recipient_address TEXT,
    amount TEXT,                   -- TEXT not INTEGER (overflow fix)
    contract_id TEXT,
    function_name TEXT,
    function_args TEXT,            -- JSON blob
    -- Indexed extracted args for efficient queries:
    arg_amount_ustx TEXT,
    arg_recipient TEXT,
    arg_delegate_to TEXT
);

CREATE TABLE stackstx_address_mappings (
    tx_id INTEGER NOT NULL,
    address TEXT NOT NULL,
    PRIMARY KEY(tx_id, address)
);

CREATE TABLE stacks_tx_mappings (
    tx_id INTEGER NOT NULL,
    value INTEGER NOT NULL,
    PRIMARY KEY (tx_id, value)
);
```

**Design decision**: Extract frequently-queried function arguments into indexed columns rather than always parsing JSON.

### 5.5 Transaction Decoding Pipeline

```
Hiro API Response
       |
       v
StacksTransactions.fetch()     --> Store raw tx in DB
       |
       v
StacksTransactionDecoder
       |
       v
+--------------------------------------------------+
| 1. Decode fee event (if tracked address)         |
| 2. Decode STX transfer (if token_transfer type)  |
| 3. Fetch token transfers from API events         |
| 4. Decode SIP-10 token transfers                 |
| 5. Apply protocol decoders:                      |
|    if is_sbtc_transaction() -> decode_sbtc()     |
|    elif is_pox_transaction() -> decode_pox()     |
|    elif is_alex_transaction() -> decode_alex()   |
|    ... (14 protocol checks)                      |
+--------------------------------------------------+
       |
       v
StacksEvent[]  --> Store in history_events table
```

### 5.6 Protocol Decoder Pattern

Each protocol module follows the same structure:

```
modules/arkadiko/
├── __init__.py      # Exports
├── constants.py     # Contract addresses, function names
└── decoder.py       # is_X_transaction(), decode_X_events()
```

**Constants define the contract landscape**:
```python
# constants.py
ARKADIKO_DAO_ADDRESS: Final = 'SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR'
ARKADIKO_FREDDIE_CONTRACT: Final = StacksAddress(
    f'{ARKADIKO_DAO_ADDRESS}.arkadiko-freddie-v1-1'
)

ARKADIKO_VAULT_DEPOSIT_FUNCTIONS: Final = frozenset({
    'collateralize-and-mint',
    'deposit',
})
```

**Decoders transform generic events into protocol-specific ones**:
```python
def decode_arkadiko_events(transaction, base_tools, existing_events):
    if function_name in ARKADIKO_VAULT_DEPOSIT_FUNCTIONS:
        for event in existing_events:
            if event.event_type == HistoryEventType.SPEND:
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.DEPOSIT_ASSET
                event.counterparty = CPT_ARKADIKO
                event.notes = f'Deposit {amount} {symbol} as collateral to Arkadiko vault'
```

### 5.7 Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| API Source | Hiro API only | Reliable, well-documented; self-hosted node deferred to v2 |
| Blocks | Anchored only | Avoid microblock reorg UX confusion |
| Tokens | Curated + lazy discovery | 13 pre-configured, unknown created on encounter |
| Function args | Full Clarity parser | Required for protocol-specific decoding |
| Amount storage | TEXT columns | Avoid SQLite integer overflow |

### 5.8 Hiro Token Metadata API Integration

**The problem**: When discovering new SIP-10 tokens (not in our curated list), we need their name, symbol, and decimals to display them properly in the UI. Without this metadata, tokens appear as "Unknown Stacks Token" with raw contract identifiers.

**The solution**: Integrate with the Hiro Token Metadata API to fetch token metadata on-demand.

**API Endpoint**:
```
GET https://api.hiro.so/metadata/v1/ft/{contract_principal}
```

**Response structure**:
```json
{
  "name": "Velar",
  "symbol": "VELAR",
  "decimals": 8,
  "total_supply": "100000000000000000",
  "image_uri": "https://...",
  "cached_image": "https://..."
}
```

**Implementation**:

1. **API Client** (`api_client.py`):
   ```python
   def get_token_metadata(self, contract_principal: str) -> StacksTokenMetadata | None:
       """Fetch token metadata from Hiro Token Metadata API."""
       url = f'{HIRO_METADATA_API_URL}/ft/{contract_principal}'
       response = requests.get(url, headers=headers, timeout=30)
       # Returns StacksTokenMetadata(name, symbol, decimals) or None
   ```

2. **Balance Fetching** (`manager.py`):
   - When parsing fungible token balances, fetch metadata before creating tokens
   - Passes name/symbol/decimals to `get_or_create_stacks_token()`

3. **Transaction Decoding** (`decoder.py`):
   - When decoding SIP-10 token transfers, fetch metadata for unknown tokens
   - Ensures decoded events show proper token names

**Colibri Integration** (Rust icon service):
- Added `query_hiro_token_icon()` function to fetch token images
- Image URL priority: `cached_image` > `cached_thumbnail_image` > `image_canonical_uri` > `image_uri`
- Falls back to STX icon for tokens without metadata images

**Benefits**:
- New tokens automatically get proper names/symbols from the API
- No manual curation required for every token
- Icons fetched dynamically for better UI experience

---

## 6. Challenges & Bug Fixes

| Issue | Discovery | Root Cause | Fix |
|-------|-----------|------------|-----|
| **SQLite integer overflow** | Large STX amounts showed as negative | SQLite INTEGER is signed 64-bit; some token amounts exceed 2^63 | Changed amount columns from INTEGER to TEXT |
| **Wrong sBTC address** | Bridge transactions not decoded | Used testnet contract address | Updated to mainnet: `SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-token` |
| **Ambiguous column name** | Query crashes on transaction fetch | `tx_id` exists in multiple joined tables | Explicit table prefix: `stacks_transactions.tx_id` |
| **Hiro API asset suffix** | Token lookup failures | API returns `contract::asset-name`, we expected just `contract` | Strip `::*` suffix before lookup |
| **CHAINS_WITH_NODES error** | Startup crash | Stacks added to set but has no node support | Exclude Stacks from node-required chains |
| **Token metadata mismatch** | Tests failing | Curated token data didn't match API responses | Updated metadata to match Hiro API exactly |
| **stack-extend decoding** | Missing locked amount in notes | Wasn't extracting `lock-amount` from args | Parse Clarity args, extract and display |
| **Icon/branding issues** | Wrong logos displayed | CDN URLs incorrect or mismatched | Multiple fixes for STX icon, Hiro logo, sBTC logo |

### Lessons Learned

1. Always use TEXT for large numbers in SQLite (or handle overflow explicitly)
2. Mainnet vs testnet contract addresses are different - verify!
3. Test with real data early - many issues only surface with actual transactions
4. External API response formats can differ from documentation

---

## 7. Commit History

Commits in chronological order:

```
b58b6de87 Add Stacks blockchain type infrastructure
821d63377 Add Stacks chain manager and balance queries
d7f79985d Add SIP-10 token support for Stacks blockchain
4728d0167 Add Stacks transaction storage infrastructure
04883ea7b Add Stacks transaction decoding infrastructure
bebb27cfb Add Stacks protocol decoders
cbe1ae224 Add Stacks frontend integration
acfb9e995 Add Stacks to dashboard blockchain address dropdown
9c81ed47d Add Stacks to asset page chain filter
8b57729e9 Update Stacks and add sBTC logos
d663fc5cf Add STX asset icon URL to Colibri backend
c37cd6e9b Use square STX logo for chain and asset icons
5d9467173 Fix curated Stacks token metadata
6052cec58 Update tests to match corrected token metadata
ec5d62f89 Enable Stacks transaction decoding in API layer
0d7d962c9 Fix CHAINS_WITH_NODES to exclude Stacks
43cf7d1b7 Add Stacks to frontend transaction history refresh
d995b7413 Fix ambiguous tx_id column in Stacks DB query
49308d43d Add Stacks protocol decoders and Clarity parser
847f4f9c5 Fix SQLite integer overflow for large Stacks amounts
edbf27bdd Fix stack-extend to show locked STX amount
b19b823e9 Add pool stacking operation decoding to PoX
ab7e9503c Add Hiro API key configuration for Stacks
a6ac92a14 Fix Hiro logo to match official branding
fb3aac225 Add Velar XYK LP staking decoder support
70780c25b Fix sBTC contract addresses for mainnet
a7a3908e9 Add decoders for pools, bridges, and PoX auth
1d3877947 Fix STX icon URL to use cryptologos CDN
bbb407b84 Add Arkadiko, enhance Hermetica/Zest/ALEX decoders
```

---

## 8. Files Reference

### Backend - New Files

```
rotkehlchen/chain/stacks/
├── __init__.py
├── api_client.py               # Hiro API client
├── clarity_parser.py           # 462-line Clarity repr parser
├── constants.py                # Curated tokens, chain constants
├── manager.py                  # StacksManager
├── node_inquirer.py            # StacksInquirer
├── transactions.py             # Transaction fetcher
├── types.py                    # StacksTransaction dataclass
├── validation.py               # Address validation
└── decoding/
    ├── __init__.py
    ├── decoder.py              # Main decoder (~500 lines)
    └── tools.py                # StacksDecoderTools

rotkehlchen/chain/stacks/modules/
├── __init__.py
├── alex/                       # DEX (swaps, liquidity, staking, lending)
├── allbridge/                  # Bridge (aeUSDC, aeETH)
├── arkadiko/                   # CDP (vaults, debt, liquidations, staking)
├── bitflow/                    # DEX (swaps)
├── hermetica/                  # Synthetics (mint, burn, stake)
├── pox/                        # Native stacking
├── sbtc/                       # sBTC bridge
├── sendmany/                   # Batch transfers
├── stacking_pools/             # Third-party pools
├── stackingdao/                # Liquid staking
├── usdcx/                      # USDC bridge
├── velar/                      # DEX (swaps, LP staking)
└── zest/                       # Lending (supply, borrow, liquidation)

rotkehlchen/db/stackstx.py
rotkehlchen/db/upgrades/v51_v52.py
rotkehlchen/data_migrations/migrations/migration_23.py
rotkehlchen/history/events/structures/stacks_event.py
rotkehlchen/tests/unit/test_stacks.py
rotkehlchen/tests/unit/test_clarity_parser.py
```

### Frontend - New/Modified Files

```
frontend/app/src/pages/accounts/stacks/index.vue           # New accounts page
frontend/app/src/modules/history/management/forms/StacksEventForm.vue  # 345 lines
frontend/app/src/components/settings/api-keys/external/HiroApiKey.vue
frontend/app/public/assets/images/protocols/stacks.svg
frontend/app/public/assets/images/protocols/sbtc.svg
frontend/app/public/assets/images/services/hiro.svg
frontend/common/src/text/index.ts                          # Validation functions
frontend/app/src/locales/en.json                           # Localization
frontend/app/src/router/routes.ts                          # Routing
... (33 files total)
```

---

## 9. Code Complexity Stats

| Metric | Value |
|--------|-------|
| Total commits | 30 |
| Total files changed | 126 |
| Lines added | ~8,900 |
| Lines deleted | ~50 |
| Python files in `chain/stacks/` | 52 |
| Protocol decoder modules | 14 |
| Clarity parser lines | 462 |
| Unit tests added | 100 |
| Frontend files modified | 33 |
| Database tables added | 3 |
| Indexes added | 5 |
| Curated tokens | 13 |

---

## 10. What's Next

### v2 Possibilities

- **NFT support** (SIP-9 tokens)
- **Mempool tracking** (pending transactions)
- **Self-hosted node** option (alternative to Hiro API)
- **More protocol decoders** as ecosystem grows
- **Cross-chain correlation** (BTC <-> sBTC cost basis linking)

### Upstream Contribution

The code is structured to potentially be contributed upstream to the main Rotki repository, following their contribution guidelines and patterns.

---

## 11. Demo Scenarios

For a 5-minute walkthrough:

1. **Add a Stacks address** - Show validation feedback
2. **View balances** - STX + token balances with USD values
3. **Browse transaction history** - Decoded events with human-readable notes
4. **Protocol-specific events** - e.g., "Stake 100 STX on StackingDAO"
5. **Counterparty labels** - Show protocol attribution

---

*Document generated: January 2025*
*Branch: feat/add-stacks-chain*
*Tests: 100 passing*

## What it Supports on DeFi

  - sBTC - bridge operations                                                                                                                                                                                                                    
  - Allbridge - aeUSDC, aeETH bridging                                                                                                                                                                                                          
  - USDCx - Circle USDC bridging                                                                                                                                                                                                                
  - PoX - native stacking                                                                                                                                                                                                                       
  - StackingDAO - liquid staking                                                                                                                                                                                                                
  - Stacking Pools - Fastpool, Xverse, etc.                                                                                                                                                                                                     
  - Send-many - batched transfers                                                                                                                                                                                                               
  - ALEX - DEX swaps/liquidity                                                                                                                                                                                                                  
  - Velar - DEX swaps/liquidity/staking                                                                                                                                                                                                         
  - Bitflow - DEX operations                                                                                                                                                                                                                    
  - Zest - lending                                                                                                                                                                                                                              
  - Hermetica - synthetic assets                                                                                                                                                                                                                
  - Arkadiko - CDP protocol   
