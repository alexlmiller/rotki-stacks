"""Third-party stacking pools constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_STACKING_POOLS: Final = 'stacking-pools'

# Fastpool - 1-cycle stacking pool
# See: https://fastpool.org
FASTPOOL_CONTRACT: Final = StacksAddress(
    'SP001SFSMC2ZY76PD4M68P3WGX154XCH7NE3TYMX.pox-pools-1-cycle-v2',
)
FASTPOOL_CONTRACT_V1: Final = StacksAddress(
    'SP001SFSMC2ZY76PD4M68P3WGX154XCH7NE3TYMX.pox-pools-1-cycle',
)

# Xverse stacking pool
# See: https://pool.xverse.app
XVERSE_POOL_CONTRACT: Final = StacksAddress(
    'SPXVRSEH2BKSXAEJ00F1BY562P45D5ERPSKR4Q33.xverse-pool-v1',
)

# StackingDAO pool delegation contract (separate from liquid staking)
# For users who delegate to StackingDAO but want BTC rewards instead of stSTX
STACKINGDAO_POOL_CONTRACT: Final = StacksAddress(
    'SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.stacking-pool-v1',
)

# Function names - Delegation
POOL_DELEGATE_STX: Final = 'delegate-stx'
POOL_REVOKE_DELEGATE_STX: Final = 'revoke-delegate-stx'

# Pool-specific function names
FASTPOOL_ALLOW_CONTRACT_CALLER: Final = 'allow-contract-caller'

# Delegation functions set
POOL_DELEGATION_FUNCTIONS: Final = frozenset({
    POOL_DELEGATE_STX,
})

# Revocation functions set
POOL_REVOCATION_FUNCTIONS: Final = frozenset({
    POOL_REVOKE_DELEGATE_STX,
})

# All stacking pool contracts
STACKING_POOL_CONTRACTS: Final = frozenset({
    FASTPOOL_CONTRACT,
    FASTPOOL_CONTRACT_V1,
    XVERSE_POOL_CONTRACT,
    STACKINGDAO_POOL_CONTRACT,
})
