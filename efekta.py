from zigpy.zcl.clusters.general import AnalogInput
from typing import Final
from zigpy.quirks import CustomCluster
import zigpy.types as t
from zigpy.quirks.v2 import (
    QuirkBuilder,
    ReportingConfig,
    SensorDeviceClass,
    SensorStateClass,
    NumberDeviceClass
)

from zigpy.quirks.v2.homeassistant import (
    UnitOfTime,
    UnitOfLength,
    CONCENTRATION_PARTS_PER_MILLION
)
from zigpy.zcl.clusters.general import (
    Basic, 
    AnalogInput, 
    OnOff, 
    Time
)
from zigpy.zcl.clusters.measurement import (
    CarbonDioxideConcentration,
    RelativeHumidity,
    TemperatureMeasurement,
    IlluminanceMeasurement
)
from zigpy.zcl.foundation import BaseAttributeDefs, ZCLAttributeDef
    
class CO2Cluster(CarbonDioxideConcentration, CustomCluster):
    class AttributeDefs(CarbonDioxideConcentration.AttributeDefs):
        reading_interval: Final = ZCLAttributeDef(id=0x0201, type=t.uint16_t, access="rw")
        forced_recalibration: Final = ZCLAttributeDef(id=0x0202, type=t.Bool, access="rw")
        manual_forced_recalibration: Final = ZCLAttributeDef(id=0x0207, type=t.uint16_t, access="rw")
        automatic_self_calibration: Final = ZCLAttributeDef(id=0x0402, type=t.Bool, access="rw")
        factory_reset_co2: Final = ZCLAttributeDef(id=0x0206, type=t.Bool, access="rw")
        enable_co2_gas: Final = ZCLAttributeDef(id=0x0220, type=t.Bool, access="rw")
        high_co2_gas: Final = ZCLAttributeDef(id=0x0221, type=t.uint16_t, access="rw")
        low_co2_gas: Final = ZCLAttributeDef(id=0x0222, type=t.uint16_t, access="rw")
        altitude: Final = ZCLAttributeDef(id=0x0205, type=t.uint16_t, access="rw")
        
class TimeCluster(Time, CustomCluster):
    name = "Time"
    class AttributeDefs(BaseAttributeDefs):
        lifetime: Final = ZCLAttributeDef(id=0x0199, type=t.uint32_t, access="r")

class IlluminanceCluster(IlluminanceMeasurement, CustomCluster):
    
    class AttributeDefs(IlluminanceMeasurement.AttributeDefs):
        night_mode: Final = ZCLAttributeDef(id=0x0401, type=t.Bool, access="rw")
        night_mode_start_hour: Final = ZCLAttributeDef(id=0x0405, type=t.uint8_t, access="rw")
        night_mode_stop_hour: Final = ZCLAttributeDef(id=0x0406, type=t.uint8_t, access="rw")

(
    QuirkBuilder("EfektaLab", "EFEKTA_AQ_Smart_Monitor_Gen2")
    .replaces(CO2Cluster, endpoint_id=2)
    .replaces(TimeCluster, endpoint_id=1)
    .replaces(IlluminanceCluster, endpoint_id=1)
    .sensor( # VOC index
        attribute_name="present_value",
        cluster_id=AnalogInput.cluster_id,
        endpoint_id=3,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.AQI,
        reporting_config=ReportingConfig(
            min_interval=10, max_interval=120, reportable_change=1
        ),
        translation_key="voc_index",
        fallback_name="VOC index",
    )
    .sensor( # Device lifetime in hours
        attribute_name=TimeCluster.AttributeDefs.lifetime.name,
        cluster_id=TimeCluster.cluster_id,
        endpoint_id=1,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.DURATION,
        unit=UnitOfTime.HOURS,
        translation_key="on_time",
        fallback_name="Device lifetime",
    )
    .switch( # Should LED turn off at night
        attribute_name=IlluminanceCluster.AttributeDefs.night_mode.name,
        cluster_id=IlluminanceCluster.cluster_id,
        endpoint_id=1,
        translation_key="night_mode",
        fallback_name="Night mode"
    )
    .number( # CO2 reading interval
        CO2Cluster.AttributeDefs.reading_interval.name,
        CO2Cluster.cluster_id,
        endpoint_id=2,
        translation_key="reading_delay",
        fallback_name="Setting the sensor reading delay",
        unique_id_suffix="reading_delay",
        min_value=6,
        max_value=600,
        step=1,
        device_class=NumberDeviceClass.DURATION,
        unit=UnitOfTime.SECONDS,
    )
    .command_button(
        CO2Cluster.AttributeDefs.forced_recalibration.name,
        CO2Cluster.cluster_id,
        endpoint_id=2,
        translation_key="forced_recalibration",
        fallback_name="Start FRC (Perform Forced Recalibration of the CO2 Sensor)",
        unique_id_suffix="forced_recalibration",
    )
    .number(
        CO2Cluster.AttributeDefs.manual_forced_recalibration.name,
        CO2Cluster.cluster_id,
        endpoint_id=2,
        translation_key="manual_forced_recalibration",
        fallback_name="Start Manual FRC (Perform Forced Recalibration of the CO2 Sensor)",
        unique_id_suffix="manual_forced_recalibration",
        min_value=0,
        max_value=5000,
        step=1,
        unit=CONCENTRATION_PARTS_PER_MILLION,
    )
    .switch( # Automatic calibration of the CO2 sensor
        CO2Cluster.AttributeDefs.automatic_self_calibration.name,
        CO2Cluster.cluster_id,
        endpoint_id=2,
        translation_key="automatic_self_calibration",
        fallback_name="Automatic self calibration",
        unique_id_suffix="automatic_self_calibration",
    )
    .command_button(
        CO2Cluster.AttributeDefs.factory_reset_co2.name,
        CO2Cluster.cluster_id,
        endpoint_id=2,
        translation_key="factory_reset_co2",
        fallback_name="Factory Reset CO2 sensor",
        unique_id_suffix="factory_reset_co2",
    )
    .number( # Night mode activation time in hours
        attribute_name=IlluminanceCluster.AttributeDefs.night_mode_start_hour.name,
        cluster_id=IlluminanceCluster.cluster_id,
        endpoint_id=1,
        translation_key="whatever",
        fallback_name="Night mode start hour",
        device_class=NumberDeviceClass.DURATION,
        unit=UnitOfTime.HOURS,
        min_value=0,
        max_value=23,
        step=1
    )
    .number( # Night mode deactivation time in hours
        attribute_name=IlluminanceCluster.AttributeDefs.night_mode_stop_hour.name,
        cluster_id=IlluminanceCluster.cluster_id,
        endpoint_id=1,
        translation_key="whatever",
        fallback_name="Night mode start hour",
        device_class=NumberDeviceClass.DURATION,
        unit=UnitOfTime.HOURS,
        min_value=0,
        max_value=23,
        step=1
    )
    .number( # Setting the altitude above sea level (for high accuracy of the CO2 sensor)
        attribute_name=CO2Cluster.AttributeDefs.altitude.name,
        cluster_id=CO2Cluster.cluster_id,
        endpoint_id=2,
        translation_key="whatever",
        fallback_name="Altitude above sea level",
        device_class=NumberDeviceClass.DISTANCE,
        unit=UnitOfLength.METERS,
        min_value=0,
        max_value=3000,
        step=1
    )
    .add_to_registry()
)
