"""Stacks blockchain constants and configuration."""
from typing import Final, NamedTuple

from rotkehlchen.fval import FVal

# Hiro API configuration
HIRO_API_BASE_URL: Final = 'https://api.mainnet.hiro.so'

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


# Curated metadata for well-known Stacks tokens
# Key is the contract ID without ::asset-name suffix
CURATED_STACKS_TOKENS: Final[dict[str, StacksTokenMetadata]] = {
    # sBTC - Bitcoin-backed token on Stacks
    'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-token': StacksTokenMetadata(
        name='sBTC',
        symbol='sBTC',
        decimals=8,  # Same as BTC
        coingecko='sbtc',
        protocol='sbtc',
    ),
    # stSTX - StackingDAO liquid staking token
    'SM3KNVZS30WM7F89SXKVVFY4SN9RMPZZ9FX929N0V.ststx-token': StacksTokenMetadata(
        name='Stacked STX',
        symbol='stSTX',
        decimals=6,  # Same as STX
        coingecko='stacked-stx',
        protocol='stackingdao',
    ),
    # ALEX - ALEX Lab governance token
    'SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.token-alex': StacksTokenMetadata(
        name='ALEX',
        symbol='ALEX',
        decimals=8,
        coingecko='alexgo',
        protocol='alex',
    ),
    # VELAR - Velar DEX token
    'SP1Y5YSTAHZ88XYK1VPDH24GY0HPX5J4JECTMY4A1.velar-token': StacksTokenMetadata(
        name='Velar',
        symbol='VELAR',
        decimals=6,
        coingecko='velar',
        protocol='velar',
    ),
    # USDA - Arkadiko stablecoin
    'SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.usda-token': StacksTokenMetadata(
        name='USDA',
        symbol='USDA',
        decimals=6,
        coingecko='usda',
        protocol='arkadiko',
    ),
    # xBTC - Wrapped Bitcoin on Stacks (legacy)
    'SP3DX3H4FEYZJZ586MFBS25ZW3HZDMEW92260R2PR.Wrapped-Bitcoin': StacksTokenMetadata(
        name='Wrapped Bitcoin',
        symbol='xBTC',
        decimals=8,
        coingecko='wrapped-bitcoin-stacks',
        protocol=None,
    ),
}


def get_curated_token_metadata(contract_id: str) -> StacksTokenMetadata | None:
    """Get curated metadata for a well-known Stacks token.

    Args:
        contract_id: The contract ID (e.g., SP3K8BC0...sbtc-token)

    Returns:
        StacksTokenMetadata if found, None otherwise
    """
    return CURATED_STACKS_TOKENS.get(contract_id)


def micro_stx_to_stx(micro_stx: int) -> FVal:
    """Convert microSTX (smallest unit) to STX.

    Args:
        micro_stx: Amount in microSTX (1 STX = 1,000,000 microSTX)

    Returns:
        Amount in STX as FVal
    """
    return FVal(micro_stx) / (10 ** STX_DECIMALS)
