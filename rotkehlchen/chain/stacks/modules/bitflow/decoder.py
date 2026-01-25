"""Bitflow DEX protocol decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    BITFLOW_CONTRACTS,
    BITFLOW_LIQUIDITY_FUNCTIONS,
    BITFLOW_SWAP_FUNCTIONS,
    CPT_BITFLOW,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_bitflow_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves Bitflow contracts."""
    if transaction.contract_id is None:
        return False
    return transaction.contract_id in BITFLOW_CONTRACTS


def _decode_bitflow_swap(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Bitflow swap transactions."""
    spend_events = [
        e for e in existing_events
        if e.event_type == HistoryEventType.SPEND
        and e.event_subtype == HistoryEventSubType.NONE
    ]
    receive_events = [
        e for e in existing_events
        if e.event_type == HistoryEventType.RECEIVE
        and e.event_subtype == HistoryEventSubType.NONE
    ]

    if not spend_events or not receive_events:
        return

    for event in spend_events:
        if event.location_label == transaction.sender_address:
            event.event_type = HistoryEventType.TRADE
            event.event_subtype = HistoryEventSubType.SPEND
            event.counterparty = CPT_BITFLOW
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            event.notes = f'Swap {event.amount} {symbol} on Bitflow'
            break

    for event in receive_events:
        if event.location_label == transaction.sender_address:
            event.event_type = HistoryEventType.TRADE
            event.event_subtype = HistoryEventSubType.RECEIVE
            event.counterparty = CPT_BITFLOW
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            event.notes = f'Receive {event.amount} {symbol} from Bitflow swap'
            break

    log.debug(f'Decoded Bitflow swap in {transaction.tx_id}')


def _decode_bitflow_liquidity(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Bitflow liquidity provision transactions."""
    function_name = transaction.function_name

    if function_name == 'add-liquidity':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.DEPOSIT_ASSET
                event.counterparty = CPT_BITFLOW
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Deposit {event.amount} {symbol} into Bitflow pool'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.RECEIVE_WRAPPED
                event.counterparty = CPT_BITFLOW
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Receive {event.amount} {symbol} LP token from Bitflow'

        log.debug(f'Decoded Bitflow add liquidity in {transaction.tx_id}')

    elif function_name == 'remove-liquidity':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.RETURN_WRAPPED
                event.counterparty = CPT_BITFLOW
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Return {event.amount} {symbol} LP token to Bitflow'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.REMOVE_ASSET
                event.counterparty = CPT_BITFLOW
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Withdraw {event.amount} {symbol} from Bitflow pool'

        log.debug(f'Decoded Bitflow remove liquidity in {transaction.tx_id}')


def decode_bitflow_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode Bitflow DEX events from a transaction.

    Handles:
    - Swaps (stablecoin swaps)
    - Liquidity provision

    Returns list of additional events to add (may modify existing_events in place).
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    function_name = transaction.function_name

    if function_name in BITFLOW_SWAP_FUNCTIONS:
        _decode_bitflow_swap(transaction, base_tools, existing_events)
    elif function_name in BITFLOW_LIQUIDITY_FUNCTIONS:
        _decode_bitflow_liquidity(transaction, base_tools, existing_events)

    return []
