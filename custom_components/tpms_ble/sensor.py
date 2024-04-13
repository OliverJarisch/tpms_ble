"""Support for TPMS sensors."""
from __future__ import annotations

from homeassistant.helpers.entity import Entity


from .const import DOMAIN


class BaseSensor(Entity):
    """Base sensor representing a device."""

    def __init__(self, name, device_id):
        self._name = name
        self._device_id = device_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": "Default",
            "manufacturer": "MaxxSensor",
            "model": "BSI-03",
        }


class PressureSensor(BaseSensor):
    """Pressure sensor entity."""

    def __init__(self, device_id):
        super().__init__("Pressure Sensor", device_id)
        self._state = 0.00  # Pressure in Bar

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
        return f"{self._device_id}_pressure"


class TemperatureSensor(BaseSensor):
    """Temperature sensor entity."""

    def __init__(self, device_id):
        super().__init__("Temperature Sensor", device_id)
        self._state = 0  # Temperature in Celsius

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
        return f"{self._device_id}_temperature"

