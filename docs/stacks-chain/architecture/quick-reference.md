# Stacks Integration Quick Reference

Essential patterns for implementing Stacks support. For details, see other files in this directory.

**Reference Implementation**: `rotkehlchen/chain/solana/`

---

## Directory Structure

```
rotkehlchen/chain/stacks/
├── __init__.py
├── constants.py          # STX_DECIMALS, contract addresses
├── manager.py            # StacksManager
├── node_inquirer.py      # StacksInquirer (Hiro API)
├── transactions.py       # StacksTransactions
├── types.py              # StacksTransaction dataclass
├── utils.py              # micro_stx_to_stx(), etc.
├── validation.py         # is_valid_stacks_address()
└── decoding/
    ├── decoder.py        # StacksTransactionDecoder
    ├── interfaces.py     # StacksDecoderInterface
    ├── structures.py     # Context/Output types
    └── tools.py          # StacksDecoderTools

rotkehlchen/chain/stacks/modules/
├── sbtc/decoder.py
├── stacking/decoder.py
└── stackingdao/decoder.py
```

---

## Class Inheritance

| Class | Inherits From | Type Parameters |
|-------|---------------|-----------------|
| `StacksManager` | `ChainManagerWithTransactions[StacksAddress]` | Address |
| `DBStacksTx` | `DBCommonTx[Addr, Tx, Hash, Filter, NotDecodedFilter]` | 5 params |
| `StacksEvent` | `OnchainEvent[str, StacksAddress]` | TxRef, Address |
| `StacksDecoderInterface` | `DecoderInterface[Addr, Inquirer, Tools]` | 3 params |

---

## Key Patterns

### Manager Initialization
```python
class StacksManager(ChainManagerWithTransactions[StacksAddress]):
    def __init__(self, node_inquirer: StacksInquirer, premium: Premium | None = None):
        super().__init__()  # No args
        self.node_inquirer = node_inquirer
        self.database = node_inquirer.database  # Extract from inquirer
```

### Balance Query
```python
def query_balances(self, addresses: Sequence[StacksAddress]) -> dict[StacksAddress, BalanceSheet]:
    balances: defaultdict[StacksAddress, BalanceSheet] = defaultdict(BalanceSheet)
    native_price = Inquirer.find_usd_price(A_STX)
    for addr, amount in self.get_multi_balance(addresses).items():
        if amount != ZERO:
            balances[addr].assets[A_STX][DEFAULT_BALANCE_LABEL] = Balance(
                amount=amount, value=amount * native_price)
    return dict(balances)
```

### API Query with Error Handling
```python
def _query(self, endpoint: str) -> dict:
    try:
        response = self.session.get(f'{self.api_url}{endpoint}', timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RemoteError(f'Stacks API error: {e}') from e
```

### Protocol Decoder
```python
class SbtcDecoder(StacksDecoderInterface):
    def addresses_to_decoders(self) -> dict[StacksAddress, tuple[Callable, ...]]:
        return {SBTC_CONTRACT: (self._decode_sbtc_operation,)}

    @staticmethod
    def counterparties() -> tuple[CounterpartyDetails, ...]:
        return (CounterpartyDetails(identifier=CPT_SBTC, label='sBTC', image='sbtc.svg'),)
```

---

## Constants

| Constant | Value | Location |
|----------|-------|----------|
| `STX_DECIMALS` | 6 | `chain/stacks/constants.py` |
| `Location.STACKS` | 57 | `types.py` |
| `SupportedBlockchain.STACKS` | 'STX' | `types.py` |
| Asset identifier format | `stacks/sip10_fungible:{contract}` | |

---

## Commands

```bash
# Lint
make lint

# Format
make format

# Test (ALWAYS use wrapper)
uv run python pytestgeventwrapper.py rotkehlchen/tests/unit/test_stacks.py

# Record VCR cassettes
RECORD_CASSETTES=true uv run python pytestgeventwrapper.py -m vcr TEST_PATH
```

---

## Solana → Stacks Mapping

| Solana | Stacks |
|--------|--------|
| `SolanaAddress` | `StacksAddress` |
| `Signature` (bytes) | `str` (tx_id) |
| SOL (9 decimals) | STX (6 decimals) |
| SPL tokens | SIP-10 tokens |
| Helius API | Hiro API |
| Location 55 | Location 57 |

---

## Files by Phase

| Phase | Key Files |
|-------|-----------|
| 1 - Types | `types.py`, `validation.py`, `constants.py` |
| 2 - Balances | `node_inquirer.py`, `manager.py`, `aggregator.py` |
| 3 - Tokens | `assets/utils.py`, `globaldb/handler.py` |
| 4 - Transactions | `transactions.py`, `db/stackstx.py`, `db/filtering.py` |
| 5 - Decoding | `decoding/*.py`, `history/events/structures/stacks_event.py` |
| 6 - Protocols | `modules/*/decoder.py` |
| 7 - Frontend | `frontend/app/src/pages/accounts/stacks/` |
