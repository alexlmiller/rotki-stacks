"""STX-20 protocol constants."""
import re
from typing import Final

CPT_STX20: Final = 'stx-20'

# STX-20 operation prefixes
STX20_DEPLOY_OP: Final = 'd'
STX20_MINT_OP: Final = 'm'
STX20_TRANSFER_OP: Final = 't'

# Regex patterns for parsing STX-20 memos
# Deploy: d{TICKER}{supply};{limit}
# Mint: m{TICKER}{amount}
# Transfer: t{TICKER}{amount}
STX20_DEPLOY_PATTERN: Final = re.compile(r'^d([A-Z]{3,8})(\d+);(\d+)$')
STX20_MINT_PATTERN: Final = re.compile(r'^m([A-Z]{3,8})(\d+)$')
STX20_TRANSFER_PATTERN: Final = re.compile(r'^t([A-Z]{3,8})(\d+)$')
