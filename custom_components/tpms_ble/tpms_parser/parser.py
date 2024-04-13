"""Parser for TPMS BLE advertisements."""
from __future__ import annotations

import logging
from struct import unpack
from dataclasses import dataclass
from enum import Enum, auto

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfoBleak
from sensor_state_data.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class TPMSSensor(StrEnum):

    PRESSURE = "pressure"
    TEMPERATURE = "temperature"
    BATTERY = "battery"
    SIGNAL_STRENGTH = "signal_strength"


class TPMSBinarySensor(StrEnum):
    ALARM = "alarm"


TPMS_MANUFACTURER = 76 # 004c for apple - cause the sensors say there are apple seonsors...


class TPMSBluetoothDeviceData(BluetoothData):
    """Data for TPMS BLE sensors."""
    # Add an __init__ method that accepts service_info and properly initializes the base class.

    def __init__(self, service_info: BluetoothServiceInfoBleak):
        super().__init__()  # Initialize the base class with no arguments.
        self.service_info = service_info  # Store the service_info for later use.
        manufacturer_data = service_info.manufacturer_data

        if TPMS_MANUFACTURER in manufacturer_data:
            mfr_data = manufacturer_data[TPMS_MANUFACTURER]
            mfr_data_str = ':'.join(f'{byte:02x}' for byte in mfr_data)
            _LOGGER.warning("mfr_data (init): %s", mfr_data_str)

        # if self.get_unique_id():
        #    self._start_update(service_info)  # smart to do it here?

    def start_update(self, service_info: BluetoothServiceInfoBleak) -> None:
        """Update from BLE advertisement data."""

        manufacturer_data = service_info.manufacturer_data
        if TPMS_MANUFACTURER not in manufacturer_data:
            return None

        mfr_data = manufacturer_data[TPMS_MANUFACTURER]

        _LOGGER.warning("mfr_data (update): %s", mfr_data)
        self.set_device_manufacturer("TPMS")

        self._process_mfr_data(mfr_data)

    def _process_mfr_data(
        self,
        data: bytes,
    ) -> None:
        """Parser for TPMS sensors."""
        _LOGGER.warning("Parsing TPMS sensor: %s", data)
        if len(data) != 23:
            return
    
        device_id = data[18:20]  # Extrahiere die Geräte-ID (86 F3 im Beispiel)
        temperature = int.from_bytes(data[20:21], byteorder='big', signed=False) - 168  # Temperatur (c1 im Beispiel)
        pressure = int.from_bytes(data[21:23], byteorder='big', signed=False) / 10000  # Druck (83 9c im Beispiel)
    

#        name = f"TPMS {short_address(address)}"
#        self.set_device_type(name)
#        self.set_device_name(name)
#        self.set_title(name)

        self.update_sensor(
            str(TPMSSensor.PRESSURE), None, pressure, None, "Pressure"
        )
        self.update_sensor(
            str(TPMSSensor.TEMPERATURE), None, temperature, None, "Temperature"
        )

    def get_unique_id(self):
        """Generate a unique ID for the TPMS sensor."""
        # Extract the last 6 characters of the MAC address (last 3 octets)
        # mac_suffix = self._address.replace(":", "")[-6:].upper()  # e.g., "1386F3"

        # Convert the manufacturer data to a hex string
        mfr_data = self.service_info.manufacturer_data[TPMS_MANUFACTURER]

        if len(mfr_data) != 23:
            return None
        else:
            _LOGGER.warning("mfr len requirement not met: %s", len(mfr_data))

        manufacturer_data_hex = ''.join(format(x, '02X') for x in mfr_data)

        sensor_id = manufacturer_data_hex[36:40]  # e.g., 86BC

        # Check if the manufacturer data starts with the expected sequence
        if manufacturer_data_hex.startswith("0215"):  # reads also Tesla Sensors
            # Use the consistent part of the MAC address as the unique ID
            unique_id = f"tpms_{sensor_id}"
            return unique_id
        else:
            _LOGGER.warning("mfr prefix requirement not met: %s", manufacturer_data_hex[0:4])
            # Handle the case where the manufacturer data does not match what we expect
            return None
