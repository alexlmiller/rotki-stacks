"""Velar DEX protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_VELAR: Final = 'velar'

# Velar Core Contracts (UniV2 style)
VELAR_ROUTER_CONTRACT: Final = StacksAddress(
    'SP1Y5YSTAHZ88XYK1VPDH24GY0HPX5J4JECTMY4A1.univ2-router',
)
VELAR_FACTORY_CONTRACT: Final = StacksAddress(
    'SP1Y5YSTAHZ88XYK1VPDH24GY0HPX5J4JECTMY4A1.univ2-core',
)
VELAR_PATH_2_CONTRACT: Final = StacksAddress(
    'SP1Y5YSTAHZ88XYK1VPDH24GY0HPX5J4JECTMY4A1.univ2-path2',
)
VELAR_STAKING_CONTRACT: Final = StacksAddress(
    'SP1Y5YSTAHZ88XYK1VPDH24GY0HPX5J4JECTMY4A1.velar-staking',
)

# Velar Token
VELAR_TOKEN_CONTRACT: Final = StacksAddress(
    'SP1Y5YSTAHZ88XYK1VPDH24GY0HPX5J4JECTMY4A1.velar-token',
)

# Velar XYK Contracts deployer (LP staking pools)
VELAR_XYK_DEPLOYER: Final = 'SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR'

# Function names for swaps
VELAR_DO_SWAP: Final = 'do-swap'
VELAR_SWAP_EXACT_TOKENS_FOR_TOKENS: Final = 'swap-exact-tokens-for-tokens'
VELAR_SWAP_TOKENS_FOR_EXACT_TOKENS: Final = 'swap-tokens-for-exact-tokens'

# Function names for liquidity
VELAR_ADD_LIQUIDITY: Final = 'add-liquidity'
VELAR_REMOVE_LIQUIDITY: Final = 'remove-liquidity'

# Function names for staking (Velar token staking)
VELAR_STAKE: Final = 'stake'
VELAR_UNSTAKE: Final = 'unstake'
VELAR_CLAIM: Final = 'claim'

# Function names for XYK LP staking
VELAR_STAKE_LP_TOKENS: Final = 'stake-lp-tokens'
VELAR_UNSTAKE_LP_TOKENS: Final = 'unstake-lp-tokens'
VELAR_CLAIM_STAKING_REWARD: Final = 'claim-staking-reward'

# Swap-related function names
VELAR_SWAP_FUNCTIONS: Final = frozenset({
    VELAR_DO_SWAP,
    VELAR_SWAP_EXACT_TOKENS_FOR_TOKENS,
    VELAR_SWAP_TOKENS_FOR_EXACT_TOKENS,
})

# Liquidity-related function names
VELAR_LIQUIDITY_FUNCTIONS: Final = frozenset({
    VELAR_ADD_LIQUIDITY,
    VELAR_REMOVE_LIQUIDITY,
})

# Staking function names (Velar token)
VELAR_STAKING_FUNCTIONS: Final = frozenset({
    VELAR_STAKE,
    VELAR_UNSTAKE,
    VELAR_CLAIM,
})

# XYK LP staking function names
VELAR_XYK_STAKING_FUNCTIONS: Final = frozenset({
    VELAR_STAKE_LP_TOKENS,
    VELAR_UNSTAKE_LP_TOKENS,
    VELAR_CLAIM_STAKING_REWARD,
})

# All Velar contracts (explicit list)
VELAR_CONTRACTS: Final = frozenset({
    VELAR_ROUTER_CONTRACT,
    VELAR_FACTORY_CONTRACT,
    VELAR_PATH_2_CONTRACT,
    VELAR_STAKING_CONTRACT,
})
