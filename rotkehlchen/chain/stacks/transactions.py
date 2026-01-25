"""Stacks transaction fetching and storage."""
import logging
from typing import TYPE_CHECKING, Final

from rotkehlchen.api.websockets.typedefs import (
    TransactionStatusStep,
    TransactionStatusSubType,
    WSMessageType,
)
from rotkehlchen.chain.stacks.types import (
    StacksTransaction,
    StacksTxStatus,
    StacksTxType,
)
from rotkehlchen.db.filtering import StacksTransactionsFilterQuery
from rotkehlchen.db.stackstx import DBStacksTx
from rotkehlchen.errors.misc import RemoteError
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.types import StacksAddress, SupportedBlockchain, Timestamp
from rotkehlchen.utils.misc import ts_now

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.node_inquirer import StacksInquirer
    from rotkehlchen.db.dbhandler import DBHandler

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)

# Maximum transactions to fetch per API request
TX_BATCH_SIZE: Final = 50


class StacksTransactions:
    """Fetches and stores Stacks transactions."""

    def __init__(
            self,
            node_inquirer: 'StacksInquirer',
            database: 'DBHandler',
    ) -> None:
        self.node_inquirer = node_inquirer
        self.database = database
        self.dbtx = DBStacksTx(database=database)

    def get_or_create_transaction(
            self,
            tx_id: str,
            relevant_address: StacksAddress | None = None,
    ) -> StacksTransaction | None:
        """Gets a transaction from the DB or from the API. If queried from API,
        it is also saved to the DB.

        May raise RemoteError if there is a problem with querying the API.
        """
        with self.database.conn.read_ctx() as cursor:
            if len(txs := self.dbtx.get_transactions(
                cursor=cursor,
                filter_=StacksTransactionsFilterQuery.make(tx_id=tx_id),
            )) == 1:
                return txs[0]

        # Transaction not in DB, fetch from API
        tx = self._fetch_transaction(tx_id)
        if tx is None:
            return None

        with self.database.conn.write_ctx() as write_cursor:
            self.dbtx.add_transactions(
                write_cursor=write_cursor,
                stacks_transactions=[tx],
                relevant_address=relevant_address,
            )

        return tx

    def _fetch_transaction(self, tx_id: str) -> StacksTransaction | None:
        """Fetch a single transaction from the API."""
        try:
            response = self.node_inquirer.api_client._make_request(
                f'extended/v1/tx/{tx_id}',
            )
        except RemoteError:
            log.error(f'Failed to fetch Stacks transaction {tx_id}')
            return None

        if not response:
            return None

        return self._parse_transaction(response)

    def _parse_transaction(self, tx_data: dict) -> StacksTransaction | None:
        """Parse a transaction from API response into StacksTransaction."""
        try:
            tx_id = tx_data.get('tx_id', '')
            block_height = tx_data.get('block_height', 0)
            block_time = tx_data.get('block_time', 0)
            if isinstance(block_time, str):
                # Handle ISO format timestamp
                from datetime import UTC, datetime
                block_time = int(datetime.fromisoformat(block_time).replace(
                    tzinfo=UTC,
                ).timestamp())

            tx_type_str = tx_data.get('tx_type', 'contract_call')
            tx_type = StacksTxType.deserialize(tx_type_str)

            sender = tx_data.get('sender_address', '')
            fee_rate = int(tx_data.get('fee_rate', 0))
            nonce = tx_data.get('nonce', 0)

            tx_status_str = tx_data.get('tx_status', 'success')
            tx_status = StacksTxStatus.deserialize(tx_status_str)

            # Parse type-specific fields
            recipient_address = None
            amount = None
            contract_id = None
            function_name = None

            if tx_type == StacksTxType.TOKEN_TRANSFER:
                token_transfer = tx_data.get('token_transfer', {})
                recipient_address = token_transfer.get('recipient_address')
                amount_str = token_transfer.get('amount', '0')
                amount = int(amount_str)
            elif tx_type == StacksTxType.CONTRACT_CALL:
                contract_call = tx_data.get('contract_call', {})
                contract_id = contract_call.get('contract_id')
                function_name = contract_call.get('function_name')

            return StacksTransaction(
                tx_id=tx_id,
                block_height=block_height,
                block_time=Timestamp(block_time),
                tx_type=tx_type,
                sender_address=StacksAddress(sender),
                fee_rate=fee_rate,
                nonce=nonce,
                tx_status=tx_status,
                recipient_address=StacksAddress(recipient_address) if recipient_address else None,
                amount=amount,
                contract_id=contract_id,
                function_name=function_name,
            )
        except (KeyError, ValueError, TypeError) as e:
            log.error(f'Failed to parse Stacks transaction: {e}')
            return None

    def _send_tx_status_message(
            self,
            address: StacksAddress,
            period: tuple[Timestamp, Timestamp],
            status: TransactionStatusStep,
    ) -> None:
        self.database.msg_aggregator.add_message(
            message_type=WSMessageType.TRANSACTION_STATUS,
            data={
                'address': address,
                'chain': SupportedBlockchain.STACKS.value,
                'subtype': str(TransactionStatusSubType.STACKS),
                'period': period,
                'status': str(status),
            },
        )

    def query_transactions_for_address(
            self,
            address: StacksAddress,
            from_ts: Timestamp | None = None,
            to_ts: Timestamp | None = None,
    ) -> None:
        """Query and save all transactions for an address.

        Args:
            address: The Stacks address to query
            from_ts: Optional start timestamp (filter after fetch)
            to_ts: Optional end timestamp (filter after fetch)
        """
        end_ts = to_ts or ts_now()
        start_ts = from_ts or Timestamp(0)

        self._send_tx_status_message(
            address=address,
            period=(start_ts, end_ts),
            status=TransactionStatusStep.QUERYING_TRANSACTIONS_STARTED,
        )

        # Get existing tx_ids to avoid re-fetching
        existing_tx_ids: set[str] = set()
        with self.database.conn.read_ctx() as cursor:
            cursor.execute(
                'SELECT DISTINCT S.tx_id FROM stackstx_address_mappings AS M '
                'INNER JOIN stacks_transactions AS S ON S.identifier = M.tx_id '
                'WHERE M.address = ?',
                (address,),
            )
            existing_tx_ids = {row[0] for row in cursor}

        # Fetch transactions with pagination
        offset = 0
        total_fetched = 0
        new_transactions: list[StacksTransaction] = []

        while True:
            try:
                response = self.node_inquirer.api_client.get_account_transactions(
                    address=address,
                    limit=TX_BATCH_SIZE,
                    offset=offset,
                )
            except RemoteError as e:
                log.error(f'Failed to fetch transactions for {address}: {e}')
                break

            results = response.get('results', [])
            if not results:
                break

            for tx_data in results:
                tx_id = tx_data.get('tx_id', '')
                if tx_id in existing_tx_ids:
                    continue  # Skip already stored transactions

                tx = self._parse_transaction(tx_data)
                if tx is None:
                    continue

                # Apply timestamp filtering
                if tx.block_time < start_ts or tx.block_time > end_ts:
                    continue

                new_transactions.append(tx)
                existing_tx_ids.add(tx_id)

            total_fetched += len(results)
            total_count = response.get('total', total_fetched)

            # Check if we've fetched all transactions
            if total_fetched >= total_count or len(results) < TX_BATCH_SIZE:
                break

            offset += TX_BATCH_SIZE

        # Save new transactions to database
        if new_transactions:
            with self.database.conn.write_ctx() as write_cursor:
                self.dbtx.add_transactions(
                    write_cursor=write_cursor,
                    stacks_transactions=new_transactions,
                    relevant_address=address,
                )
            log.debug(f'Saved {len(new_transactions)} new transactions for {address}')

        self._send_tx_status_message(
            address=address,
            period=(start_ts, end_ts),
            status=TransactionStatusStep.QUERYING_TRANSACTIONS_FINISHED,
        )
