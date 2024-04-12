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

        device = DeviceData(discovery_info)
        unique_id = device.get_unique_id()
        if not unique_id:    # if none
            return self.async_abort(reason="not_supported")

        existing_entry = await self.async_set_unique_id(unique_id)
        if existing_entry:
            # If the unique ID is already configured, perform your custom function
            await device._start_update(discovery_info) # -> Make Public?
            # Then abort the flow
            return self.async_abort(reason="already_configured")

        self._discovery_info = discovery_info
        self._discovered_device = device
        return await self.async_step_bluetooth_confirm()
        
    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the step to confirm the Bluetooth discovery and set a custom name."""
        assert self._discovered_device is not None
        device = self._discovered_device
        assert self._discovery_info is not None
        discovery_info = self._discovery_info
        # Use the unique ID as the fallback name if no custom name is provided by the user
        fallback_name = self.unique_id
    
        errors = {}
        if user_input is not None:
            # Save the custom name provided by the user, or use the unique ID as a fallback
            custom_name = user_input.get("custom_name", fallback_name)
            # Create the entry with the necessary data
            return self.async_create_entry(
                title=custom_name,  # Use custom name or unique ID as the entry title
                data={
                    "unique_id": self.unique_id,  # Store the unique_id
                    "name": custom_name,  # Store the custom name
                    # Additional fields like Pressure, Temperature will be created
                    # later by the entity platform setup (sensor.py)
                }
            )
    
        # If no user input, show the form with the unique ID as the default custom name
        self._set_confirm_only()
        placeholders = {"name": fallback_name}
        self.context["title_placeholders"] = placeholders
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders=placeholders,
            data_schema=vol.Schema(
                {
                    vol.Optional("custom_name", default=fallback_name): str,
                }
            ),
            errors=errors,
        )
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step to set up the integration."""
        if user_input is not None:
            # User input is not needed in this case, since we're proceeding without devices
            pass

        # Proceed to create the entry for the integration without any devices
        return self.async_create_entry(title="TPMS", data={})
        
