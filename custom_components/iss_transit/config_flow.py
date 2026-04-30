import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE, CONF_ELEVATION

class ISSTransitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Create a unique ID based on the coordinates to prevent exact duplicates
            await self.async_set_unique_id(f"{user_input[CONF_LATITUDE]}_{user_input[CONF_LONGITUDE]}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input[CONF_NAME], data=user_input
            )

        # Default to the Home Assistant configured location
        default_lat = self.hass.config.latitude
        default_lon = self.hass.config.longitude
        default_elev = self.hass.config.elevation

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Home"): str,
                vol.Required(CONF_LATITUDE, default=default_lat): vol.Coerce(float),
                vol.Required(CONF_LONGITUDE, default=default_lon): vol.Coerce(float),
                vol.Required(CONF_ELEVATION, default=default_elev): vol.Coerce(float),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
