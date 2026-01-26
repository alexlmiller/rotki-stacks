"""Allbridge bridge protocol decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    ALLBRIDGE_CONTRACTS,
    ALLBRIDGE_RECEIVE_FUNCTIONS,
    ALLBRIDGE_SEND_FUNCTIONS,
    CPT_ALLBRIDGE,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_allbridge_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves Allbridge bridge contracts."""
    if transaction.contract_id is None:
        return False
    return transaction.contract_id in ALLBRIDGE_CONTRACTS


def decode_allbridge_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode Allbridge bridge events from a transaction.

    Handles:
    - unlock: Receive bridged tokens from Ethereum/other chains (mints aeTokens)
    - lock: Send tokens to Ethereum/other chains (burns aeTokens)

    Returns list of additional events to add (may modify existing_events in place).
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    function_name = transaction.function_name

    # Handle receiving bridged tokens (unlock)
    if function_name in ALLBRIDGE_RECEIVE_FUNCTIONS:
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.BRIDGE
                event.counterparty = CPT_ALLBRIDGE
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Bridge {event.amount} {symbol} to Stacks via Allbridge'
                log.debug(f'Decoded Allbridge unlock (deposit) in {transaction.tx_id}')

    # Handle sending tokens to other chains (lock)
    elif function_name in ALLBRIDGE_SEND_FUNCTIONS:
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.BRIDGE
                event.counterparty = CPT_ALLBRIDGE
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Bridge {event.amount} {symbol} from Stacks via Allbridge'
                log.debug(f'Decoded Allbridge lock (withdrawal) in {transaction.tx_id}')

    return []
