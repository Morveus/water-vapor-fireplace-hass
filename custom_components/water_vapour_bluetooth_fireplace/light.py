"""Light platform for Water Vapour Bluetooth Fireplace integration."""
import asyncio
import logging

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    PLATFORM_SCHEMA,
    SUPPORT_BRIGHTNESS,
    SUPPORT_EFFECT,
    LightEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_FLAME_HEIGHT,
    ATTR_FLAME_SPEED,
    DOMAIN,
    DEFAULT_NAME,
)

_LOGGER = logging.getLogger(__name__)

# Define flame speeds as effects
FLAME_EFFECTS = {
    "Speed 1": 1,
    "Speed 2": 2,
    "Speed 3": 3,
    "Speed 4": 4,
    "Speed 5": 5,
    "Speed 6": 6,
    "Speed 7": 7,
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Water Vapour Bluetooth Fireplace light based on config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([FireplaceLight(coordinator, entry)], True)


class FireplaceLight(CoordinatorEntity, LightEntity):
    """Representation of a Water Vapour Bluetooth Fireplace."""

    def __init__(self, coordinator, entry):
        """Initialize the fireplace."""
        super().__init__(coordinator)
        self._server_address = f"http://{entry.data['host']}:{entry.data['port']}"
        self._name = DEFAULT_NAME
        self._effect_list = list(FLAME_EFFECTS.keys())
        self._effect = "Speed 1"  # Default effect
        
    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the light."""
        return self.coordinator.server_address

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.server_address)},
            "name": self._name,
            "manufacturer": "Water Vapour Bluetooth Fireplace",
            "model": "Bluetooth Fireplace",
        }

    @property
    def is_on(self):
        """Return true if light is on."""
        return self.coordinator.data["state"]

    @property
    def brightness(self):
        """Return the brightness of this light between 1..255."""
        # Scale flame height (1-7) to brightness (1-255)
        flame_height = self.coordinator.data["flame_height"]
        return int((flame_height / 7) * 255)
    
    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS | SUPPORT_EFFECT

    @property
    def effect_list(self):
        """Return the list of supported effects."""
        return self._effect_list

    @property
    def effect(self):
        """Return the current effect."""
        flame_speed = self.coordinator.data["flame_speed"]
        for effect_name, speed_value in FLAME_EFFECTS.items():
            if speed_value == flame_speed:
                return effect_name
        return None

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        session = async_get_clientsession(self.hass)
        
        try:
            async with async_timeout.timeout(10):
                # Turn on the fireplace
                async with session.get(f"{self._server_address}/control/on") as response:
                    if response.status != 200:
                        _LOGGER.error("Failed to turn on fireplace: %s", response.status)
                        return
                
                self.coordinator.state = True
                
                # Set brightness (flame height) if provided
                if ATTR_BRIGHTNESS in kwargs:
                    # Convert brightness (1-255) to flame height (1-7)
                    flame_height = max(1, min(7, int((kwargs[ATTR_BRIGHTNESS] / 255) * 7)))
                    
                    async with session.get(
                        f"{self._server_address}/control/flame_height/{flame_height}"
                    ) as response:
                        if response.status != 200:
                            _LOGGER.error("Failed to set flame height: %s", response.status)
                        else:
                            self.coordinator.flame_height = flame_height
                
                # Set effect (flame speed) if provided
                if ATTR_EFFECT in kwargs and kwargs[ATTR_EFFECT] in self._effect_list:
                    flame_speed = FLAME_EFFECTS[kwargs[ATTR_EFFECT]]
                    
                    async with session.get(
                        f"{self._server_address}/control/flame_speed/{flame_speed}"
                    ) as response:
                        if response.status != 200:
                            _LOGGER.error("Failed to set flame speed: %s", response.status)
                        else:
                            self.coordinator.flame_speed = flame_speed
        
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error("Error communicating with API: %s", error)
        
        # Request a data refresh
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        session = async_get_clientsession(self.hass)
        
        try:
            async with async_timeout.timeout(10):
                async with session.get(f"{self._server_address}/control/off") as response:
                    if response.status != 200:
                        _LOGGER.error("Failed to turn off fireplace: %s", response.status)
                        return
                
                self.coordinator.state = False
        
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error("Error communicating with API: %s", error)
        
        # Request a data refresh
        await self.coordinator.async_request_refresh()
        
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_FLAME_HEIGHT: self.coordinator.data["flame_height"],
            ATTR_FLAME_SPEED: self.coordinator.data["flame_speed"],
        } 