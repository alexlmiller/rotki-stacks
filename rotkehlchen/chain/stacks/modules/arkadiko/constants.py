"""Arkadiko CDP protocol constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_ARKADIKO: Final = 'arkadiko'

# Arkadiko DAO Address
ARKADIKO_DAO_ADDRESS: Final = 'SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR'

# Arkadiko Core Contracts
ARKADIKO_FREDDIE_CONTRACT: Final = StacksAddress(
    f'{ARKADIKO_DAO_ADDRESS}.arkadiko-freddie-v1-1',
)
ARKADIKO_VAULT_DATA_CONTRACT: Final = StacksAddress(
    f'{ARKADIKO_DAO_ADDRESS}.arkadiko-vault-data-v1-1',
)
ARKADIKO_USDA_CONTRACT: Final = StacksAddress(
    f'{ARKADIKO_DAO_ADDRESS}.usda-token',
)
ARKADIKO_DIKO_CONTRACT: Final = StacksAddress(
    f'{ARKADIKO_DAO_ADDRESS}.arkadiko-token',
)
ARKADIKO_AUCTION_CONTRACT: Final = StacksAddress(
    f'{ARKADIKO_DAO_ADDRESS}.arkadiko-auction-engine-v4-5',
)
ARKADIKO_LIQUIDATOR_CONTRACT: Final = StacksAddress(
    f'{ARKADIKO_DAO_ADDRESS}.arkadiko-liquidator-v2-1',
)
ARKADIKO_STAKE_POOL_CONTRACT: Final = StacksAddress(
    f'{ARKADIKO_DAO_ADDRESS}.arkadiko-stake-pool-diko-v1-1',
)
ARKADIKO_SIP10_RESERVE_CONTRACT: Final = StacksAddress(
    f'{ARKADIKO_DAO_ADDRESS}.arkadiko-sip10-reserve-v2-1',
)
ARKADIKO_STX_RESERVE_CONTRACT: Final = StacksAddress(
    f'{ARKADIKO_DAO_ADDRESS}.arkadiko-stx-reserve-v1-1',
)

# Vault management function names
ARKADIKO_COLLATERALIZE_AND_MINT: Final = 'collateralize-and-mint'
ARKADIKO_DEPOSIT: Final = 'deposit'
ARKADIKO_WITHDRAW: Final = 'withdraw'
ARKADIKO_MINT: Final = 'mint'
ARKADIKO_BURN: Final = 'burn'

# Liquidation function names
ARKADIKO_LIQUIDATE: Final = 'liquidate'
ARKADIKO_BID: Final = 'bid'

# Staking function names
ARKADIKO_STAKE: Final = 'stake'
ARKADIKO_UNSTAKE: Final = 'unstake'
ARKADIKO_CLAIM_STAKING_REWARDS: Final = 'claim-staking-rewards'
ARKADIKO_GET_REWARDS_TO_ADD: Final = 'get-rewards-to-add'

# Vault function sets
ARKADIKO_VAULT_DEPOSIT_FUNCTIONS: Final = frozenset({
    ARKADIKO_COLLATERALIZE_AND_MINT,
    ARKADIKO_DEPOSIT,
})

ARKADIKO_VAULT_WITHDRAW_FUNCTIONS: Final = frozenset({
    ARKADIKO_WITHDRAW,
})

# Debt function sets
ARKADIKO_MINT_FUNCTIONS: Final = frozenset({
    ARKADIKO_COLLATERALIZE_AND_MINT,
    ARKADIKO_MINT,
})

ARKADIKO_BURN_FUNCTIONS: Final = frozenset({
    ARKADIKO_BURN,
})

# Liquidation function set
ARKADIKO_LIQUIDATION_FUNCTIONS: Final = frozenset({
    ARKADIKO_LIQUIDATE,
    ARKADIKO_BID,
})

# Staking function set
ARKADIKO_STAKING_FUNCTIONS: Final = frozenset({
    ARKADIKO_STAKE,
    ARKADIKO_UNSTAKE,
    ARKADIKO_CLAIM_STAKING_REWARDS,
    ARKADIKO_GET_REWARDS_TO_ADD,
})

# All Arkadiko contracts
ARKADIKO_CONTRACTS: Final = frozenset({
    ARKADIKO_FREDDIE_CONTRACT,
    ARKADIKO_VAULT_DATA_CONTRACT,
    ARKADIKO_USDA_CONTRACT,
    ARKADIKO_DIKO_CONTRACT,
    ARKADIKO_AUCTION_CONTRACT,
    ARKADIKO_LIQUIDATOR_CONTRACT,
    ARKADIKO_STAKE_POOL_CONTRACT,
    ARKADIKO_SIP10_RESERVE_CONTRACT,
    ARKADIKO_STX_RESERVE_CONTRACT,
})
