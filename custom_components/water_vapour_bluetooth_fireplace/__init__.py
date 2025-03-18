"""The Water Vapour Bluetooth Fireplace integration."""
import asyncio
import logging
from datetime import timedelta

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["light"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Water Vapour Bluetooth Fireplace component."""
    hass.data.setdefault(DOMAIN, {})
    
    # Set up services
    await async_setup_services(hass)
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Water Vapour Bluetooth Fireplace from a config entry."""
    host = entry.data["host"]
    port = entry.data["port"]
    
    session = async_get_clientsession(hass)
    coordinator = FireplaceDataUpdateCoordinator(hass, session, f"{host}:{port}")
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove a config entry."""
    # Unload services when the last instance is removed
    if len(hass.data.get(DOMAIN, {})) == 0:
        await async_unload_services(hass)


class FireplaceDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, session, server_address):
        """Initialize."""
        self.session = session
        self.server_address = server_address
        self.state = False
        self.flame_height = 1
        self.flame_speed = 1

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via API."""
        try:
            async with async_timeout.timeout(10):
                # In a real integration, we would fetch the current state here
                # Since there's no API endpoint specified for getting the current state,
                # we'll just return the current tracked state
                return {
                    "state": self.state,
                    "flame_height": self.flame_height,
                    "flame_speed": self.flame_speed
                }
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            raise UpdateFailed(f"Error communicating with API: {error}") 