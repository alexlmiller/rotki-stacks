"""Tests for the Clarity repr parser."""
import pytest

from rotkehlchen.chain.stacks.clarity_parser import (
    ClarityLexer,
    ClarityLexerError,
    ClarityParser,
    ClarityParserError,
    TokenType,
    get_principal_from_repr,
    get_uint_from_repr,
    parse_clarity_repr,
    parse_clarity_repr_safe,
)


class TestClarityLexer:
    """Tests for the Clarity tokenizer."""

    def test_tokenize_uint(self):
        lexer = ClarityLexer('u123')
        tokens = lexer.tokenize()
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.UINT
        assert tokens[0].value == '123'

    def test_tokenize_int(self):
        lexer = ClarityLexer('123')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.INT
        assert tokens[0].value == '123'

    def test_tokenize_negative_int(self):
        lexer = ClarityLexer('-456')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.INT
        assert tokens[0].value == '-456'

    def test_tokenize_bool_true(self):
        lexer = ClarityLexer('true')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.BOOL
        assert tokens[0].value == 'true'

    def test_tokenize_bool_false(self):
        lexer = ClarityLexer('false')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.BOOL
        assert tokens[0].value == 'false'

    def test_tokenize_principal_quoted(self):
        lexer = ClarityLexer("'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.PRINCIPAL
        assert tokens[0].value == 'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9'

    def test_tokenize_principal_unquoted(self):
        lexer = ClarityLexer('SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.PRINCIPAL
        assert tokens[0].value == 'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9'

    def test_tokenize_principal_with_contract(self):
        lexer = ClarityLexer("'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-token")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.PRINCIPAL
        assert tokens[0].value == 'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-token'

    def test_tokenize_buff(self):
        lexer = ClarityLexer('0x1234abcd')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.BUFF
        assert tokens[0].value == '1234abcd'

    def test_tokenize_empty_buff(self):
        lexer = ClarityLexer('0x')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.BUFF
        assert tokens[0].value == ''

    def test_tokenize_string(self):
        lexer = ClarityLexer('"hello world"')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == 'hello world'

    def test_tokenize_string_utf8(self):
        lexer = ClarityLexer('u"hello"')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING_UTF8
        assert tokens[0].value == 'hello'

    def test_tokenize_symbols(self):
        lexer = ClarityLexer('none')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.SYMBOL
        assert tokens[0].value == 'none'

    def test_tokenize_parens(self):
        lexer = ClarityLexer('(tuple)')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[1].type == TokenType.SYMBOL
        assert tokens[1].value == 'tuple'
        assert tokens[2].type == TokenType.RPAREN

    def test_tokenize_complex_expression(self):
        lexer = ClarityLexer("(tuple (to 'SP123) (ustx u100))")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens[:-1]]  # exclude EOF
        assert types == [
            TokenType.LPAREN,
            TokenType.SYMBOL,  # tuple
            TokenType.LPAREN,
            TokenType.SYMBOL,  # to
            TokenType.PRINCIPAL,
            TokenType.RPAREN,
            TokenType.LPAREN,
            TokenType.SYMBOL,  # ustx
            TokenType.UINT,
            TokenType.RPAREN,
            TokenType.RPAREN,
        ]

    def test_tokenize_whitespace_handling(self):
        lexer = ClarityLexer('  u123  \n  u456  ')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.UINT
        assert tokens[0].value == '123'
        assert tokens[1].type == TokenType.UINT
        assert tokens[1].value == '456'

    def test_tokenize_invalid_character(self):
        lexer = ClarityLexer('@invalid')
        with pytest.raises(ClarityLexerError):
            lexer.tokenize()


class TestClarityParser:
    """Tests for the Clarity parser."""

    def test_parse_uint(self):
        assert parse_clarity_repr('u100') == 100
        assert parse_clarity_repr('u0') == 0
        assert parse_clarity_repr('u999999999999') == 999999999999

    def test_parse_int(self):
        assert parse_clarity_repr('100') == 100
        assert parse_clarity_repr('-100') == -100
        assert parse_clarity_repr('0') == 0

    def test_parse_bool(self):
        assert parse_clarity_repr('true') is True
        assert parse_clarity_repr('false') is False

    def test_parse_principal(self):
        assert parse_clarity_repr("'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9") == \
            'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9'
        assert parse_clarity_repr('SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9') == \
            'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9'

    def test_parse_principal_with_contract(self):
        result = parse_clarity_repr("'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-token")
        assert result == 'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-token'

    def test_parse_buff(self):
        assert parse_clarity_repr('0x1234') == b'\x12\x34'
        assert parse_clarity_repr('0x') == b''
        assert parse_clarity_repr('0xdeadbeef') == b'\xde\xad\xbe\xef'

    def test_parse_string(self):
        assert parse_clarity_repr('"hello"') == 'hello'
        assert parse_clarity_repr('"hello world"') == 'hello world'
        assert parse_clarity_repr('""') == ''

    def test_parse_string_utf8(self):
        assert parse_clarity_repr('u"hello"') == 'hello'

    def test_parse_none(self):
        assert parse_clarity_repr('none') is None

    def test_parse_some(self):
        assert parse_clarity_repr('(some u100)') == 100
        assert parse_clarity_repr('(some true)') is True
        assert parse_clarity_repr("(some 'SP123)") == 'SP123'

    def test_parse_ok(self):
        assert parse_clarity_repr('(ok u100)') == {'ok': 100}
        assert parse_clarity_repr('(ok true)') == {'ok': True}

    def test_parse_err(self):
        assert parse_clarity_repr('(err u21)') == {'err': 21}
        assert parse_clarity_repr('(err false)') == {'err': False}

    def test_parse_tuple_simple(self):
        result = parse_clarity_repr('(tuple (a u1) (b u2))')
        assert result == {'a': 1, 'b': 2}

    def test_parse_tuple_with_principal(self):
        result = parse_clarity_repr("(tuple (to 'SP123) (ustx u100))")
        assert result == {'to': 'SP123', 'ustx': 100}

    def test_parse_tuple_with_buff(self):
        result = parse_clarity_repr('(tuple (hashbytes 0x1234) (version 0x00))')
        assert result == {'hashbytes': b'\x12\x34', 'version': b'\x00'}

    def test_parse_list_simple(self):
        assert parse_clarity_repr('(list u1 u2 u3)') == [1, 2, 3]
        assert parse_clarity_repr('(list)') == []

    def test_parse_list_mixed_types(self):
        result = parse_clarity_repr('(list u1 true "hello")')
        assert result == [1, True, 'hello']

    def test_parse_list_of_tuples(self):
        """Test parsing send-many style recipient list."""
        result = parse_clarity_repr(
            '(list (tuple (to \'SP123) (ustx u100)) (tuple (to \'SP456) (ustx u200)))',
        )
        assert result == [
            {'to': 'SP123', 'ustx': 100},
            {'to': 'SP456', 'ustx': 200},
        ]

    def test_parse_nested_structures(self):
        """Test deeply nested Clarity structures."""
        result = parse_clarity_repr(
            '(tuple (pox-addr (tuple (hashbytes 0x1234) (version 0x01))) (amount u1000))',
        )
        assert result == {
            'pox-addr': {'hashbytes': b'\x12\x34', 'version': b'\x01'},
            'amount': 1000,
        }

    def test_parse_real_pox_tuple(self):
        """Test parsing a real PoX address tuple from the API."""
        result = parse_clarity_repr(
            '(tuple (hashbytes 0x1d50f219d4d64fdeb2d33d7f5c405c26396962d7) (version 0x01))',
        )
        assert result == {
            'hashbytes': bytes.fromhex('1d50f219d4d64fdeb2d33d7f5c405c26396962d7'),
            'version': b'\x01',
        }

    def test_parse_optional_some(self):
        result = parse_clarity_repr('(some u718402)')
        assert result == 718402

    def test_parse_complex_send_many(self):
        """Test parsing a complete send-many recipients structure."""
        repr_str = '''(list
            (tuple (to 'SP1ADDR1) (ustx u1000000) (memo 0x68656c6c6f))
            (tuple (to 'SP2ADDR2) (ustx u2000000) (memo 0x776f726c64))
        )'''
        result = parse_clarity_repr(repr_str)
        assert len(result) == 2
        assert result[0]['to'] == 'SP1ADDR1'
        assert result[0]['ustx'] == 1000000
        assert result[0]['memo'] == b'hello'
        assert result[1]['to'] == 'SP2ADDR2'
        assert result[1]['ustx'] == 2000000
        assert result[1]['memo'] == b'world'


class TestClarityParserSafe:
    """Tests for the safe parsing function."""

    def test_safe_parse_valid(self):
        assert parse_clarity_repr_safe('u100') == 100

    def test_safe_parse_invalid_returns_none(self):
        assert parse_clarity_repr_safe('invalid@@@') is None
        assert parse_clarity_repr_safe('(unterminated') is None
        assert parse_clarity_repr_safe('') is None


class TestHelperFunctions:
    """Tests for convenience helper functions."""

    def test_get_uint_simple(self):
        assert get_uint_from_repr('u100') == 100
        assert get_uint_from_repr('u0') == 0
        assert get_uint_from_repr('u999999999999999') == 999999999999999

    def test_get_uint_from_complex(self):
        # Should parse even if wrapped in some structure
        assert get_uint_from_repr('100') == 100

    def test_get_uint_invalid(self):
        assert get_uint_from_repr('not-a-number') is None
        assert get_uint_from_repr("'SP123") is None

    def test_get_principal_quoted(self):
        assert get_principal_from_repr("'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9") == \
            'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9'

    def test_get_principal_unquoted(self):
        assert get_principal_from_repr('SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9') == \
            'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9'

    def test_get_principal_with_contract(self):
        assert get_principal_from_repr("'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-token") == \
            'SP3K8BC0PPEVCV7NZ6QSRWPQ2JE9E5B6N3PA0KBR9.sbtc-token'

    def test_get_principal_invalid(self):
        assert get_principal_from_repr('u100') is None
        assert get_principal_from_repr('not-a-principal') is None


class TestRealWorldExamples:
    """Tests with actual API response data."""

    def test_delegate_stx_amount(self):
        """From real delegate-stx transaction."""
        assert parse_clarity_repr('u200000000') == 200000000

    def test_stack_stx_amount(self):
        """From real stack-stx transaction."""
        assert parse_clarity_repr('u100000000000') == 100000000000

    def test_pox_addr_tuple(self):
        """From real PoX transaction pox-addr argument."""
        result = parse_clarity_repr(
            '(tuple (hashbytes 0x1d50f219d4d64fdeb2d33d7f5c405c26396962d7) (version 0x01))',
        )
        assert result['version'] == b'\x01'
        assert len(result['hashbytes']) == 20

    def test_delegate_to_principal(self):
        """From real delegate-stx transaction."""
        result = parse_clarity_repr("'SP700C57YJFD5RGHK0GN46478WBAM2KG3A4MN2QJ")
        assert result == 'SP700C57YJFD5RGHK0GN46478WBAM2KG3A4MN2QJ'

    def test_optional_none(self):
        """From real transaction with optional field."""
        assert parse_clarity_repr('none') is None

    def test_response_ok(self):
        """From real transaction result."""
        assert parse_clarity_repr('(ok true)') == {'ok': True}

    def test_response_err(self):
        """From failed PoX transaction."""
        assert parse_clarity_repr('(err u21)') == {'err': 21}
