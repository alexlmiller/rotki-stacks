import logging
from typing import TYPE_CHECKING

from rotkehlchen.logging import RotkehlchenLogsAdapter, enter_exit_debug_log
from rotkehlchen.utils.progress import perform_globaldb_upgrade_steps, progress_step

if TYPE_CHECKING:
    from rotkehlchen.db.drivers.gevent import DBConnection, DBCursor
    from rotkehlchen.db.upgrade_manager import DBUpgradeProgressHandler

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


@enter_exit_debug_log(name='globaldb v16->v17 upgrade')
def migrate_to_v17(
        connection: 'DBConnection',
        progress_handler: 'DBUpgradeProgressHandler',
) -> None:
    """This globalDB upgrade fixes Stacks token identifiers.

    The original migration (v15->v16) created identifiers with spaces in the token type
    (e.g., 'stacks/sip10 fungible:...') due to the enum's __str__ method. This migration
    corrects them to use underscores (e.g., 'stacks/sip10_fungible:...') to match the
    format expected by Colibri for icon lookups.

    This upgrade takes place in v1.43.0"""

    @progress_step('Fix Stacks token identifiers format')
    def _fix_stacks_identifiers(write_cursor: 'DBCursor') -> None:
        """Update all Stacks identifiers from 'sip10 fungible' to 'sip10_fungible'.

        If the correct format identifier already exists, we delete the old format entry.
        If not, we update the old format entry to the new format.

        We disable foreign key checks temporarily to avoid constraint failures during
        the updates, then re-enable and verify.
        """
        # Disable foreign key checks during migration
        write_cursor.execute('PRAGMA foreign_keys = OFF')

        # For sip10 fungible -> sip10_fungible
        # First delete old format entries where the correct format already exists
        # Order: stacks_tokens (child) -> common_asset_details -> assets (parent)
        for table in ('stacks_tokens', 'common_asset_details', 'assets'):
            write_cursor.execute(
                f"""
                DELETE FROM {table}
                WHERE identifier LIKE 'stacks/sip10 fungible:%'
                AND REPLACE(identifier, 'stacks/sip10 fungible:', 'stacks/sip10_fungible:')
                    IN (SELECT identifier FROM {table} WHERE identifier LIKE 'stacks/sip10_fungible:%')
                """,  # noqa: E501
            )
            log.debug(f'Deleted {write_cursor.rowcount} duplicate entries from {table}')

        # Now update remaining old format entries (those without a correct format counterpart)
        # Order: assets (parent) -> common_asset_details -> stacks_tokens (child)
        for table in ('assets', 'common_asset_details', 'stacks_tokens'):
            write_cursor.execute(
                f"""
                UPDATE {table}
                SET identifier = REPLACE(identifier, 'stacks/sip10 fungible:', 'stacks/sip10_fungible:')
                WHERE identifier LIKE 'stacks/sip10 fungible:%'
                """,  # noqa: E501
            )
            log.debug(f'Updated {write_cursor.rowcount} sip10_fungible identifiers in {table}')

        # For sip10 nft -> sip10_nft (same approach)
        for table in ('stacks_tokens', 'common_asset_details', 'assets'):
            write_cursor.execute(
                f"""
                DELETE FROM {table}
                WHERE identifier LIKE 'stacks/sip10 nft:%'
                AND REPLACE(identifier, 'stacks/sip10 nft:', 'stacks/sip10_nft:')
                    IN (SELECT identifier FROM {table} WHERE identifier LIKE 'stacks/sip10_nft:%')
                """,
            )

        for table in ('assets', 'common_asset_details', 'stacks_tokens'):
            write_cursor.execute(
                f"""
                UPDATE {table}
                SET identifier = REPLACE(identifier, 'stacks/sip10 nft:', 'stacks/sip10_nft:')
                WHERE identifier LIKE 'stacks/sip10 nft:%'
                """,
            )

        # Re-enable foreign key checks
        write_cursor.execute('PRAGMA foreign_keys = ON')

    perform_globaldb_upgrade_steps(connection, progress_handler, [_fix_stacks_identifiers])
