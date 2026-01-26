"""Zest lending protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_ZEST: Final = 'zest'

# Zest Core Contracts (v1-0)
ZEST_POOL_CONTRACT: Final = StacksAddress(
    'SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.pool-v1-0',
)
ZEST_BORROW_CONTRACT: Final = StacksAddress(
    'SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.borrow-helper-v1-0',
)
ZEST_SUPPLY_CONTRACT: Final = StacksAddress(
    'SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.supply-helper-v1-0',
)
ZEST_LIQUIDATOR_CONTRACT: Final = StacksAddress(
    'SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.liquidator-v1-0',
)

# Zest Core Contracts (v2-0-0) - current active version
ZEST_POOL_V2_CONTRACT: Final = StacksAddress(
    'SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.pool-v2-0-0',
)
ZEST_BORROW_V2_CONTRACT: Final = StacksAddress(
    'SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.borrow-helper-v2-0-0',
)
ZEST_SUPPLY_V2_CONTRACT: Final = StacksAddress(
    'SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.supply-helper-v2-0-0',
)
ZEST_LIQUIDATOR_V2_CONTRACT: Final = StacksAddress(
    'SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.liquidator-v2-0-0',
)

# Function names for supply/borrow
ZEST_SUPPLY: Final = 'supply'
ZEST_WITHDRAW: Final = 'withdraw'
ZEST_BORROW: Final = 'borrow'
ZEST_REPAY: Final = 'repay'
ZEST_LIQUIDATE: Final = 'liquidate'

# Supply-related function names
ZEST_SUPPLY_FUNCTIONS: Final = frozenset({
    ZEST_SUPPLY,
})

# Withdrawal-related function names
ZEST_WITHDRAW_FUNCTIONS: Final = frozenset({
    ZEST_WITHDRAW,
})

# Borrow-related function names
ZEST_BORROW_FUNCTIONS: Final = frozenset({
    ZEST_BORROW,
})

# Repay-related function names
ZEST_REPAY_FUNCTIONS: Final = frozenset({
    ZEST_REPAY,
})

# Liquidation function names
ZEST_LIQUIDATION_CALL: Final = 'liquidation-call'

ZEST_LIQUIDATION_FUNCTIONS: Final = frozenset({
    ZEST_LIQUIDATION_CALL,
    ZEST_LIQUIDATE,
})

# All Zest contracts (v1 and v2)
ZEST_CONTRACTS: Final = frozenset({
    # v1-0 contracts
    ZEST_POOL_CONTRACT,
    ZEST_BORROW_CONTRACT,
    ZEST_SUPPLY_CONTRACT,
    ZEST_LIQUIDATOR_CONTRACT,
    # v2-0-0 contracts
    ZEST_POOL_V2_CONTRACT,
    ZEST_BORROW_V2_CONTRACT,
    ZEST_SUPPLY_V2_CONTRACT,
    ZEST_LIQUIDATOR_V2_CONTRACT,
})
