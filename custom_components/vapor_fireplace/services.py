"""Services for Water Vapour Bluetooth Fireplace integration."""
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN

from .const import (
    DOMAIN,
    SERVICE_SET_FLAME_HEIGHT,
    SERVICE_SET_FLAME_SPEED,
    ATTR_FLAME_HEIGHT,
    ATTR_FLAME_SPEED,
)

_LOGGER = logging.getLogger(__name__)

SET_FLAME_HEIGHT_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Required(ATTR_FLAME_HEIGHT): vol.All(vol.Coerce(int), vol.Range(min=1, max=7))
    }
)

SET_FLAME_SPEED_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Required(ATTR_FLAME_SPEED): vol.All(vol.Coerce(int), vol.Range(min=1, max=7))
    }
)


async def async_setup_services(hass: HomeAssistant):
    """Set up services for Water Vapour Bluetooth Fireplace integration."""
    
    async def async_set_flame_height(call: ServiceCall):
        """Service to set the flame height."""
        entity_id = call.data["entity_id"]
        flame_height = call.data[ATTR_FLAME_HEIGHT]
        
        # Convert flame height (1-7) to brightness (1-255)
        brightness = int((flame_height / 7) * 255)
        
        # Call the light.turn_on service with the calculated brightness
        await hass.services.async_call(
            LIGHT_DOMAIN, 
            "turn_on", 
            {"entity_id": entity_id, "brightness": brightness},
            blocking=True,
        )
    
    async def async_set_flame_speed(call: ServiceCall):
        """Service to set the flame speed."""
        entity_id = call.data["entity_id"]
        flame_speed = call.data[ATTR_FLAME_SPEED]
        
        # Find the effect name that corresponds to the flame speed
        from .light import FLAME_EFFECTS
        
        effect_name = None
        for name, speed in FLAME_EFFECTS.items():
            if speed == flame_speed:
                effect_name = name
                break
        
        if effect_name is None:
            _LOGGER.error("Invalid flame speed: %s", flame_speed)
            return
        
        # Call the light.turn_on service with the effect
        await hass.services.async_call(
            LIGHT_DOMAIN, 
            "turn_on", 
            {"entity_id": entity_id, "effect": effect_name},
            blocking=True,
        )
    
    hass.services.async_register(
        DOMAIN, SERVICE_SET_FLAME_HEIGHT, async_set_flame_height, schema=SET_FLAME_HEIGHT_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_SET_FLAME_SPEED, async_set_flame_speed, schema=SET_FLAME_SPEED_SCHEMA
    )


async def async_unload_services(hass: HomeAssistant):
    """Unload services for Water Vapour Bluetooth Fireplace integration."""
    hass.services.async_remove(DOMAIN, SERVICE_SET_FLAME_HEIGHT)
    hass.services.async_remove(DOMAIN, SERVICE_SET_FLAME_SPEED) 