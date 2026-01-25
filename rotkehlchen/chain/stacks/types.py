"""Stacks blockchain types and data structures."""
from dataclasses import dataclass
from enum import auto
from typing import TYPE_CHECKING

from rotkehlchen.types import StacksAddress, Timestamp
from rotkehlchen.utils.mixins.enums import DBCharEnumMixIn

if TYPE_CHECKING:
    from rotkehlchen.db.drivers.gevent import DBCursor


class StacksTxType(DBCharEnumMixIn):
    """Stacks transaction types as returned by the Hiro API."""
    TOKEN_TRANSFER = auto()
    CONTRACT_CALL = auto()
    SMART_CONTRACT = auto()
    COINBASE = auto()
    POISON_MICROBLOCK = auto()
    TENURE_CHANGE = auto()

    @classmethod
    def deserialize(cls, value: str) -> 'StacksTxType':
        """Deserialize a transaction type from API string format."""
        try:
            return cls[value.upper()]
        except KeyError:
            # Default to CONTRACT_CALL for unknown types
            return cls.CONTRACT_CALL


class StacksTxStatus(DBCharEnumMixIn):
    """Stacks transaction status."""
    SUCCESS = auto()
    ABORT_BY_RESPONSE = auto()
    ABORT_BY_POST_CONDITION = auto()
    PENDING = auto()

    @classmethod
    def deserialize(cls, value: str) -> 'StacksTxStatus':
        """Deserialize a transaction status from API string format."""
        try:
            return cls[value.upper()]
        except KeyError:
            # Default to SUCCESS for unknown statuses
            return cls.SUCCESS


@dataclass(frozen=True)
class StacksTransaction:
    """Represent a Stacks transaction."""
    tx_id: str  # Transaction hash (0x prefixed hex string)
    block_height: int  # Block number where transaction was included
    block_time: Timestamp  # Unix timestamp when block was created
    tx_type: StacksTxType  # Transaction type (token_transfer, contract_call, etc.)
    sender_address: StacksAddress  # Address that initiated the transaction
    fee_rate: int  # Transaction fee in microSTX
    nonce: int  # Transaction nonce for the sender
    tx_status: StacksTxStatus  # Transaction execution status
    # Optional fields for specific transaction types
    recipient_address: StacksAddress | None = None  # For token transfers
    amount: int | None = None  # Amount in microSTX/tokens for transfers
    contract_id: str | None = None  # For contract calls
    function_name: str | None = None  # For contract calls
    db_id: int = -1

    def get_or_query_db_id(self, cursor: 'DBCursor') -> int:
        """Returns the DB identifier for the transaction. Assumes it exists in the DB."""
        if self.db_id == -1:
            db_id = cursor.execute(
                'SELECT identifier FROM stacks_transactions WHERE tx_id=?',
                (self.tx_id,),
            ).fetchone()[0]
            object.__setattr__(self, 'db_id', db_id)

        return self.db_id

    def __str__(self) -> str:
        return self.tx_id
