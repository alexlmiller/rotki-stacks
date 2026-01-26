"""Clarity repr string parser for Stacks blockchain.

Parses Clarity value representations as returned by the Hiro API in the
`repr` field of function arguments.

Supported types:
- uint: u123 -> int
- int: 123 or -123 -> int
- bool: true/false -> bool
- principal: 'SP... or SP... -> str
- buff: 0x1234... -> bytes
- string-ascii: "hello" -> str
- string-utf8: u"hello" -> str
- optional: (some val) -> val, none -> None
- tuple: (tuple (k1 v1) (k2 v2)) -> dict
- list: (list v1 v2 v3) -> list
- response: (ok val) -> {'ok': val}, (err val) -> {'err': val}
"""
import logging
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Final

from rotkehlchen.logging import RotkehlchenLogsAdapter

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


# Type alias for parsed Clarity values
ClarityValue = int | str | bool | bytes | list['ClarityValue'] | dict[str, 'ClarityValue'] | None


class TokenType(Enum):
    """Token types for the Clarity lexer."""
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    UINT = auto()        # u123
    INT = auto()         # 123 or -123
    BOOL = auto()        # true or false
    PRINCIPAL = auto()   # 'SP... or SP...
    BUFF = auto()        # 0x...
    STRING = auto()       # "..."
    STRING_UTF8 = auto()  # u"..."
    SYMBOL = auto()      # tuple, list, some, none, ok, err, etc.
    EOF = auto()


@dataclass
class Token:
    """A token from the Clarity lexer."""
    type: TokenType
    value: str
    position: int


class ClarityLexerError(Exception):
    """Error during Clarity repr lexing."""


class ClarityParserError(Exception):
    """Error during Clarity repr parsing."""


# Regex patterns for tokenization
UINT_PATTERN: Final = re.compile(r'u(\d+)')
INT_PATTERN: Final = re.compile(r'-?\d+')
PRINCIPAL_PATTERN: Final = re.compile(r"'?([ST][A-Z0-9]+(?:\.[a-zA-Z][a-zA-Z0-9_-]*)?)")
BUFF_PATTERN: Final = re.compile(r'0x([0-9a-fA-F]*)')
STRING_PATTERN: Final = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')
STRING_UTF8_PATTERN: Final = re.compile(r'u"([^"\\]*(?:\\.[^"\\]*)*)"')
SYMBOL_PATTERN: Final = re.compile(r'[a-zA-Z][a-zA-Z0-9_-]*')


class ClarityLexer:
    """Tokenizer for Clarity repr strings."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.length = len(text)

    def _skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def _current_char(self) -> str | None:
        """Get current character or None if at end."""
        if self.pos >= self.length:
            return None
        return self.text[self.pos]

    def _match_pattern(self, pattern: re.Pattern[str]) -> str | None:
        """Try to match a regex pattern at current position."""
        match = pattern.match(self.text, self.pos)
        if match:
            return match.group(0)
        return None

    def tokenize(self) -> list[Token]:
        """Tokenize the entire input string."""
        tokens: list[Token] = []

        while self.pos < self.length:
            self._skip_whitespace()
            if self.pos >= self.length:
                break

            start_pos = self.pos
            char = self._current_char()
            assert char is not None  # we've checked pos < length above

            if char == '(':
                tokens.append(Token(TokenType.LPAREN, '(', start_pos))
                self.pos += 1

            elif char == ')':
                tokens.append(Token(TokenType.RPAREN, ')', start_pos))
                self.pos += 1

            elif char == 'u' and self.pos + 1 < self.length:
                # Could be uint (u123) or utf8 string (u"...")
                if self.text[self.pos + 1] == '"':
                    # UTF-8 string
                    match = STRING_UTF8_PATTERN.match(self.text, self.pos)
                    if match:
                        tokens.append(Token(TokenType.STRING_UTF8, match.group(1), start_pos))
                        self.pos = match.end()
                    else:
                        raise ClarityLexerError(
                            f'Invalid UTF-8 string at position {start_pos}',
                        )
                elif self.text[self.pos + 1].isdigit():
                    # Unsigned integer
                    match = UINT_PATTERN.match(self.text, self.pos)
                    if match:
                        tokens.append(Token(TokenType.UINT, match.group(1), start_pos))
                        self.pos = match.end()
                    else:
                        raise ClarityLexerError(
                            f'Invalid uint at position {start_pos}',
                        )
                else:
                    # Symbol starting with 'u'
                    match = SYMBOL_PATTERN.match(self.text, self.pos)
                    if match:
                        tokens.append(Token(TokenType.SYMBOL, match.group(0), start_pos))
                        self.pos = match.end()
                    else:
                        raise ClarityLexerError(
                            f'Invalid token at position {start_pos}',
                        )

            elif char == '"':
                # ASCII string
                match = STRING_PATTERN.match(self.text, self.pos)
                if match:
                    tokens.append(Token(TokenType.STRING, match.group(1), start_pos))
                    self.pos = match.end()
                else:
                    raise ClarityLexerError(
                        f'Unterminated string at position {start_pos}',
                    )

            elif char == '0' and self.pos + 1 < self.length and self.text[self.pos + 1] == 'x':
                # Buffer (hex)  # noqa: ERA001
                match = BUFF_PATTERN.match(self.text, self.pos)
                if match:
                    tokens.append(Token(TokenType.BUFF, match.group(1), start_pos))
                    self.pos = match.end()
                else:
                    raise ClarityLexerError(
                        f'Invalid buffer at position {start_pos}',
                    )

            elif char == "'" or char in 'ST':
                # Principal (with or without leading quote)
                match = PRINCIPAL_PATTERN.match(self.text, self.pos)
                if match:
                    tokens.append(Token(TokenType.PRINCIPAL, match.group(1), start_pos))
                    self.pos = match.end()
                else:
                    # Could be a symbol starting with S or T
                    match = SYMBOL_PATTERN.match(self.text, self.pos)
                    if match:
                        tokens.append(Token(TokenType.SYMBOL, match.group(0), start_pos))
                        self.pos = match.end()
                    else:
                        raise ClarityLexerError(
                            f'Invalid token at position {start_pos}',
                        )

            elif char == '-' or char.isdigit():
                # Signed or unsigned integer (without u prefix)
                match = INT_PATTERN.match(self.text, self.pos)
                if match:
                    tokens.append(Token(TokenType.INT, match.group(0), start_pos))
                    self.pos = match.end()
                else:
                    raise ClarityLexerError(
                        f'Invalid integer at position {start_pos}',
                    )

            elif char.isalpha():
                # Symbol (true, false, none, tuple, list, some, ok, err, etc.)
                match = SYMBOL_PATTERN.match(self.text, self.pos)
                if match:
                    symbol = match.group(0)
                    if symbol in ('true', 'false'):
                        tokens.append(Token(TokenType.BOOL, symbol, start_pos))
                    else:
                        tokens.append(Token(TokenType.SYMBOL, symbol, start_pos))
                    self.pos = match.end()
                else:
                    raise ClarityLexerError(
                        f'Invalid symbol at position {start_pos}',
                    )

            else:
                raise ClarityLexerError(
                    f'Unexpected character {char!r} at position {start_pos}',
                )

        tokens.append(Token(TokenType.EOF, '', self.pos))
        return tokens


class ClarityParser:
    """Parser for Clarity repr token streams."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def _current_token(self) -> Token:
        """Get current token."""
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        """Advance to next token and return the previous one."""
        token = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def _expect(self, token_type: TokenType) -> Token:
        """Expect and consume a specific token type."""
        token = self._current_token()
        if token.type != token_type:
            raise ClarityParserError(
                f'Expected {token_type.name}, got {token.type.name} at position {token.position}',
            )
        return self._advance()

    def parse(self) -> ClarityValue:
        """Parse tokens into a ClarityValue."""
        result = self._parse_value()
        if self._current_token().type != TokenType.EOF:
            raise ClarityParserError(
                f'Unexpected token after value: {self._current_token().type.name}',
            )
        return result

    def _parse_value(self) -> ClarityValue:
        """Parse a single Clarity value."""
        token = self._current_token()

        if token.type == TokenType.UINT:
            self._advance()
            return int(token.value)

        if token.type == TokenType.INT:
            self._advance()
            return int(token.value)

        if token.type == TokenType.BOOL:
            self._advance()
            return token.value == 'true'

        if token.type == TokenType.PRINCIPAL:
            self._advance()
            return token.value

        if token.type == TokenType.BUFF:
            self._advance()
            return bytes.fromhex(token.value) if token.value else b''

        if token.type == TokenType.STRING:
            self._advance()
            return self._unescape_string(token.value)

        if token.type == TokenType.STRING_UTF8:
            self._advance()
            return self._unescape_string(token.value)

        if token.type == TokenType.SYMBOL:
            if token.value == 'none':
                self._advance()
                return None
            # Standalone symbol - might be an error or unknown type
            self._advance()
            return token.value

        if token.type == TokenType.LPAREN:
            return self._parse_compound()

        raise ClarityParserError(
            f'Unexpected token {token.type.name} at position {token.position}',
        )

    def _parse_compound(self) -> ClarityValue:
        """Parse a compound value (tuple, list, some, ok, err, response)."""
        self._expect(TokenType.LPAREN)
        keyword_token = self._current_token()

        if keyword_token.type != TokenType.SYMBOL:
            raise ClarityParserError(
                f'Expected keyword after (, got {keyword_token.type.name}',
            )

        keyword = keyword_token.value
        self._advance()

        if keyword == 'tuple':
            return self._parse_tuple_contents()

        if keyword == 'list':
            return self._parse_list_contents()

        if keyword == 'some':
            value = self._parse_value()
            self._expect(TokenType.RPAREN)
            return value

        if keyword == 'ok':
            value = self._parse_value()
            self._expect(TokenType.RPAREN)
            return {'ok': value}

        if keyword == 'err':
            value = self._parse_value()
            self._expect(TokenType.RPAREN)
            return {'err': value}

        # Unknown compound type - try to parse as generic structure
        log.warning(f'Unknown Clarity compound type: {keyword}')
        values = []
        while self._current_token().type != TokenType.RPAREN:
            values.append(self._parse_value())
        self._expect(TokenType.RPAREN)
        return {keyword: values}

    def _parse_tuple_contents(self) -> dict[str, ClarityValue]:
        """Parse tuple contents: (k1 v1) (k2 v2) ... )"""
        result: dict[str, ClarityValue] = {}

        while self._current_token().type == TokenType.LPAREN:
            self._advance()  # consume (

            # Key name
            key_token = self._current_token()
            if key_token.type != TokenType.SYMBOL:
                raise ClarityParserError(
                    f'Expected tuple key name, got {key_token.type.name}',
                )
            key = key_token.value
            self._advance()

            # Value
            value = self._parse_value()
            result[key] = value

            self._expect(TokenType.RPAREN)

        self._expect(TokenType.RPAREN)  # closing ) of tuple
        return result

    def _parse_list_contents(self) -> list[ClarityValue]:
        """Parse list contents: v1 v2 v3 ... )"""
        result: list[ClarityValue] = []

        while self._current_token().type != TokenType.RPAREN:
            result.append(self._parse_value())

        self._expect(TokenType.RPAREN)
        return result

    @staticmethod
    def _unescape_string(s: str) -> str:
        """Unescape a Clarity string value."""
        # Handle common escape sequences
        result = s.replace('\\n', '\n').replace('\\t', '\t')
        return result.replace('\\\\', '\\').replace('\\"', '"')


def parse_clarity_repr(repr_str: str) -> ClarityValue:
    """Parse a Clarity repr string into a Python value.

    Args:
        repr_str: The Clarity repr string (e.g., "u100", "(tuple (to 'SP...) (ustx u100))")

    Returns:
        The parsed Python value

    Raises:
        ClarityLexerError: If tokenization fails
        ClarityParserError: If parsing fails
    """
    lexer = ClarityLexer(repr_str)
    tokens = lexer.tokenize()
    parser = ClarityParser(tokens)
    return parser.parse()


def parse_clarity_repr_safe(repr_str: str) -> ClarityValue | None:
    """Parse a Clarity repr string, returning None on any error.

    Args:
        repr_str: The Clarity repr string

    Returns:
        The parsed Python value, or None if parsing fails
    """
    try:
        return parse_clarity_repr(repr_str)
    except (ClarityLexerError, ClarityParserError) as e:
        log.debug(f'Failed to parse Clarity repr {repr_str!r}: {e}')
        return None


def get_uint_from_repr(repr_str: str) -> int | None:
    """Extract a uint value from a repr string.

    Handles both simple "u123" format and wrapped values.
    """
    if repr_str.startswith('u') and repr_str[1:].isdigit():
        return int(repr_str[1:])

    value = parse_clarity_repr_safe(repr_str)
    if isinstance(value, int):
        return value
    return None


def get_principal_from_repr(repr_str: str) -> str | None:
    """Extract a principal (address) from a repr string."""
    # Handle quoted format: 'SP...
    if repr_str.startswith("'"):
        return repr_str[1:]

    # Handle unquoted format: SP...
    if repr_str.startswith(('SP', 'ST')):
        # Extract just the principal part (may have contract suffix)
        match = PRINCIPAL_PATTERN.match(repr_str)
        if match:
            return match.group(1)

    value = parse_clarity_repr_safe(repr_str)
    if isinstance(value, str) and value.startswith(('SP', 'ST')):
        return value
    return None
