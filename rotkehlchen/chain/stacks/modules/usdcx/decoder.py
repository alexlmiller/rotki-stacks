"""Circle USDCx (xReserve) bridge decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    CPT_USDCX,
    USDCX_CONTRACTS,
    USDCX_RECEIVE_FUNCTIONS,
    USDCX_SEND_FUNCTIONS,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_usdcx_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves USDCx/xReserve bridge contracts."""
    if transaction.contract_id is None:
        return False
    return transaction.contract_id in USDCX_CONTRACTS


def decode_usdcx_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode USDCx bridge events from a transaction.

    Handles Circle's USDC bridging via xReserve:
    - mint/deposit: Receive bridged USDC from other chains (creates USDCx)
    - burn/withdraw: Send USDC to other chains (destroys USDCx)

    Returns list of additional events to add (may modify existing_events in place).
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    function_name = transaction.function_name

    # Handle receiving bridged USDC (mint)
    if function_name in USDCX_RECEIVE_FUNCTIONS:
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                'usdc' in event.asset.identifier.lower()
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.BRIDGE
                event.counterparty = CPT_USDCX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Bridge {event.amount} {symbol} to Stacks via Circle'
                log.debug(f'Decoded USDCx mint (deposit) in {transaction.tx_id}')

    # Handle sending USDC to other chains (burn)
    elif function_name in USDCX_SEND_FUNCTIONS:
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                'usdc' in event.asset.identifier.lower()
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.BRIDGE
                event.counterparty = CPT_USDCX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Bridge {event.amount} {symbol} from Stacks via Circle'
                log.debug(f'Decoded USDCx burn (withdrawal) in {transaction.tx_id}')

    return []
