"""Config flow for TPMS BLE integration."""
from __future__ import annotations

from typing import Any
import logging

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import device_registry as dr
import voluptuous as vol

from .const import DOMAIN
from .tpms_parser import TPMSBluetoothDeviceData as DeviceData

_LOGGER = logging.getLogger(__name__)


class TPMSConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TPMS."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_device: DeviceData | None = None
        self._discovered_devices: dict[str, str] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle the bluetooth discovery step."""

        device = DeviceData(discovery_info)
        unique_id = device.get_unique_id()
        if not unique_id:    # if none
            return self.async_abort(reason="not_supported")

        dev_registry = dr.async_get(self.hass)
        _device_exist = False
        for hass_device in dev_registry.devices.values():
            # The device name might be under `name` or `name_by_user`.
            if hass_device.name == unique_id:
                _device_exist = True

        if not _device_exist:
            return self.async_abort(reason="parent_missing")

        self.hass.states.async_set(
            f"sensor.{unique_id}_pressure",
            device.get_pressure(),
            {"name": f"{unique_id} Pressure",
             "unit_of_measurement": "bar"})

        self.hass.states.async_set(
            f"sensor.{unique_id}_temperature",
            device.get_temperature(),
            {"name": f"{unique_id} Temperature",
             "unit_of_measurement": "°C"})

        return self.async_abort(reason="finished")
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step to set up the integration."""
        if user_input is not None:
            # User input is not needed in this case, since we're proceeding without devices
            pass

        # Proceed to create the entry for the integration without any devices
        return self.async_create_entry(
            title="TPMS Head Unit",  # Use custom name or unique ID as the entry title
            data={
                "unique_id": "TMPS_Amarok",  # Store the unique_id
                "name": "TPMS Head Unit",  # Store the custom name
            })
        
