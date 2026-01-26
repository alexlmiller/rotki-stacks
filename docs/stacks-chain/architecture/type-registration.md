# Type Registration Guide

Complete checklist for registering Stacks in `rotkehlchen/types.py`.

**Status**: Phase 1 complete - all items below are implemented.

---

## 1. Address Type

```python
# Near SolanaAddress definition
T_StacksAddress = str
StacksAddress = NewType('StacksAddress', T_StacksAddress)
```

---

## 2. BlockchainAddress Union

```python
BlockchainAddress = BTCAddress | ... | SolanaAddress | StacksAddress
```

---

## 3. AnyBlockchainAddress TypeVar

```python
AnyBlockchainAddress = TypeVar(
    'AnyBlockchainAddress',
    ...,
    SolanaAddress,
    StacksAddress,
)
```

---

## 4. ChainType Enum

```python
class ChainType(SerializableEnumNameMixin):
    STACKS = auto()
```

Add to `type_to_blockchains()`:
```python
if self == ChainType.STACKS:
    return [SupportedBlockchain.STACKS]
```

---

## 5. SupportedBlockchain Enum

```python
class SupportedBlockchain(SerializableEnumValueMixin):
    STACKS = 'STX'
```

Add to methods:
```python
# get_native_token_id()
if self == SupportedBlockchain.STACKS:
    return 'STX'

# get_chain_type()
if self == SupportedBlockchain.STACKS:
    return ChainType.STACKS

# get_address_chain_group()
if self == SupportedBlockchain.STACKS:
    return ChainType.STACKS
```

---

## 6. Display Mappings

```python
SUPPORTED_BLOCKCHAIN_NAMES_MAPPING = {
    SupportedBlockchain.STACKS: 'Stacks',
}

SUPPORTED_BLOCKCHAIN_IMAGE_NAME_MAPPING = {
    SupportedBlockchain.STACKS: 'stacks.svg',
}
```

---

## 7. Transaction Type Unions

```python
OTHER_CHAINS_WITH_TRANSACTIONS_TYPE = Literal[
    SupportedBlockchain.BITCOIN,
    SupportedBlockchain.BITCOIN_CASH,
    SupportedBlockchain.SOLANA,
    SupportedBlockchain.STACKS,
]
```

---

## 8. Chain Manager Union

```python
CHAINS_WITH_CHAIN_MANAGER: tuple[...] = (
    ...,
    SupportedBlockchain.STACKS,
)
```

---

## 9. Location Enum

```python
class Location(DBCharEnumMixIn):
    STACKS = 57  # Next after AVALANCHE = 56
```

Add to `from_chain()`:
```python
case SupportedBlockchain.STACKS:
    return Location.STACKS
```

---

## 10. Location Type Unions

```python
BLOCKCHAIN_LOCATIONS_TYPE = Literal[..., Location.STACKS]
BLOCKCHAIN_LOCATIONS: tuple[BLOCKCHAIN_LOCATIONS_TYPE, ...] = (
    ...,
    Location.STACKS,
)
```

---

## 11. AddressbookEntry Validation

In `check_chain_ecosystem()`:
```python
from rotkehlchen.chain.stacks.validation import is_valid_stacks_address

if is_valid_stacks_address(address=address):
    return ChainType.STACKS
```

---

## 12. TokenKind Enum

```python
class TokenKind(DBCharEnumMixIn):
    SIP10_FUNGIBLE = auto()
    SIP10_NFT = auto()

STACKS_TOKEN_KINDS_TYPE = Literal[TokenKind.SIP10_FUNGIBLE, TokenKind.SIP10_NFT]
STACKS_TOKEN_KINDS: tuple[STACKS_TOKEN_KINDS_TYPE, ...] = typing.get_args(STACKS_TOKEN_KINDS_TYPE)
```

---

## Verification

After all changes, verify:
```python
>>> from rotkehlchen.types import SupportedBlockchain, Location
>>> SupportedBlockchain.STACKS.serialize()
'stx'
>>> str(SupportedBlockchain.STACKS)
'Stacks'
>>> Location.STACKS.value
57
```
