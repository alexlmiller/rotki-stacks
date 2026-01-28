"""Stacks blockchain types and data structures."""
from dataclasses import dataclass
from enum import auto
from typing import TYPE_CHECKING, TypedDict

from rotkehlchen.types import StacksAddress, Timestamp
from rotkehlchen.utils.mixins.enums import DBCharEnumMixIn

if TYPE_CHECKING:
    from rotkehlchen.chain.stacks.clarity_parser import ClarityValue
    from rotkehlchen.db.drivers.gevent import DBCursor


class FunctionArg(TypedDict):
    """A function argument from the Hiro API."""
    name: str
    type: str
    repr: str
    hex: str


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
    # Function arguments for contract calls (parsed from API response)
    function_args: tuple[FunctionArg, ...] | None = None
    memo: str | None = None  # Transaction memo (used by STX-20 protocol)
    db_id: int = -1

    def get_or_query_db_id(self, cursor: 'DBCursor') -> int:
        """Returns the DB identifier for the transaction.

        Raises:
            ValueError: If the transaction is not found in the database.
        """
        if self.db_id == -1:
            result = cursor.execute(
                'SELECT identifier FROM stacks_transactions WHERE tx_id=?',
                (self.tx_id,),
            ).fetchone()
            if result is None:
                raise ValueError(f'Stacks transaction {self.tx_id} not found in database')
            object.__setattr__(self, 'db_id', result[0])

        return self.db_id

    def get_arg(self, name: str) -> FunctionArg | None:
        """Get a function argument by name.

        Args:
            name: The argument name (e.g., 'amount-ustx', 'delegate-to')

        Returns:
            The FunctionArg dict if found, None otherwise
        """
        if self.function_args is None:
            return None
        for arg in self.function_args:
            if arg.get('name') == name:
                return arg
        return None

    def get_arg_repr(self, name: str) -> str | None:
        """Get the repr string for a function argument.

        Args:
            name: The argument name

        Returns:
            The repr string if found, None otherwise
        """
        arg = self.get_arg(name)
        if arg is None:
            return None
        return arg.get('repr')

    def get_arg_parsed(self, name: str) -> 'ClarityValue | None':
        """Get a parsed function argument value.

        Args:
            name: The argument name

        Returns:
            The parsed Clarity value, or None if not found or parsing fails
        """
        repr_str = self.get_arg_repr(name)
        if repr_str is None:
            return None

        from rotkehlchen.chain.stacks.clarity_parser import parse_clarity_repr_safe
        return parse_clarity_repr_safe(repr_str)

    def get_uint_arg(self, name: str) -> int | None:
        """Get a uint argument value.

        Convenience method for extracting uint values from function arguments.

        Args:
            name: The argument name (e.g., 'amount-ustx', 'increase-by')

        Returns:
            The integer value if found and valid, None otherwise
        """
        repr_str = self.get_arg_repr(name)
        if repr_str is None:
            return None

        from rotkehlchen.chain.stacks.clarity_parser import get_uint_from_repr
        return get_uint_from_repr(repr_str)

    def get_principal_arg(self, name: str) -> str | None:
        """Get a principal (address) argument value.

        Convenience method for extracting principal values from function arguments.

        Args:
            name: The argument name (e.g., 'delegate-to', 'recipient')

        Returns:
            The principal string if found and valid, None otherwise
        """
        repr_str = self.get_arg_repr(name)
        if repr_str is None:
            return None

        from rotkehlchen.chain.stacks.clarity_parser import get_principal_from_repr
        return get_principal_from_repr(repr_str)

    def __str__(self) -> str:
        return self.tx_id
