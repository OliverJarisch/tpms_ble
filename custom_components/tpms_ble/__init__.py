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

SCAN_INTERVAL = timedelta(minutes=2)  # Set the desired scan interval


PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)



async def async_setup_entry(hass, config_entry, async_add_entities) -> bool:
    """Set up TPMS BLE device from a config entry."""

    installed_sensors = ["TPMS_186F3", "TPMS_184C6", "TPMS_18511", "TPMS_186BC", "TPMS_18764"]
    for unique_id in installed_sensors:
        sensors = [PressureSensor(unique_id), TemperatureSensor(unique_id)]
        async_add_entities(sensors)
        _LOGGER.warning("Sesnor %s added", unique_id)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

    
