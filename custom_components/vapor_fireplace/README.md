# Water Vapor Bluetooth Fireplace

This Home Assistant integration allows you to control your Water Vapour Bluetooth Fireplace through Home Assistant.

## Installation

### HACS (Home Assistant Community Store)

1. Make sure [HACS](https://hacs.xyz/) is installed.
2. Add this repository as a custom repository in HACS:
   - Go to HACS > Integrations
   - Click the three dots in the top right corner
   - Select "Custom repositories"
   - Add the URL to this repository and select "Integration" as the category
3. Click "Install" after searching for "Vapor Bluetooth Fireplace" in HACS.
4. Restart Home Assistant.

### Manual Installation

1. Download this repository.
2. Copy the `custom_components/vapor_fireplace` directory to your Home Assistant's `custom_components` directory.
3. Restart Home Assistant.

## Configuration

1. Go to Configuration > Integrations in the Home Assistant UI.
2. Click "Add Integration" and search for "Water Vapor Bluetooth Fireplace".
3. Follow the configuration flow and enter:
   - The IP address of your fireplace server
   - The port number of your fireplace server

## Usage

The fireplace will appear as a light entity in Home Assistant with the following features:

- Turn on/off the fireplace
- Adjust flame height (via brightness control)
- Change flame speed (via effects)

### Services

This integration also provides two custom services:

#### `water_vapour_bluetooth_fireplace.set_flame_height`

Set the flame height of the fireplace (values 1-7).

| Parameter | Description |
|-----------|-------------|
| `entity_id` | The entity ID of your fireplace |
| `flame_height` | Flame height value (1-7) |

#### `water_vapour_bluetooth_fireplace.set_flame_speed`

Set the flame speed of the fireplace (values 1-7).

| Parameter | Description |
|-----------|-------------|
| `entity_id` | The entity ID of your fireplace |
| `flame_speed` | Flame speed value (1-7) |

## Control Endpoints

The integration uses the following control endpoints:

- Turn On: `http://ip:port/control/on`
- Turn Off: `http://ip:port/control/off`
- Set Flame Height: `http://ip:port/control/flame_height/n` (n = 1-7)
- Set Flame Speed: `http://ip:port/control/flame_speed/n` (n = 1-7)

## Troubleshooting

- Make sure your fireplace server is running and accessible from your Home Assistant instance.
- Check that the correct IP and port are configured.
- Enable debug logging for this integration if you encounter issues.

## Support

For issues, feature requests, or questions, please open an issue on GitHub. 