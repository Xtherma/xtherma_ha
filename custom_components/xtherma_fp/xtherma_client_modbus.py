"""Client to access Modbus server on Xtherma FP module."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from homeassistant.helpers.entity import EntityDescription

from custom_components.xtherma_fp.const import (
    KEY_ENTRY_INPUT_FACTOR,
    KEY_ENTRY_KEY,
    KEY_ENTRY_VALUE,
)
from custom_components.xtherma_fp.entity_descriptors import (
    MODBUS_ENTITY_DESCRIPTIONS,
    XtSensorEntityDescription,
)

from .vendor.pymodbus import AsyncModbusTcpClient, ExceptionResponse, ModbusException
from .xtherma_client_common import (
    XthermaBusyError,
    XthermaClient,
    XthermaError,
    XthermaModbusError,
    XthermaNotConnectedError,
)

_LOGGER = logging.getLogger(__name__)

_MODBUS_MAX_VALUE: int = 65535
_MODBUS_UPDATE_PERIOD_S: int = 30


class XthermaClientModbus(XthermaClient):
    """Modbus access client."""

    _client: AsyncModbusTcpClient | None = None

    def __init__(
        self,
        host: str,
        port: int,
        address: int,
    ) -> None:
        """Class constructor."""
        self._host = host
        self._port = port
        self._address = address
        self._desc_regset_cache: dict[str, int] = {}

    async def connect(self) -> None:
        """Connect client to server endpoint."""
        self._client = AsyncModbusTcpClient(host=self._host, port=self._port)
        try:
            _LOGGER.debug("connecting client")
            result = await self._client.connect()
            _LOGGER.debug(
                "connected client success = %s, connected = %s",
                result,
                self._client.connected,
            )
        except Exception as err:
            _LOGGER.exception("connection error")
            raise XthermaNotConnectedError from err
        if not result:
            raise XthermaNotConnectedError

    async def disconnect(self) -> None:
        """Disconnect client."""
        if self._client:
            _LOGGER.debug("disconnect")
            self._client.close()
            self._client = None

    def update_interval(self) -> timedelta:
        """Return update interval for data coordinator."""
        return timedelta(seconds=_MODBUS_UPDATE_PERIOD_S)

    # apply two's complement for negative values. For now, only temperatures can be
    # negative.
    def _decode_int(self, raw_value: int, desc: EntityDescription) -> int:
        if (
            desc.device_class
            in (SensorDeviceClass.TEMPERATURE, NumberDeviceClass.TEMPERATURE)
            and raw_value > _MODBUS_MAX_VALUE // 2
        ):
            return -((raw_value - 1) ^ _MODBUS_MAX_VALUE)
        return raw_value

    # apply two's complement for negative values. For now, only temperatures can be
    # negative.
    def _encode_int(self, signed_value: int, desc: EntityDescription) -> int:
        if (
            desc.device_class
            in (SensorDeviceClass.TEMPERATURE, NumberDeviceClass.TEMPERATURE)
            and signed_value < 0
        ):
            return ((-signed_value) ^ _MODBUS_MAX_VALUE) + 1
        return signed_value

    async def _get_client(self) -> AsyncModbusTcpClient:
        if self._client is None or not self._client.connected:
            _LOGGER.debug("not connected, try connecting")
            await self.connect()
            # the following check is only for safety and ruff, self.connect() will have
            # alredy raised an exception if the reconnect fails
            if self._client is None or not self._client.connected:
                raise XthermaNotConnectedError
        return self._client

    async def async_get_data(self) -> list[dict[str, Any]]:
        """Obtain fresh data."""
        result: list[dict[str, Any]] = []
        client = await self._get_client()
        try:
            for reg_desc in MODBUS_ENTITY_DESCRIPTIONS:
                regs = await client.read_holding_registers(
                    address=reg_desc.base,
                    count=len(reg_desc.descriptors),
                    slave=int(self._address),
                )
                for i, desc in enumerate(reg_desc.descriptors):
                    if not desc:
                        _LOGGER.debug("no descriptor for %d.%d", reg_desc.base, i)
                    else:
                        entry = {}
                        entry[KEY_ENTRY_KEY] = desc.key
                        value = self._decode_int(regs.registers[i], desc)
                        entry[KEY_ENTRY_VALUE] = str(value)
                        if isinstance(desc, XtSensorEntityDescription):
                            entry[KEY_ENTRY_INPUT_FACTOR] = desc.factor
                        else:
                            entry[KEY_ENTRY_INPUT_FACTOR] = None
                        result.append(entry)
        except ModbusException as err:
            _LOGGER.error("Modbus error: %s", err.string)  # noqa: TRY400
            raise XthermaModbusError from err
        except Exception as err:
            _LOGGER.exception("Exception error")
            raise XthermaError from err
        else:
            if regs.isError():
                _LOGGER.error("Modbus error %s", regs.exception_code)
                raise XthermaModbusError
            return result

    async def async_put_data(self, value: int, desc: EntityDescription) -> None:
        """Write data."""
        client = await self._get_client()
        try:
            address = self._get_register_address(desc.key)
            encoded_value = self._encode_int(value, desc)
            _LOGGER.debug(
                'Writing "%s" = %d @ address %d',
                desc.key,
                encoded_value,
                address,
            )
            regs = await client.write_register(
                address=address,
                value=encoded_value,
                slave=int(self._address),
            )
        except Exception as err:
            _LOGGER.exception("Exception error")
            raise XthermaModbusError from err
        else:
            if regs.isError():
                exc_code = regs.exception_code
                if exc_code == ExceptionResponse.SLAVE_BUSY:
                    _LOGGER.error("Device busy")
                    raise XthermaBusyError
                _LOGGER.error("Modbus write error %s", exc_code)
                raise XthermaModbusError

    def _get_register_address(self, key: str) -> int:
        if not self._desc_regset_cache:
            for reg_desc in MODBUS_ENTITY_DESCRIPTIONS:
                address = reg_desc.base
                for desc in reg_desc.descriptors:
                    if desc is not None and desc.key == key:
                        self._desc_regset_cache[key.lower()] = address
                    address += 1
        address = self._desc_regset_cache.get(key.lower())
        if address is None:
            _LOGGER.error("Unknown register %s", key)
            raise XthermaModbusError
        return address

    def get_entity_descriptions(self) -> list[EntityDescription]:
        """Get all entity descriptions."""
        return [
            desc
            for reg_desc in MODBUS_ENTITY_DESCRIPTIONS
            for desc in reg_desc.descriptors
            if desc is not None
        ]
