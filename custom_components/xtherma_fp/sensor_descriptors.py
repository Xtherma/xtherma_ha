"""Sensor descriptions."""

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    REVOLUTIONS_PER_MINUTE,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)


@dataclass(kw_only=True, frozen=True)
class XtSensorEntityDescription(SensorEntityDescription):
    """Abstract base class."""

    factor: float|None = None

@dataclass(kw_only=True, frozen=True)
class XtBinarySensorEntityDescription(BinarySensorEntityDescription):
    """A binary sensor."""

SENSOR_DESCRIPTIONS = [
    XtSensorEntityDescription(
        key="tvl",
        name="[TVL] Vorlauftemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="trl",
        name="[TRL] Rücklauftemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="tw",
        name="[TW] Warmwassertemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="tk",
        name="[TK] Heiz-/ Kühltemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="tk1",
        name="[TK1] Kreis 1 Temperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="tk2",
        name="[TK2] Kreis 2 Temperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="vf",
        name="Verdichter Frequenz",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    XtSensorEntityDescription(
        key="ta",
        name="[TA] Außentemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="ta1",
        name="[TA1] Außentemperatur Mittelwert 1h",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="ta4",
        name="[TA4] Außentemperatur Mittelwert 4h",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="ta24",
        name="[TA24] Außentemperatur Mittelwert 24h",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="ld1",
        name="[LD1] Lüfter 1 Drehzahl",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    XtSensorEntityDescription(
        key="ld2",
        name="[LD2] Lüfter 2 Drehzahl",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    XtSensorEntityDescription(
        key="tr",
        name="[TR] Raumtemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtBinarySensorEntityDescription(
        key="evu",
        name="EVU Status",
    ),
    XtBinarySensorEntityDescription(
        key="pk",
        name="[PK] Umwälzpumpe eingeschaltet",
    ),
    XtBinarySensorEntityDescription(
        key="pk1",
        name="[PK1] Umwälzpumpe Kreis 1 eingeschaltet",
    ),
    XtBinarySensorEntityDescription(
        key="pk2",
        name="[PK2] Umwälzpumpe Kreis 2 eingeschaltet",
    ),
    XtBinarySensorEntityDescription(
        key="pww",
        name="[PWW] Zirkulationspumpe Warmwasser eingeschaltet",
    ),
    XtSensorEntityDescription(
        key="hw_target",
        name="Sollwert Warmwasserbereitung",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="h_target",
        name="Sollwert Heizbetrieb",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="c_target",
        name="Sollwert Kühlbetrieb",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="in_hp",
        name="Leistungsaufnahme Wärmepumpe (elektrisch)",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    XtSensorEntityDescription(
        key="v",
        name="[V] Volumenstrom",
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=.1,
    ),
    XtSensorEntityDescription(
        key="out_hp",
        name="Leistungsabgabe Wärmepumpe (thermisch)",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    XtSensorEntityDescription(
        key="efficiency_hp",
        name="Leistungszahl Wärmepumpe",
        state_class=SensorStateClass.MEASUREMENT,
        factor=.01,
    ),
    XtSensorEntityDescription(
        key="efficiency_total",
        name="Leistungszahl Gesamtsystem (inkl. Zusatzheizing)",
        state_class=SensorStateClass.MEASUREMENT,
        factor=.01,
    ),
    XtSensorEntityDescription(
        key="in_backup",
        name="Leistungsaufnahme Zusatz-/Notheizung (elektrisch)",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    XtSensorEntityDescription(
        key="out_backup",
        name="Leistungsabgabe Zusatz-/Notheizung (thermisch)",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    XtSensorEntityDescription(
        key="mode_3",
        name="Betriebsmodus",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    XtSensorEntityDescription(
        key="ta8",
        name="[TA8] Außentemperatur Mittelwert 8h",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor = .1,
    ),
    XtSensorEntityDescription(
        key="sg",
        name="SG-Ready Status",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    XtSensorEntityDescription(
        key="day_hp_out_h",
        name="Tag Heizbetrieb thermische Leistungsabgabe",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_hp_out_c",
        name="Tag Kühlbetrieb thermische Leistungsabgabe",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_hp_out_hw",
        name="Tag Warmwasserbetrieb thermische Leistungsabgabe",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_backup3_out_h",
        name="Tag Heizbetrieb Zusatzheizung Stufe 1 (3 kW) thermische Leistungsabgabe",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_backup6_out_h",
        name="Tag Heizbetrieb Zusatzheizung Stufe 2 (6 kW) thermische Leistungsabgabe",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_backup6_out_hw",
        name="Tag Warmwasserbetrieb Zusatzheizung Stufe 2 (6 kW) thermische Leistungsabgabe",  # noqa: E501
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_backup3_out_hw",
        name="Tag Warmwasserbetrieb Zusatzheizung Stufe 1 (3 kW) thermische Leistungsabgabe",  # noqa: E501
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_hp_in_h",
        name="Tag Heizbetrieb elektrische Leistungsaufnahme",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_hp_in_c",
        name="Tag Kühlbetrieb elektrische Leistungsaufnahme",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_hp_in_hw",
        name="Tag Warmwasserbetrieb elektrische Leistungsaufnahme",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_backup3_in_hw",
        name="Tag Warmwasserbetrieb Zusatzheizung Stufe 1 (3 kW) elektrische Leistungsaufnahme",  # noqa: E501
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_backup6_in_hw",
        name="Tag Warmwasserbetrieb Zusatzheizung Stufe 2 (6 kW) elektrische Leistungsaufnahme",  # noqa: E501
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_backup3_in_h",
        name="Tag Heizbetrieb Zusatzheizung Stufe 1 (3 kW) elektrische Leistungsaufnahme",  # noqa: E501
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    XtSensorEntityDescription(
        key="day_backup6_in_h",
        name="Tag Heizbetrieb Zusatzheizung Stufe 2 (6 kW) elektrische Leistungsaufnahme",  # noqa: E501
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    )
]
