"""PoX stacking protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_POX: Final = 'pox'

# PoX Contract Addresses (native stacking)
# pox-4 is the current active version
POX4_CONTRACT: Final = StacksAddress(
    'SP000000000000000000002Q6VF78.pox-4',
)
# pox-3 for historical transaction support
POX3_CONTRACT: Final = StacksAddress(
    'SP000000000000000000002Q6VF78.pox-3',
)

# PoX Function Names - Solo stacking
POX_STACK_STX: Final = 'stack-stx'
POX_STACK_EXTEND: Final = 'stack-extend'
POX_STACK_INCREASE: Final = 'stack-increase'

# PoX Function Names - Delegation
POX_DELEGATE_STX: Final = 'delegate-stx'
POX_REVOKE_DELEGATE_STX: Final = 'revoke-delegate-stx'

# PoX Function Names - Pool operations (pools stacking on behalf of delegators)
POX_DELEGATE_STACK_STX: Final = 'delegate-stack-stx'
POX_DELEGATE_STACK_EXTEND: Final = 'delegate-stack-extend'
POX_DELEGATE_STACK_INCREASE: Final = 'delegate-stack-increase'

# PoX Function Names - Authorization
POX_ALLOW_CONTRACT_CALLER: Final = 'allow-contract-caller'
POX_DISALLOW_CONTRACT_CALLER: Final = 'disallow-contract-caller'

# All stacking functions that lock/extend STX
POX_LOCK_FUNCTIONS: Final = frozenset({
    POX_STACK_STX,
    POX_STACK_EXTEND,
    POX_STACK_INCREASE,
    POX_DELEGATE_STX,
    POX_DELEGATE_STACK_STX,
    POX_DELEGATE_STACK_EXTEND,
    POX_DELEGATE_STACK_INCREASE,
})

# Functions that need to fetch locked amount from events (no amount in args)
POX_NEEDS_EVENT_AMOUNT: Final = frozenset({
    POX_STACK_EXTEND,
    POX_DELEGATE_STACK_EXTEND,
})

# Authorization functions (informational - no asset movement)
POX_AUTHORIZATION_FUNCTIONS: Final = frozenset({
    POX_ALLOW_CONTRACT_CALLER,
    POX_DISALLOW_CONTRACT_CALLER,
})

# All PoX contracts (pox-3 and pox-4)
POX_CONTRACTS: Final = frozenset({
    POX3_CONTRACT,
    POX4_CONTRACT,
})
