"""Stacks blockchain constants and configuration."""

import csv
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Final, NamedTuple

from rotkehlchen.fval import FVal
from rotkehlchen.history.events.structures.types import HistoryEventType

if TYPE_CHECKING:
    from rotkehlchen.chain.decoding.types import CounterpartyDetails

# Hiro API configuration
HIRO_API_BASE_URL: Final = 'https://api.mainnet.hiro.so'
HIRO_METADATA_API_URL: Final = 'https://api.hiro.so/metadata/v1'

# Retry/backoff configuration for rate limiting
INITIAL_BACKOFF: Final = 4  # seconds
BACKOFF_MULTIPLIER: Final = 2
MAX_RETRIES: Final = 3

# STX token configuration
STX_DECIMALS: Final = 6


class StacksTokenMetadata(NamedTuple):
    """Metadata for well-known Stacks tokens."""

    name: str
    symbol: str
    decimals: int
    coingecko: str | None = None
    cryptocompare: str | None = None
    protocol: str | None = None


@lru_cache(maxsize=1)
def _load_curated_tokens() -> dict[str, StacksTokenMetadata]:
    """Load curated token metadata from CSV. Cached after first load."""
    tokens: dict[str, StacksTokenMetadata] = {}
    csv_path = Path(__file__).resolve().parent.parent.parent / 'data' / 'stacks_tokens_data.csv'

    if not csv_path.exists():
        return tokens

    with csv_path.open(encoding='utf-8') as f:
        for row in csv.DictReader(f):
            tokens[row['contract_id']] = StacksTokenMetadata(
                name=row['name'],
                symbol=row['symbol'],
                decimals=int(row['decimals']) if row['decimals'] else 0,
                coingecko=row['coingecko'] or None,
                cryptocompare=row['cryptocompare'] or None,
                protocol=row['protocol'] or None,
            )
    return tokens


def get_curated_token_metadata(contract_id: str) -> StacksTokenMetadata | None:
    """Get curated metadata for a well-known Stacks token.

    Args:
        contract_id: The contract ID (e.g., SP3K8BC0...sbtc-token)

    Returns:
        StacksTokenMetadata if found, None otherwise
    """
    return _load_curated_tokens().get(contract_id)


# Backward compatibility for code that imports CURATED_STACKS_TOKENS
def __getattr__(name: str) -> dict[str, StacksTokenMetadata]:
    if name == 'CURATED_STACKS_TOKENS':
        return _load_curated_tokens()
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


def micro_stx_to_stx(micro_stx: int) -> FVal:
    """Convert microSTX (smallest unit) to STX.

    Args:
        micro_stx: Amount in microSTX (1 STX = 1,000,000 microSTX)

    Returns:
        Amount in STX as FVal
    """
    return FVal(micro_stx) / (10**STX_DECIMALS)


# Event types that represent outgoing transfers (used for note directionality)
# Defined here to avoid dependency on EVM-specific constants
OUTGOING_EVENT_TYPES: Final = frozenset({
    HistoryEventType.SPEND,
    HistoryEventType.TRANSFER,
    HistoryEventType.DEPOSIT,
})


def get_all_stacks_counterparties() -> set['CounterpartyDetails']:
    """Get all Stacks protocol counterparties for UI filtering.

    Returns a set of CounterpartyDetails for all supported Stacks protocols.
    This function avoids circular imports by importing at runtime.
    """
    from rotkehlchen.chain.decoding.types import CounterpartyDetails
    return {
        CounterpartyDetails(identifier='alex', label='ALEX', image='alex.svg'),
        CounterpartyDetails(identifier='allbridge', label='Allbridge', image='allbridge.svg'),
        CounterpartyDetails(identifier='arkadiko', label='Arkadiko', image='arkadiko.svg'),
        CounterpartyDetails(identifier='bitflow', label='Bitflow', image='bitflow.svg'),
        CounterpartyDetails(identifier='dual-stacking', label='Dual Stacking', image='stacks.svg'),
        CounterpartyDetails(identifier='hermetica', label='Hermetica', image='hermetica.svg'),
        CounterpartyDetails(identifier='pox', label='Proof of Transfer', image='stacks.svg'),
        CounterpartyDetails(identifier='sbtc', label='sBTC', image='sbtc.png'),
        CounterpartyDetails(identifier='send-many', label='Send Many', image='stacks.svg'),
        CounterpartyDetails(
            identifier='stacking-pools', label='Stacking Pools', image='stacks.svg',
        ),
        CounterpartyDetails(
            identifier='stackingdao', label='StackingDAO', image='stackingdao.svg',
        ),
        CounterpartyDetails(identifier='stx-20', label='STX-20', image='stacks.svg'),
        CounterpartyDetails(identifier='usdcx', label='USDCx', image='usdc.svg'),
        CounterpartyDetails(identifier='velar', label='Velar', image='velar.svg'),
        CounterpartyDetails(identifier='zest', label='Zest', image='zest.svg'),
    }
