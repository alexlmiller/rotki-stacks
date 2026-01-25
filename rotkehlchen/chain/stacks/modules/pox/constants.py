"""PoX stacking protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_POX: Final = 'pox'

# PoX-4 Contract Address (native stacking)
POX4_CONTRACT: Final = StacksAddress(
    'SP000000000000000000002Q6VF78.pox-4',
)

# PoX Function Names
POX_STACK_STX: Final = 'stack-stx'
POX_STACK_EXTEND: Final = 'stack-extend'
POX_STACK_INCREASE: Final = 'stack-increase'
POX_DELEGATE_STX: Final = 'delegate-stx'
POX_REVOKE_DELEGATE_STX: Final = 'revoke-delegate-stx'

# All stacking functions
POX_LOCK_FUNCTIONS: Final = frozenset({
    POX_STACK_STX,
    POX_STACK_EXTEND,
    POX_STACK_INCREASE,
    POX_DELEGATE_STX,
})

# All PoX contracts
POX_CONTRACTS: Final = frozenset({
    POX4_CONTRACT,
})
