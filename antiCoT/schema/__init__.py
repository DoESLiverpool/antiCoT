import math
from units import unit, scaled_unit, leaf_unit, NamedComposedUnit
from units.predefined import define_units


define_units()

unity = leaf_unit.LeafUnit('', False)
degC = leaf_unit.LeafUnit('degC', False)

AMON_units = {
    'absoluteHumidity': unit('g') / unit('Kg'),
    'barometricPressure': unit('hPa'),
    'co2': unit('ppm'),
    'currentSignal': unit('mA'),
    'electricityAmps': unit('A'),
    'electricityConsumption': unit('kW') * unit('h'),
    'electricityExport': unit('kW') * unit('h'),
    'electricityFrequency': unit('Hz'),
    'electricityGeneration': unit('kW') * unit('h'),
    'electricityImport': unit('kW') * unit('h'),
    'electricityKiloVoltAmpHours': unit('kV') * unit('A') * unit('h'),
    'electricityKiloWatts': unit('kW'),
    'electricityVolts': unit('V'),
    'electricityVoltAmps': unit('V') * unit('A'),
    'electricityVoltAmpsReactive': unit('V') * unit('A'),
    'flowRateAir': (unit('m') ** 3) / unit('h'),
    'flowRateLiquid': unit('L') / unit('s'),
    'gasConsumption': unit('m') ** 3,  #: ft^3: kWh',
    'heatConsumption': unit('kW') * unit('h'),
    'heatExport': unit('kW') * unit('h'),
    'heatGeneration': unit('kW') * unit('h'),
    'heatImport': unit('kW') * unit('h'),
    'heatTransferCoefficient': unit('W') / (unit('m') ** 2 * unit('K')),
    'liquidFlowRate': unit('L') / scaled_unit('5min', 'min', 5.0),
    'oilConsumption': unit('m') ** 3,  #: ft^3: kWh',
    'powerFactor': unity,
    'pulseCount': unity,
    'relativeHumidityPercent': unit('%RH'),
    'relativeHumidity': unit('w') / unit('m') ** 2,
    'solarRadiation': unit('W') / unit('m') ** 2,
    'status': unity,
    'temperatureAir': degC,
    'temperatureAmbient': degC,
    'temperatureFluid': degC,
    'temperatureGround': degC,
    'temperatureRadiant': degC,
    'temperatureSurface': degC,
    'thermalEnergy': NamedComposedUnit('kWhth', unit('kW') * unit('h')),
    'time': unit('ms'),
    'voltageSignal': unit('mV'),
    'waterConsumption': unit('L'),
    'windDirection': scaled_unit('deg', 'rad', 180.0 / math.pi),
    'windSpeed': unit('m') / unit('s')
}
