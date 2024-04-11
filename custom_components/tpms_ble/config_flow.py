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
        device = TPMSBluetoothDeviceData(discovery_info)
        unique_id = device.get_unique_id()
        if not unique_id:
            return self.async_abort(reason="not_supported")

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        self._discovery_info = discovery_info
        self._discovered_device = device
        return await self.async_step_bluetooth_confirm()
        
    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        assert self._discovered_device is not None
        device = self._discovered_device
        assert self._discovery_info is not None
        discovery_info = self._discovery_info
        title = device.title or device.get_device_name() or discovery_info.name
        if user_input is not None:
            return self.async_create_entry(title=title, data={})

        self._set_confirm_only()
        placeholders = {"name": title}
        self.context["title_placeholders"] = placeholders
        return self.async_show_form(
            step_id="bluetooth_confirm", description_placeholders=placeholders
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> data_entry_flow.FlowResult:
        """Handle the user step to pick a discovered device or continue without a device."""
        errors = {}
    
        if user_input is not None:
            if user_input.get("confirm_setup", False):
                # User has confirmed setup without selecting a specific device
                return self.async_create_entry(title="TPMS", data={})
    
        current_addresses = self._async_current_ids()
        for discovery_info in async_discovered_service_info(self.hass, False):
            address = discovery_info.address
            if address in current_addresses or address in self._discovered_devices:
                continue
            device = DeviceData()
            if device.supported(discovery_info):
                self._discovered_devices[address] = (
                    device.title or device.get_device_name() or discovery_info.name
                )
        _LOGGER.warning("Loop abgeschlossen")

        if not self._discovered_devices:
                # No devices discovered. Allow user to confirm setup without devices.
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema(
                        {vol.Optional("confirm_setup", default=False): bool}
                    ),
                    errors=errors,
                    description_placeholders={
                        "message": "No devices found. Would you like to set up the integration and add devices later?"
                    }
                )
                
            # Adjusted logic to continue without specifying devices
            return self.async_create_entry(title="TPMS", data={})
        

