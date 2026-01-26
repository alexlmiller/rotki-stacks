"""Dual Stacking protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_DUAL_STACKING: Final = 'dual-stacking'

# Dual Stacking deployer address
DUAL_STACKING_DEPLOYER: Final = 'SP1HFCRKEJ8BYW4D0E3FAWHFDX8A25PPAA83HWWZ9'

# Dual Stacking contracts
DUAL_STACKING_V1_CONTRACT: Final = StacksAddress(
    f'{DUAL_STACKING_DEPLOYER}.dual-stacking-v1',
)
DUAL_STACKING_V2_CONTRACT: Final = StacksAddress(
    f'{DUAL_STACKING_DEPLOYER}.dual-stacking-v2_0_2',
)

# User enrollment functions
DUAL_STACKING_ENROLL: Final = 'enroll'
DUAL_STACKING_OPT_OUT: Final = 'opt-out'
DUAL_STACKING_CHANGE_REWARD_ADDRESS: Final = 'change-reward-address'

# DeFi enrollment functions
DUAL_STACKING_ENROLL_DEFI: Final = 'enroll-defi'
DUAL_STACKING_ENROLL_DEFI_BATCH: Final = 'enroll-defi-batch'
DUAL_STACKING_OPT_OUT_DEFI: Final = 'opt-out-defi'
DUAL_STACKING_OPT_OUT_DEFI_BATCH: Final = 'opt-out-defi-batch'
DUAL_STACKING_CHANGE_ADDRESSES_DEFI: Final = 'change-addresses-defi'
DUAL_STACKING_CHANGE_ADDRESSES_DEFI_BATCH: Final = 'change-addresses-defi-batch'

# Reward distribution function
DUAL_STACKING_DISTRIBUTE_REWARDS: Final = 'distribute-rewards'

# User enrollment function set
DUAL_STACKING_ENROLL_FUNCTIONS: Final = frozenset({
    DUAL_STACKING_ENROLL,
})

# User opt-out function set
DUAL_STACKING_OPT_OUT_FUNCTIONS: Final = frozenset({
    DUAL_STACKING_OPT_OUT,
})

# User settings change functions
DUAL_STACKING_SETTINGS_FUNCTIONS: Final = frozenset({
    DUAL_STACKING_CHANGE_REWARD_ADDRESS,
})

# DeFi enrollment functions
DUAL_STACKING_DEFI_ENROLL_FUNCTIONS: Final = frozenset({
    DUAL_STACKING_ENROLL_DEFI,
    DUAL_STACKING_ENROLL_DEFI_BATCH,
})

# DeFi opt-out functions
DUAL_STACKING_DEFI_OPT_OUT_FUNCTIONS: Final = frozenset({
    DUAL_STACKING_OPT_OUT_DEFI,
    DUAL_STACKING_OPT_OUT_DEFI_BATCH,
})

# DeFi settings change functions
DUAL_STACKING_DEFI_SETTINGS_FUNCTIONS: Final = frozenset({
    DUAL_STACKING_CHANGE_ADDRESSES_DEFI,
    DUAL_STACKING_CHANGE_ADDRESSES_DEFI_BATCH,
})

# Reward distribution functions
DUAL_STACKING_REWARD_FUNCTIONS: Final = frozenset({
    DUAL_STACKING_DISTRIBUTE_REWARDS,
})

# All Dual Stacking contracts
DUAL_STACKING_CONTRACTS: Final = frozenset({
    DUAL_STACKING_V1_CONTRACT,
    DUAL_STACKING_V2_CONTRACT,
})
