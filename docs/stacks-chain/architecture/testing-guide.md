# Testing Guide

Testing patterns and requirements for Stacks integration.

---

## Critical: Use Gevent Wrapper

**Never run pytest directly.** Always use:

```bash
uv run python pytestgeventwrapper.py [OPTIONS] [TEST_PATH]
```

---

## Running Tests

```bash
# Run specific file
uv run python pytestgeventwrapper.py rotkehlchen/tests/unit/test_stacks.py

# Run with verbose output
uv run python pytestgeventwrapper.py -v rotkehlchen/tests/unit/test_stacks.py

# Filter by name
uv run python pytestgeventwrapper.py -k stacks

# Run specific test
uv run python pytestgeventwrapper.py rotkehlchen/tests/unit/test_stacks.py::test_valid_address
```

---

## Unit Test Structure

**File**: `rotkehlchen/tests/unit/test_stacks.py`

```python
import pytest
from rotkehlchen.chain.stacks.validation import is_valid_stacks_address
from rotkehlchen.types import SupportedBlockchain, Location


class TestStacksAddressValidation:
    """Group related tests in classes."""

    def test_valid_mainnet_standard_addresses(self) -> None:
        """SP prefix - mainnet standard."""
        assert is_valid_stacks_address('SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7')

    def test_valid_mainnet_contract_addresses(self) -> None:
        """SM prefix - mainnet contract."""
        assert is_valid_stacks_address('SM3KNVZS30WM7F89SXKVVFY4SN9RMPZZ9FX929N0V')

    def test_invalid_addresses(self) -> None:
        """Test rejection of invalid addresses."""
        invalid = [
            '',
            'invalid',
            '0x1234567890abcdef',  # EVM address
            'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ',  # Too short
        ]
        for addr in invalid:
            assert not is_valid_stacks_address(addr), f'{addr} should be invalid'


class TestStacksTypeRegistration:
    """Test type system integration."""

    def test_blockchain_serialization(self) -> None:
        assert SupportedBlockchain.STACKS.serialize() == 'stx'

    def test_blockchain_string(self) -> None:
        assert str(SupportedBlockchain.STACKS) == 'Stacks'

    def test_location_value(self) -> None:
        assert Location.STACKS.value == 57
```

---

## Fixtures

**File**: `rotkehlchen/tests/fixtures/stacks.py`

```python
import pytest
from rotkehlchen.chain.stacks.node_inquirer import StacksInquirer
from rotkehlchen.types import StacksAddress


@pytest.fixture
def stacks_inquirer(database, greenlet_manager):
    return StacksInquirer(
        greenlet_manager=greenlet_manager,
        database=database,
    )


@pytest.fixture
def stacks_accounts() -> list[StacksAddress]:
    return [
        StacksAddress('SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7'),
    ]


@pytest.fixture
def stacks_manager(stacks_inquirer):
    from rotkehlchen.chain.stacks.manager import StacksManager
    return StacksManager(node_inquirer=stacks_inquirer)
```

Register in `rotkehlchen/tests/conftest.py`:
```python
pytest_plugins = [
    # ... existing
    'rotkehlchen.tests.fixtures.stacks',
]
```

---

## VCR Cassettes (Network Tests)

For tests that call external APIs:

```python
@pytest.mark.vcr
@pytest.mark.freeze_time('2025-01-24 12:00:00 GMT')
def test_query_balance(stacks_inquirer, stacks_accounts):
    """Test with recorded API response."""
    balance = stacks_inquirer.get_stx_balance(stacks_accounts[0])
    assert balance > 0
```

**Recording cassettes**:
```bash
RECORD_CASSETTES=true uv run python pytestgeventwrapper.py -m vcr \
    rotkehlchen/tests/unit/test_stacks_api.py
```

Cassettes stored in: `rotkehlchen/tests/cassettes/`

---

## Decoder Tests

**File**: `rotkehlchen/tests/unit/stacks_decoders/test_sbtc.py`

```python
import pytest
from rotkehlchen.history.events.structures.types import (
    HistoryEventType,
    HistoryEventSubType,
)


@pytest.mark.vcr
def test_sbtc_pegin(stacks_inquirer, stacks_accounts):
    """Test sBTC bridge pegin decoding."""
    tx_id = '0x...'
    events = get_decoded_events_of_stacks_tx(
        stacks_inquirer=stacks_inquirer,
        tx_id=tx_id,
    )

    assert len(events) >= 2

    # Fee event
    assert events[0].event_type == HistoryEventType.SPEND
    assert events[0].event_subtype == HistoryEventSubType.FEE

    # Bridge event
    bridge_event = events[1]
    assert bridge_event.event_type == HistoryEventType.DEPOSIT
    assert bridge_event.event_subtype == HistoryEventSubType.BRIDGE
    assert bridge_event.counterparty == 'sbtc'
```

**Note**: Do NOT use `@pytest.mark.vcr` for decoder tests per CLAUDE.md.

---

## Database Tests

**File**: `rotkehlchen/tests/db/test_stacks_tx.py`

```python
def test_add_and_get_transactions(database):
    """Test transaction CRUD operations."""
    from rotkehlchen.db.stackstx import DBStacksTx
    from rotkehlchen.chain.stacks.types import StacksTransaction

    db_tx = DBStacksTx(database)
    tx = StacksTransaction(
        tx_id='0x1234...',
        block_height=100000,
        block_time=1700000000,
        tx_type='token_transfer',
        sender_address='SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7',
        fee_rate='1000',
        nonce=1,
        tx_status='success',
    )

    with database.user_write() as cursor:
        db_tx.add_transactions(cursor, [tx], tx.sender_address)

    with database.conn.read_ctx() as cursor:
        from rotkehlchen.db.filtering import StacksTransactionsFilterQuery
        result = db_tx.get_transactions(cursor, StacksTransactionsFilterQuery.make())

    assert len(result) == 1
    assert result[0].tx_id == '0x1234...'
```

---

## API Tests

**File**: `rotkehlchen/tests/api/test_stacks.py`

```python
def test_add_stacks_account(rotkehlchen_api_server):
    """Test account addition via API."""
    response = requests.put(
        f'{api_url}/blockchains/stacks/accounts',
        json={'accounts': [{'address': 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7'}]},
    )
    assert response.status_code == 200


def test_query_stacks_balances(rotkehlchen_api_server_with_stacks):
    """Test balance query."""
    response = requests.get(f'{api_url}/balances/blockchains/stacks')
    assert response.status_code == 200
    data = response.json()
    assert 'result' in data
```

---

## Frontend Tests

**File**: `frontend/app/tests/e2e/stacks.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test('can navigate to Stacks accounts page', async ({ page }) => {
  await page.goto('/accounts/stacks');
  await expect(page).toHaveURL('/accounts/stacks');
});

test('can add Stacks account', async ({ page }) => {
  await page.goto('/accounts/stacks');
  await page.click('[data-cy="add-account"]');
  await page.fill(
    '[data-cy="address-input"]',
    'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7'
  );
  await page.click('[data-cy="submit"]');
  await expect(page.locator('[data-cy="account-row"]')).toBeVisible();
});
```

---

## Linting Before Commit

```bash
# Must pass before any PR
make lint
make format
```

---

## Test Coverage Goals

| Component | Target |
|-----------|--------|
| Address validation | 100% |
| Type registration | 100% |
| Balance queries | 80%+ |
| Transaction storage | 80%+ |
| Decoders | One test per operation type |
