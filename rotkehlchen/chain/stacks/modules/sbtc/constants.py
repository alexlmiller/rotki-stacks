"""sBTC protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_SBTC: Final = 'sbtc'

# sBTC Contract Addresses
SBTC_TOKEN_CONTRACT: Final = StacksAddress(
    'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-token',
)
SBTC_REGISTRY_CONTRACT: Final = StacksAddress(
    'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-registry',
)
SBTC_DEPOSIT_CONTRACT: Final = StacksAddress(
    'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-deposit',
)

# sBTC Function Names
SBTC_COMPLETE_DEPOSIT: Final = 'complete-deposit-wrapper'
SBTC_INITIATE_WITHDRAWAL: Final = 'initiate-withdrawal-request'

# All sBTC contracts for quick lookup
SBTC_CONTRACTS: Final = frozenset({
    SBTC_TOKEN_CONTRACT,
    SBTC_REGISTRY_CONTRACT,
    SBTC_DEPOSIT_CONTRACT,
})
