"""sBTC protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_SBTC: Final = 'sbtc'

# sBTC Contract Deployer (mainnet)
SBTC_DEPLOYER: Final = 'SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4'

# sBTC Contract Addresses (mainnet)
# See: https://github.com/stacks-sbtc/sbtc
SBTC_TOKEN_CONTRACT: Final = StacksAddress(
    f'{SBTC_DEPLOYER}.sbtc-token',
)
SBTC_REGISTRY_CONTRACT: Final = StacksAddress(
    f'{SBTC_DEPLOYER}.sbtc-registry',
)
SBTC_DEPOSIT_CONTRACT: Final = StacksAddress(
    f'{SBTC_DEPLOYER}.sbtc-deposit',
)
SBTC_WITHDRAWAL_CONTRACT: Final = StacksAddress(
    f'{SBTC_DEPLOYER}.sbtc-withdrawal',
)

# sBTC Function Names - Deposits
SBTC_COMPLETE_DEPOSIT: Final = 'complete-deposit-wrapper'
SBTC_COMPLETE_DEPOSITS: Final = 'complete-deposits-wrapper'

# sBTC Function Names - Withdrawals
SBTC_INITIATE_WITHDRAWAL: Final = 'initiate-withdrawal-request'
SBTC_ACCEPT_WITHDRAWAL: Final = 'accept-withdrawal-request'
SBTC_REJECT_WITHDRAWAL: Final = 'reject-withdrawal-request'

# All sBTC contracts for quick lookup
SBTC_CONTRACTS: Final = frozenset({
    SBTC_TOKEN_CONTRACT,
    SBTC_REGISTRY_CONTRACT,
    SBTC_DEPOSIT_CONTRACT,
    SBTC_WITHDRAWAL_CONTRACT,
})
