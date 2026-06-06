"""Allbridge bridge protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_ALLBRIDGE: Final = 'allbridge'

# Allbridge Core Deployer
ALLBRIDGE_DEPLOYER: Final = 'SP3Y2ZSH8P7D50B0VBTSX11S7XSG24M1VB9YFQA4K'

# Allbridge Bridge Contract
ALLBRIDGE_BRIDGE_CONTRACT: Final = StacksAddress(
    f'{ALLBRIDGE_DEPLOYER}.bridge',
)

# Allbridge Token Contracts
ALLBRIDGE_AEUSDC_CONTRACT: Final = StacksAddress(
    f'{ALLBRIDGE_DEPLOYER}.token-aeusdc',
)
ALLBRIDGE_AEETH_CONTRACT: Final = StacksAddress(
    f'{ALLBRIDGE_DEPLOYER}.token-aeeth',
)

# Function names
ALLBRIDGE_UNLOCK: Final = 'unlock'
ALLBRIDGE_LOCK: Final = 'lock'

# Functions for receiving bridged tokens from other chains
ALLBRIDGE_RECEIVE_FUNCTIONS: Final = frozenset({
    ALLBRIDGE_UNLOCK,
})

# Functions for sending tokens to other chains
ALLBRIDGE_SEND_FUNCTIONS: Final = frozenset({
    ALLBRIDGE_LOCK,
})

# All Allbridge contracts
ALLBRIDGE_CONTRACTS: Final = frozenset({
    ALLBRIDGE_BRIDGE_CONTRACT,
})

# Allbridge token contracts (for identifying token transfers)
ALLBRIDGE_TOKEN_CONTRACTS: Final = frozenset({
    ALLBRIDGE_AEUSDC_CONTRACT,
    ALLBRIDGE_AEETH_CONTRACT,
})
