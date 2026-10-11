"""Button platform for Qista integration."""
from __future__ import annotations

import logging
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import QistaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Qista buttons from config entry."""
    coordinator: QistaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[QistaConsumableResetButton] = []
    devices = coordinator.data.get("devices", {})

    for device_id, device_data in devices.items():
        entities.append(
            QistaConsumableResetButton(
                coordinator=coordinator,
                device_id=device_id,
                consumable_type="co2",
                name="Réinitialiser compteur CO2",
                icon="mdi:gas-cylinder",
            )
        )
        entities.append(
            QistaConsumableResetButton(
                coordinator=coordinator,
                device_id=device_id,
                consumable_type="bait",
                name="Réinitialiser compteur Leurre",
                icon="mdi:flask-empty-outline",
            )
        )

    async_add_entities(entities)


class QistaConsumableResetButton(
    CoordinatorEntity[QistaDataUpdateCoordinator], ButtonEntity
):
    """Button to reset consumables for a Qista trap."""

    def __init__(
        self,
        coordinator: QistaDataUpdateCoordinator,
        device_id: str,
        consumable_type: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.device_id = device_id
        self._consumable_type = consumable_type
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"qista_{device_id}_reset_{consumable_type}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        device_data = self.coordinator.data.get("devices", {}).get(self.device_id, {})
        return DeviceInfo(
            identifiers={(DOMAIN, str(self.device_id))},
            name=device_data.get("name", f"Borne Qista {self.device_id}"),
            manufacturer="QISTA",
            model=device_data.get("type", "Borne anti-moustique"),
            serial_number=device_data.get("reference"),
        )

    async def async_press(self) -> None:
        """Handle button press to reset consumable."""
        is_co2 = self._consumable_type == "co2"
        is_bait = self._consumable_type == "bait"
        _LOGGER.info(
            "Resetting consumable '%s' on BAM %s", self._consumable_type, self.device_id
        )
        await self.coordinator.client.reset_consumables(
            bam_id=self.device_id, co2=is_co2, bait=is_bait
        )
        await self.coordinator.async_request_refresh()
