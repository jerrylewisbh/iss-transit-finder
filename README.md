# ISS Transit Finder for Home Assistant

A custom integration that calculates International Space Station (ISS) transits across the Sun and Moon locally using your Home Assistant coordinates. Powered by Skyfield.

## Installation

1. Copy the `custom_components/iss_transit` directory to your Home Assistant `config/custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration** and search for "ISS Transit Finder".

## Sensors

* `sensor.next_iss_sun_transit`
* `sensor.next_iss_moon_transit`
