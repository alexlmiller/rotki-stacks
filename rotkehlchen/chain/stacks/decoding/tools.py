"""Stacks decoder tools for event creation and decoding utilities."""
import logging
from typing import TYPE_CHECKING, Any

from rotkehlchen.chain.decoding.tools import BaseDecoderTools
from rotkehlchen.chain.stacks.types import StacksTransaction
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
