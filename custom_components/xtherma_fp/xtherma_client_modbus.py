"""Client to access Modbus server on Xtherma FP module."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from homeassistant.helpers.entity import EntityDescription
from pymodbus import ModbusException
from pymodbus.client import (
    AsyncModbusTcpClient,
)

from custom_components.xtherma_fp.pymodbus_compat import (
    COMPAT_DEVICE_BUSY,
    COMPAT_DEVICE_ID,
)

from .const import (
    MODBUS_TIMEOUT_S,
)
from .entity_descriptors import (
    MODBUS_ENTITY_DESCRIPTIONS,
    MODBUS_REGISTER_RANGES,
    MODBUS_REGISTER_SIZE,
    ModbusRegisterSet,
    XtNumericEntityDescription,
    XtSensorEntityDescription,
)
from .xtherma_client_common import (
    XthermaClient,
    XthermaError,
    XthermaModbusBusyError,
    XthermaModbusEmptyDataError,
    XthermaModbusError,
    XthermaNotConnectedError,
)

_LOGGER = logging.getLogger(__name__)

_MODBUS_MAX_VALUE: int = 65535
_MODBUS_UPDATE_PERIOD_S: int = 30


class XthermaClientModbus(XthermaClient):
    """Modbus access client."""

    _client: AsyncModbusTcpClient | None = None
    detect_empty_modbus_data: bool

    def __init__(
        self,
        host: str,
        port: int,
        address: int,
    ) -> None:
        """Class constructor."""
        self._host = host
        self._port = port
        self._device_address_kwarg: dict[str, Any] = {COMPAT_DEVICE_ID: int(address)}
        self._desc_regset_cache: dict[str, int] = {}
        self._last_update: dict[str, int | float] = {}
        self._read_buffer = [0] * MODBUS_REGISTER_SIZE
        self.detect_empty_modbus_data = True

    async def connect(self) -> None:
        """Connect client to server endpoint."""
        self._client = AsyncModbusTcpClient(
            host=self._host,
            port=self._port,
            timeout=float(MODBUS_TIMEOUT_S),
        )
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

    # decode two's complement for negative scalar values.
    def _decode_int(self, raw_value: int, desc: EntityDescription) -> int:
        if not isinstance(desc, XtNumericEntityDescription):
            return raw_value
        if desc.device_class == SensorDeviceClass.ENUM:
            return raw_value
        if raw_value > _MODBUS_MAX_VALUE // 2:
            return -((raw_value - 1) ^ _MODBUS_MAX_VALUE)
        return raw_value

    # apply two's complement for negative scalar values.
    def _encode_int(self, signed_value: int, desc: EntityDescription) -> int:
        if not isinstance(desc, XtNumericEntityDescription):
            return signed_value
        if desc.device_class == SensorDeviceClass.ENUM:
            return signed_value
        if signed_value < 0:
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

    async def _read_modbus_range(
        self, client: AsyncModbusTcpClient, address: int, length: int
    ) -> None:
        """Read a range of modbus holding registers into read buffer."""
        try:
            regs = await client.read_holding_registers(
                address=address, count=length, **self._device_address_kwarg
            )
        except ModbusException as err:
            _LOGGER.debug("Modbus exception: %s", err.string)
            raise XthermaModbusError from err
        except Exception as err:
            _LOGGER.exception("Exception error")
            raise XthermaError from err
        else:
            if regs.isError():
                exc_code = regs.exception_code
                if exc_code == COMPAT_DEVICE_BUSY:
                    _LOGGER.debug("Modbus device busy")
                    raise XthermaModbusBusyError
                _LOGGER.debug("Modbus error %s", regs.exception_code)
                raise XthermaModbusError
            self._read_buffer[address : address + length] = regs.registers

    async def _read_modbus_ranges(self, client: AsyncModbusTcpClient) -> None:
        """Read ranges defined in MODBUS_REGISTER_RANGES into read buffer."""
        for r in MODBUS_REGISTER_RANGES:
            await self._read_modbus_range(client, address=r.first_reg, length=r.length)
            # we know that no single register range can ever be empty, so lets
            # throw an exception if we just read empty data.
            # see also test_modbus_register_ranges_cannot_be_empty()
            if (
                self.detect_empty_modbus_data
                and self._read_buffer[r.non_empty_reg] == 0
            ):
                raise XthermaModbusEmptyDataError

    async def _read_bank(
        self,
        reg_desc: ModbusRegisterSet,
    ) -> None:
        """Read a bank of modbus holding registers."""
        for i, desc in enumerate(reg_desc.descriptors):
            if not desc:
                _LOGGER.debug("no descriptor for %d.%d", reg_desc.base, i)
            else:
                raw_value = self._read_buffer[reg_desc.base + i]
                decoded_value = self._decode_int(raw_value, desc)
                if isinstance(desc, XtSensorEntityDescription) and desc.factor:
                    input_factor = desc.factor
                    value = self._apply_input_factor(decoded_value, input_factor)
                else:
                    input_factor = ""
                    value = decoded_value
                self._last_update[desc.key] = value
                _LOGGER.debug(
                    'key="%s" raw="%s" value="%s" inputfactor="%s"',
                    desc.key,
                    raw_value,
                    value,
                    input_factor,
                )

    async def async_get_data(self) -> dict[str, int | float]:
        """Obtain fresh data."""
        self._last_update = {}
        client = await self._get_client()
        await self._read_modbus_ranges(client)
        for reg_desc in MODBUS_ENTITY_DESCRIPTIONS:
            await self._read_bank(reg_desc)
        return self._last_update

    async def async_put_data(self, value: int | float, desc: EntityDescription) -> None:
        """Write data."""
        client = await self._get_client()
        try:
            address = self._get_register_address(desc.key)
            if isinstance(desc, XtSensorEntityDescription):
                int_value = self._reverse_apply_input_factor(value, desc.factor)
            else:
                int_value = int(value)
            encoded_value = self._encode_int(int_value, desc)
            _LOGGER.debug(
                'Writing "%s" = %d @ address %d',
                desc.key,
                encoded_value,
                address,
            )
            regs = await client.write_register(
                address=address, value=encoded_value, **self._device_address_kwarg
            )
        except Exception as err:
            _LOGGER.exception("Exception error")
            raise XthermaModbusError from err
        else:
            if regs.isError():
                exc_code = regs.exception_code
                if exc_code == COMPAT_DEVICE_BUSY:
                    _LOGGER.error("Device busy")
                    raise XthermaModbusBusyError
                _LOGGER.error("Modbus write error %s", exc_code)
                raise XthermaModbusError

    def _get_register_address(self, key: str) -> int:
        if not self._desc_regset_cache:
            for reg_desc in MODBUS_ENTITY_DESCRIPTIONS:
                address = reg_desc.base
                for desc in reg_desc.descriptors:
                    if desc is not None:
                        self._desc_regset_cache[desc.key.lower()] = address
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
