from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ISSTransitSensor(coordinator, "sun"), ISSTransitSensor(coordinator, "moon")])

class ISSTransitSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, target):
        super().__init__(coordinator)
        self.target = target
        self._attr_name = f"Next ISS {target.capitalize()} Transit"
        self._attr_unique_id = f"iss_transit_{target}"
        self._attr_icon = "mdi:weather-sunny" if target == "sun" else "mdi:moon-waning-crescent"

    @property
    def native_value(self):
        if self.coordinator.data and self.target in self.coordinator.data:
            return self.coordinator.data[self.target].get("time")
        return "Unknown"

    @property
    def extra_state_attributes(self):
        if self.coordinator.data and self.target in self.coordinator.data:
            return self.coordinator.data[self.target]
        return {}
