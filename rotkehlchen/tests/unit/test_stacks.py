"""Tests for Stacks blockchain types and validation - Phase 1."""
from rotkehlchen.chain.stacks.validation import (
    ALL_PREFIXES,
    C32_ALPHABET,
    MAINNET_PREFIX,
    MAINNET_PREFIXES,
    TESTNET_PREFIX,
    TESTNET_PREFIXES,
    is_valid_stacks_address,
)
from rotkehlchen.constants.assets import A_STX
from rotkehlchen.types import (
    BLOCKCHAIN_LOCATIONS,
    CHAINS_WITH_CHAIN_MANAGER,
    STACKS_TOKEN_KINDS,
    AddressbookEntry,
    ChainType,
    Location,
    StacksAddress,
    SupportedBlockchain,
    TokenKind,
)


class TestStacksAddressValidation:
    """Tests for Stacks address validation."""

    def test_valid_mainnet_addresses(self) -> None:
        """Test that valid mainnet addresses are accepted."""
        valid_addresses = [
            'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7',
            'SP000000000000000000002Q6VF78',  # PoX contract address (shorter)
            'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9',  # sBTC registry
            'SM3KNVZS30WM7F89SXKVVFY4SN9RMPZZ9FX929N0V',  # LISA contract (SM prefix)
        ]
        for address in valid_addresses:
            assert is_valid_stacks_address(address), f'Expected {address} to be valid'

    def test_valid_testnet_addresses(self) -> None:
        """Test that valid testnet addresses are accepted."""
        valid_addresses = [
            'ST2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRVF5T9',
            'ST000000000000000000002AMW42H',  # Testnet PoX
        ]
        for address in valid_addresses:
            assert is_valid_stacks_address(address), f'Expected {address} to be valid'

    def test_invalid_prefix(self) -> None:
        """Test that addresses with invalid prefixes are rejected."""
        invalid_addresses = [
            'SX2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7',  # SX prefix
            'AB2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7',  # AB prefix
            '0x2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7',  # EVM-style prefix
        ]
        for address in invalid_addresses:
            assert not is_valid_stacks_address(address), f'Expected {address} to be invalid'

    def test_invalid_length(self) -> None:
        """Test that addresses with invalid length are rejected."""
        invalid_addresses = [
            'SP123',  # Too short
            'SP12',  # Way too short
            '',  # Empty
            'SP' + 'A' * 50,  # Too long
        ]
        for address in invalid_addresses:
            assert not is_valid_stacks_address(address), f'Expected {address} to be invalid'

    def test_invalid_c32_characters(self) -> None:
        """Test that addresses with invalid c32 characters are rejected.

        c32 alphabet excludes: I, L, O, U (to avoid visual confusion)
        """
        # Replace valid characters with excluded ones
        base_address = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7'
        for invalid_char in ['I', 'L', 'O', 'U']:
            # Replace a character with an invalid one
            invalid_address = base_address[:5] + invalid_char + base_address[6:]
            assert not is_valid_stacks_address(invalid_address), \
                f'Expected address with {invalid_char} to be invalid'

    def test_non_string_input(self) -> None:
        """Test that non-string inputs are rejected."""
        assert not is_valid_stacks_address(None)  # type: ignore
        assert not is_valid_stacks_address(12345)  # type: ignore
        assert not is_valid_stacks_address(['SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7'])  # type: ignore

    def test_c32_alphabet_completeness(self) -> None:
        """Test that the c32 alphabet is correct."""
        expected = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
        assert expected == C32_ALPHABET
        assert 'I' not in C32_ALPHABET
        assert 'L' not in C32_ALPHABET
        assert 'O' not in C32_ALPHABET
        assert 'U' not in C32_ALPHABET

    def test_prefix_constants(self) -> None:
        """Test that prefix constants are correct."""
        assert MAINNET_PREFIX == 'SP'
        assert TESTNET_PREFIX == 'ST'
        assert MAINNET_PREFIXES == ('SP', 'SM')
        assert TESTNET_PREFIXES == ('ST', 'SN')
        assert ALL_PREFIXES == ('SP', 'SM', 'ST', 'SN')


class TestStacksTypeRegistration:
    """Tests for Stacks type registration in rotkehlchen.types."""

    def test_supported_blockchain_enum(self) -> None:
        """Test that STACKS is properly registered in SupportedBlockchain."""
        assert hasattr(SupportedBlockchain, 'STACKS')
        assert SupportedBlockchain.STACKS.value == 'STX'
        assert str(SupportedBlockchain.STACKS) == 'Stacks'
        assert SupportedBlockchain.STACKS.serialize() == 'stx'

    def test_location_enum(self) -> None:
        """Test that STACKS is properly registered in Location."""
        assert hasattr(Location, 'STACKS')
        assert Location.STACKS.value == 57  # After AVALANCHE = 56
        assert Location.STACKS in BLOCKCHAIN_LOCATIONS

    def test_chain_type_enum(self) -> None:
        """Test that STACKS is properly registered in ChainType."""
        assert hasattr(ChainType, 'STACKS')
        assert SupportedBlockchain.STACKS.get_chain_type() == ChainType.STACKS

    def test_token_kinds(self) -> None:
        """Test that SIP10 token kinds are properly registered."""
        assert hasattr(TokenKind, 'SIP10_FUNGIBLE')
        assert hasattr(TokenKind, 'SIP10_NFT')
        assert TokenKind.SIP10_FUNGIBLE in STACKS_TOKEN_KINDS
        assert TokenKind.SIP10_NFT in STACKS_TOKEN_KINDS

    def test_chains_with_chain_manager(self) -> None:
        """Test that STACKS is in CHAINS_WITH_CHAIN_MANAGER."""
        # CHAINS_WITH_CHAIN_MANAGER is a union of Literal types
        # We need to recursively extract all enum values
        from typing import Union, get_args, get_origin

        def extract_literal_values(type_hint):
            """Recursively extract all values from nested Literal/Union types."""
            values = set()
            origin = get_origin(type_hint)
            args = get_args(type_hint)

            if origin is Union:
                for arg in args:
                    values.update(extract_literal_values(arg))
            elif args:  # It's a Literal type
                for arg in args:
                    if isinstance(arg, SupportedBlockchain):
                        values.add(arg)
                    else:
                        values.update(extract_literal_values(arg))
            return values

        chains = extract_literal_values(CHAINS_WITH_CHAIN_MANAGER)
        assert SupportedBlockchain.STACKS in chains

    def test_native_token_id(self) -> None:
        """Test that the native token ID is correct."""
        assert SupportedBlockchain.STACKS.get_native_token_id() == 'STX'

    def test_image_name(self) -> None:
        """Test that the image name is correct."""
        assert SupportedBlockchain.STACKS.get_image_name() == 'stacks.svg'

    def test_address_chain_group(self) -> None:
        """Test that the address chain group is correct."""
        assert SupportedBlockchain.STACKS.get_address_chain_group() == ChainType.STACKS

    def test_location_from_chain(self) -> None:
        """Test that Location.from_chain works for STACKS."""
        # We need to update OTHER_CHAINS_WITH_TRANSACTIONS first, but let's test the mapping
        assert Location.from_chain(SupportedBlockchain.STACKS) == Location.STACKS


class TestStacksAddressbookEcosystem:
    """Tests for Stacks address ecosystem detection."""

    def test_check_chain_ecosystem_stacks(self) -> None:
        """Test that Stacks addresses are detected as STACKS ecosystem."""
        stacks_address = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7'
        ecosystem = AddressbookEntry.check_chain_ecosystem(stacks_address)
        assert ecosystem == ChainType.STACKS

    def test_ecosystem_isolation(self) -> None:
        """Test that Stacks addresses don't match other ecosystems."""
        stacks_address = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7'
        ecosystem = AddressbookEntry.check_chain_ecosystem(stacks_address)

        # Should not be any other ecosystem
        assert ecosystem != ChainType.BITCOIN
        assert ecosystem != ChainType.EVMLIKE
        assert ecosystem != ChainType.SUBSTRATE
        assert ecosystem != ChainType.SOLANA


class TestStacksAssetConstant:
    """Tests for the A_STX asset constant."""

    def test_a_stx_exists(self) -> None:
        """Test that A_STX asset constant exists and is correct."""
        assert A_STX is not None
        assert A_STX.identifier == 'STX'


class TestStacksAddressType:
    """Tests for StacksAddress type."""

    def test_stacks_address_type_creation(self) -> None:
        """Test that StacksAddress type can be used."""
        address: StacksAddress = StacksAddress('SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7')
        assert isinstance(address, str)
        assert address == 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7'
