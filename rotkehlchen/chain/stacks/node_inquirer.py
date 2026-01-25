"""Stacks node inquirer for balance queries."""
import logging
from typing import TYPE_CHECKING

from rotkehlchen.chain.stacks.api_client import StacksApiClient
from rotkehlchen.chain.stacks.constants import micro_stx_to_stx
from rotkehlchen.errors.misc import RemoteError
from rotkehlchen.fval import FVal
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.types import StacksAddress, SupportedBlockchain

if TYPE_CHECKING:
    from rotkehlchen.db.dbhandler import DBHandler
    from rotkehlchen.greenlets.manager import GreenletManager

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


class StacksInquirer:
    """Inquirer for Stacks blockchain data via Hiro REST API.

    Unlike EVM chains which use RPC nodes, Stacks uses the Hiro REST API
    for all blockchain queries. This class does NOT inherit from RPCManagerMixin
    as there are no RPC nodes to manage.
    """

    def __init__(
            self,
            greenlet_manager: 'GreenletManager',
            database: 'DBHandler',
    ) -> None:
        """Initialize the Stacks inquirer.

        Args:
            greenlet_manager: The greenlet manager for async operations
            database: The database handler
        """
        self.greenlet_manager = greenlet_manager
        self.database = database
        self.blockchain = SupportedBlockchain.STACKS
        self.api_client = StacksApiClient(database=database)

    def get_stx_balance(self, address: StacksAddress) -> FVal:
        """Get the STX balance for an address.

        Args:
            address: The Stacks address to query

        Returns:
            The STX balance as FVal

        Raises:
            RemoteError: If the query fails
        """
        try:
            response = self.api_client.get_account_balances(address)
        except RemoteError:
            log.error(f'Failed to get STX balance for {address}')
            raise

        if not response:
            # Empty response means no balance data (new/empty address)
            return FVal(0)

        stx_data = response.get('stx', {})
        balance_str = stx_data.get('balance', '0')

        try:
            balance_micro = int(balance_str)
        except (ValueError, TypeError):
            log.error(f'Invalid STX balance response for {address}: {balance_str}')
            return FVal(0)

        return micro_stx_to_stx(balance_micro)

    def get_balances(self, address: StacksAddress) -> dict:
        """Get all balances for an address including STX and tokens.

        Args:
            address: The Stacks address to query

        Returns:
            Dictionary with all balance data from the API

        Raises:
            RemoteError: If the query fails
        """
        return self.api_client.get_account_balances(address)
