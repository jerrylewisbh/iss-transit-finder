# ISS Transit Finder for Home Assistant

A custom integration that calculates International Space Station (ISS) transits across the Sun and Moon locally using your Home Assistant coordinates. Powered by Skyfield.

## Installation

### Method 1: HACS (Recommended)

1. Open **HACS** in your Home Assistant instance.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add the URL of this repository and select **Integration** as the category.
4. Click **Add**, then search for "ISS Transit Finder" and click **Download**.
5. Restart Home Assistant.
6. Go to **Settings > Devices & Services > Add Integration** and search for "ISS Transit Finder" to configure your location(s).

### Method 2: Manual

1. Copy the `custom_components/iss_transit` directory to your Home Assistant `config/custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration** and search for "ISS Transit Finder" to configure your location(s).

## Configuration

You can install this integration multiple times to track transits from different locations (e.g., "Home", "Observatory", "Cabin"). During setup, you will be prompted to provide:
* **Name**: The name of the location.
* **Latitude & Longitude**: The coordinates for the calculation.
* **Elevation**: Altitude in meters.

## Sensors

Each location will generate grouped sensors under a single Device:
* `sensor.[location_name]_next_iss_sun_transit`
* `sensor.[location_name]_next_iss_moon_transit`
