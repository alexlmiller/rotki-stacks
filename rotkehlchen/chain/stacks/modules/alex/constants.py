"""ALEX DEX protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_ALEX: Final = 'alex'

# ALEX Core Contracts
ALEX_SWAP_CONTRACT: Final = StacksAddress(
    'SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.amm-pool-v2-01',
)
ALEX_SWAP_HELPER_CONTRACT: Final = StacksAddress(
    'SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.swap-helper-v1-03',
)
ALEX_FARMING_CONTRACT: Final = StacksAddress(
    'SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.alex-farming',
)
ALEX_STAKING_CONTRACT: Final = StacksAddress(
    'SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.alex-staking',
)
ALEX_LAUNCHPAD_CONTRACT: Final = StacksAddress(
    'SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.alex-launchpad',
)

# ALEX Token
ALEX_TOKEN_CONTRACT: Final = StacksAddress(
    'SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.token-alex',
)

# Function names for swaps
ALEX_SWAP_HELPER: Final = 'swap-helper'
ALEX_SWAP_HELPER_A: Final = 'swap-helper-a'
ALEX_SWAP_HELPER_B: Final = 'swap-helper-b'
ALEX_SWAP_HELPER_C: Final = 'swap-helper-c'
ALEX_SWAP_X_FOR_Y: Final = 'swap-x-for-y'
ALEX_SWAP_Y_FOR_X: Final = 'swap-y-for-x'

# Function names for liquidity
ALEX_ADD_TO_POSITION: Final = 'add-to-position'
ALEX_REDUCE_POSITION: Final = 'reduce-position'

# Function names for farming
ALEX_STAKE: Final = 'stake'
ALEX_UNSTAKE: Final = 'unstake'
ALEX_CLAIM_REWARDS: Final = 'claim-rewards'
ALEX_CLAIM: Final = 'claim'

# Swap-related function names
ALEX_SWAP_FUNCTIONS: Final = frozenset({
    ALEX_SWAP_HELPER,
    ALEX_SWAP_HELPER_A,
    ALEX_SWAP_HELPER_B,
    ALEX_SWAP_HELPER_C,
    ALEX_SWAP_X_FOR_Y,
    ALEX_SWAP_Y_FOR_X,
})

# Liquidity-related function names
ALEX_LIQUIDITY_FUNCTIONS: Final = frozenset({
    ALEX_ADD_TO_POSITION,
    ALEX_REDUCE_POSITION,
})

# Staking/farming function names
ALEX_STAKING_FUNCTIONS: Final = frozenset({
    ALEX_STAKE,
    ALEX_UNSTAKE,
    ALEX_CLAIM_REWARDS,
    ALEX_CLAIM,
})

# All ALEX contracts
ALEX_CONTRACTS: Final = frozenset({
    ALEX_SWAP_CONTRACT,
    ALEX_SWAP_HELPER_CONTRACT,
    ALEX_FARMING_CONTRACT,
    ALEX_STAKING_CONTRACT,
    ALEX_LAUNCHPAD_CONTRACT,
})
