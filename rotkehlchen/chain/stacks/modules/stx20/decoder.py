"""STX-20 protocol decoder for Stacks inscription tokens."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.modules.stx20.constants import (
    CPT_STX20,
    STX20_DEPLOY_OP,
    STX20_DEPLOY_PATTERN,
    STX20_MINT_OP,
    STX20_MINT_PATTERN,
    STX20_TRANSFER_OP,
    STX20_TRANSFER_PATTERN,
)
from rotkehlchen.chain.stacks.types import StacksTransaction, StacksTxType
from rotkehlchen.constants.assets import A_STX
from rotkehlchen.constants.misc import ZERO
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools
    from rotkehlchen.history.events.structures.stacks_event import StacksEvent

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_stx20_transaction(transaction: StacksTransaction) -> bool:
    """Check if transaction contains STX-20 protocol data in memo.

    STX-20 transactions are TOKEN_TRANSFER transactions with a memo
    starting with 'd' (deploy), 'm' (mint), or 't' (transfer).
    """
    if transaction.tx_type != StacksTxType.TOKEN_TRANSFER:
        return False

    if transaction.memo is None:
        return False

    memo = transaction.memo.strip()
    if not memo:
        return False

    first_char = memo[0].lower()
    return first_char in (STX20_DEPLOY_OP, STX20_MINT_OP, STX20_TRANSFER_OP)


def decode_stx20_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list['StacksEvent'],
) -> list['StacksEvent']:
    """Decode STX-20 protocol operations from transaction memo.

    STX-20 uses the transaction memo field (34 chars max) to encode:
    - Deploy: d{TICKER}{supply};{limit} (e.g., dSTXS21000000;1000)
    - Mint: m{TICKER}{amount} (e.g., mSTXS1000)
    - Transfer: t{TICKER}{amount} (e.g., tSTXS90)

    Returns list of additional events to add (may modify existing_events in place).
    """
    if transaction.memo is None:
        return []

    memo = transaction.memo.strip()
    op = memo[0].lower()

    if op == STX20_DEPLOY_OP:
        return _decode_stx20_deploy(transaction, base_tools, memo)
    elif op == STX20_MINT_OP:
        return _decode_stx20_mint(transaction, base_tools, existing_events, memo)
    elif op == STX20_TRANSFER_OP:
        return _decode_stx20_transfer(transaction, existing_events, memo)

    return []


def _decode_stx20_deploy(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        memo: str,
) -> list['StacksEvent']:
    """Decode STX-20 token deployment.

    Deploy memo format: d{TICKER}{total_supply};{limit_per_mint}
    Example: dSTXS21000000;1000
    """
    match = STX20_DEPLOY_PATTERN.match(memo)
    if not match:
        log.debug(f'Failed to parse STX-20 deploy memo: {memo}')
        return []

    ticker, total_supply, mint_limit = match.groups()

    if not base_tools.is_tracked(transaction.sender_address):
        return []

    # Create deploy event (informational - no tokens transferred)
    event = base_tools.make_event_next_index(
        tx_ref=transaction.tx_id,
        timestamp=transaction.block_time,
        event_type=HistoryEventType.INFORMATIONAL,
        event_subtype=HistoryEventSubType.CREATE,
        asset=A_STX,
        amount=ZERO,
        location_label=str(transaction.sender_address),
        notes=f'Deploy STX-20 token {ticker} with supply {total_supply}, limit {mint_limit}',
        counterparty=CPT_STX20,
    )
    log.debug(f'Decoded STX-20 deploy in {transaction.tx_id}: {ticker}')
    return [event]


def _decode_stx20_mint(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list['StacksEvent'],
        memo: str,
) -> list['StacksEvent']:
    """Decode STX-20 token mint.

    Mint memo format: m{TICKER}{amount}
    Example: mSTXS1000

    STX-20 mints are self-transfers (sender == recipient) with the mint
    instruction in the memo. We enrich the existing STX transfer event
    with STX-20 context.
    """
    match = STX20_MINT_PATTERN.match(memo)
    if not match:
        log.debug(f'Failed to parse STX-20 mint memo: {memo}')
        return []

    ticker, amount = match.groups()

    # Enrich existing transfer event with STX-20 mint context
    for event in existing_events:
        if event.event_type == HistoryEventType.RECEIVE:
            event.counterparty = CPT_STX20
            event.notes = f'Mint {amount} {ticker} STX-20 tokens'
            log.debug(f'Decoded STX-20 mint in {transaction.tx_id}: {amount} {ticker}')
            return []

    # If no existing receive event but sender is tracked, create informational event
    if base_tools.is_tracked(transaction.sender_address):
        event = base_tools.make_event_next_index(
            tx_ref=transaction.tx_id,
            timestamp=transaction.block_time,
            event_type=HistoryEventType.INFORMATIONAL,
            event_subtype=HistoryEventSubType.NONE,
            asset=A_STX,
            amount=ZERO,
            location_label=str(transaction.sender_address),
            notes=f'Mint {amount} {ticker} STX-20 tokens',
            counterparty=CPT_STX20,
        )
        log.debug(f'Decoded STX-20 mint in {transaction.tx_id}: {amount} {ticker}')
        return [event]

    return []


def _decode_stx20_transfer(
        transaction: StacksTransaction,
        existing_events: list['StacksEvent'],
        memo: str,
) -> list['StacksEvent']:
    """Decode STX-20 token transfer.

    Transfer memo format: t{TICKER}{amount}
    Example: tSTXS90

    STX-20 transfers are regular STX transfers with the transfer
    instruction in the memo. We enrich the existing STX transfer
    events with STX-20 context.
    """
    match = STX20_TRANSFER_PATTERN.match(memo)
    if not match:
        log.debug(f'Failed to parse STX-20 transfer memo: {memo}')
        return []

    ticker, amount = match.groups()

    # Enrich existing STX transfer events with STX-20 context
    for event in existing_events:
        if event.event_type in (HistoryEventType.SPEND, HistoryEventType.RECEIVE):
            event.counterparty = CPT_STX20
            if event.event_type == HistoryEventType.SPEND:
                event.notes = f'Transfer {amount} {ticker} STX-20 tokens'
            else:
                event.notes = f'Receive {amount} {ticker} STX-20 tokens'
            log.debug(
                f'Decoded STX-20 transfer in {transaction.tx_id}: '
                f'{amount} {ticker} ({event.event_type})',
            )

    return []
