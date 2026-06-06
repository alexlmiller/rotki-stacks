"""Send-many batched transfer decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.decoding.constants import CPT_GAS
from rotkehlchen.chain.stacks.clarity_parser import parse_clarity_repr_safe
from rotkehlchen.chain.stacks.constants import micro_stx_to_stx
from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.constants.assets import A_STX
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.types import StacksAddress

from .constants import (
    CPT_SENDMANY,
    SENDMANY_CONTRACTS,
    SENDMANY_FUNCTION,
    SENDMANY_MEMO_FUNCTION,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_sendmany_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves send-many contracts."""
    if transaction.contract_id is None:
        return False
    return transaction.contract_id in SENDMANY_CONTRACTS


def _extract_recipients_from_args(
        transaction: StacksTransaction,
) -> list[tuple[str, int]]:
    """Extract recipients and amounts from send-many function arguments.

    Returns a list of (recipient_address, amount_ustx) tuples.
    """
    if transaction.function_args is None:
        return []

    recipients: list[tuple[str, int]] = []

    # Find the recipients argument (usually named 'recipients' or the first list arg)
    for arg in transaction.function_args:
        arg_name = arg.get('name', '')
        arg_repr = arg.get('repr', '')
        arg_type = arg.get('type', '')

        # Check if this is the recipients list
        if arg_name != 'recipients' and 'list' not in arg_type.lower():
            continue

        # Parse the list of recipients
        parsed = parse_clarity_repr_safe(arg_repr)

        if not isinstance(parsed, list):
            continue

        for item in parsed:
            if not isinstance(item, dict):
                continue

            # Extract recipient address (may be 'to' or 'recipient')
            recipient = item.get('to') or item.get('recipient')
            # Extract amount (may be 'ustx', 'amount', 'amount-ustx')
            amount = item.get('ustx') or item.get('amount') or item.get('amount-ustx')

            if recipient is not None and amount is not None:
                try:
                    if isinstance(amount, int):
                        amount_int = amount
                    elif isinstance(amount, str):
                        amount_int = int(amount)
                    else:
                        continue  # Skip unsupported amount types
                    recipients.append((str(recipient), amount_int))
                except (ValueError, TypeError):
                    log.debug(f'Failed to parse recipient {recipient!r} with amount {amount!r}')
                    continue

    return recipients


def decode_sendmany_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode send-many batched transfer events from a transaction.

    Handles:
    - send-many: Send STX to multiple recipients
    - send-many-memo: Send STX to multiple recipients with memos

    This decoder enhances existing events by adding send-many context
    and may create additional events for recipients not in existing events.

    Returns list of additional events to add.
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    function_name = transaction.function_name
    if function_name not in (SENDMANY_FUNCTION, SENDMANY_MEMO_FUNCTION):
        return []

    # Extract recipients from function arguments
    recipients = _extract_recipients_from_args(transaction)

    if not recipients:
        log.debug(f'No recipients found in send-many transaction {transaction.tx_id}')
        return []

    log.debug(f'Found {len(recipients)} recipients in send-many tx {transaction.tx_id}')

    additional_events: list[StacksEvent] = []
    sender_is_tracked = base_tools.is_tracked(transaction.sender_address)

    # Build a map of existing receive events by address for quick lookup
    existing_receive_by_address: dict[str, StacksEvent] = {}
    for event in existing_events:
        if (
            event.event_type == HistoryEventType.RECEIVE and
            event.event_subtype == HistoryEventSubType.NONE and
            'STX' in event.asset.identifier.upper()
        ):
            # Use the address field if available, otherwise location_label
            addr = event.address or event.location_label
            if addr:
                existing_receive_by_address[addr] = event

    # Check if sender already has a spend event for total amount
    sender_has_spend = any(
        event.event_type == HistoryEventType.SPEND and
        event.event_subtype == HistoryEventSubType.NONE and
        'STX' in event.asset.identifier.upper() and
        event.location_label == transaction.sender_address
        for event in existing_events
    )

    # Process each recipient
    total_amount = 0
    for recipient_address, amount_ustx in recipients:
        total_amount += amount_ustx
        recipient_is_tracked = base_tools.is_tracked(StacksAddress(recipient_address))

        # Check if we already have a receive event for this recipient
        if recipient_address in existing_receive_by_address:
            # Update the existing event with send-many context
            event = existing_receive_by_address[recipient_address]
            event.counterparty = CPT_SENDMANY
            event.notes = (
                f'Receive {event.amount} STX from {transaction.sender_address} '
                f'via send-many'
            )
            log.debug(f'Enhanced existing receive event for {recipient_address}')
            continue

        # Create new event if recipient is tracked and not already covered
        if recipient_is_tracked:
            amount = micro_stx_to_stx(amount_ustx)
            additional_events.append(base_tools.make_event_next_index(
                tx_ref=transaction.tx_id,
                timestamp=transaction.block_time,
                event_type=HistoryEventType.RECEIVE,
                event_subtype=HistoryEventSubType.NONE,
                asset=A_STX,
                amount=amount,
                location_label=recipient_address,
                notes=f'Receive {amount} STX from {transaction.sender_address} via send-many',
                counterparty=CPT_SENDMANY,
                address=transaction.sender_address,
            ))
            log.debug(f'Created receive event for tracked recipient {recipient_address}')

    # If sender is tracked and no spend event exists, create one for total
    if sender_is_tracked and not sender_has_spend and total_amount > 0:
        # Validate that parsed total matches transaction amount if available
        if transaction.amount is not None and transaction.amount != total_amount:
            log.warning(
                f'Send-many tx {transaction.tx_id}: parsed total ({total_amount}) '
                f'differs from transaction amount ({transaction.amount}). '
                f'Some recipients may not have been parsed correctly.',
            )
        amount = micro_stx_to_stx(total_amount)
        additional_events.append(base_tools.make_event_next_index(
            tx_ref=transaction.tx_id,
            timestamp=transaction.block_time,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.NONE,
            asset=A_STX,
            amount=amount,
            location_label=transaction.sender_address,
            notes=f'Send {amount} STX to {len(recipients)} recipients via send-many',
            counterparty=CPT_SENDMANY,
        ))
        log.debug(f'Created spend event for sender {transaction.sender_address}')

    # Update any existing spend events from sender with send-many context
    for event in existing_events:
        if (
            event.event_type == HistoryEventType.SPEND and
            event.event_subtype != HistoryEventSubType.FEE and
            event.counterparty != CPT_GAS and
            'STX' in event.asset.identifier.upper() and
            event.location_label == transaction.sender_address
        ):
            event.counterparty = CPT_SENDMANY
            event.notes = f'Send {event.amount} STX to {len(recipients)} recipients via send-many'

    return additional_events
