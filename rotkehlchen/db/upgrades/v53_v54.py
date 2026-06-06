"""Database upgrade from v53 to v54.

This upgrade adds Stacks blockchain support tables.
"""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.logging import RotkehlchenLogsAdapter, enter_exit_debug_log
from rotkehlchen.utils.progress import perform_userdb_upgrade_steps, progress_step

if TYPE_CHECKING:
    from rotkehlchen.db.dbhandler import DBHandler
    from rotkehlchen.db.drivers.gevent import DBCursor
    from rotkehlchen.db.upgrade_manager import DBUpgradeProgressHandler

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


@enter_exit_debug_log(name='UserDB v53->v54 upgrade')
def upgrade_v53_to_v54(db: 'DBHandler', progress_handler: 'DBUpgradeProgressHandler') -> None:
    """Upgrades the DB from v53 to v54. This adds Stacks blockchain support."""

    @progress_step(description='Adding Stacks location to the DB.')
    def _add_stacks_location(write_cursor: 'DBCursor') -> None:
        write_cursor.executescript("""
        /* Stacks */
        INSERT OR IGNORE INTO location(location, seq) VALUES ('|', 60);
        """)

    @progress_step(description='Creating Stacks transaction tables.')
    def _create_stacks_tables(write_cursor: 'DBCursor') -> None:
        """Create the Stacks blockchain tables."""
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
            tx_status TEXT NOT NULL,
            recipient_address TEXT,
            amount TEXT,
            contract_id TEXT,
            function_name TEXT,
            function_args TEXT,
            arg_amount_ustx TEXT,
            arg_recipient TEXT,
            arg_delegate_to TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_stacks_tx_contract_function
            ON stacks_transactions(contract_id, function_name);
        CREATE INDEX IF NOT EXISTS idx_stacks_tx_arg_amount
            ON stacks_transactions(arg_amount_ustx) WHERE arg_amount_ustx IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_stacks_tx_arg_recipient
            ON stacks_transactions(arg_recipient) WHERE arg_recipient IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_stacks_tx_arg_delegate
            ON stacks_transactions(arg_delegate_to) WHERE arg_delegate_to IS NOT NULL;

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
            FOREIGN KEY(tx_id) REFERENCES stacks_transactions(identifier)
                ON UPDATE CASCADE ON DELETE CASCADE,
            PRIMARY KEY (tx_id, value)
        );
        """)

    perform_userdb_upgrade_steps(db=db, progress_handler=progress_handler, should_vacuum=False)
