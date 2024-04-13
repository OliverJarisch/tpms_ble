"""Support for TPMS sensors."""
from __future__ import annotations

from homeassistant.helpers.entity import Entity
from homeassistant.const import PRESSURE_BAR
from homeassistant.const import TEMP_CELSIUS

import logging

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN


class BaseSensor(Entity):
    """Base sensor representing a device."""

    def __init__(self, name, device_id):
        self._name = name
        self._device_id = device_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_id,
            "manufacturer": "MaxxSensor",
            "model": "BSI-03",
        }


class PressureSensor(BaseSensor):
    """Pressure sensor entity."""

    def __init__(self, device_id):
        super().__init__("Pressure Sensor", device_id)
        self.entity_id = f"sensor.{device_id}_pressure"
        self._attr_name = f"{device_id} Pressure"
        self._attr_unit_of_measurement = PRESSURE_BAR
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return 'Bar'

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self.entity_id


class TemperatureSensor(BaseSensor):
    """Temperature sensor entity."""

    def __init__(self, device_id):
        super().__init__("Temperature Sensor", device_id)
        self.entity_id = f"sensor.{device_id}_temperature"
        self._attr_name = f"{device_id} Temperature"
        self._attr_unit_of_measurement = TEMP_CELSIUS
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return '°C'

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self.entity_id


async def async_setup_entry(hass, config_entry, async_add_entities) -> bool:
    """Set up TPMS BLE device from a config entry."""

    installed_sensors = ["TPMS_186F3", "TPMS_184C6", "TPMS_18511", "TPMS_186BC", "TPMS_18764"]
    entities = []
    for unique_id in installed_sensors:
        # Append each new entity to the entities list
        entities.append(PressureSensor(unique_id))
        entities.append(TemperatureSensor(unique_id))
        _LOGGER.warning("Sensor %s added", unique_id)

    # Add all entities at once
    if entities:
        async_add_entities(entities)

    return True