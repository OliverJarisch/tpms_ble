"""The TPMS integration."""
from __future__ import annotations

import logging

from .tpms_parser import TPMSBluetoothDeviceData

from homeassistant.components.bluetooth import BluetoothScanningMode
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothProcessorCoordinator,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .sensor import (PressureSensor, TemperatureSensor)

from .const import DOMAIN

from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta


PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the tpms_ble component."""
    # Handle YAML configuration if necessary
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up tpms_ble from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, Platform.SENSOR)
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

    
