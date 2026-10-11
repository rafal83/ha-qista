"""The Qista Mosquito Trap integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import QistaApiClient
from .const import CONF_GRAPHQL_URL, DEFAULT_GRAPHQL_URL, DOMAIN
from .coordinator import QistaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Qista from a config entry."""
    session = async_get_clientsession(hass)

    client = QistaApiClient(
        session=session,
        email=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        endpoint_url=entry.data.get(CONF_GRAPHQL_URL, DEFAULT_GRAPHQL_URL),
    )

    coordinator = QistaDataUpdateCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
