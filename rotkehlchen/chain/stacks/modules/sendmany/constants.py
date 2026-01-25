"""Send-many protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_SENDMANY: Final = 'send-many'

# Known send-many contract addresses on Stacks mainnet
SENDMANY_MEMO_CONTRACT: Final = StacksAddress(
    'SP3FBR2AGK5H9QBDH3EEN6DF8EK8JY7RX8QJ5SVTE.send-many-memo',
)
SENDMANY_CONTRACT: Final = StacksAddress(
    'SP1K1A1PMGW2ZJCNF46NWZWHG8TS1D23EGH1KNK60.send-many',
)
# Send-many for SIP-10 tokens
SENDMANY_SIP10_CONTRACT: Final = StacksAddress(
    'SP3FBR2AGK5H9QBDH3EEN6DF8EK8JY7RX8QJ5SVTE.send-many-stx-memo',
)

# Function names
SENDMANY_FUNCTION: Final = 'send-many'
SENDMANY_MEMO_FUNCTION: Final = 'send-many-memo'

# All send-many contracts
SENDMANY_CONTRACTS: Final = frozenset({
    SENDMANY_MEMO_CONTRACT,
    SENDMANY_CONTRACT,
    SENDMANY_SIP10_CONTRACT,
})
