"""StackingDAO liquid staking protocol decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    CPT_STACKINGDAO,
    STACKINGDAO_CLAIM_REWARDS,
    STACKINGDAO_CONTRACTS,
    STACKINGDAO_DEPOSIT,
    STACKINGDAO_WITHDRAW,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_stackingdao_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves StackingDAO contracts."""
    if transaction.contract_id is None:
        return False
    return transaction.contract_id in STACKINGDAO_CONTRACTS


def decode_stackingdao_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode StackingDAO liquid staking events from a transaction.

    Handles:
    - deposit: STX → stSTX or STX → stSTXBTC
    - withdraw: stSTX → STX or stSTXBTC → STX
    - claim-rewards: Claim sBTC rewards from stSTXBTC

    Reward handling:
    - stSTX: Rewards accrue in backing. Gain recognized at redemption
      (receive more STX than deposited)
    - stSTXBTC: sBTC rewards claimable separately. Each claim is income at FMV.

    Returns list of additional events to add (may modify existing_events in place).
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    function_name = transaction.function_name

    # Handle deposit (STX → stSTX or stSTXBTC)
    if function_name == STACKINGDAO_DEPOSIT:
        stx_spend = None
        token_receive = None

        for event in existing_events:
            # Find STX spend event
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                'STX' in event.asset.identifier.upper() and
                'ststx' not in event.asset.identifier.lower()
            ):
                stx_spend = event
            # Find stSTX or stSTXBTC receive event
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                ('ststx' in event.asset.identifier.lower() or
                 'ststxbtc' in event.asset.identifier.lower())
            ):
                token_receive = event

        # Update events with StackingDAO context
        if stx_spend is not None:
            stx_spend.event_type = HistoryEventType.DEPOSIT
            stx_spend.event_subtype = HistoryEventSubType.DEPOSIT_ASSET
            stx_spend.counterparty = CPT_STACKINGDAO
            stx_spend.notes = f'Deposit {stx_spend.amount} STX into StackingDAO'

        if token_receive is not None:
            token_receive.event_type = HistoryEventType.DEPOSIT
            token_receive.event_subtype = HistoryEventSubType.RECEIVE_WRAPPED
            token_receive.counterparty = CPT_STACKINGDAO
            symbol = token_receive.asset.resolve_to_asset_with_symbol().symbol
            token_receive.notes = f'Receive {token_receive.amount} {symbol} from StackingDAO'

        if stx_spend or token_receive:
            log.debug(f'Decoded StackingDAO deposit in {transaction.tx_id}')

    # Handle withdrawal (stSTX/stSTXBTC → STX)
    elif function_name == STACKINGDAO_WITHDRAW:
        token_spend = None
        stx_receive = None

        for event in existing_events:
            # Find stSTX or stSTXBTC spend event
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                ('ststx' in event.asset.identifier.lower() or
                 'ststxbtc' in event.asset.identifier.lower())
            ):
                token_spend = event
            # Find STX receive event
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                'STX' in event.asset.identifier.upper() and
                'ststx' not in event.asset.identifier.lower()
            ):
                stx_receive = event

        # Update events with StackingDAO context
        if token_spend is not None:
            token_spend.event_type = HistoryEventType.WITHDRAWAL
            token_spend.event_subtype = HistoryEventSubType.RETURN_WRAPPED
            token_spend.counterparty = CPT_STACKINGDAO
            symbol = token_spend.asset.resolve_to_asset_with_symbol().symbol
            token_spend.notes = f'Return {token_spend.amount} {symbol} to StackingDAO'

        if stx_receive is not None:
            stx_receive.event_type = HistoryEventType.WITHDRAWAL
            stx_receive.event_subtype = HistoryEventSubType.REMOVE_ASSET
            stx_receive.counterparty = CPT_STACKINGDAO
            stx_receive.notes = f'Withdraw {stx_receive.amount} STX from StackingDAO'

        if token_spend or stx_receive:
            log.debug(f'Decoded StackingDAO withdrawal in {transaction.tx_id}')

    # Handle sBTC rewards claim (stSTXBTC)
    elif function_name == STACKINGDAO_CLAIM_REWARDS:
        for event in existing_events:
            # Find sBTC receive event
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                'sbtc' in event.asset.identifier.lower()
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.REWARD
                event.counterparty = CPT_STACKINGDAO
                event.notes = f'Claim {event.amount} sBTC staking reward from StackingDAO'
                log.debug(f'Decoded StackingDAO reward claim in {transaction.tx_id}')

    return []  # We modify existing events in place, no new events needed
