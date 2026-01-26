"""Hermetica synthetic assets protocol decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    CPT_HERMETICA,
    HERMETICA_BURN_FUNCTIONS,
    HERMETICA_CONFIRM_MINT_FUNCTIONS,
    HERMETICA_CONFIRM_REDEEM_FUNCTIONS,
    HERMETICA_CONTRACTS,
    HERMETICA_MINT_FUNCTIONS,
    HERMETICA_REQUEST_FUNCTIONS,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_hermetica_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves Hermetica contracts."""
    if transaction.contract_id is None:
        return False
    return transaction.contract_id in HERMETICA_CONTRACTS


def decode_hermetica_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode Hermetica protocol events from a transaction.

    Handles:
    - Mint USDh (deposit collateral, receive synthetic)
    - Burn/Redeem USDh (return synthetic, receive collateral)
    - Staking (stake, unstake, claim rewards)

    Returns list of additional events to add (may modify existing_events in place).
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    function_name = transaction.function_name

    # Handle two-phase request operations (informational only)
    if function_name in HERMETICA_REQUEST_FUNCTIONS:
        # Request operations don't involve actual transfers, just track intent
        for event in existing_events:
            if event.location_label == transaction.sender_address:
                event.event_type = HistoryEventType.INFORMATIONAL
                event.event_subtype = HistoryEventSubType.NONE
                event.counterparty = CPT_HERMETICA
                if function_name == 'request-mint':
                    event.notes = 'Request to mint USDh on Hermetica'
                else:
                    event.notes = 'Request to redeem USDh on Hermetica'

        log.debug(f'Decoded Hermetica request in {transaction.tx_id}')

    # Handle two-phase confirm mint (actual deposit with BRIDGE subtype)
    elif function_name in HERMETICA_CONFIRM_MINT_FUNCTIONS:
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.BRIDGE
                event.counterparty = CPT_HERMETICA
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Confirm mint: deposit {event.amount} {symbol} to Hermetica'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.BRIDGE
                event.counterparty = CPT_HERMETICA
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Confirm mint: receive {event.amount} {symbol} from Hermetica'

        log.debug(f'Decoded Hermetica confirm mint in {transaction.tx_id}')

    # Handle two-phase confirm redeem (actual withdrawal with BRIDGE subtype)
    elif function_name in HERMETICA_CONFIRM_REDEEM_FUNCTIONS:
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.BRIDGE
                event.counterparty = CPT_HERMETICA
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Confirm redeem: return {event.amount} {symbol} to Hermetica'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.BRIDGE
                event.counterparty = CPT_HERMETICA
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Confirm redeem: receive {event.amount} {symbol} from Hermetica'

        log.debug(f'Decoded Hermetica confirm redeem in {transaction.tx_id}')

    # Handle minting USDh
    elif function_name in HERMETICA_MINT_FUNCTIONS:
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.DEPOSIT_ASSET
                event.counterparty = CPT_HERMETICA
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Deposit {event.amount} {symbol} as collateral to Hermetica'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.DEPOSIT
                event.event_subtype = HistoryEventSubType.RECEIVE_WRAPPED
                event.counterparty = CPT_HERMETICA
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Mint {event.amount} {symbol} from Hermetica'

        log.debug(f'Decoded Hermetica mint in {transaction.tx_id}')

    # Handle burning/redeeming USDh
    elif function_name in HERMETICA_BURN_FUNCTIONS:
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.RETURN_WRAPPED
                event.counterparty = CPT_HERMETICA
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Burn {event.amount} {symbol} in Hermetica'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.WITHDRAWAL
                event.event_subtype = HistoryEventSubType.REMOVE_ASSET
                event.counterparty = CPT_HERMETICA
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Redeem {event.amount} {symbol} from Hermetica'

        log.debug(f'Decoded Hermetica burn/redeem in {transaction.tx_id}')

    # Handle staking
    elif function_name == 'stake':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.DEPOSIT_ASSET
                event.counterparty = CPT_HERMETICA
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Stake {event.amount} {symbol} on Hermetica'

        log.debug(f'Decoded Hermetica stake in {transaction.tx_id}')

    elif function_name == 'unstake':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.REMOVE_ASSET
                event.counterparty = CPT_HERMETICA
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Unstake {event.amount} {symbol} from Hermetica'

        log.debug(f'Decoded Hermetica unstake in {transaction.tx_id}')

    elif function_name == 'claim':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.REWARD
                event.counterparty = CPT_HERMETICA
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Claim {event.amount} {symbol} reward from Hermetica'

        log.debug(f'Decoded Hermetica claim in {transaction.tx_id}')

    return []
