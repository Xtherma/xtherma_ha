"""Compatibility helpers for pymodbus API changes.

Pymodbus does not use semantic versioning. Breaking changes are introduced in
minor releases. This module provides compatibility shims for such changes.
Fortunately we don't need many features of pymodbus, so the shims are few and
simple.

pymodbus Releases:
https://github.com/pymodbus-dev/pymodbus/releases

Pymodbus version required by HA's modbus core integration:
https://github.com/home-assistant/core/blob/dev/homeassistant/components/modbus/manifest.json

Starting with 3.11.3 HA might begin using an aliased version of pymodbus,
decoupling the version required by HA's modbus core integration from the
version required by custom components.
https://github.com/pymodbus-dev/pymodbus/releases/tag/v3.11.3
"""

from importlib.metadata import version

from packaging.version import parse as parse_version

_PYMODBUS_PACKAGE_NAME = "pymodbus"
_installed_version_str = version(_PYMODBUS_PACKAGE_NAME)
_installed_version = parse_version(_installed_version_str)

if _installed_version < parse_version("3.9.0"):
    msg = f"{_PYMODBUS_PACKAGE_NAME} version >= 3.9.0 required, found {_installed_version_str}"
    raise ImportError(msg)

"""
Expose exception_code to API. #2615
https://github.com/pymodbus-dev/pymodbus/pull/2615

This was added in v3.9.0, which we require via manifest.json
"""

"""
Change slave to device_id and slave= to device_id=.
https://github.com/pymodbus-dev/pymodbus/pull/2600
"""

COMPAT_DEVICE_ID: str = "slave"
if _installed_version >= parse_version("3.10.0"):
    COMPAT_DEVICE_ID = "device_id"

"""
Move ExceptionResponse to proper file.
https://github.com/pymodbus-dev/pymodbus/pull/2727
"""

COMPAT_DEVICE_BUSY: int
if _installed_version >= parse_version("3.11.1"):
    from pymodbus.constants import ExcCodes

    COMPAT_DEVICE_BUSY = ExcCodes.DEVICE_BUSY
else:
    from pymodbus import ExceptionResponse

    COMPAT_DEVICE_BUSY = ExceptionResponse.SLAVE_BUSY
