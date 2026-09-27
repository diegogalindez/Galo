"""Constants for the Shimano Di2 integration."""

from __future__ import annotations

DOMAIN = "shimano_di2"

# Bluetooth SIG company identifier for Shimano (0x044A).
SHIMANO_MANUFACTURER_ID = 1098

# Standard GATT characteristic UUIDs exposed by the Di2 unit.
BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"
MANUFACTURER_NAME_UUID = "00002a29-0000-1000-8000-00805f9b34fb"
SERIAL_NUMBER_UUID = "00002a25-0000-1000-8000-00805f9b34fb"
FIRMWARE_REVISION_UUID = "00002a26-0000-1000-8000-00805f9b34fb"

# Battery changes very slowly on a Di2 system, so we poll infrequently
# to avoid holding the BLE connection open (E-TUBE app needs it too).
DEFAULT_SCAN_INTERVAL = 1800  # seconds (30 minutes)

# How long to wait for a single connect+read cycle before giving up.
CONNECT_TIMEOUT = 30  # seconds
