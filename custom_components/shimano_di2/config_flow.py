"""Config flow for the Shimano Di2 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS

from .const import (
    DOMAIN,
    SHIMANO_BASE_UUID_SUFFIX,
    SHIMANO_DI2_NAME_PREFIX,
    SHIMANO_MANUFACTURER_ID,
)


def _is_shimano_di2(info: BluetoothServiceInfoBleak) -> bool:
    """Return True if the advertisement looks like a Shimano Di2 unit."""
    if SHIMANO_MANUFACTURER_ID in info.manufacturer_data:
        return True
    if (info.name or "").upper().startswith(SHIMANO_DI2_NAME_PREFIX):
        return True
    uuids = (*info.service_uuids, *info.service_data)
    return any(uuid.lower().endswith(SHIMANO_BASE_UUID_SUFFIX) for uuid in uuids)


class ShimanoDi2ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Shimano Di2."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle a device discovered by the Bluetooth integration."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {"name": discovery_info.name}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm adding a discovered device."""
        assert self._discovery_info is not None
        if user_input is not None:
            return self.async_create_entry(
                title=self._discovery_info.name, data={}
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={"name": self._discovery_info.name},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the manual setup step (pick from discovered devices)."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            info = self._discovered_devices[address]
            return self.async_create_entry(title=info.name, data={})

        current_addresses = self._async_current_ids()
        for info in async_discovered_service_info(self.hass, connectable=True):
            address = info.address
            if address in current_addresses or address in self._discovered_devices:
                continue
            if _is_shimano_di2(info):
                self._discovered_devices[address] = info

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(
                        {
                            address: f"{info.name} ({address})"
                            for address, info in self._discovered_devices.items()
                        }
                    )
                }
            ),
        )
