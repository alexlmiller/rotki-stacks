"""Stacks blockchain constants and configuration."""
from typing import Final

from rotkehlchen.fval import FVal

# Hiro API configuration
HIRO_API_BASE_URL: Final = 'https://api.mainnet.hiro.so'

# Retry/backoff configuration for rate limiting
INITIAL_BACKOFF: Final = 4  # seconds
BACKOFF_MULTIPLIER: Final = 2
MAX_RETRIES: Final = 3

# STX token configuration
STX_DECIMALS: Final = 6


def micro_stx_to_stx(micro_stx: int) -> FVal:
    """Convert microSTX (smallest unit) to STX.

    Args:
        micro_stx: Amount in microSTX (1 STX = 1,000,000 microSTX)

    Returns:
        Amount in STX as FVal
    """
    return FVal(micro_stx) / (10 ** STX_DECIMALS)
