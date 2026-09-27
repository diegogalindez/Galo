"""Sensor platform for the Shimano Di2 integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import ShimanoDi2ConfigEntry, ShimanoDi2Coordinator

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="battery_level",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ShimanoDi2ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Shimano Di2 sensors from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        ShimanoDi2Sensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class ShimanoDi2Sensor(CoordinatorEntity[ShimanoDi2Coordinator], SensorEntity):
    """Representation of a Shimano Di2 sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ShimanoDi2Coordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.address}_{description.key}"
        self._attr_translation_key = description.key
        self._attr_device_info = DeviceInfo(
            connections={(CONNECTION_BLUETOOTH, coordinator.address)},
            manufacturer=coordinator.data.manufacturer or "Shimano",
            model="Di2",
            name=coordinator.device_name,
            serial_number=coordinator.data.serial_number,
            sw_version=coordinator.data.firmware_revision,
        )

    @property
    def native_value(self) -> int | None:
        """Return the current value of the sensor."""
        return getattr(self.coordinator.data, self.entity_description.key)

    @property
    def available(self) -> bool:
        """Return True if the coordinator has data and last update succeeded."""
        return (
            super().available
            and getattr(self.coordinator.data, self.entity_description.key)
            is not None
        )
