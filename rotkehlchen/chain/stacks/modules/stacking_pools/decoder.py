"""Third-party stacking pools decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.constants import micro_stx_to_stx
from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.constants.assets import A_STX
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    CPT_STACKING_POOLS,
    FASTPOOL_CONTRACT,
    FASTPOOL_CONTRACT_V1,
    POOL_DELEGATION_FUNCTIONS,
    POOL_REVOCATION_FUNCTIONS,
    STACKING_POOL_CONTRACTS,
    STACKINGDAO_POOL_CONTRACT,
    XVERSE_POOL_CONTRACT,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def _get_pool_name(contract_id: str) -> str:
    """Get human-readable pool name from contract ID."""
    if contract_id in (FASTPOOL_CONTRACT, FASTPOOL_CONTRACT_V1):
        return 'Fastpool'
    elif contract_id == XVERSE_POOL_CONTRACT:
        return 'Xverse Pool'
    elif contract_id == STACKINGDAO_POOL_CONTRACT:
        return 'StackingDAO Pool'
    return 'stacking pool'


def is_stacking_pool_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves a third-party stacking pool contract."""
    if transaction.contract_id is None:
        return False
    return transaction.contract_id in STACKING_POOL_CONTRACTS


def decode_stacking_pool_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode third-party stacking pool events from a transaction.

    Handles:
    - delegate-stx: User delegates STX to a pool
    - revoke-delegate-stx: User revokes delegation from pool

    Returns list of additional events to add.
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    additional_events: list[StacksEvent] = []
    function_name = transaction.function_name
    pool_name = _get_pool_name(transaction.contract_id)

    # Handle delegation to pool
    if function_name in POOL_DELEGATION_FUNCTIONS:
        amount_ustx = transaction.get_uint_arg('amount-ustx')

        if amount_ustx:
            amount = micro_stx_to_stx(amount_ustx)
            notes = f'Delegate {amount} STX to {pool_name}'
        else:
            amount = micro_stx_to_stx(0)
            notes = f'Delegate STX to {pool_name}'

        if base_tools.is_tracked(transaction.sender_address):
            additional_events.append(base_tools.make_event_next_index(
                tx_ref=transaction.tx_id,
                timestamp=transaction.block_time,
                event_type=HistoryEventType.STAKING,
                event_subtype=HistoryEventSubType.DEPOSIT_ASSET,
                asset=A_STX,
                amount=amount,
                location_label=transaction.sender_address,
                notes=notes,
                counterparty=CPT_STACKING_POOLS,
            ))
            log.debug(f'Decoded stacking pool delegation in {transaction.tx_id}: {notes}')

    # Handle revocation of delegation
    elif function_name in POOL_REVOCATION_FUNCTIONS:
        if base_tools.is_tracked(transaction.sender_address):
            additional_events.append(base_tools.make_event_next_index(
                tx_ref=transaction.tx_id,
                timestamp=transaction.block_time,
                event_type=HistoryEventType.STAKING,
                event_subtype=HistoryEventSubType.REMOVE_ASSET,
                asset=A_STX,
                amount=micro_stx_to_stx(0),
                location_label=transaction.sender_address,
                notes=f'Revoke STX delegation from {pool_name}',
                counterparty=CPT_STACKING_POOLS,
            ))
            log.debug(f'Decoded stacking pool revoke delegation in {transaction.tx_id}')

    return additional_events
