"""Zest lending protocol decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    CPT_ZEST,
    ZEST_BORROW_FUNCTIONS,
    ZEST_CONTRACTS,
    ZEST_REPAY_FUNCTIONS,
    ZEST_SUPPLY_FUNCTIONS,
    ZEST_WITHDRAW_FUNCTIONS,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_zest_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves Zest contracts."""
    if transaction.contract_id is None:
        return False
    return transaction.contract_id in ZEST_CONTRACTS


def decode_zest_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode Zest lending protocol events from a transaction.

    Handles:
    - Supply (deposit collateral)
    - Withdraw (withdraw collateral)
    - Borrow (take out loan)
    - Repay (repay loan)

    Returns list of additional events to add (may modify existing_events in place).
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    function_name = transaction.function_name

    # Handle supply (deposit collateral)
    if function_name in ZEST_SUPPLY_FUNCTIONS:
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.DEPOSIT_ASSET
                event.counterparty = CPT_ZEST
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Supply {event.amount} {symbol} as collateral to Zest'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.RECEIVE_WRAPPED
                event.counterparty = CPT_ZEST
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Receive {event.amount} {symbol} supply token from Zest'

        log.debug(f'Decoded Zest supply in {transaction.tx_id}')

    # Handle withdraw (withdraw collateral)
    elif function_name in ZEST_WITHDRAW_FUNCTIONS:
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.RETURN_WRAPPED
                event.counterparty = CPT_ZEST
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Return {event.amount} {symbol} supply token to Zest'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.REMOVE_ASSET
                event.counterparty = CPT_ZEST
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Withdraw {event.amount} {symbol} collateral from Zest'

        log.debug(f'Decoded Zest withdraw in {transaction.tx_id}')

    # Handle borrow
    elif function_name in ZEST_BORROW_FUNCTIONS:
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.RECEIVE
                event.event_subtype = HistoryEventSubType.GENERATE_DEBT
                event.counterparty = CPT_ZEST
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Borrow {event.amount} {symbol} from Zest'

        log.debug(f'Decoded Zest borrow in {transaction.tx_id}')

    # Handle repay
    elif function_name in ZEST_REPAY_FUNCTIONS:
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.SPEND
                event.event_subtype = HistoryEventSubType.PAYBACK_DEBT
                event.counterparty = CPT_ZEST
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Repay {event.amount} {symbol} to Zest'

        log.debug(f'Decoded Zest repay in {transaction.tx_id}')

    return []
