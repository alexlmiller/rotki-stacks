"""Data migration 27: Populate function_args for existing Stacks transactions.

This migration re-fetches Stacks contract call transactions from the Hiro API
to populate the function_args column and indexed argument columns.
"""
import contextlib
import json
import logging
from typing import TYPE_CHECKING

import gevent

from rotkehlchen.chain.stacks.constants import (
    BACKOFF_MULTIPLIER,
    HIRO_API_BASE_URL,
    INITIAL_BACKOFF,
    MAX_RETRIES,
)
from rotkehlchen.chain.stacks.types import FunctionArg
from rotkehlchen.logging import RotkehlchenLogsAdapter, enter_exit_debug_log
from rotkehlchen.utils.progress import perform_userdb_migration_steps, progress_step

if TYPE_CHECKING:
    import requests

    from rotkehlchen.data_migrations.progress import MigrationProgressHandler
    from rotkehlchen.db.drivers.gevent import DBCursor
    from rotkehlchen.rotkehlchen import Rotkehlchen

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)

# Batch size for re-fetching transactions
REFETCH_BATCH_SIZE = 25
# Delay between batches to avoid rate limiting (seconds)
BATCH_DELAY = 2


def _fetch_transaction_from_api(
        session: 'requests.Session',
        tx_id: str,
) -> tuple[FunctionArg, ...] | None:
    """Fetch a single transaction from Hiro API and extract function_args.

    Returns tuple of FunctionArg dicts, or None if fetch fails or no args.
    """
    url = f'{HIRO_API_BASE_URL}/extended/v1/tx/{tx_id}'
    backoff = INITIAL_BACKOFF

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=30)

            if response.status_code == 429:
                # Rate limited
                retry_after = response.headers.get('retry-after')
                if retry_after is not None:
                    with contextlib.suppress(ValueError):
                        backoff = int(retry_after) + 1

                if attempt < MAX_RETRIES:
                    log.debug(f'Rate limited fetching {tx_id}, backing off {backoff}s')
                    gevent.sleep(backoff)
                    backoff *= BACKOFF_MULTIPLIER
                    continue
                return None

            if response.status_code == 404:
                log.debug(f'Transaction {tx_id} not found in API')
                return None

            response.raise_for_status()
            data = response.json()

            # Extract function_args from contract_call
            contract_call = data.get('contract_call', {})
            raw_args = contract_call.get('function_args', [])

            if not raw_args:
                return None

            return tuple(
                FunctionArg(
                    name=arg.get('name', ''),
                    type=arg.get('type', ''),
                    repr=arg.get('repr', ''),
                    hex=arg.get('hex', ''),
                )
                for arg in raw_args
            )

        except Exception as e:
            if attempt < MAX_RETRIES:
                log.debug(f'Error fetching {tx_id}: {e}, retrying...')
                gevent.sleep(backoff)
                backoff *= BACKOFF_MULTIPLIER
                continue
            log.error(f'Failed to fetch transaction {tx_id} after {MAX_RETRIES + 1} attempts: {e}')
            return None

    return None


def _update_transaction_function_args(
        write_cursor: 'DBCursor',
        tx_id: str,
        function_args: tuple[FunctionArg, ...],
) -> None:
    """Update a transaction's function_args and indexed columns in the DB."""
    # Create a minimal transaction object to use the extraction helper
    # We just need to extract indexed values from the args
    indexed = _extract_indexed_args_from_tuple(function_args)

    write_cursor.execute(
        """UPDATE stacks_transactions
           SET function_args = ?,
               arg_amount_ustx = ?,
               arg_recipient = ?,
               arg_delegate_to = ?
           WHERE tx_id = ?""",
        (
            json.dumps(list(function_args)),
            indexed['arg_amount_ustx'],
            indexed['arg_recipient'],
            indexed['arg_delegate_to'],
            tx_id,
        ),
    )


def _extract_indexed_args_from_tuple(
        function_args: tuple[FunctionArg, ...],
) -> dict[str, int | str | None]:
    """Extract indexed arg values from function_args tuple.

    Similar to DBStacksTx._extract_indexed_args but works with tuple directly.
    """
    from rotkehlchen.chain.stacks.clarity_parser import (
        get_principal_from_repr,
        get_uint_from_repr,
    )

    indexed: dict[str, int | str | None] = {
        'arg_amount_ustx': None,
        'arg_recipient': None,
        'arg_delegate_to': None,
    }

    for arg in function_args:
        name = arg.get('name', '')
        repr_str = arg.get('repr', '')

        # Extract amounts
        if (
            name in ('amount-ustx', 'increase-by', 'ustx') and
            indexed['arg_amount_ustx'] is None and
            (amount := get_uint_from_repr(repr_str)) is not None
        ):
            indexed['arg_amount_ustx'] = amount

        # Extract recipient
        if (
            name in ('recipient', 'to') and
            indexed['arg_recipient'] is None and
            (principal := get_principal_from_repr(repr_str)) is not None
        ):
            indexed['arg_recipient'] = principal

        # Extract delegate-to
        if (
            name == 'delegate-to' and
            indexed['arg_delegate_to'] is None and
            (principal := get_principal_from_repr(repr_str)) is not None
        ):
            indexed['arg_delegate_to'] = principal

    return indexed


@enter_exit_debug_log()
def data_migration_27(rotki: 'Rotkehlchen', progress_handler: 'MigrationProgressHandler') -> None:
    """Introduced with Stacks function_args support.

    Re-fetches Stacks contract call transactions to populate function_args column.
    """
    @progress_step(description='Populating Stacks transaction function arguments')
    def _populate_stacks_function_args(rotki: 'Rotkehlchen') -> None:
        import requests

        # Query transactions that need updating
        with rotki.data.db.conn.read_ctx() as cursor:
            cursor.execute(
                """SELECT tx_id FROM stacks_transactions
                   WHERE function_args IS NULL
                   AND tx_type = 'CONTRACT_CALL'
                   ORDER BY block_time DESC""",
            )
            tx_ids = [row[0] for row in cursor.fetchall()]

        if not tx_ids:
            log.info('No Stacks transactions need function_args population')
            return

        log.info(f'Populating function_args for {len(tx_ids)} Stacks transactions')

        # Create session for API requests
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

        updated_count = 0
        failed_count = 0

        # Process in batches
        for i in range(0, len(tx_ids), REFETCH_BATCH_SIZE):
            batch = tx_ids[i:i + REFETCH_BATCH_SIZE]

            for tx_id in batch:
                function_args = _fetch_transaction_from_api(session, tx_id)

                if function_args is not None:
                    with rotki.data.db.conn.write_ctx() as write_cursor:
                        _update_transaction_function_args(write_cursor, tx_id, function_args)
                    updated_count += 1
                else:
                    failed_count += 1

            # Delay between batches to be nice to the API
            if i + REFETCH_BATCH_SIZE < len(tx_ids):
                gevent.sleep(BATCH_DELAY)

        log.info(
            f'Stacks function_args migration complete: '
            f'{updated_count} updated, {failed_count} failed/skipped',
        )

    perform_userdb_migration_steps(rotki, progress_handler, should_vacuum=False)
