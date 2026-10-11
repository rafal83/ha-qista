"""GraphQL API Client for Qista mosquito traps (modern cloud API)."""
from __future__ import annotations

import logging
from typing import Any
import aiohttp
import async_timeout

from .const import DEFAULT_GRAPHQL_URL

_LOGGER = logging.getLogger(__name__)

LOGIN_MUTATION = """
mutation login($signInInput: SignInInput!, $platform: String) {
  signIn(signInInput: $signInInput, platform: $platform) {
    accessToken
    refreshToken
    user {
      id
      email
      fullname
    }
  }
}
"""

BAMS_QUERY = """
query bams {
  bams {
    id
    reference
    internalCustomName
    externalCustomName
    type
    workingStatus
    operatingStatus
    simStatus
    isConnected
    lat
    lng
    mosquitoeCatchDay
    mosquitoeCatchWeek
    mosquitoeCatchTotal
    consumablesRemaining {
      bait {
        hours
        days
      }
      co2 {
        hours
        days
      }
    }
    loadedCo2BottleLabel
  }
}
"""

RESET_CONSUMABLES_MUTATION = """
mutation resetBamConsumables($resetBamConsumablesDto: ResetBamConsumablesDto!) {
  resetBamConsumables(resetBamConsumablesDto: $resetBamConsumablesDto)
}
"""


class QistaAuthError(Exception):
    """Exception raised when authentication fails."""


class QistaConnectionError(Exception):
    """Exception raised when connection to the Qista API fails."""


class QistaApiClient:
    """Client for Qista GraphQL Cloud API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        email: str,
        password: str,
        endpoint_url: str = DEFAULT_GRAPHQL_URL,
    ) -> None:
        """Initialize the client."""
        self._session = session
        self._email = email
        self._password = password
        self._endpoint_url = endpoint_url
        self._access_token: str | None = None
        self._user_info: dict[str, Any] | None = None

    @property
    def user_info(self) -> dict[str, Any] | None:
        """Return authenticated user info."""
        return self._user_info

    async def _execute_graphql(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        """Execute a GraphQL query/mutation."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 14) Qista/2.4.0",
        }

        if authenticated:
            if not self._access_token:
                await self.authenticate()
            headers["Authorization"] = f"Bearer {self._access_token}"

        payload: dict[str, Any] = {"query": query}
        if operation_name:
            payload["operationName"] = operation_name
        if variables:
            payload["variables"] = variables

        try:
            async with async_timeout.timeout(15):
                async with self._session.post(
                    self._endpoint_url,
                    json=payload,
                    headers=headers,
                ) as response:
                    if response.status == 401:
                        # Token expired, retry once
                        self._access_token = None
                        if authenticated:
                            await self.authenticate()
                            headers["Authorization"] = f"Bearer {self._access_token}"
                            async with self._session.post(
                                self._endpoint_url,
                                json=payload,
                                headers=headers,
                            ) as retry_response:
                                data = await retry_response.json()
                                return self._handle_graphql_response(data)
                        raise QistaAuthError("Invalid credentials or expired session.")

                    if response.status >= 400:
                        body = await response.text()
                        raise QistaConnectionError(f"HTTP {response.status}: {body}")

                    data = await response.json()
                    return self._handle_graphql_response(data)

        except aiohttp.ClientError as err:
            raise QistaConnectionError(f"Network error communicating with Qista: {err}") from err
        except TimeoutError as err:
            raise QistaConnectionError("Timeout communicating with Qista API.") from err

    def _handle_graphql_response(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle errors in GraphQL response body."""
        if "errors" in data and data["errors"]:
            error_msg = data["errors"][0].get("message", "Unknown GraphQL error")
            _LOGGER.error("GraphQL error: %s", data["errors"])
            raise QistaConnectionError(f"GraphQL error: {error_msg}")
        return data.get("data", {})

    async def authenticate(self) -> bool:
        """Authenticate using signIn GraphQL mutation."""
        try:
            data = await self._execute_graphql(
                LOGIN_MUTATION,
                variables={
                    "signInInput": {
                        "email": self._email,
                        "password": self._password,
                    },
                    "platform": "android",
                },
                operation_name="login",
                authenticated=False,
            )
            sign_in_data = data.get("signIn", {})
            self._access_token = sign_in_data.get("accessToken")
            self._user_info = sign_in_data.get("user")
            return self._access_token is not None
        except Exception as err:
            _LOGGER.error("Authentication failed: %s", err)
            raise QistaAuthError(f"Invalid email or password: {err}") from err

    async def get_bams(self) -> list[dict[str, Any]]:
        """Fetch all mosquito traps (BAMs) linked to user account."""
        data = await self._execute_graphql(BAMS_QUERY)
        return data.get("bams", [])

    async def reset_consumables(
        self, bam_id: str, co2: bool = False, bait: bool = False
    ) -> bool:
        """Reset consumables date counter for a BAM."""
        variables = {
            "resetBamConsumablesDto": {
                "bamId": bam_id,
                "resetCo2": co2,
                "resetBait": bait,
            }
        }
        await self._execute_graphql(
            RESET_CONSUMABLES_MUTATION,
            variables=variables,
            operation_name="resetBamConsumables",
        )
        return True
