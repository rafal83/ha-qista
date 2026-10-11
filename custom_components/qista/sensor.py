"""Sensor platform for Qista integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import QistaDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class QistaSensorEntityDescription(SensorEntityDescription):
    """Class describing Qista sensor entities."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSOR_TYPES: tuple[QistaSensorEntityDescription, ...] = (
    QistaSensorEntityDescription(
        key="mosquitoe_catch_day",
        translation_key="mosquitoe_catch_day",
        name="Moustiques capturés aujourd'hui",
        icon="mdi:bug",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="moustiques",
        value_fn=lambda device: device.get("mosquitoe_catch_day"),
    ),
    QistaSensorEntityDescription(
        key="mosquitoe_catch_week",
        translation_key="mosquitoe_catch_week",
        name="Moustiques capturés (7 jours)",
        icon="mdi:chart-bell-curve",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="moustiques",
        value_fn=lambda device: device.get("mosquitoe_catch_week"),
    ),
    QistaSensorEntityDescription(
        key="mosquitoe_catch_total",
        translation_key="mosquitoe_catch_total",
        name="Total des moustiques capturés",
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="moustiques",
        value_fn=lambda device: device.get("mosquitoe_catch_total"),
    ),
    QistaSensorEntityDescription(
        key="working_status",
        translation_key="working_status",
        name="Statut de marche",
        icon="mdi:power",
        value_fn=lambda device: device.get("working_status"),
    ),
    QistaSensorEntityDescription(
        key="operating_status",
        translation_key="operating_status",
        name="Statut de fonctionnement",
        icon="mdi:cog",
        value_fn=lambda device: device.get("operating_status"),
    ),
    QistaSensorEntityDescription(
        key="sim_status",
        translation_key="sim_status",
        name="Statut SIM",
        icon="mdi:sim",
        value_fn=lambda device: device.get("sim_status"),
    ),
    QistaSensorEntityDescription(
        key="bait_remaining_days",
        translation_key="bait_remaining_days",
        name="Leurre restant",
        icon="mdi:flask-round-bottom",
        native_unit_of_measurement="j",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.get("bait_remaining_days"),
    ),
    QistaSensorEntityDescription(
        key="co2_remaining_days",
        translation_key="co2_remaining_days",
        name="CO2 restant",
        icon="mdi:gas-cylinder",
        native_unit_of_measurement="j",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.get("co2_remaining_days"),
    ),
    QistaSensorEntityDescription(
        key="loaded_co2_bottle_label",
        translation_key="loaded_co2_bottle_label",
        name="Type de bouteille CO2",
        icon="mdi:tag-text-outline",
        value_fn=lambda device: device.get("loaded_co2_bottle_label"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Qista sensors from config entry."""
    coordinator: QistaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[QistaSensor] = []
    devices = coordinator.data.get("devices", {})

    for device_id, device_data in devices.items():
        for description in SENSOR_TYPES:
            entities.append(QistaSensor(coordinator, device_id, description))

    async_add_entities(entities)


class QistaSensor(CoordinatorEntity[QistaDataUpdateCoordinator], SensorEntity):
    """Representation of a Qista trap sensor."""

    entity_description: QistaSensorEntityDescription

    def __init__(
        self,
        coordinator: QistaDataUpdateCoordinator,
        device_id: str,
        description: QistaSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
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
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        device_data = self.coordinator.data.get("devices", {}).get(self.device_id, {})
        return self.entity_description.value_fn(device_data)
