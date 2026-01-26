"""Arkadiko CDP protocol decoder."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter

from .constants import (
    ARKADIKO_BURN_FUNCTIONS,
    ARKADIKO_CONTRACTS,
    ARKADIKO_DAO_ADDRESS,
    ARKADIKO_LIQUIDATION_FUNCTIONS,
    ARKADIKO_MINT_FUNCTIONS,
    ARKADIKO_STAKING_FUNCTIONS,
    ARKADIKO_VAULT_DEPOSIT_FUNCTIONS,
    ARKADIKO_VAULT_WITHDRAW_FUNCTIONS,
    CPT_ARKADIKO,
)

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.decoding.tools import StacksDecoderTools

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def is_arkadiko_transaction(transaction: StacksTransaction) -> bool:
    """Check if the transaction involves Arkadiko contracts."""
    if transaction.contract_id is None:
        return False
    # Check if contract is in known contracts or belongs to Arkadiko DAO address
    if transaction.contract_id in ARKADIKO_CONTRACTS:
        return True
    # Also match contracts deployed by Arkadiko DAO
    return transaction.contract_id.startswith(ARKADIKO_DAO_ADDRESS + '.')


def _decode_arkadiko_vault_deposit(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Arkadiko vault deposit/collateralize operations.

    For collateralize-and-mint: User deposits collateral and receives USDA
    For deposit: User deposits additional collateral to an existing vault
    """
    function_name = transaction.function_name

    for event in existing_events:
        # Mark STX/collateral spent as deposit
        if (
            event.event_type == HistoryEventType.SPEND and
            event.event_subtype == HistoryEventSubType.NONE and
            event.location_label == transaction.sender_address
        ):
            event.event_type = HistoryEventType.DEPOSIT
            event.event_subtype = HistoryEventSubType.DEPOSIT_ASSET
            event.counterparty = CPT_ARKADIKO
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            if function_name == 'collateralize-and-mint':
                event.notes = f'Deposit {event.amount} {symbol} as collateral to Arkadiko vault'
            else:
                event.notes = f'Deposit {event.amount} {symbol} collateral to Arkadiko vault'

        # Mark USDA received as debt generation (only for collateralize-and-mint)
        elif (
            function_name == 'collateralize-and-mint' and
            event.event_type == HistoryEventType.RECEIVE and
            event.event_subtype == HistoryEventSubType.NONE and
            event.location_label == transaction.sender_address
        ):
            event.event_type = HistoryEventType.RECEIVE
            event.event_subtype = HistoryEventSubType.GENERATE_DEBT
            event.counterparty = CPT_ARKADIKO
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            event.notes = f'Mint {event.amount} {symbol} debt on Arkadiko'

    log.debug(f'Decoded Arkadiko vault deposit in {transaction.tx_id}')


def _decode_arkadiko_vault_withdraw(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Arkadiko vault withdrawal operations.

    User withdraws collateral from their vault.
    """
    for event in existing_events:
        if (
            event.event_type == HistoryEventType.RECEIVE and
            event.event_subtype == HistoryEventSubType.NONE and
            event.location_label == transaction.sender_address
        ):
            event.event_type = HistoryEventType.WITHDRAWAL
            event.event_subtype = HistoryEventSubType.REMOVE_ASSET
            event.counterparty = CPT_ARKADIKO
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            event.notes = f'Withdraw {event.amount} {symbol} collateral from Arkadiko vault'

    log.debug(f'Decoded Arkadiko vault withdrawal in {transaction.tx_id}')


def _decode_arkadiko_mint(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Arkadiko mint (debt generation) operations.

    User mints additional USDA debt against existing collateral.
    Note: collateralize-and-mint is handled in _decode_arkadiko_vault_deposit.
    """
    if transaction.function_name == 'collateralize-and-mint':
        return  # Already handled in vault deposit

    for event in existing_events:
        if (
            event.event_type == HistoryEventType.RECEIVE and
            event.event_subtype == HistoryEventSubType.NONE and
            event.location_label == transaction.sender_address
        ):
            event.event_type = HistoryEventType.RECEIVE
            event.event_subtype = HistoryEventSubType.GENERATE_DEBT
            event.counterparty = CPT_ARKADIKO
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            event.notes = f'Mint {event.amount} {symbol} debt on Arkadiko'

    log.debug(f'Decoded Arkadiko mint in {transaction.tx_id}')


def _decode_arkadiko_burn(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Arkadiko burn (debt repayment) operations.

    User repays USDA debt to their vault.
    """
    for event in existing_events:
        if (
            event.event_type == HistoryEventType.SPEND and
            event.event_subtype == HistoryEventSubType.NONE and
            event.location_label == transaction.sender_address
        ):
            event.event_type = HistoryEventType.SPEND
            event.event_subtype = HistoryEventSubType.PAYBACK_DEBT
            event.counterparty = CPT_ARKADIKO
            symbol = event.asset.resolve_to_asset_with_symbol().symbol
            event.notes = f'Repay {event.amount} {symbol} debt on Arkadiko'

    log.debug(f'Decoded Arkadiko burn in {transaction.tx_id}')


def _decode_arkadiko_liquidation(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Arkadiko liquidation operations.

    For liquidate: A vault is being liquidated
    For bid: User bids on liquidation auction
    """
    function_name = transaction.function_name

    for event in existing_events:
        if function_name == 'liquidate':
            # The vault owner loses collateral (if we track them)
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE
            ):
                event.event_type = HistoryEventType.LOSS
                event.event_subtype = HistoryEventSubType.LIQUIDATE
                event.counterparty = CPT_ARKADIKO
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Vault liquidated: lost {event.amount} {symbol} on Arkadiko'

        elif function_name == 'bid':
            # Bidder spends to purchase collateral at auction
            if (
                event.event_type == HistoryEventType.SPEND and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.TRADE
                event.event_subtype = HistoryEventSubType.SPEND
                event.counterparty = CPT_ARKADIKO
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Bid {event.amount} {symbol} in Arkadiko liquidation auction'
            elif (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.TRADE
                event.event_subtype = HistoryEventSubType.RECEIVE
                event.counterparty = CPT_ARKADIKO
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Receive {event.amount} {symbol} from Arkadiko liquidation auction'

    log.debug(f'Decoded Arkadiko liquidation in {transaction.tx_id}')


def _decode_arkadiko_staking(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> None:
    """Decode Arkadiko DIKO staking operations.

    For stake: User stakes DIKO tokens
    For unstake: User unstakes DIKO tokens
    For claim-staking-rewards: User claims DIKO rewards
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
                event.counterparty = CPT_ARKADIKO
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Stake {event.amount} {symbol} on Arkadiko'

        log.debug(f'Decoded Arkadiko stake in {transaction.tx_id}')

    elif function_name == 'unstake':
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.REMOVE_ASSET
                event.counterparty = CPT_ARKADIKO
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Unstake {event.amount} {symbol} from Arkadiko'

        log.debug(f'Decoded Arkadiko unstake in {transaction.tx_id}')

    elif function_name in ('claim-staking-rewards', 'get-rewards-to-add'):
        for event in existing_events:
            if (
                event.event_type == HistoryEventType.RECEIVE and
                event.event_subtype == HistoryEventSubType.NONE and
                event.location_label == transaction.sender_address
            ):
                event.event_type = HistoryEventType.STAKING
                event.event_subtype = HistoryEventSubType.REWARD
                event.counterparty = CPT_ARKADIKO
                symbol = event.asset.resolve_to_asset_with_symbol().symbol
                event.notes = f'Claim {event.amount} {symbol} staking reward from Arkadiko'

        log.debug(f'Decoded Arkadiko claim rewards in {transaction.tx_id}')


def decode_arkadiko_events(
        transaction: StacksTransaction,
        base_tools: 'StacksDecoderTools',
        existing_events: list[StacksEvent],
) -> list[StacksEvent]:
    """Decode Arkadiko CDP protocol events from a transaction.

    Handles:
    - Vault operations (collateralize-and-mint, deposit, withdraw)
    - Debt operations (mint, burn)
    - Liquidations (liquidate, bid)
    - Staking (stake, unstake, claim-staking-rewards)

    Returns list of additional events to add (may modify existing_events in place).
    """
    if transaction.contract_id is None or transaction.function_name is None:
        return []

    function_name = transaction.function_name

    # Handle vault deposits (including collateralize-and-mint)
    if function_name in ARKADIKO_VAULT_DEPOSIT_FUNCTIONS:
        _decode_arkadiko_vault_deposit(transaction, base_tools, existing_events)

    # Handle vault withdrawals
    elif function_name in ARKADIKO_VAULT_WITHDRAW_FUNCTIONS:
        _decode_arkadiko_vault_withdraw(transaction, base_tools, existing_events)

    # Handle minting (standalone mint, not collateralize-and-mint)
    elif function_name in ARKADIKO_MINT_FUNCTIONS:
        _decode_arkadiko_mint(transaction, base_tools, existing_events)

    # Handle burning (debt repayment)
    elif function_name in ARKADIKO_BURN_FUNCTIONS:
        _decode_arkadiko_burn(transaction, base_tools, existing_events)

    # Handle liquidations
    elif function_name in ARKADIKO_LIQUIDATION_FUNCTIONS:
        _decode_arkadiko_liquidation(transaction, base_tools, existing_events)

    # Handle staking
    elif function_name in ARKADIKO_STAKING_FUNCTIONS:
        _decode_arkadiko_staking(transaction, base_tools, existing_events)

    return []  # We modify existing events in place
