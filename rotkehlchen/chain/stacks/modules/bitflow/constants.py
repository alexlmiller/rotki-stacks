"""Bitflow DEX protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_BITFLOW: Final = 'bitflow'

# Bitflow Core Contracts
BITFLOW_CORE_CONTRACT: Final = StacksAddress(
    'SPQC38PW542EQJ5M11CR25P7BS1CA6QT4TBXGB3M.stableswap-core-v-1-2',
)
BITFLOW_ROUTER_CONTRACT: Final = StacksAddress(
    'SPQC38PW542EQJ5M11CR25P7BS1CA6QT4TBXGB3M.stableswap-router-v-1-1',
)
BITFLOW_POOL_SBTC_XBTC: Final = StacksAddress(
    'SPQC38PW542EQJ5M11CR25P7BS1CA6QT4TBXGB3M.stableswap-sbtc-xbtc-v-1-2',
)
BITFLOW_POOL_USDA_SUSDT: Final = StacksAddress(
    'SPQC38PW542EQJ5M11CR25P7BS1CA6QT4TBXGB3M.stableswap-usda-susdt-v-1-2',
)

# Bitflow LP token deployer address (deploys stableswap-pool-* and xyk-pool-* contracts)
BITFLOW_LP_DEPLOYER: Final = 'SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR'

# Function names for swaps
BITFLOW_SWAP: Final = 'swap'
BITFLOW_SWAP_HELPER: Final = 'swap-helper'
BITFLOW_SWAP_X_FOR_Y: Final = 'swap-x-for-y'
BITFLOW_SWAP_Y_FOR_X: Final = 'swap-y-for-x'

# Function names for liquidity
BITFLOW_ADD_LIQUIDITY: Final = 'add-liquidity'
BITFLOW_REMOVE_LIQUIDITY: Final = 'remove-liquidity'

# Swap-related function names
BITFLOW_SWAP_FUNCTIONS: Final = frozenset({
    BITFLOW_SWAP,
    BITFLOW_SWAP_HELPER,
    BITFLOW_SWAP_X_FOR_Y,
    BITFLOW_SWAP_Y_FOR_X,
})

# Liquidity-related function names
BITFLOW_LIQUIDITY_FUNCTIONS: Final = frozenset({
    BITFLOW_ADD_LIQUIDITY,
    BITFLOW_REMOVE_LIQUIDITY,
})

# All Bitflow contracts
BITFLOW_CONTRACTS: Final = frozenset({
    BITFLOW_CORE_CONTRACT,
    BITFLOW_ROUTER_CONTRACT,
    BITFLOW_POOL_SBTC_XBTC,
    BITFLOW_POOL_USDA_SUSDT,
})
