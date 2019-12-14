
# ===================================
# Class Sensor and sensor definitions
# ===================================

import sys

class Sensors():

    NUMBER_OF_SENSORS               = 7
    SENSOR_IDX_HUMIDITY             = 0
    SENSOR_IDX_RADON_SHORT_TERM_AVG = 1
    SENSOR_IDX_RADON_LONG_TERM_AVG  = 2
    SENSOR_IDX_TEMPERATURE          = 3
    SENSOR_IDX_REL_ATM_PRESSURE     = 4
    SENSOR_IDX_CO2_LVL              = 5
    SENSOR_IDX_VOC_LVL              = 6

    def __init__(self):
        self.sensor_version = None
        self.sensor_data    = [None]*self.NUMBER_OF_SENSORS
        self.sensor_units   = ["%rH", "Bq/m3", "Bq/m3", "degC", "hPa", "ppm", "ppb"]
        self.header = ['Humidity', 'Radon ST avg', 'Radon LT avg', 'Temperature', 'Pressure', 'CO2 level', 'VOC level']

    
    def set(self, rawData):
        self.sensor_version = rawData[0]
        if (self.sensor_version == 1):
            self.sensor_data[self.SENSOR_IDX_HUMIDITY]             = rawData[1]/2.0
            self.sensor_data[self.SENSOR_IDX_RADON_SHORT_TERM_AVG] = self.conv2radon(rawData[4])
            self.sensor_data[self.SENSOR_IDX_RADON_LONG_TERM_AVG]  = self.conv2radon(rawData[5])
            self.sensor_data[self.SENSOR_IDX_TEMPERATURE]          = rawData[6]/100.0
            self.sensor_data[self.SENSOR_IDX_REL_ATM_PRESSURE]     = rawData[7]/50.0
            self.sensor_data[self.SENSOR_IDX_CO2_LVL]              = rawData[8]*1.0
            self.sensor_data[self.SENSOR_IDX_VOC_LVL]              = rawData[9]*1.0
        else:
            print ("ERROR: Unknown sensor version.\n")
            print ("GUIDE: Contact Airthings for support.\n")
            sys.exit(1)
   
    def conv2radon(self, radon_raw):
        radon = "N/A" # Either invalid measurement, or not available
        if 0 <= radon_raw <= 16383:
            radon  = radon_raw
        return radon

    def getValue(self, sensor_index):
        return self.sensor_data[sensor_index]

    def getUnit(self, sensor_index):
        return self.sensor_units[sensor_index]
