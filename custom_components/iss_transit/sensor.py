from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType
from .const import DOMAIN, CONF_NAME

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    site_name = entry.data.get(CONF_NAME, "ISS Transit")
    
    async_add_entities([
        ISSTransitSensor(coordinator, entry.entry_id, site_name, "sun"), 
        ISSTransitSensor(coordinator, entry.entry_id, site_name, "moon")
    ])

class ISSTransitSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry_id, site_name, target):
        super().__init__(coordinator)
        self.target = target
        self._site_name = site_name
        self._entry_id = entry_id
        
        # e.g., "Cabin Next ISS Sun Transit"
        self._attr_name = f"{site_name} Next ISS {target.capitalize()} Transit"
        self._attr_unique_id = f"iss_transit_{entry_id}_{target}"
        self._attr_icon = "mdi:weather-sunny" if target == "sun" else "mdi:moon-waning-crescent"

    @property
    def device_info(self):
        """Return device information to group sensors together."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": f"ISS Transit Finder ({self._site_name})",
            "manufacturer": "Custom Integration",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def native_value(self):
        if self.coordinator.data and self.target in self.coordinator.data:
            data = self.coordinator.data[self.target]
            return data.get("time") if data else "No transits in 21 days"
        return "Unknown"

    @property
    def extra_state_attributes(self):
        if self.coordinator.data and self.target in self.coordinator.data:
            return self.coordinator.data[self.target] or {}
        return {}
