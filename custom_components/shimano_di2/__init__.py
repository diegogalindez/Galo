"""The Shimano Di2 integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import ShimanoDi2ConfigEntry, ShimanoDi2Coordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, entry: ShimanoDi2ConfigEntry
) -> bool:
    """Set up Shimano Di2 from a config entry."""
    address = entry.unique_id
    assert address is not None

    coordinator = ShimanoDi2Coordinator(hass, entry, address, entry.title)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ShimanoDi2ConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
