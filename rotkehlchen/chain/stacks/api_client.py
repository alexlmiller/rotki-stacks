"""Stacks API client for Hiro REST API."""
import contextlib
import logging
import random
from typing import TYPE_CHECKING, Any, Final

import gevent
import requests

from rotkehlchen.chain.stacks.constants import (
    BACKOFF_MULTIPLIER,
    HIRO_API_BASE_URL,
    HIRO_METADATA_API_URL,
    INITIAL_BACKOFF,
    MAX_RETRIES,
    StacksTokenMetadata,
)
from rotkehlchen.errors.misc import RemoteError
from rotkehlchen.externalapis.interface import ExternalServiceWithRecommendedApiKey
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.types import ExternalService, StacksAddress

if TYPE_CHECKING:
    from rotkehlchen.db.dbhandler import DBHandler

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)

DEFAULT_TIMEOUT: Final = 30  # seconds


class StacksApiClient(ExternalServiceWithRecommendedApiKey):
    """Client for the Hiro Stacks REST API with rate limiting support.

    The Hiro API provides REST endpoints for querying Stacks blockchain data.
    Rate limits:
    - Without API key: 50 requests/minute
    - With API key: 500 requests/minute

    The client handles rate limiting with exponential backoff and
    respects retry-after headers when provided.
    """

    def __init__(self, database: 'DBHandler') -> None:
        """Initialize the Stacks API client.

        Args:
            database: The database handler for API key lookup
        """
        super().__init__(database=database, service_name=ExternalService.HIRO)
        self.base_url = HIRO_API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

    def _make_request(
            self,
            endpoint: str,
            params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a request to the Hiro API with rate limiting and retry logic.

        Args:
            endpoint: API endpoint path (e.g., 'extended/v1/address/{addr}/balances')
            params: Optional query parameters

        Returns:
            JSON response as a dictionary

        Raises:
            RemoteError: If the request fails after all retries
        """
        # Update headers with API key on each request (may change at runtime)
        api_key = self._get_api_key()
        if api_key:
            self.session.headers['x-api-key'] = api_key
        elif 'x-api-key' in self.session.headers:
            del self.session.headers['x-api-key']

        url = f'{self.base_url}/{endpoint}'
        backoff = INITIAL_BACKOFF
        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT)

                if response.status_code == 429:
                    # Rate limited - check for retry-after header
                    retry_after = response.headers.get('retry-after')
                    if retry_after is not None:
                        with contextlib.suppress(ValueError):
                            backoff = int(retry_after) + 1

                    if attempt < MAX_RETRIES:
                        jitter = random.uniform(0, 0.5)
                        sleep_time = backoff + jitter
                        log.warning(
                            f'Rate limited by Hiro API. Backing off {sleep_time:.2f} seconds... '
                            f'(attempt {attempt + 1}/{MAX_RETRIES + 1})',
                        )
                        gevent.sleep(sleep_time)
                        backoff *= BACKOFF_MULTIPLIER
                        continue
                    raise RemoteError(
                        f'Hiro API rate limit exceeded after {MAX_RETRIES + 1} attempts',
                    )

                if response.status_code == 404:
                    # Address not found or no data
                    return None

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    jitter = random.uniform(0, 0.5)
                    sleep_time = backoff + jitter
                    log.warning(
                        f'Hiro API request timed out. Retrying in {sleep_time:.2f}s... '
                        f'(attempt {attempt + 1}/{MAX_RETRIES + 1})',
                    )
                    gevent.sleep(sleep_time)
                    backoff *= BACKOFF_MULTIPLIER
                    continue

            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    jitter = random.uniform(0, 0.5)
                    sleep_time = backoff + jitter
                    log.warning(
                        f'Hiro API request failed: {e}. Retrying in {sleep_time:.2f}s... '
                        f'(attempt {attempt + 1}/{MAX_RETRIES + 1})',
                    )
                    gevent.sleep(sleep_time)
                    backoff *= BACKOFF_MULTIPLIER
                    continue

        raise RemoteError(
            f'Failed to query Hiro API after {MAX_RETRIES + 1} attempts: {last_error}',
        )

    def get_account_balances(self, address: StacksAddress) -> dict[str, Any]:
        """Get account balances for a Stacks address.

        Args:
            address: The Stacks address to query

        Returns:
            Dictionary containing STX balance and token balances:
            {
                'stx': {
                    'balance': '1000000',  # in microSTX
                    'total_sent': '0',
                    'total_received': '1000000',
                    ...
                },
                'fungible_tokens': {...},
                'non_fungible_tokens': {...}
            }

        Raises:
            RemoteError: If the request fails
        """
        return self._make_request(f'extended/v1/address/{address}/balances')

    def get_account_transactions(
            self,
            address: StacksAddress,
            limit: int = 50,
            offset: int = 0,
    ) -> dict[str, Any]:
        """Get transactions for a Stacks address.

        Args:
            address: The Stacks address to query
            limit: Maximum number of transactions to return (default 50)
            offset: Number of transactions to skip (for pagination)

        Returns:
            Dictionary containing transaction list and pagination info

        Raises:
            RemoteError: If the request fails
        """
        return self._make_request(
            f'extended/v1/address/{address}/transactions',
            params={'limit': limit, 'offset': offset},
        )

    def get_transaction(self, tx_id: str) -> dict[str, Any]:
        """Get a single transaction by its ID.

        Args:
            tx_id: The transaction ID (hash)

        Returns:
            Transaction data including events

        Raises:
            RemoteError: If the request fails
        """
        return self._make_request(f'extended/v1/tx/{tx_id}')

    def get_transaction_events(self, tx_id: str) -> list[dict]:
        """Get events for a transaction.

        Args:
            tx_id: The transaction ID (hash)

        Returns:
            List of events from the transaction

        Raises:
            RemoteError: If the request fails
        """
        response = self.get_transaction(tx_id)
        return response.get('events', [])

    def get_token_metadata(self, contract_principal: str) -> StacksTokenMetadata | None:
        """Fetch token metadata from the Hiro Token Metadata API.

        Args:
            contract_principal: The contract principal (e.g., SP3K8BC...sbtc-token)

        Returns:
            StacksTokenMetadata if found, None otherwise

        Note:
            This uses the Hiro Token Metadata API which is separate from the main API.
            The metadata includes name, symbol, decimals, and image URLs.
        """
        url = f'{HIRO_METADATA_API_URL}/ft/{contract_principal}'

        # Update headers with API key
        api_key = self._get_api_key()
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if api_key:
            headers['x-api-key'] = api_key

        try:
            response = requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)

            if response.status_code == 404:
                log.debug(f'No metadata found for token {contract_principal}')
                return None

            if response.status_code != 200:
                log.warning(
                    f'Failed to fetch metadata for {contract_principal}: '
                    f'{response.status_code} {response.text}',
                )
                return None

            data = response.json()

            # Extract metadata from response
            name = data.get('name')
            symbol = data.get('symbol')
            decimals = data.get('decimals')

            if not name or not symbol:
                log.debug(
                    f'Incomplete metadata for {contract_principal}: '
                    f'name={name}, symbol={symbol}',
                )
                return None

            return StacksTokenMetadata(
                name=name,
                symbol=symbol,
                decimals=decimals if decimals is not None else 6,  # Default to 6 like STX
            )

        except requests.RequestException as e:
            log.warning(f'Error fetching token metadata for {contract_principal}: {e}')
            return None
        except (KeyError, ValueError) as e:
            log.warning(f'Error parsing token metadata for {contract_principal}: {e}')
            return None
