"""StackingDAO protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_STACKINGDAO: Final = 'stackingdao'

# StackingDAO Contract Addresses
STACKINGDAO_CORE_CONTRACT: Final = StacksAddress(
    'SM3KNVZS30WM7F89SXKVVFY4SN9RMPZZ9FX929N0V.stacking-dao-core-v2',
)
STSTX_TOKEN_CONTRACT: Final = StacksAddress(
    'SM3KNVZS30WM7F89SXKVVFY4SN9RMPZZ9FX929N0V.ststx-token',
)
STSTXBTC_TOKEN_CONTRACT: Final = StacksAddress(
    'SM3KNVZS30WM7F89SXKVVFY4SN9RMPZZ9FX929N0V.ststxbtc-token',
)

# StackingDAO Function Names
STACKINGDAO_DEPOSIT: Final = 'deposit'
STACKINGDAO_WITHDRAW: Final = 'withdraw'
STACKINGDAO_CLAIM_REWARDS: Final = 'claim-rewards'

# All StackingDAO contracts
STACKINGDAO_CONTRACTS: Final = frozenset({
    STACKINGDAO_CORE_CONTRACT,
    STSTX_TOKEN_CONTRACT,
    STSTXBTC_TOKEN_CONTRACT,
})
