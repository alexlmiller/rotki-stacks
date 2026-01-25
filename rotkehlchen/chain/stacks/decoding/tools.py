"""Stacks decoder tools for event creation and decoding utilities."""
import logging
from typing import TYPE_CHECKING, Any

from rotkehlchen.chain.decoding.tools import BaseDecoderTools
from rotkehlchen.chain.stacks.types import StacksTransaction
from rotkehlchen.errors.misc import RemoteError
from rotkehlchen.fval import FVal
from rotkehlchen.history.events.structures.stacks_event import StacksEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.types import StacksAddress, Timestamp
from rotkehlchen.utils.misc import ts_sec_to_ms

if TYPE_CHECKING:
    from rotkehlchen.assets.asset import Asset
    from rotkehlchen.chain.stacks.node_inquirer import StacksInquirer
    from rotkehlchen.db.dbhandler import DBHandler

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


class StacksDecoderTools(BaseDecoderTools[StacksTransaction, StacksAddress, str, StacksEvent]):
    """Decoder tools for creating Stacks events."""

    def __init__(
            self,
            database: 'DBHandler',
            node_inquirer: 'StacksInquirer',
    ) -> None:
        super().__init__(
            database=database,
            blockchain=node_inquirer.blockchain,
            address_is_exchange_fn=lambda x: None,
        )
        self.node_inquirer = node_inquirer

    def make_event(
            self,
            tx_ref: str,
            sequence_index: int,
            timestamp: Timestamp,
            event_type: HistoryEventType,
            event_subtype: HistoryEventSubType,
            asset: 'Asset',
            amount: FVal,
            location_label: str | None = None,
            notes: str | None = None,
            counterparty: str | None = None,
            address: StacksAddress | None = None,
            extra_data: dict[str, Any] | None = None,
    ) -> StacksEvent:
        """A convenience function to create a StacksEvent."""
        return StacksEvent(
            tx_ref=tx_ref,
            sequence_index=sequence_index,
            timestamp=ts_sec_to_ms(timestamp),
            event_type=event_type,
            event_subtype=event_subtype,
            asset=asset,
            amount=amount,
            location_label=location_label,
            notes=notes,
            counterparty=counterparty,
            address=address,
            extra_data=extra_data,
        )

    def get_stx_lock_amount(self, tx_id: str) -> int | None:
        """Fetch the STX lock amount from a transaction's stx_lock events.

        This requires fetching the full transaction details from the API
        since the list endpoint doesn't include events.

        Returns the locked_amount in micro-STX, or None if not found.
        """
        try:
            response = self.node_inquirer.api_client._make_request(
                f'extended/v1/tx/{tx_id}',
            )
        except RemoteError:
            log.error(f'Failed to fetch transaction {tx_id} for stx_lock amount')
            return None

        if not response:
            return None

        events = response.get('events', [])
        for event in events:
            if event.get('event_type') == 'stx_lock':
                stx_lock = event.get('stx_lock_event', {})
                locked_amount = stx_lock.get('locked_amount')
                if locked_amount is not None:
                    try:
                        return int(locked_amount)
                    except (ValueError, TypeError):
                        log.warning(f'Invalid locked_amount in tx {tx_id}: {locked_amount}')
                        return None

        return None
