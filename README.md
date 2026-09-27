# Shimano Di2 for Home Assistant

A custom [Home Assistant](https://www.home-assistant.io/) integration that reads
**Shimano Di2** electronic groupset data over **Bluetooth Low Energy (BLE)**.

It exposes the Di2 system's **battery level** as a sensor, plus device
information (manufacturer, serial number, firmware version), using Home
Assistant's native Bluetooth stack.

## Supported hardware

Verified against:

- **Dura-Ace Di2 12-speed** rear derailleur **RD-R9250** (advertises as `RDR9250 ...`)

Should also work with other modern Di2 units that expose the standard BLE
**Battery Service** (`0x180F`) and advertise any of the following (used for
auto-discovery):

- a local name starting with `RDR` (e.g. `RDR9250 ...`)
- the Shimano manufacturer ID (`0x044A` / `1098`)
- a service UUID on Shimano's `SHIMANO_BLE` base
  (`000018ef-5348-494d-414e-4f5f424c4500` / `000018ff-...`)

This includes:

- **105 Di2** rear derailleur **RD-R7150**
- Ultegra Di2 **RD-R8150**

> The integration reads the **standard** GATT Battery Level characteristic
> (`0x2A19`), which the Di2 unit exposes without authentication. It does **not**
> use Shimano's proprietary/authenticated `SHIMANO_BLE` services, so it does not
> require pairing with the E-TUBE app.

## Requirements

- Home Assistant with a working **Bluetooth adapter** or an **ESPHome Bluetooth
  Proxy** within range of the bike.
- The Di2 unit must be **within BLE range** of Home Assistant. Since Di2 only
  serves battery data over an active connection, keep the bike stored near the
  Home Assistant host (or a Bluetooth proxy).

## Installation

### HACS (recommended)

1. In HACS, go to **Integrations → ⋮ → Custom repositories**.
2. Add this repository URL and choose category **Integration**.
3. Search for **Shimano Di2**, install it, and restart Home Assistant.

### Manual

1. Copy the `custom_components/shimano_di2` folder into your Home Assistant
   `config/custom_components/` directory.
2. Restart Home Assistant.

## Setup

1. Wake the Di2 unit (press a shift button) so it advertises over BLE.
2. Home Assistant should auto-discover it — go to
   **Settings → Devices & Services** and confirm the discovered **Shimano Di2**
   device.
3. Discovery only happens while the unit is awake and advertising, and requires
   a **connectable** adapter (local Bluetooth or an *active* ESPHome proxy —
   passive proxies are ignored). After installing or updating the integration,
   restart Home Assistant so the new Bluetooth matchers are loaded.
4. If it isn't auto-discovered, click **Add Integration**, search for
   **Shimano Di2**, and pick your unit from the list.

## Entities

| Entity | Description |
| ------ | ----------- |
| `sensor.<device>_battery` | Di2 battery level (%) |

Device info (manufacturer, model, serial number, firmware) is attached to the
device page.

## Notes & limitations

- **Battery only.** Gear position and shift data live behind Shimano's
  authenticated proprietary services and are not read by this integration.
- **Polling.** Battery is polled every 30 minutes by default (it changes
  slowly). The connection is opened, read, and closed each cycle so the E-TUBE
  app can still connect when needed.
- If the bike is out of BLE range, the battery sensor becomes **unavailable**
  until it returns.

## How it was built

The GATT layout was captured with a BLE scan of the RD-R9250, which revealed the
standard `0x180F` Battery Service with a readable, notify-capable
`0x2A19` Battery Level characteristic (reporting e.g. `0x32` = 50%).

## Disclaimer

Not affiliated with or endorsed by Shimano. "Di2", "Dura-Ace", "Ultegra" and
"105" are trademarks of Shimano Inc.
