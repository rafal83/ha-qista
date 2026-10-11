"""Binary sensor platform for Qista integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import QistaDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class QistaBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing Qista binary sensor entities."""

    is_on_fn: Callable[[dict[str, Any]], bool | None]


BINARY_SENSOR_TYPES: tuple[QistaBinarySensorEntityDescription, ...] = (
    QistaBinarySensorEntityDescription(
        key="is_connected",
        translation_key="is_connected",
        name="Connectivité",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        is_on_fn=lambda device: device.get("is_connected", True),
    ),
    QistaBinarySensorEntityDescription(
        key="is_low_bait",
        translation_key="is_low_bait",
        name="Niveau leurre critique",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:flask-empty-outline",
        is_on_fn=lambda device: (
            device.get("bait_remaining_days") is not None
            and device.get("bait_remaining_days", 999) <= 3
        ),
    ),
    QistaBinarySensorEntityDescription(
        key="is_low_co2",
        translation_key="is_low_co2",
        name="Niveau CO2 critique",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:gas-cylinder",
        is_on_fn=lambda device: (
            device.get("co2_remaining_days") is not None
            and device.get("co2_remaining_days", 999) <= 3
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Qista binary sensors from config entry."""
    coordinator: QistaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[QistaBinarySensor] = []
    devices = coordinator.data.get("devices", {})

    for device_id, device_data in devices.items():
        for description in BINARY_SENSOR_TYPES:
            entities.append(QistaBinarySensor(coordinator, device_id, description))

    async_add_entities(entities)


class QistaBinarySensor(
    CoordinatorEntity[QistaDataUpdateCoordinator], BinarySensorEntity
):
    """Representation of a Qista trap binary sensor."""

    entity_description: QistaBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: QistaDataUpdateCoordinator,
        device_id: str,
        description: QistaBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.device_id = device_id
        self.entity_description = description
        self._attr_unique_id = f"qista_{device_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the device."""
        device_data = self.coordinator.data.get("devices", {}).get(self.device_id, {})
        return DeviceInfo(
            identifiers={(DOMAIN, str(self.device_id))},
            name=device_data.get("name", f"Borne Qista {self.device_id}"),
            manufacturer="QISTA",
            model=device_data.get("type", "Borne anti-moustique"),
            serial_number=device_data.get("reference"),
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        device_data = self.coordinator.data.get("devices", {}).get(self.device_id, {})
        return self.entity_description.is_on_fn(device_data)

