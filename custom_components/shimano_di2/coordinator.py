"""Data update coordinator for the Shimano Di2 integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from bleak import BleakClient, BleakError
from bleak_retry_connector import establish_connection

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    BATTERY_LEVEL_UUID,
    CONNECT_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    FIRMWARE_REVISION_UUID,
    MANUFACTURER_NAME_UUID,
    SERIAL_NUMBER_UUID,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class ShimanoDi2Data:
    """Parsed data read from the Di2 unit."""

    battery_level: int | None = None
    manufacturer: str | None = None
    serial_number: str | None = None
    firmware_revision: str | None = None


type ShimanoDi2ConfigEntry = ConfigEntry[ShimanoDi2Coordinator]


class ShimanoDi2Coordinator(DataUpdateCoordinator[ShimanoDi2Data]):
    """Connect to the Di2 unit over BLE and read its battery level."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ShimanoDi2ConfigEntry,
        address: str,
        device_name: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} {address}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            config_entry=entry,
        )
        self.address = address
        self.device_name = device_name
        self.data = ShimanoDi2Data()
        self._static_info_read = False

    async def _async_read_static_info(
        self, client: BleakClient, data: ShimanoDi2Data
    ) -> None:
        """Read the device-information characteristics once."""
        for attr, uuid in (
            ("manufacturer", MANUFACTURER_NAME_UUID),
            ("serial_number", SERIAL_NUMBER_UUID),
            ("firmware_revision", FIRMWARE_REVISION_UUID),
        ):
            try:
                raw = await client.read_gatt_char(uuid)
            except BleakError as err:
                _LOGGER.debug("Could not read %s (%s): %s", attr, uuid, err)
                continue
            setattr(data, attr, raw.decode("utf-8", "replace").strip("\x00").strip())
        self._static_info_read = True

    async def _async_update_data(self) -> ShimanoDi2Data:
        """Connect to the Di2 unit, read the battery level and disconnect."""
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if ble_device is None:
            raise UpdateFailed(
                f"Shimano Di2 {self.address} is not currently in Bluetooth range"
            )

        # Carry previously-read static info forward across updates.
        data = ShimanoDi2Data(
            battery_level=self.data.battery_level,
            manufacturer=self.data.manufacturer,
            serial_number=self.data.serial_number,
            firmware_revision=self.data.firmware_revision,
        )

        try:
            client = await establish_connection(
                BleakClient,
                ble_device,
                self.address,
                timeout=CONNECT_TIMEOUT,
            )
        except (BleakError, TimeoutError) as err:
            raise UpdateFailed(f"Could not connect to Di2 unit: {err}") from err

        try:
            raw_battery = await client.read_gatt_char(BATTERY_LEVEL_UUID)
            if raw_battery:
                data.battery_level = int(raw_battery[0])

            if not self._static_info_read:
                await self._async_read_static_info(client, data)
        except BleakError as err:
            raise UpdateFailed(f"Could not read Di2 data: {err}") from err
        finally:
            await client.disconnect()

        return data
