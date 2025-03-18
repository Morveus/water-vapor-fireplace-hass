"""Constants for the Vapor Fireplace integration."""

DOMAIN = "vapor_fireplace"
DEFAULT_NAME = "Vapor Fireplace"

# Scan interval for updating values (in seconds)
SCAN_INTERVAL = 30

# Attributes
ATTR_FLAME_HEIGHT = "flame_height"
ATTR_FLAME_SPEED = "flame_speed"

# Service consts
SERVICE_SET_FLAME_HEIGHT = "set_flame_height"
SERVICE_SET_FLAME_SPEED = "set_flame_speed"

# Config flow
CONF_HOST = "host"
CONF_PORT = "port" 