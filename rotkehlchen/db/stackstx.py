"""Database handler for Stacks transactions."""
import json
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import (
    FunctionArg,
    StacksTransaction,
    StacksTxStatus,
    StacksTxType,
)
from rotkehlchen.db.dbtx import DBCommonTx
from rotkehlchen.db.filtering import (
    StacksTransactionsFilterQuery,
    StacksTransactionsNotDecodedFilterQuery,
)
from rotkehlchen.db.history_events import DBHistoryEvents
from rotkehlchen.types import Location, StacksAddress, Timestamp

if TYPE_CHECKING:
    from rotkehlchen.db.drivers.gevent import DBCursor

log = logging.getLogger(__name__)


class DBStacksTx(DBCommonTx[StacksAddress, StacksTransaction, str, StacksTransactionsFilterQuery, StacksTransactionsNotDecodedFilterQuery]):  # noqa: E501
    """Database handler for Stacks transactions."""

    @staticmethod
    def _extract_indexed_args(tx: StacksTransaction) -> dict[str, str | None]:
        """Extract commonly-queried argument values for indexing.

        Returns a dict with keys: arg_amount_ustx, arg_recipient, arg_delegate_to
        All values are stored as TEXT to avoid SQLite integer overflow.
        """
        indexed: dict[str, str | None] = {
            'arg_amount_ustx': None,
            'arg_recipient': None,
            'arg_delegate_to': None,
        }

        # Extract amount from various arg names (store as string to avoid overflow)
        amount = (
            tx.get_uint_arg('amount-ustx') or
            tx.get_uint_arg('increase-by') or
            tx.get_uint_arg('ustx')
        )
        if amount is not None:
            indexed['arg_amount_ustx'] = str(amount)
        elif tx.get_arg('amount-ustx') is not None:
            log.warning(f'Failed to parse amount-ustx argument in tx {tx.tx_id}')
        elif tx.get_arg('increase-by') is not None:
            log.warning(f'Failed to parse increase-by argument in tx {tx.tx_id}')

        # Extract recipient
        recipient = tx.get_principal_arg('recipient') or tx.get_principal_arg('to')
        if recipient is not None:
            indexed['arg_recipient'] = recipient
        elif tx.get_arg('recipient') is not None:
            log.warning(f'Failed to parse recipient argument in tx {tx.tx_id}')

        # Extract delegate-to for stacking delegation
        if (delegate := tx.get_principal_arg('delegate-to')) is not None:
            indexed['arg_delegate_to'] = delegate
        elif tx.get_arg('delegate-to') is not None:
            log.warning(f'Failed to parse delegate-to argument in tx {tx.tx_id}')

        return indexed

    @staticmethod
    def _serialize_function_args(function_args: tuple[FunctionArg, ...] | None) -> str | None:
        """Serialize function_args to JSON for database storage."""
        if function_args is None:
            return None
        return json.dumps(list(function_args))

    @staticmethod
    def _deserialize_function_args(json_str: str | None) -> tuple[FunctionArg, ...] | None:
        """Deserialize function_args from JSON database storage."""
        if json_str is None:
            return None
        try:
            args_list = json.loads(json_str)
            return tuple(
                FunctionArg(
                    name=arg.get('name', ''),
                    type=arg.get('type', ''),
                    repr=arg.get('repr', ''),
                    hex=arg.get('hex', ''),
                )
                for arg in args_list
            )
        except (json.JSONDecodeError, TypeError, KeyError):
            return None

    def add_transactions(
            self,
            write_cursor: 'DBCursor',
            stacks_transactions: list[StacksTransaction],
            relevant_address: StacksAddress | None,
    ) -> None:
        """Add Stacks transactions to the database."""
        query = """
            INSERT OR IGNORE INTO stacks_transactions(
                tx_id, block_height, block_time, tx_type, sender_address,
                fee_rate, nonce, tx_status, recipient_address, amount,
                contract_id, function_name, function_args,
                arg_amount_ustx, arg_recipient, arg_delegate_to
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        for tx in stacks_transactions:
            # Extract indexed argument values
            indexed = self._extract_indexed_args(tx)

            if (tx_id := self.db.write_single_tuple(
                write_cursor=write_cursor,
                tuple_type='stacks_transaction',
                query=query,
                entry=(
                    tx.tx_id,
                    tx.block_height,
                    tx.block_time,
                    str(tx.tx_type),
                    tx.sender_address,
                    str(tx.fee_rate),
                    tx.nonce,
                    str(tx.tx_status),
                    tx.recipient_address,
                    str(tx.amount) if tx.amount is not None else None,
                    tx.contract_id,
                    tx.function_name,
                    self._serialize_function_args(tx.function_args),
                    indexed['arg_amount_ustx'],
                    indexed['arg_recipient'],
                    indexed['arg_delegate_to'],
                ),
                relevant_address=relevant_address,
            )) is None:
                continue

            # Add address mapping for the sender
            write_cursor.execute(
                'INSERT OR IGNORE INTO stackstx_address_mappings(tx_id, address) VALUES (?, ?)',
                (tx_id, tx.sender_address),
            )
            # Add mapping for recipient if present
            if tx.recipient_address is not None:
                write_cursor.execute(
                    'INSERT OR IGNORE INTO stackstx_address_mappings(tx_id, address) '
                    'VALUES (?, ?)',
                    (tx_id, tx.recipient_address),
                )

    def get_transactions(
            self,
            cursor: 'DBCursor',
            filter_: StacksTransactionsFilterQuery,
    ) -> list[StacksTransaction]:
        """Get Stacks transactions from the database with filtering."""
        query, bindings = filter_.prepare()
        return [
            StacksTransaction(
                tx_id=row[1],
                block_height=row[2],
                block_time=Timestamp(row[3]),
                tx_type=StacksTxType.deserialize(row[4]),
                sender_address=StacksAddress(row[5]),
                fee_rate=int(row[6]),
                nonce=row[7],
                tx_status=StacksTxStatus.deserialize(row[8]),
                recipient_address=StacksAddress(row[9]) if row[9] else None,
                amount=int(row[10]) if row[10] else None,
                contract_id=row[11],
                function_name=row[12],
                function_args=self._deserialize_function_args(row[13]),
                db_id=row[0],
            )
            for row in cursor.execute(
                f'SELECT identifier, tx_id, block_height, block_time, tx_type, '
                f'sender_address, fee_rate, nonce, tx_status, recipient_address, '
                f'amount, contract_id, function_name, function_args '
                f'FROM stacks_transactions {query}',
                bindings,
            )
        ]

    def deserialize_tx_hash_from_db(self, raw_tx_hash: bytes) -> str:
        """Stacks tx hashes are stored as text, not bytes."""
        return raw_tx_hash.decode() if isinstance(raw_tx_hash, bytes) else str(raw_tx_hash)

    def _get_txs_not_decoded_column_and_query(self) -> tuple[str, str]:
        return (
            'A.tx_id',
            (
                'stacks_transactions AS A LEFT JOIN stacks_tx_mappings AS B '
                'ON A.identifier = B.tx_id '
            ),
        )

    def get_existing_tx_ids(
            self,
            cursor: 'DBCursor',
            tx_ids: list[str],
    ) -> set[str]:
        """Get tx_ids that already exist in the database."""
        if not tx_ids:
            return set()

        placeholders = ','.join('?' * len(tx_ids))
        cursor.execute(
            f'SELECT tx_id FROM stacks_transactions WHERE tx_id IN ({placeholders})',
            tx_ids,
        )
        return {row[0] for row in cursor}

    def delete_transaction_data(
            self,
            write_cursor: 'DBCursor',
            tx_id: str | None = None,
    ) -> None:
        """Deletes Stacks transactions from the DB. If tx_id is given, only deletes
        the transaction with that ID.
        """
        query = 'DELETE FROM stacks_transactions'
        bindings: list[str] = []
        if tx_id is not None:
            query += ' WHERE tx_id = ?'
            bindings.append(tx_id)

        write_cursor.execute(query, bindings)

    def count_transactions_in_range(
            self,
            from_ts: Timestamp,
            to_ts: Timestamp,
    ) -> int:
        """Return the number of transactions between from_ts and to_ts."""
        with self.db.conn.read_ctx() as cursor:
            return cursor.execute(
                'SELECT COUNT(*) FROM stacks_transactions WHERE block_time BETWEEN ? AND ?',
                (from_ts, to_ts),
            ).fetchone()[0]

    def delete_data_for_address(
            self,
            write_cursor: 'DBCursor',
            address: StacksAddress,
    ) -> None:
        """Deletes all Stacks transactions and their related data for a given address."""
        # Get transactions that are only associated with this address
        where_str = """
        WHERE M.address = ?
        AND M.tx_id NOT IN (SELECT tx_id FROM stackstx_address_mappings WHERE address != ?)
        """
        results = write_cursor.execute(
            'SELECT DISTINCT S.tx_id FROM stackstx_address_mappings AS M '
            f'INNER JOIN stacks_transactions AS S ON S.identifier = M.tx_id {where_str}',
            (address, address),
        ).fetchall()

        if not results:
            return  # No transactions that are only for this address

        DBHistoryEvents(self.db).delete_events_by_tx_ref(
            write_cursor=write_cursor,
            tx_refs=[row[0] for row in results],
            location=Location.STACKS,
        )
        write_cursor.execute(
            'DELETE FROM stacks_transactions WHERE identifier IN ('
            f'SELECT DISTINCT tx_id FROM stackstx_address_mappings AS M {where_str})',
            (address, address),
        )
