"""Dual Stacking protocol decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    CPT_DUAL_STACKING,
    DUAL_STACKING_CONTRACTS,
    DUAL_STACKING_DEFI_ENROLL_FUNCTIONS,
    DUAL_STACKING_DEFI_OPT_OUT_FUNCTIONS,
    DUAL_STACKING_DEFI_SETTINGS_FUNCTIONS,
    DUAL_STACKING_DEPLOYER,
    DUAL_STACKING_ENROLL_FUNCTIONS,
    DUAL_STACKING_OPT_OUT_FUNCTIONS,
    DUAL_STACKING_REWARD_FUNCTIONS,
    DUAL_STACKING_SETTINGS_FUNCTIONS,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_dual_stacking_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves Dual Stacking contracts."""
    if transaction.contract_id is None:
        return False
    # Check if contract is in known contracts or deployed by Dual Stacking deployer
    if transaction.contract_id in DUAL_STACKING_CONTRACTS:
        return True
    # Also match other dual-stacking contracts from the same deployer
    return (
        transaction.contract_id.startswith(DUAL_STACKING_DEPLOYER + '.') and
        'dual-stacking' in transaction.contract_id
    )


def _decode_dual_stacking_enroll(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Dual Stacking enrollment.

    User enrolls in dual stacking to earn sBTC rewards.
    """
    for event in existing_events:
        if event.location_label == transaction.sender_address:
            event.event_type = HistoryEventType.INFORMATIONAL
            event.event_subtype = HistoryEventSubType.NONE
            event.counterparty = CPT_DUAL_STACKING
            event.notes = 'Enroll in Dual Stacking to earn sBTC rewards'

    log.debug(f'Decoded Dual Stacking enroll in {transaction.tx_id}')


def _decode_dual_stacking_opt_out(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Dual Stacking opt-out.

    User opts out of dual stacking.
    """
    for event in existing_events:
        if event.location_label == transaction.sender_address:
            event.event_type = HistoryEventType.INFORMATIONAL
            event.event_subtype = HistoryEventSubType.NONE
            event.counterparty = CPT_DUAL_STACKING
            event.notes = 'Opt out of Dual Stacking'

    log.debug(f'Decoded Dual Stacking opt-out in {transaction.tx_id}')


def _decode_dual_stacking_settings(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Dual Stacking settings changes.

    User changes their reward address or other settings.
    """
    function_name = transaction.function_name

    for event in existing_events:
        if event.location_label == transaction.sender_address:
            event.event_type = HistoryEventType.INFORMATIONAL
            event.event_subtype = HistoryEventSubType.NONE
            event.counterparty = CPT_DUAL_STACKING
            if function_name == 'change-reward-address':
                event.notes = 'Change Dual Stacking reward address'
            else:
                event.notes = 'Update Dual Stacking settings'

    log.debug(f'Decoded Dual Stacking settings change in {transaction.tx_id}')


def _decode_dual_stacking_defi_enroll(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Dual Stacking DeFi enrollment.

    User enrolls DeFi positions in dual stacking.
    """
    for event in existing_events:
        if event.location_label == transaction.sender_address:
            event.event_type = HistoryEventType.INFORMATIONAL
            event.event_subtype = HistoryEventSubType.NONE
            event.counterparty = CPT_DUAL_STACKING
            event.notes = 'Enroll DeFi positions in Dual Stacking'

    log.debug(f'Decoded Dual Stacking DeFi enroll in {transaction.tx_id}')


def _decode_dual_stacking_defi_opt_out(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Dual Stacking DeFi opt-out.

    User removes DeFi positions from dual stacking.
    """
    for event in existing_events:
        if event.location_label == transaction.sender_address:
            event.event_type = HistoryEventType.INFORMATIONAL
            event.event_subtype = HistoryEventSubType.NONE
            event.counterparty = CPT_DUAL_STACKING
            event.notes = 'Remove DeFi positions from Dual Stacking'

    log.debug(f'Decoded Dual Stacking DeFi opt-out in {transaction.tx_id}')


def _decode_dual_stacking_defi_settings(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Dual Stacking DeFi settings changes."""
    for event in existing_events:
        if event.location_label == transaction.sender_address:
            event.event_type = HistoryEventType.INFORMATIONAL
            event.event_subtype = HistoryEventSubType.NONE
            event.counterparty = CPT_DUAL_STACKING
            event.notes = 'Update DeFi Dual Stacking settings'

    log.debug(f'Decoded Dual Stacking DeFi settings in {transaction.tx_id}')


def _decode_dual_stacking_rewards(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Dual Stacking reward distribution.

    When rewards are distributed, users receive sBTC.
    """
    for event in existing_events:
        # Mark received sBTC as staking rewards
        if (
            event.event_type == HistoryEventType.RECEIVE and
            event.event_subtype == HistoryEventSubType.NONE
        ):
            event.event_type = HistoryEventType.STAKING
            event.event_subtype = HistoryEventSubType.REWARD
            event.counterparty = CPT_DUAL_STACKING
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            event.notes = f'Receive {event.amount} {symbol} from Dual Stacking rewards'

    log.debug(f'Decoded Dual Stacking rewards in {transaction.tx_id}')


def decode_dual_stacking_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode Dual Stacking protocol events from a transaction.

    Handles:
    - User enrollment (enroll)
    - User opt-out (opt-out)
    - Settings changes (change-reward-address)
    - DeFi enrollment (enroll-defi, enroll-defi-batch)
    - DeFi opt-out (opt-out-defi, opt-out-defi-batch)
    - Reward distribution (distribute-rewards)

    Returns list of additional events to add (may modify existing_events in place).
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    function_name = transaction.function_name

    # Handle user enrollment
    if function_name in DUAL_STACKING_ENROLL_FUNCTIONS:
        _decode_dual_stacking_enroll(transaction, base_tools, existing_events)

    # Handle user opt-out
    elif function_name in DUAL_STACKING_OPT_OUT_FUNCTIONS:
        _decode_dual_stacking_opt_out(transaction, base_tools, existing_events)

    # Handle user settings changes
    elif function_name in DUAL_STACKING_SETTINGS_FUNCTIONS:
        _decode_dual_stacking_settings(transaction, base_tools, existing_events)

    # Handle DeFi enrollment
    elif function_name in DUAL_STACKING_DEFI_ENROLL_FUNCTIONS:
        _decode_dual_stacking_defi_enroll(transaction, base_tools, existing_events)

    # Handle DeFi opt-out
    elif function_name in DUAL_STACKING_DEFI_OPT_OUT_FUNCTIONS:
        _decode_dual_stacking_defi_opt_out(transaction, base_tools, existing_events)

    # Handle DeFi settings changes
    elif function_name in DUAL_STACKING_DEFI_SETTINGS_FUNCTIONS:
        _decode_dual_stacking_defi_settings(transaction, base_tools, existing_events)

    # Handle reward distribution
    elif function_name in DUAL_STACKING_REWARD_FUNCTIONS:
        _decode_dual_stacking_rewards(transaction, base_tools, existing_events)

    return []  # We modify existing events in place
