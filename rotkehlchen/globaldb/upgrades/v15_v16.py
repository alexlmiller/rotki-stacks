import logging
from typing import TYPE_CHECKING

from rotkehlchen.assets.types import AssetType
from rotkehlchen.chain.stacks.constants import CURATED_STACKS_TOKENS
from rotkehlchen.constants.resolver import stacks_contract_to_identifier
from rotkehlchen.logging import RotkehlchenLogsAdapter, enter_exit_debug_log
from rotkehlchen.types import StacksAddress, TokenKind
from rotkehlchen.utils.progress import perform_globaldb_upgrade_steps, progress_step

if TYPE_CHECKING:
    from rotkehlchen.db.drivers.gevent import DBConnection, DBCursor
    from rotkehlchen.db.upgrade_manager import DBUpgradeProgressHandler

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


@enter_exit_debug_log(name='globaldb v15->v16 upgrade')
def migrate_to_v16(connection: 'DBConnection', progress_handler: 'DBUpgradeProgressHandler') -> None:  # noqa: E501
    """This globalDB upgrade adds Stacks blockchain support to the database.

    - Adds token_kinds for Stacks SIP-10 tokens (F=fungible, G=NFT)
    - Creates stacks_tokens table
    - Populates stacks_tokens table with well-known SIP-10 tokens
    - Adds corresponding entries to assets and common_asset_details tables
    - Sets swapped_for on STX-2 (Blockstack) to point to STX (Stacks)

    This upgrade takes place in v1.43.0"""

    @progress_step('Add Stacks token kinds to token_kinds table')
    def _add_stacks_token_kinds(write_cursor: 'DBCursor') -> None:
        """Add token kinds F (SIP10_FUNGIBLE) and G (SIP10_NFT) for Stacks."""
        write_cursor.execute("""
            /* SIP10 FUNGIBLE (Stacks) */
            INSERT OR IGNORE INTO token_kinds(token_kind, seq) VALUES ('F', 6);
            /* SIP10 NFT (Stacks) */
            INSERT OR IGNORE INTO token_kinds(token_kind, seq) VALUES ('G', 7);
        """)
        log.debug('Added Stacks token kinds F and G to token_kinds table')

    @progress_step('Create stacks_tokens table')
    def _create_stacks_tokens_table(write_cursor: 'DBCursor') -> None:
        """Create the stacks_tokens table for Stacks SIP-10 tokens."""
        write_cursor.execute("""
        CREATE TABLE IF NOT EXISTS stacks_tokens (
            identifier TEXT PRIMARY KEY NOT NULL COLLATE NOCASE,
            token_kind CHAR(1) NOT NULL DEFAULT('F') REFERENCES token_kinds(token_kind),
            contract_id TEXT NOT NULL,
            decimals INTEGER,
            protocol TEXT,
            FOREIGN KEY(identifier) REFERENCES assets(identifier)
                ON UPDATE CASCADE ON DELETE CASCADE
        )""")
        write_cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_stacks_tokens_identifier '
            'ON stacks_tokens (identifier, protocol);',
        )
        log.debug('Created stacks_tokens table')

    @progress_step('Populate stacks_tokens table with curated tokens')
    def _populate_stacks_tokens(write_cursor: 'DBCursor') -> None:
        """Add curated Stacks tokens from constants to the database."""
        stacks_type_char = AssetType.STACKS_TOKEN.serialize_for_db()
        token_kind_char = TokenKind.SIP10_FUNGIBLE.serialize_for_db()

        assets_data: list[tuple[str, str, str]] = []
        details_data: list[tuple[str, str, str | None, str | None]] = []
        tokens_data: list[tuple[str, str, str, int | None, str | None]] = []

        for contract_id, metadata in CURATED_STACKS_TOKENS.items():
            identifier = stacks_contract_to_identifier(
                contract_id=StacksAddress(contract_id),
                token_type=TokenKind.SIP10_FUNGIBLE,
            )

            assets_data.append((
                identifier,
                stacks_type_char,
                metadata.name,
            ))
            details_data.append((
                identifier,
                metadata.symbol,
                metadata.coingecko,
                metadata.cryptocompare,
            ))
            tokens_data.append((
                identifier,
                token_kind_char,
                contract_id,
                metadata.decimals,
                metadata.protocol,
            ))

        # Use INSERT OR IGNORE to handle any tokens already added manually
        write_cursor.executemany(
            'INSERT OR IGNORE INTO assets (identifier, type, name) VALUES (?, ?, ?)',
            assets_data,
        )
        write_cursor.executemany(
            'INSERT OR IGNORE INTO common_asset_details '
            '(identifier, symbol, coingecko, cryptocompare) VALUES (?, ?, ?, ?)',
            details_data,
        )
        write_cursor.executemany(
            'INSERT OR IGNORE INTO stacks_tokens '
            '(identifier, token_kind, contract_id, decimals, protocol) VALUES (?, ?, ?, ?, ?)',
            tokens_data,
        )

        log.debug(f'Added {len(CURATED_STACKS_TOKENS)} curated Stacks tokens to the database')

    @progress_step('Update STX-2 (Blockstack) to point to STX (Stacks)')
    def _update_stx_swapped_for(write_cursor: 'DBCursor') -> None:
        """Set swapped_for on STX-2 (Blockstack) to point to STX (Stacks).

        The old Blockstack asset (STX-2) was renamed to Stacks (STX). This ensures
        that any exchange balances or historical data referencing STX-2 will be
        consolidated with the new STX asset.
        """
        write_cursor.execute(
            'UPDATE common_asset_details SET swapped_for=? WHERE identifier=?',
            ('STX', 'STX-2'),
        )
        log.debug('Updated STX-2 (Blockstack) swapped_for to point to STX (Stacks)')

    perform_globaldb_upgrade_steps(connection, progress_handler)
