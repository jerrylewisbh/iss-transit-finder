from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.components.sensor import SensorDeviceClass
import datetime
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
        
        self._attr_name = f"{site_name} Next ISS {target.capitalize()} Transit"
        self._attr_unique_id = f"iss_transit_{entry_id}_{target}"
        self._attr_icon = "mdi:weather-sunny" if target == "sun" else "mdi:moon-waning-crescent"
        
        # Use the official enum for device class
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def device_info(self):
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
            if data and data.get("time"):
                # HA Timestamp class absolutely requires a native Python datetime object,
                # NOT a string, when returning native_value.
                try:
                    return datetime.datetime.fromisoformat(data.get("time"))
                except ValueError:
                    return None
        return None

    @property
    def extra_state_attributes(self):
        if self.coordinator.data and self.target in self.coordinator.data:
            data = self.coordinator.data[self.target]
            if data:
                return {
                    "separation_degrees": data.get("separation_degrees"),
                    "altitude": data.get("altitude"),
                    "azimuth": data.get("azimuth")
                }
        return {"status": "No transits in 21 days"}
