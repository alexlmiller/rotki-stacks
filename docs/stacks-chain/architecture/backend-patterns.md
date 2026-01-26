# Backend Implementation Patterns

Patterns for manager, inquirer, transactions, database, and decoder classes.

---

## Node Inquirer

**File**: `rotkehlchen/chain/stacks/node_inquirer.py`

```python
import logging
import requests
from typing import TYPE_CHECKING, Any

from rotkehlchen.errors.misc import RemoteError
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.types import StacksAddress

if TYPE_CHECKING:
    from rotkehlchen.db.dbhandler import DBHandler
    from rotkehlchen.greenlets.manager import GreenletManager

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


class StacksInquirer:
    """Interface to Stacks blockchain via Hiro API."""

    def __init__(
            self,
            greenlet_manager: 'GreenletManager',
            database: 'DBHandler',
    ) -> None:
        self.greenlet_manager = greenlet_manager
        self.database = database
        self.api_url = 'https://api.mainnet.hiro.so'
        self.session = requests.Session()

    def _query(self, endpoint: str, params: dict | None = None) -> dict[str, Any]:
        """Make API query with error handling."""
        url = f'{self.api_url}{endpoint}'
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RemoteError(f'Stacks API error for {endpoint}: {e}') from e

    def get_stx_balance(self, address: StacksAddress) -> int:
        """Get STX balance in micro-STX."""
        data = self._query(f'/extended/v1/address/{address}/stx')
        return int(data.get('balance', 0))
```

---

## Chain Manager

**File**: `rotkehlchen/chain/stacks/manager.py`

```python
from collections import defaultdict
from collections.abc import Sequence
from typing import TYPE_CHECKING

from rotkehlchen.accounting.structures.balance import Balance, BalanceSheet
from rotkehlchen.chain.manager import ChainManagerWithTransactions
from rotkehlchen.constants import DEFAULT_BALANCE_LABEL
from rotkehlchen.constants.assets import A_STX
from rotkehlchen.constants.misc import ZERO
from rotkehlchen.inquirer import Inquirer
from rotkehlchen.types import StacksAddress, Timestamp

from .node_inquirer import StacksInquirer
from .transactions import StacksTransactions
from .utils import micro_stx_to_stx

if TYPE_CHECKING:
    from rotkehlchen.premium.premium import Premium


class StacksManager(ChainManagerWithTransactions[StacksAddress]):

    def __init__(
            self,
            node_inquirer: StacksInquirer,
            premium: 'Premium | None' = None,
    ) -> None:
        super().__init__()
        self.node_inquirer = node_inquirer
        self.database = node_inquirer.database
        self.transactions = StacksTransactions(
            node_inquirer=self.node_inquirer,
            database=self.database,
        )

    def get_multi_balance(
            self,
            accounts: Sequence[StacksAddress],
    ) -> dict[StacksAddress, FVal]:
        """Query STX balances for multiple accounts."""
        result: dict[StacksAddress, FVal] = {}
        for account in accounts:
            try:
                balance = self.node_inquirer.get_stx_balance(account)
                result[account] = micro_stx_to_stx(balance)
            except RemoteError as e:
                log.error(f'Failed to query balance for {account}: {e}')
                result[account] = ZERO
        return result

    def query_balances(
            self,
            addresses: Sequence[StacksAddress],
    ) -> dict[StacksAddress, BalanceSheet]:
        """Query all balances with USD values."""
        chain_balances: defaultdict[StacksAddress, BalanceSheet] = defaultdict(BalanceSheet)
        native_price = Inquirer.find_usd_price(A_STX)

        for account, balance in self.get_multi_balance(addresses).items():
            if balance != ZERO:
                chain_balances[account].assets[A_STX][DEFAULT_BALANCE_LABEL] = Balance(
                    amount=balance,
                    value=balance * native_price,
                )

        return dict(chain_balances)

    def query_transactions(
            self,
            addresses: list[StacksAddress],
            from_timestamp: Timestamp,
            to_timestamp: Timestamp,
    ) -> None:
        """Query transactions for addresses and save to DB."""
        for address in addresses:
            self.transactions.query_transactions_for_address(address=address)
```

---

## Database Handler

**File**: `rotkehlchen/db/stackstx.py`

```python
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.db.dbtx import DBCommonTx
from rotkehlchen.db.filtering import (
    StacksTransactionsFilterQuery,
    StacksTransactionsNotDecodedFilterQuery,
)
from rotkehlchen.types import StacksAddress

if TYPE_CHECKING:
    from rotkehlchen.db.drivers.gevent import DBCursor


class DBStacksTx(DBCommonTx[
    StacksAddress,
    StacksTransaction,
    str,  # TX hash type
    StacksTransactionsFilterQuery,
    StacksTransactionsNotDecodedFilterQuery,
]):
    """Database handler for Stacks transactions."""

    def add_transactions(
            self,
            write_cursor: 'DBCursor',
            transactions: list[StacksTransaction],
            relevant_address: StacksAddress,
    ) -> None:
        """Insert transactions into database."""
        for tx in transactions:
            tx_id = self.db.write_single_tuple(
                write_cursor=write_cursor,
                tuple_type='stacks_transaction',
                query='INSERT OR IGNORE INTO stacks_transactions '
                      '(tx_id, block_height, block_time, tx_type, sender_address, '
                      'fee_rate, nonce, tx_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                entry=(tx.tx_id, tx.block_height, tx.block_time, tx.tx_type,
                       tx.sender_address, tx.fee_rate, tx.nonce, tx.tx_status),
                relevant_address=relevant_address,
            )
            if tx_id is not None:
                write_cursor.execute(
                    'INSERT OR IGNORE INTO stackstx_address_mappings (tx_id, address) '
                    'VALUES (?, ?)',
                    (tx_id, relevant_address),
                )

    def deserialize_tx_hash_from_db(self, raw_tx_hash: bytes) -> str:
        return raw_tx_hash.decode()

    def _get_txs_not_decoded_column_and_query(self) -> tuple[str, str]:
        return (
            'tx_id',
            'stacks_transactions AS A LEFT JOIN stacks_tx_mappings AS B ON A.identifier = B.tx_id ',
        )
```

---

## Aggregator Integration

**File**: `rotkehlchen/chain/aggregator.py`

Add import:
```python
if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.manager import StacksManager
```

Add parameter to `__init__`:
```python
stacks_manager: 'StacksManager',
```

Add attribute:
```python
self.stacks = stacks_manager
```

Add overload:
```python
@overload
def get_chain_manager(
    self, blockchain: Literal[SupportedBlockchain.STACKS]
) -> 'StacksManager':
    ...
```

---

## Rotkehlchen Initialization

**File**: `rotkehlchen/rotkehlchen.py`

```python
from rotkehlchen.chain.stacks.manager import StacksManager
from rotkehlchen.chain.stacks.node_inquirer import StacksInquirer

# In _initialize_blockchain_aggregator():
stacks_manager=StacksManager(
    node_inquirer=StacksInquirer(
        greenlet_manager=self.greenlet_manager,
        database=self.data.db,
    ),
    premium=self.premium,
),
```

---

## DB Migration

**File**: `rotkehlchen/db/upgrades/v{N}_v{N+1}.py`

```python
from rotkehlchen.db.upgrade_manager import (
    enter_exit_debug_log,
    perform_userdb_upgrade_steps,
    progress_step,
)

@enter_exit_debug_log(name='UserDB v{N}->v{N+1} upgrade')
def upgrade_v{N}_to_v{N+1}(db: DBHandler, progress_handler: DBUpgradeProgressHandler) -> None:

    @progress_step(description='Creating Stacks transaction tables.')
    def _create_stacks_tables(write_cursor: DBCursor) -> None:
        write_cursor.executescript("""
            CREATE TABLE IF NOT EXISTS stacks_transactions (
                identifier INTEGER PRIMARY KEY NOT NULL,
                tx_id TEXT NOT NULL UNIQUE,
                block_height INTEGER NOT NULL,
                block_time INTEGER NOT NULL,
                tx_type TEXT NOT NULL,
                sender_address TEXT NOT NULL,
                fee_rate TEXT NOT NULL,
                nonce INTEGER NOT NULL,
                tx_status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS stackstx_address_mappings (
                tx_id INTEGER NOT NULL,
                address TEXT NOT NULL,
                PRIMARY KEY(tx_id, address),
                FOREIGN KEY(tx_id) REFERENCES stacks_transactions(identifier)
                    ON DELETE CASCADE ON UPDATE CASCADE
            );

            CREATE TABLE IF NOT EXISTS stacks_tx_mappings (
                tx_id INTEGER NOT NULL,
                value INTEGER NOT NULL,
                PRIMARY KEY(tx_id, value),
                FOREIGN KEY(tx_id) REFERENCES stacks_transactions(identifier)
                    ON DELETE CASCADE ON UPDATE CASCADE
            );
        """)

    perform_userdb_upgrade_steps(db=db, progress_handler=progress_handler, should_vacuum=True)
```

**Important**: Increment `ROTKEHLCHEN_DB_VERSION` in `rotkehlchen/db/settings.py`.

---

## WebSocket Status Messages

**File**: `rotkehlchen/api/websockets/typedefs.py`

```python
class TransactionStatusSubType(StrEnum):
    STACKS = auto()
```

Usage:
```python
self.database.msg_aggregator.add_message(
    message_type=WSMessageType.TRANSACTION_STATUS,
    data={
        'address': address,
        'chain': SupportedBlockchain.STACKS.value,
        'subtype': str(TransactionStatusSubType.STACKS),
        'period': (start_ts, end_ts),
        'status': str(TransactionStatusStep.QUERYING_TRANSACTIONS_STARTED),
    },
)
```
