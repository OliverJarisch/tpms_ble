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


TPMS_MANUFACTURER = 256 # indicator of the manufacturer Data set


class TPMSBluetoothDeviceData(BluetoothData):
    """Data for TPMS BLE sensors."""

    def _start_update(self, service_info: BluetoothServiceInfoBleak) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing TPMS BLE advertisement data: %s", service_info)
        manufacturer_data = service_info.manufacturer_data
        address = service_info.address
        if TPMS_MANUFACTURER not in manufacturer_data:
            return None

        mfr_data = manufacturer_data[TPMS_MANUFACTURER]
        self.set_device_manufacturer("TPMS")

        self._process_mfr_data(mfr_data)   #(address, mfr_data)

    def _process_mfr_data(
        self,
#        address: str,
        data: bytes,
    ) -> None:
        """Parser for TPMS sensors."""
        _LOGGER.debug("Parsing TPMS sensor: %s", data)
        msg_length = len(data)
        if msg_length != 16:
            return
    
        device_id = data[4:6]  # Extrahiere die Geräte-ID (86 F3 in Ihrem Beispiel)
        temperature = int.from_bytes(data[5:6], byteorder='big', signed=False) - 168  # Temperatur (c1 in Ihrem Beispiel)
        pressure = int.from_bytes(data[14:16], byteorder='big', signed=False) / 10000  # Druck (83 9c in Ihrem Beispiel)
    

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
        mac_suffix = self._address.replace(":", "")[-6:].upper()  # e.g., "1386F3"

        # Convert the manufacturer data to a hex string
        manufacturer_data_hex = ''.join(format(x, '02X') for x in self._mfr_data)

        # Check if the manufacturer data starts with the expected sequence
        if manufacturer_data_hex.startswith("0215B54A"):
            # Use the consistent part of the MAC address as the unique ID
            unique_id = f"tpms_{mac_suffix}"
            return unique_id
        else:
            # Handle the case where the manufacturer data does not match what we expect
            return None
