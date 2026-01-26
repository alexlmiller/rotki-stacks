"""Hermetica protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_HERMETICA: Final = 'hermetica'

# Hermetica Core Contracts
HERMETICA_USDH_CONTRACT: Final = StacksAddress(
    'SP2H3SBR2W97SZ4V93RY82DKTKHHVRP0VQTH7DH0M.usdh-token-v1',
)
HERMETICA_RESERVE_CONTRACT: Final = StacksAddress(
    'SP2H3SBR2W97SZ4V93RY82DKTKHHVRP0VQTH7DH0M.hermetica-reserve-v1',
)
HERMETICA_POOL_CONTRACT: Final = StacksAddress(
    'SP2H3SBR2W97SZ4V93RY82DKTKHHVRP0VQTH7DH0M.hermetica-pool-v1',
)
HERMETICA_STAKING_CONTRACT: Final = StacksAddress(
    'SP2H3SBR2W97SZ4V93RY82DKTKHHVRP0VQTH7DH0M.hermetica-staking-v1',
)

# Function names
HERMETICA_MINT: Final = 'mint'
HERMETICA_BURN: Final = 'burn'
HERMETICA_REDEEM: Final = 'redeem'
HERMETICA_STAKE: Final = 'stake'
HERMETICA_UNSTAKE: Final = 'unstake'
HERMETICA_CLAIM: Final = 'claim'

# Two-phase minting/redemption function names
HERMETICA_REQUEST_MINT: Final = 'request-mint'
HERMETICA_CONFIRM_MINT: Final = 'confirm-mint'
HERMETICA_REQUEST_REDEEM: Final = 'request-redeem'
HERMETICA_CONFIRM_REDEEM: Final = 'confirm-redeem'

# Minting-related function names
HERMETICA_MINT_FUNCTIONS: Final = frozenset({
    HERMETICA_MINT,
})

# Burning/redemption-related function names
HERMETICA_BURN_FUNCTIONS: Final = frozenset({
    HERMETICA_BURN,
    HERMETICA_REDEEM,
})

# Two-phase request functions (informational)
HERMETICA_REQUEST_FUNCTIONS: Final = frozenset({
    HERMETICA_REQUEST_MINT,
    HERMETICA_REQUEST_REDEEM,
})

# Two-phase confirm functions (actual transfers)
HERMETICA_CONFIRM_MINT_FUNCTIONS: Final = frozenset({
    HERMETICA_CONFIRM_MINT,
})

HERMETICA_CONFIRM_REDEEM_FUNCTIONS: Final = frozenset({
    HERMETICA_CONFIRM_REDEEM,
})

# Staking function names
HERMETICA_STAKING_FUNCTIONS: Final = frozenset({
    HERMETICA_STAKE,
    HERMETICA_UNSTAKE,
    HERMETICA_CLAIM,
})

# All Hermetica contracts
HERMETICA_CONTRACTS: Final = frozenset({
    HERMETICA_USDH_CONTRACT,
    HERMETICA_RESERVE_CONTRACT,
    HERMETICA_POOL_CONTRACT,
    HERMETICA_STAKING_CONTRACT,
})
