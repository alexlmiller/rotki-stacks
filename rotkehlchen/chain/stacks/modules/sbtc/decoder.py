"""sBTC bridge protocol decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    CPT_SBTC,
    SBTC_COMPLETE_DEPOSIT,
    SBTC_CONTRACTS,
    SBTC_INITIATE_WITHDRAWAL,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_sbtc_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves sBTC contracts."""
    if transaction.contract_id is None:
        return False
    return transaction.contract_id in SBTC_CONTRACTS


def decode_sbtc_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode sBTC bridge events from a transaction.

    Handles:
    - BTC → sBTC pegin (complete-deposit-wrapper)
    - sBTC → BTC pegout (initiate-withdrawal-request)

    Returns list of additional events to add (may modify existing_events in place).
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    additional_events: list[StacksEvent] = []

    # Handle pegin (BTC → sBTC deposit)
    if transaction.function_name == SBTC_COMPLETE_DEPOSIT:
        # Find any sBTC receive events and mark them as bridge deposits
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                'sbtc' in event.asset.identifier.lower()
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.BRIDGE
                event.counterparty = CPT_SBTC
                event.notes = (
                    f'Bridge {event.amount} BTC to sBTC via sBTC bridge'
                )
                log.debug(f'Decoded sBTC pegin in {transaction.tx_id}')

    # Handle pegout (sBTC → BTC withdrawal request)
    elif transaction.function_name == SBTC_INITIATE_WITHDRAWAL:
        # Find any sBTC spend events and mark them as bridge withdrawals
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                'sbtc' in event.asset.identifier.lower()
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.BRIDGE
                event.counterparty = CPT_SBTC
                event.notes = (
                    f'Bridge {event.amount} sBTC to BTC via sBTC bridge'
                )
                log.debug(f'Decoded sBTC pegout in {transaction.tx_id}')

    return additional_events
