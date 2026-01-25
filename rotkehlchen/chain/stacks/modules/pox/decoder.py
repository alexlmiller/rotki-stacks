"""PoX native stacking protocol decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.constants import micro_stx_to_stx
from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.constants.assets import A_STX
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    CPT_POX,
    POX_CONTRACTS,
    POX_DELEGATE_STX,
    POX_LOCK_FUNCTIONS,
    POX_REVOKE_DELEGATE_STX,
    POX_STACK_EXTEND,
    POX_STACK_INCREASE,
    POX_STACK_STX,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_pox_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves PoX stacking contracts."""
    if transaction.contract_id is None:
        return False
    return transaction.contract_id in POX_CONTRACTS


def decode_pox_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode PoX stacking events from a transaction.

    Handles:
    - stack-stx: Lock STX for stacking
    - stack-extend: Extend stacking period
    - stack-increase: Increase stacked amount
    - delegate-stx: Delegate to a pool
    - revoke-delegate-stx: Revoke delegation

    Note: BTC rewards go to the user's Bitcoin address and are tracked
    via Rotki's Bitcoin wallet integration, not here.

    Returns list of additional events to add.
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    additional_events: list[StacksEvent] = []
    function_name = transaction.function_name

    # For stacking operations, we create a STAKING deposit event
    if function_name in POX_LOCK_FUNCTIONS:
        # Extract amount from function arguments
        amount_ustx: int | None = None

        if function_name == POX_STACK_STX:
            amount_ustx = transaction.get_uint_arg('amount-ustx')
            lock_period = transaction.get_uint_arg('lock-period')
            period_str = f' for {lock_period} cycles' if lock_period else ''
            if amount_ustx:
                amount = micro_stx_to_stx(amount_ustx)
                notes = f'Lock {amount} STX for stacking{period_str}'
            else:
                amount = micro_stx_to_stx(0)
                notes = f'Lock STX for stacking{period_str}'
            event_subtype = HistoryEventSubType.DEPOSIT_ASSET

        elif function_name == POX_STACK_EXTEND:
            extend_count = transaction.get_uint_arg('extend-count')
            count_str = f' by {extend_count} cycles' if extend_count else ''
            amount = micro_stx_to_stx(0)  # extend doesn't have an amount
            notes = f'Extend STX stacking period{count_str}'
            event_subtype = HistoryEventSubType.DEPOSIT_ASSET

        elif function_name == POX_STACK_INCREASE:
            amount_ustx = transaction.get_uint_arg('increase-by')
            if amount_ustx:
                amount = micro_stx_to_stx(amount_ustx)
                notes = f'Increase stacked STX by {amount}'
            else:
                amount = micro_stx_to_stx(0)
                notes = 'Increase stacked STX amount'
            event_subtype = HistoryEventSubType.DEPOSIT_ASSET

        elif function_name == POX_DELEGATE_STX:
            amount_ustx = transaction.get_uint_arg('amount-ustx')
            delegate_to = transaction.get_principal_arg('delegate-to')
            if amount_ustx:
                amount = micro_stx_to_stx(amount_ustx)
                if delegate_to:
                    notes = f'Delegate {amount} STX to {delegate_to}'
                else:
                    notes = f'Delegate {amount} STX to stacking pool'
            else:
                amount = micro_stx_to_stx(0)
                notes = 'Delegate STX to stacking pool'
            event_subtype = HistoryEventSubType.DEPOSIT_ASSET

        else:
            amount = micro_stx_to_stx(0)
            notes = f'Stacking operation: {function_name}'
            event_subtype = HistoryEventSubType.DEPOSIT_ASSET

        # Only create event if we have a tracked sender
        if base_tools.is_tracked(transaction.sender_address):
            additional_events.append(base_tools.make_event_next_index(
                tx_ref=transaction.tx_id,
                timestamp=transaction.block_time,
                event_type=HistoryEventType.STAKING,
                event_subtype=event_subtype,
                asset=A_STX,
                amount=amount,
                location_label=transaction.sender_address,
                notes=notes,
                counterparty=CPT_POX,
            ))
            log.debug(f'Decoded PoX stacking event in {transaction.tx_id}: {notes}')

    # Handle delegation revocation
    elif function_name == POX_REVOKE_DELEGATE_STX:
        if base_tools.is_tracked(transaction.sender_address):
            additional_events.append(base_tools.make_event_next_index(
                tx_ref=transaction.tx_id,
                timestamp=transaction.block_time,
                event_type=HistoryEventType.STAKING,
                event_subtype=HistoryEventSubType.REMOVE_ASSET,
                asset=A_STX,
                amount=micro_stx_to_stx(0),
                location_label=transaction.sender_address,
                notes='Revoke STX stacking delegation',
                counterparty=CPT_POX,
            ))
            log.debug(f'Decoded PoX revoke delegation in {transaction.tx_id}')

    return additional_events
