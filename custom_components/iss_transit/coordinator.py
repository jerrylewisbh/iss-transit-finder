from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from .calculator import calculate_transits
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ISSTransitCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=12),
        )
        self.entry = entry

    async def _async_update_data(self):
        try:
            lat = self.hass.config.latitude
            lon = self.hass.config.longitude
            elev = self.hass.config.elevation
            return await self.hass.async_add_executor_job(
                calculate_transits, lat, lon, elev
            )
        except Exception as err:
            raise UpdateFailed(f"Error calculating transits: {err}")
