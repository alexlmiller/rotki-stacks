"""Velar DEX protocol decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    CPT_VELAR,
    VELAR_CONTRACTS,
    VELAR_LIQUIDITY_FUNCTIONS,
    VELAR_STAKING_FUNCTIONS,
    VELAR_SWAP_FUNCTIONS,
    VELAR_XYK_STAKING_FUNCTIONS,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_velar_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves Velar contracts.

    Velar core UniV2 contracts are at SP1Y5YSTAHZ88XYK1VPDH24GY0HPX5J4JECTMY4A1
    """
    if transaction.contract_id is None:
        return False
    return transaction.contract_id in VELAR_CONTRACTS


def _decode_velar_swap(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Velar swap transactions."""
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
            event.counterparty = CPT_VELAR
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            event.notes = f'Swap {event.amount} {symbol} on Velar'
            break

    for event in receive_events:
        if event.location_label == transaction.sender_address:
            event.event_type = HistoryEventType.TRADE
            event.event_subtype = HistoryEventSubType.RECEIVE
            event.counterparty = CPT_VELAR
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            event.notes = f'Receive {event.amount} {symbol} from Velar swap'
            break

    log.debug(f'Decoded Velar swap in {transaction.tx_id}')


def _decode_velar_liquidity(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Velar liquidity provision transactions."""
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
                event.counterparty = CPT_VELAR
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Deposit {event.amount} {symbol} into Velar liquidity pool'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.RECEIVE
                event.event_subtype = HistoryEventSubType.RECEIVE_WRAPPED
                event.counterparty = CPT_VELAR
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Receive {event.amount} {symbol} LP token from Velar'

        log.debug(f'Decoded Velar add liquidity in {transaction.tx_id}')

    elif function_name == 'remove-liquidity':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.SPEND
                event.event_subtype = HistoryEventSubType.RETURN_WRAPPED
                event.counterparty = CPT_VELAR
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Return {event.amount} {symbol} LP token to Velar'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.REMOVE_ASSET
                event.counterparty = CPT_VELAR
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Withdraw {event.amount} {symbol} from Velar liquidity pool'

        log.debug(f'Decoded Velar remove liquidity in {transaction.tx_id}')


def _decode_velar_staking(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Velar staking transactions."""
    function_name = transaction.function_name

    if function_name == 'stake':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.DEPOSIT_ASSET
                event.counterparty = CPT_VELAR
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Stake {event.amount} {symbol} on Velar'

        log.debug(f'Decoded Velar stake in {transaction.tx_id}')

    elif function_name == 'unstake':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.REMOVE_ASSET
                event.counterparty = CPT_VELAR
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Unstake {event.amount} {symbol} from Velar'

        log.debug(f'Decoded Velar unstake in {transaction.tx_id}')

    elif function_name == 'claim':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.REWARD
                event.counterparty = CPT_VELAR
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Claim {event.amount} {symbol} staking reward from Velar'

        log.debug(f'Decoded Velar claim rewards in {transaction.tx_id}')


def _decode_velar_xyk_staking(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Velar XYK LP staking transactions."""
    function_name = transaction.function_name

    if function_name == 'stake-lp-tokens':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.DEPOSIT_ASSET
                event.counterparty = CPT_VELAR
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Stake {event.amount} {symbol} LP tokens on Velar'

        log.debug(f'Decoded Velar XYK stake LP in {transaction.tx_id}')

    elif function_name == 'unstake-lp-tokens':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.REMOVE_ASSET
                event.counterparty = CPT_VELAR
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Unstake {event.amount} {symbol} LP tokens from Velar'

        log.debug(f'Decoded Velar XYK unstake LP in {transaction.tx_id}')

    elif function_name == 'claim-staking-reward':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.REWARD
                event.counterparty = CPT_VELAR
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Claim {event.amount} {symbol} LP staking reward from Velar'

        log.debug(f'Decoded Velar XYK claim reward in {transaction.tx_id}')


def decode_velar_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode Velar DEX events from a transaction.

    Handles:
    - Swaps
    - Liquidity provision
    - Staking (VELAR token)
    - XYK LP staking

    Returns list of additional events to add (may modify existing_events in place).
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    function_name = transaction.function_name

    if function_name in VELAR_SWAP_FUNCTIONS:
        _decode_velar_swap(transaction, base_tools, existing_events)
    elif function_name in VELAR_LIQUIDITY_FUNCTIONS:
        _decode_velar_liquidity(transaction, base_tools, existing_events)
    elif function_name in VELAR_STAKING_FUNCTIONS:
        _decode_velar_staking(transaction, base_tools, existing_events)
    elif function_name in VELAR_XYK_STAKING_FUNCTIONS:
        _decode_velar_xyk_staking(transaction, base_tools, existing_events)

    return []
