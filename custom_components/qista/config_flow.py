"""Config flow for Qista integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import QistaApiClient, QistaAuthError, QistaConnectionError
from .const import CONF_GRAPHQL_URL, DEFAULT_GRAPHQL_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_GRAPHQL_URL, default=DEFAULT_GRAPHQL_URL): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate user credentials against Qista GraphQL API."""
    session = async_get_clientsession(hass)
    client = QistaApiClient(
        session=session,
        email=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        endpoint_url=data.get(CONF_GRAPHQL_URL, DEFAULT_GRAPHQL_URL),
    )

    if not await client.authenticate():
        raise QistaAuthError("Authentication failed")

    return {"title": f"Qista ({data[CONF_USERNAME]})"}


class QistaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Qista."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except QistaAuthError:
                errors["base"] = "invalid_auth"
            except QistaConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
