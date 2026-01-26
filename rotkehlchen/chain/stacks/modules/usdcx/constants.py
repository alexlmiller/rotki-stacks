"""Circle USDCx (xReserve) bridge constants."""
from typing import Final

from rotkehlchen.types import StacksAddress

CPT_USDCX: Final = 'usdcx'

# xReserve Deployer (Circle's partner for Stacks USDC)
XRESERVE_DEPLOYER: Final = 'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE'

# USDCx Token Contract
USDCX_TOKEN_CONTRACT: Final = StacksAddress(
    f'{XRESERVE_DEPLOYER}.usdcx',
)

# xReserve Bridge Contracts
XRESERVE_BRIDGE_CONTRACT: Final = StacksAddress(
    f'{XRESERVE_DEPLOYER}.bridge',
)
XRESERVE_GATEWAY_CONTRACT: Final = StacksAddress(
    f'{XRESERVE_DEPLOYER}.gateway',
)

# Function names for bridging
USDCX_MINT: Final = 'mint'
USDCX_BURN: Final = 'burn'
USDCX_DEPOSIT: Final = 'deposit'
USDCX_WITHDRAW: Final = 'withdraw'

# Functions for receiving bridged USDC (mint on Stacks)
USDCX_RECEIVE_FUNCTIONS: Final = frozenset({
    USDCX_MINT,
    USDCX_DEPOSIT,
})

# Functions for sending USDC to other chains (burn from Stacks)
USDCX_SEND_FUNCTIONS: Final = frozenset({
    USDCX_BURN,
    USDCX_WITHDRAW,
})

# All USDCx/xReserve contracts
USDCX_CONTRACTS: Final = frozenset({
    XRESERVE_BRIDGE_CONTRACT,
    XRESERVE_GATEWAY_CONTRACT,
})
