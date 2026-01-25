"""Stacks blockchain manager."""
import logging
from collections import defaultdict
from collections.abc import Sequence
from typing import TYPE_CHECKING

from rotkehlchen.accounting.structures.balance import Balance, BalanceSheet
from rotkehlchen.chain.manager import ChainManagerWithTransactions
from rotkehlchen.chain.stacks.constants import micro_stx_to_stx
from rotkehlchen.chain.stacks.node_inquirer import StacksInquirer
from rotkehlchen.constants import DEFAULT_BALANCE_LABEL
from rotkehlchen.constants.assets import A_STX
from rotkehlchen.errors.misc import RemoteError
from rotkehlchen.inquirer import Inquirer
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.types import StacksAddress, Timestamp

if TYPE_CHECKING:
    from rotkehlchen.premium.premium import Premium

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


class StacksManager(ChainManagerWithTransactions[StacksAddress]):
    """Manager for Stacks blockchain operations.

    Handles balance queries and transaction fetching for Stacks addresses.
    Uses the Hiro REST API through StacksInquirer.
    """

    def __init__(
            self,
            node_inquirer: StacksInquirer,
            premium: 'Premium | None' = None,
    ) -> None:
        """Initialize the Stacks manager.

        Args:
            node_inquirer: The Stacks node inquirer for API queries
            premium: Optional premium subscription for extended features
        """
        self.node_inquirer = node_inquirer
        self.database = node_inquirer.database
        self.premium = premium

    def query_balances(
            self,
            addresses: Sequence[StacksAddress],
    ) -> dict[StacksAddress, BalanceSheet]:
        """Query the balances of the given addresses.

        Args:
            addresses: List of Stacks addresses to query

        Returns:
            Dictionary mapping addresses to their balance sheets

        May raise RemoteError if there is a problem with querying the API.
        """
        chain_balances: defaultdict[StacksAddress, BalanceSheet] = defaultdict(BalanceSheet)

        if not addresses:
            return dict(chain_balances)

        stx_price = Inquirer.find_main_currency_price(A_STX)

        for address in addresses:
            try:
                response = self.node_inquirer.get_balances(address)
            except RemoteError as e:
                log.error(f'Failed to query Stacks balances for {address}: {e}')
                continue

            if not response:
                continue

            # Get STX balance
            stx_data = response.get('stx', {})
            balance_str = stx_data.get('balance', '0')

            try:
                balance_micro = int(balance_str)
            except (ValueError, TypeError):
                log.error(f'Invalid STX balance for {address}: {balance_str}')
                continue

            if balance_micro > 0:
                balance = micro_stx_to_stx(balance_micro)
                chain_balances[address].assets[A_STX][DEFAULT_BALANCE_LABEL] = Balance(
                    amount=balance,
                    value=balance * stx_price,
                )

            # Phase 3 will add SIP-10 fungible/non-fungible token balance queries

        return dict(chain_balances)

    def query_transactions(
            self,
            addresses: list[StacksAddress],
            from_timestamp: Timestamp,
            to_timestamp: Timestamp,
    ) -> None:
        """Query and save transactions for the given addresses.

        Args:
            addresses: List of Stacks addresses to query
            from_timestamp: Start of time range
            to_timestamp: End of time range

        Note:
            Transaction support will be added in Phase 4.
            Currently this is a no-op placeholder.
        """
        # TODO: Phase 4 will implement transaction querying
        log.debug(
            f'Stacks transaction query called for {len(addresses)} addresses '
            f'(not yet implemented)',
        )
