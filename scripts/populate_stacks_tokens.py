#!/usr/bin/env python3
"""Script to populate the packaged global database with curated Stacks tokens.

This script adds Stacks tokens to rotkehlchen/data/global.db so that new installs
have the tokens available without needing a migration.

Usage:
    python scripts/populate_stacks_tokens.py
"""

import sqlite3
import sys
from pathlib import Path

# Add the project root to the path so we can import rotkehlchen modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rotkehlchen.assets.types import AssetType  # noqa: E402
from rotkehlchen.chain.stacks.constants import CURATED_STACKS_TOKENS  # noqa: E402
from rotkehlchen.constants.resolver import stacks_contract_to_identifier  # noqa: E402
from rotkehlchen.types import StacksAddress, TokenKind  # noqa: E402


def populate_stacks_tokens(db_path: Path) -> int:
    """Populate the database with curated Stacks tokens.

    Returns the number of tokens added.
    """
    stacks_type_char = AssetType.STACKS_TOKEN.serialize_for_db()
    token_kind_char = TokenKind.SIP10_FUNGIBLE.serialize_for_db()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    added_count = 0

    for contract_id, metadata in CURATED_STACKS_TOKENS.items():
        identifier = stacks_contract_to_identifier(
            contract_id=StacksAddress(contract_id),
            token_type=TokenKind.SIP10_FUNGIBLE,
        )

        # Check if token already exists
        cursor.execute('SELECT 1 FROM assets WHERE identifier = ?', (identifier,))
        if cursor.fetchone() is not None:
            print(f'  Skipping {metadata.symbol} (already exists)')
            continue

        # Insert into assets table
        cursor.execute(
            'INSERT INTO assets (identifier, type, name) VALUES (?, ?, ?)',
            (identifier, stacks_type_char, metadata.name),
        )

        # Insert into common_asset_details table
        cursor.execute(
            'INSERT INTO common_asset_details '
            '(identifier, symbol, coingecko, cryptocompare) VALUES (?, ?, ?, ?)',
            (identifier, metadata.symbol, metadata.coingecko, metadata.cryptocompare),
        )

        # Insert into stacks_tokens table
        cursor.execute(
            'INSERT INTO stacks_tokens '
            '(identifier, token_kind, contract_id, decimals, protocol) VALUES (?, ?, ?, ?, ?)',
            (identifier, token_kind_char, contract_id, metadata.decimals, metadata.protocol),
        )

        added_count += 1
        print(f'  Added {metadata.symbol} ({contract_id})')

    conn.commit()
    conn.close()

    return added_count


def main() -> None:
    packaged_db_path = project_root / 'rotkehlchen' / 'data' / 'global.db'

    if not packaged_db_path.exists():
        print(f'Error: Packaged database not found at {packaged_db_path}')
        sys.exit(1)

    print(f'Populating Stacks tokens in {packaged_db_path}')
    print(f'Total curated tokens: {len(CURATED_STACKS_TOKENS)}')
    print()

    added = populate_stacks_tokens(packaged_db_path)

    print()
    print(f'Done! Added {added} new Stacks tokens.')

    # Verify
    conn = sqlite3.connect(packaged_db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM stacks_tokens')
    total = cursor.fetchone()[0]
    conn.close()

    print(f'Total Stacks tokens in database: {total}')


if __name__ == '__main__':
    main()
