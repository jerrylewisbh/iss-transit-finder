from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from .calculator import calculate_transits
from .const import DOMAIN, CONF_LATITUDE, CONF_LONGITUDE, CONF_ELEVATION

_LOGGER = logging.getLogger(__name__)

class ISSTransitCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry):
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(hours=12),
        )
        self.entry = entry

    async def _async_update_data(self):
        try:
            # Use the coordinates specified in this specific config entry
            lat = self.entry.data.get(CONF_LATITUDE)
            lon = self.entry.data.get(CONF_LONGITUDE)
            elev = self.entry.data.get(CONF_ELEVATION)
            
            return await self.hass.async_add_executor_job(
                calculate_transits, lat, lon, elev
            )
        except Exception as err:
            _LOGGER.error("Error calculating transits: %s", err)
            raise UpdateFailed(f"Error calculating transits: {err}")
