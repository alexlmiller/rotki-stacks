"""ALEX DEX protocol decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    ALEX_BORROWING_FUNCTIONS,
    ALEX_CONTRACTS,
    ALEX_LENDING_FUNCTIONS,
    ALEX_LENDING_WITHDRAW_FUNCTIONS,
    ALEX_LIQUIDITY_FUNCTIONS,
    ALEX_REPAY_FUNCTIONS,
    ALEX_STAKING_FUNCTIONS,
    ALEX_SWAP_FUNCTIONS,
    ALEX_YIELD_FUNCTIONS,
    CPT_ALEX,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_alex_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves ALEX contracts."""
    if transaction.contract_id is None:
        return False
    return transaction.contract_id in ALEX_CONTRACTS


def _decode_alex_swap(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode ALEX swap transactions.

    ALEX swaps involve exchanging one token for another.
    We look for paired SPEND and RECEIVE events and mark them as a swap.
    """
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

    # Mark the first spend as SWAP OUT and first receive as SWAP IN
    for event in spend_events:
        if event.location_label == transaction.sender_address:
            event.event_type = HistoryEventType.TRADE
            event.event_subtype = HistoryEventSubType.SPEND
            event.counterparty = CPT_ALEX
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            event.notes = f'Swap {event.amount} {symbol} on ALEX'
            break

    for event in receive_events:
        if event.location_label == transaction.sender_address:
            event.event_type = HistoryEventType.TRADE
            event.event_subtype = HistoryEventSubType.RECEIVE
            event.counterparty = CPT_ALEX
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            event.notes = f'Receive {event.amount} {symbol} from ALEX swap'
            break

    log.debug(f'Decoded ALEX swap in {transaction.tx_id}')


def _decode_alex_liquidity(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode ALEX liquidity provision transactions.

    For add-to-position: User deposits tokens, receives LP tokens
    For reduce-position: User returns LP tokens, receives underlying tokens
    """
    function_name = transaction.function_name

    if function_name == 'add-to-position':
        # Find deposit events
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.DEPOSIT_ASSET
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Deposit {event.amount} {symbol} into ALEX liquidity pool'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.RECEIVE
                event.event_subtype = HistoryEventSubType.RECEIVE_WRAPPED
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Receive {event.amount} {symbol} LP token from ALEX'

        log.debug(f'Decoded ALEX add liquidity in {transaction.tx_id}')

    elif function_name == 'reduce-position':
        # Find withdrawal events
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.SPEND
                event.event_subtype = HistoryEventSubType.RETURN_WRAPPED
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Return {event.amount} {symbol} LP token to ALEX'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.REMOVE_ASSET
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Withdraw {event.amount} {symbol} from ALEX liquidity pool'

        log.debug(f'Decoded ALEX reduce liquidity in {transaction.tx_id}')


def _decode_alex_staking(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode ALEX staking transactions.

    For stake: User stakes tokens
    For unstake: User unstakes tokens
    For claim-rewards/claim: User claims staking rewards
    """
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
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Stake {event.amount} {symbol} on ALEX'

        log.debug(f'Decoded ALEX stake in {transaction.tx_id}')

    elif function_name == 'unstake':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.REMOVE_ASSET
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Unstake {event.amount} {symbol} from ALEX'

        log.debug(f'Decoded ALEX unstake in {transaction.tx_id}')

    elif function_name in ('claim-rewards', 'claim'):
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.REWARD
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Claim {event.amount} {symbol} staking reward from ALEX'

        log.debug(f'Decoded ALEX claim rewards in {transaction.tx_id}')


def _decode_alex_lending(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode ALEX lending pool transactions.

    For supply: User deposits tokens to lending pool
    For withdraw: User withdraws tokens from lending pool
    """
    function_name = transaction.function_name

    if function_name == 'supply':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.DEPOSIT_ASSET
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Lend {event.amount} {symbol} to ALEX lending pool'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.RECEIVE
                event.event_subtype = HistoryEventSubType.RECEIVE_WRAPPED
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Receive {event.amount} {symbol} lending receipt from ALEX'

        log.debug(f'Decoded ALEX lending supply in {transaction.tx_id}')

    elif function_name == 'withdraw':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.SPEND
                event.event_subtype = HistoryEventSubType.RETURN_WRAPPED
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Return {event.amount} {symbol} lending receipt to ALEX'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.REMOVE_ASSET
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Withdraw {event.amount} {symbol} from ALEX lending pool'

        log.debug(f'Decoded ALEX lending withdraw in {transaction.tx_id}')


def _decode_alex_borrowing(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode ALEX borrowing transactions.

    For borrow: User borrows tokens from lending pool
    For repay: User repays borrowed tokens
    """
    function_name = transaction.function_name

    if function_name == 'borrow':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.RECEIVE
                event.event_subtype = HistoryEventSubType.GENERATE_DEBT
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Borrow {event.amount} {symbol} from ALEX'

        log.debug(f'Decoded ALEX borrow in {transaction.tx_id}')

    elif function_name == 'repay':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.SPEND
                event.event_subtype = HistoryEventSubType.PAYBACK_DEBT
                event.counterparty = CPT_ALEX
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Repay {event.amount} {symbol} to ALEX'

        log.debug(f'Decoded ALEX repay in {transaction.tx_id}')


def _decode_alex_yield(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode ALEX yield claim transactions.

    For claim-yield: User claims yield from lending pool
    """
    for event in existing_events:
        if (
            event.event_type == HistoryEventType.RECEIVE and
            event.event_subtype == HistoryEventSubType.NONE and
            event.location_label == transaction.sender_address
        ):
            event.event_type = HistoryEventType.RECEIVE
            event.event_subtype = HistoryEventSubType.REWARD
            event.counterparty = CPT_ALEX
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            event.notes = f'Claim {event.amount} {symbol} yield from ALEX lending'

    log.debug(f'Decoded ALEX yield claim in {transaction.tx_id}')


def decode_alex_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode ALEX DEX events from a transaction.

    Handles:
    - Swaps (swap-helper, swap-x-for-y, etc.)
    - Liquidity provision (add-to-position, reduce-position)
    - Staking (stake, unstake, claim-rewards)
    - Lending (supply, withdraw)
    - Borrowing (borrow, repay)
    - Yield claims (claim-yield)

    Returns list of additional events to add (may modify existing_events in place).
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    function_name = transaction.function_name

    if function_name in ALEX_SWAP_FUNCTIONS:
        _decode_alex_swap(transaction, base_tools, existing_events)
    elif function_name in ALEX_LIQUIDITY_FUNCTIONS:
        _decode_alex_liquidity(transaction, base_tools, existing_events)
    elif function_name in ALEX_STAKING_FUNCTIONS:
        _decode_alex_staking(transaction, base_tools, existing_events)
    elif (
        function_name in ALEX_LENDING_FUNCTIONS or
        function_name in ALEX_LENDING_WITHDRAW_FUNCTIONS
    ):
        _decode_alex_lending(transaction, base_tools, existing_events)
    elif function_name in ALEX_BORROWING_FUNCTIONS or function_name in ALEX_REPAY_FUNCTIONS:
        _decode_alex_borrowing(transaction, base_tools, existing_events)
    elif function_name in ALEX_YIELD_FUNCTIONS:
        _decode_alex_yield(transaction, base_tools, existing_events)

    return []  # We modify existing events in place
