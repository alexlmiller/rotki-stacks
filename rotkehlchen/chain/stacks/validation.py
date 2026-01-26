"""Stacks address validation.

Stacks addresses use c32check encoding with the following format:
- Mainnet standard: SP prefix (version 22)
- Mainnet contract: SM prefix (version 26)
- Testnet standard: ST prefix (version 20)
- Format: 2-char prefix + c32 encoded data

The c32 alphabet is: 0123456789ABCDEFGHJKMNPQRSTVWXYZ
(excludes I, L, O, U to avoid visual confusion)
"""
from typing import Final

# c32 alphabet used in Stacks addresses
C32_ALPHABET: Final = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'

# Valid Stacks address prefixes
# SP = mainnet standard (version 22)
# SM = mainnet multisig/contract (version 26)
# ST = testnet standard (version 20)
# SN = testnet multisig/contract (version 21)
MAINNET_PREFIXES: Final = ('SP', 'SM')
TESTNET_PREFIXES: Final = ('ST', 'SN')
ALL_PREFIXES: Final = MAINNET_PREFIXES + TESTNET_PREFIXES

# Legacy constants for backwards compatibility
MAINNET_PREFIX: Final = 'SP'
TESTNET_PREFIX: Final = 'ST'

# Address length constraints (prefix + c32 encoded data)
# Standard addresses: 39-41 characters
# Contract addresses can be shorter (e.g., PoX contract)
MIN_ADDRESS_LENGTH: Final = 28
MAX_ADDRESS_LENGTH: Final = 41


def is_valid_stacks_address(address: object) -> bool:
    """Check if a string is a valid Stacks address.

    Validates:
    - Correct prefix (SP/SM for mainnet, ST/SN for testnet)
    - Proper length (28-41 characters)
    - All characters after prefix are in c32 alphabet (case-insensitive)

    Args:
        address: The address to validate (can be any type)

    Returns:
        True if the address is valid, False otherwise
    """
    if not isinstance(address, str):
        return False

    # Check length
    if len(address) < MIN_ADDRESS_LENGTH or len(address) > MAX_ADDRESS_LENGTH:
        return False

    # Check prefix (case-sensitive)
    has_valid_prefix = False
    for prefix in ALL_PREFIXES:
        if address.startswith(prefix):
            has_valid_prefix = True
            break

    if not has_valid_prefix:
        return False

    # Check that all characters after prefix are in c32 alphabet
    # Stacks addresses are uppercase
    address_body = address[2:]
    return all(char.upper() in C32_ALPHABET for char in address_body)
