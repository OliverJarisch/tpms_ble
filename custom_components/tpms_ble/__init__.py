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

from .const import DOMAIN

from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

SCAN_INTERVAL = timedelta(minutes=2)  # Set the desired scan interval


PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TPMS BLE device from a config entry."""
    address = entry.unique_id
    assert address is not None
    data = TPMSBluetoothDeviceData()
    coordinator = hass.data.setdefault(DOMAIN, {})[
        entry.entry_id
    ] = PassiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=address,
        mode=BluetoothScanningMode.PASSIVE,
        update_method=data.update,
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(
        async_track_time_interval(hass, async_scan_for_tpms_sensors, SCAN_INTERVAL)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_scan_for_tpms_sensors(hass: HomeAssistant):
    """Scan for new TPMS sensors and set them up."""
    
