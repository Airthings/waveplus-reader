# MIT License
#
# Copyright (c) 2018 Airthings AS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://airthings.com

# ===============================
# Module import dependencies
# ===============================

from bluepy.btle import UUID, Peripheral, ADDR_TYPE_RANDOM, Scanner, DefaultDelegate
import sys
import time
import struct
import tableprint
import paho.mqtt.publish as mqtt
import json

# ===============================
# Script guards for correct usage
# ===============================
if len(sys.argv) < 6:
    print("ERROR: Missing input argument SN or SAMPLE-PERIOD.")
    print("USAGE: read_waveplus.py SN SAMPLE-PERIOD [pipe > yourfile.txt]")
    print("    where SN is the 10-digit serial number found under the magnetic backplate of your Wave Plus.")
    print("    where SAMPLE-PERIOD is the time in seconds between reading the current values.")
    print("    where MQTT-HOST is the hostname of your mqtt broker.")
    print("    where MQTT-PORT is port of your MQTT broker.")
    print("    where MQTT-TOPIC is the topic to post data to.")
    print("    where [pipe > yourfile.txt] is optional and specifies that you want to pipe your results to yourfile.txt.")
    sys.exit(1)

if sys.argv[1].isdigit() is not True or len(sys.argv[1]) != 10:
    print("ERROR: Invalid SN format.")
    print("USAGE: read_waveplus.py SN SAMPLE-PERIOD [pipe > yourfile.txt]")
    print("    where SN is the 10-digit serial number found under the magnetic backplate of your Wave Plus.")
    print("    where SAMPLE-PERIOD is the time in seconds between reading the current values.")
    print("    where MQTT-HOST is the hostname of your mqtt broker.")
    print("    where MQTT-PORT is port of your MQTT broker.")
    print("    where MQTT-TOPIC is the topic to post data to.")
    print("    where [pipe > yourfile.txt] is optional and specifies that you want to pipe your results to yourfile.txt.")
    sys.exit(1)

if sys.argv[2].isdigit() is not True or int(sys.argv[2])<0:
    print("ERROR: Invalid SAMPLE-PERIOD. Must be a numerical value larger than zero.")
    print("USAGE: read_waveplus.py SN SAMPLE-PERIOD [pipe > yourfile.txt]")
    print("    where SN is the 10-digit serial number found under the magnetic backplate of your Wave Plus.")
    print("    where SAMPLE-PERIOD is the time in seconds between reading the current values.")
    print("    where MQTT-HOST is the hostname of your mqtt broker.")
    print("    where MQTT-PORT is port of your MQTT broker.")
    print("    where MQTT-TOPIC is the topic to post data to.")
    print("    where [pipe > yourfile.txt] is optional and specifies that you want to pipe your results to yourfile.txt.")
    sys.exit(1)

if sys.argv[4].isdigit() is not True or int(sys.argv[4])<0:
    print("ERROR: Invalid MQTT-PORT. Must be numerical value larger than zero.")

if len(sys.argv) > 6:
    Mode = sys.argv[6].lower()
else:
    Mode = 'terminal' # (default) print to terminal 

if Mode!='pipe' and Mode!='terminal':
    print("ERROR: Invalid piping method.")
    print("USAGE: read_waveplus.py SN SAMPLE-PERIOD [pipe > yourfile.txt]")
    print("    where SN is the 10-digit serial number found under the magnetic backplate of your Wave Plus.")
    print("    where SAMPLE-PERIOD is the time in seconds between reading the current values.")
    print("    where [pipe > yourfile.txt] is optional and specifies that you want to pipe your results to yourfile.txt.")
    sys.exit(1)

SerialNumber = int(sys.argv[1])
SamplePeriod = int(sys.argv[2])
MqttBroker = sys.argv[3]
MqttPort = int(sys.argv[4])
MqttTopic = sys.argv[5]

# ====================================
# Utility functions for WavePlus class
# ====================================

def parseSerialNumber(ManuDataHexStr):
    if ManuDataHexStr == "None" or not ManuDataHexStr:
        SN = "Unknown"
    else:
        ManuData = bytearray.fromhex(ManuDataHexStr)

        if (((ManuData[1] << 8) | ManuData[0]) == 0x0334):
            SN  =  ManuData[2]
            SN |= (ManuData[3] << 8)
            SN |= (ManuData[4] << 16)
            SN |= (ManuData[5] << 24)
        else:
            SN = "Unknown"
    return SN

class sensorMessage():
    def __init__(self, address, port, topic):
        self.address = address
        self.port = port
        self.topic = topic
        self.client = mqtt.Client("waveplus_reader")

    def send(self, message):
        self.client.connect(self.address, port=int(self.port))
        self.client.publish(self.topic, message, 0, True)
        self.client.disconnect()

# ===============================
# Class WavePlus
# ===============================

class WavePlus():

    
    
    def __init__(self, SerialNumber):
        self.periph        = None
        self.curr_val_char = None
        self.MacAddr       = None
        self.SN            = SerialNumber
        self.uuid          = UUID("b42e2a68-ade7-11e4-89d3-123b93f75cba")

    def connect(self):
        # Auto-discover device on first connection
        if (self.MacAddr is None):
            scanner     = Scanner().withDelegate(DefaultDelegate())
            searchCount = 0
            while self.MacAddr is None and searchCount < 500:
                devices      = scanner.scan(0.1) # 0.1 seconds scan period
                searchCount += 1
                for dev in devices:
                    ManuData = dev.getValueText(255)
                    SN = parseSerialNumber(ManuData)
                    if (SN == self.SN):
                        self.MacAddr = dev.addr # exits the while loop on next conditional check
                        break # exit for loop
            
            if (self.MacAddr is None):
                print("ERROR: Could not find device.")
                print("GUIDE: (1) Please verify the serial number.")
                print("       (2) Ensure that the device is advertising.")
                print("       (3) Retry connection.")
                sys.exit(1)
        
        # Connect to device
        if (self.periph is None):
            self.periph = Peripheral(self.MacAddr)
        if (self.curr_val_char is None):
            self.curr_val_char = self.periph.getCharacteristics(uuid=self.uuid)[0]
        
    def read(self):
        if (self.curr_val_char is None):
            print("ERROR: Devices are not connected.")
            sys.exit(1)            
        rawdata = self.curr_val_char.read()
        rawdata = struct.unpack('BBBBHHHHHHHH', rawdata)
        sensors = Sensors()
        sensors.set(rawdata)
        return sensors
    
    def disconnect(self):
        if self.periph is not None:
            self.periph.disconnect()
            self.periph = None
            self.curr_val_char = None

# ===================================
# Class Sensor and sensor definitions
# ===================================

NUMBER_OF_SENSORS               = 7
SENSOR_IDX_HUMIDITY             = 0
SENSOR_IDX_RADON_SHORT_TERM_AVG = 1
SENSOR_IDX_RADON_LONG_TERM_AVG  = 2
SENSOR_IDX_TEMPERATURE          = 3
SENSOR_IDX_REL_ATM_PRESSURE     = 4
SENSOR_IDX_CO2_LVL              = 5
SENSOR_IDX_VOC_LVL              = 6

class Sensors():
    def __init__(self):
        self.sensor_version = None
        self.sensor_data    = [None]*NUMBER_OF_SENSORS
        self.sensor_units   = ["%rH", "Bq/m3", "Bq/m3", "degC", "hPa", "ppm", "ppb"]
    
    def set(self, rawData):
        self.sensor_version = rawData[0]
        if (self.sensor_version == 1):
            self.sensor_data[SENSOR_IDX_HUMIDITY]             = rawData[1]/2.0
            self.sensor_data[SENSOR_IDX_RADON_SHORT_TERM_AVG] = self.conv2radon(rawData[4])
            self.sensor_data[SENSOR_IDX_RADON_LONG_TERM_AVG]  = self.conv2radon(rawData[5])
            self.sensor_data[SENSOR_IDX_TEMPERATURE]          = rawData[6]/100.0
            self.sensor_data[SENSOR_IDX_REL_ATM_PRESSURE]     = rawData[7]/50.0
            self.sensor_data[SENSOR_IDX_CO2_LVL]              = rawData[8]*1.0
            self.sensor_data[SENSOR_IDX_VOC_LVL]              = rawData[9]*1.0
        else:
            print("ERROR: Unknown sensor version.\n")
            print("GUIDE: Contact Airthings for support.\n")
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

try:
    #---- Initialize ----#
    waveplus = WavePlus(SerialNumber)
    
    if (Mode=='terminal'):
        print("\nPress ctrl+C to exit program\n")
    
    print("Device serial number: %s" %(SerialNumber))
    
    header = ['Humidity', 'Radon ST avg', 'Radon LT avg', 'Temperature', 'Pressure', 'CO2 level', 'VOC level']
    
    if (Mode=='terminal'):
        print(tableprint.header(header, width=12))
    elif (Mode=='pipe'):
        print(header)

    while True:
  
        try:
            print("trying to connect to waveplus")
            waveplus.connect()
            
            # read values
            print("trying to read sensor values")
            sensors = waveplus.read()
            
            # extract
            humidity_val = str(sensors.getValue(SENSOR_IDX_HUMIDITY))
            radon_st_avg_val = str(sensors.getValue(SENSOR_IDX_RADON_SHORT_TERM_AVG))
            radon_lt_avg_val = str(sensors.getValue(SENSOR_IDX_RADON_LONG_TERM_AVG))
            temperature_val  = str(sensors.getValue(SENSOR_IDX_TEMPERATURE))
            pressure_val     = str(sensors.getValue(SENSOR_IDX_REL_ATM_PRESSURE))
            co2_lvl_val  = str(sensors.getValue(SENSOR_IDX_CO2_LVL))
            voc_lvl_val  = str(sensors.getValue(SENSOR_IDX_VOC_LVL))            

            humidity_unit = str(sensors.getUnit(SENSOR_IDX_HUMIDITY))
            radon_st_avg_unit = str(sensors.getUnit(SENSOR_IDX_RADON_SHORT_TERM_AVG))
            radon_lt_avg_unit = str(sensors.getUnit(SENSOR_IDX_RADON_LONG_TERM_AVG))
            temperature_unit  = str(sensors.getUnit(SENSOR_IDX_TEMPERATURE))
            pressure_unit     = str(sensors.getUnit(SENSOR_IDX_REL_ATM_PRESSURE))
            co2_lvl_unit  = str(sensors.getUnit(SENSOR_IDX_CO2_LVL))
            voc_lvl_unit  = str(sensors.getUnit(SENSOR_IDX_VOC_LVL))            

            humidity     = humidity_val      + " " + humidity_unit
            radon_st_avg = radon_st_avg_val  + " " + radon_st_avg_unit
            radon_lt_avg = radon_lt_avg_val  + " " + radon_lt_avg_unit
            temperature  = temperature_val   + " " + temperature_unit
            pressure     = pressure_val      + " " + pressure_unit
            CO2_lvl      = co2_lvl_val       + " " + co2_lvl_unit
            VOC_lvl      = voc_lvl_val       + " " + voc_lvl_unit
            
            # Print data
            data = [humidity, radon_st_avg, radon_lt_avg, temperature, pressure, CO2_lvl, VOC_lvl]
            
            if (Mode=='terminal'):
                print(tableprint.row(data, width=12))
            elif (Mode=='pipe'):
                print(data)

            msgData = {}
            msgData['Time'] = time.asctime( time.localtime(time.time()) )
            msgData['humidity'] = humidity_val
            msgData['radon_st_avg'] = radon_st_avg_val
            msgData['radon_lt_avg'] = radon_lt_avg_val
            msgData['temperature'] = temperature_val
            msgData['pressure'] = pressure_val
            msgData['co2_lvl'] = co2_lvl_val
            msgData['voc_lvl'] = voc_lvl_val
            msgData['humidity_unit'] = humidity_unit
            msgData['radon_st_avg_unit'] = radon_st_avg_unit
            msgData['radon_lt_avg_unit'] = radon_lt_avg_unit
            msgData['temperature_unit'] = temperature_unit
            msgData['pressure_unit'] = pressure_unit
            msgData['co2_lvl_unit'] = co2_lvl_unit
            msgData['voc_lvl_unit'] = voc_lvl_unit
            json_data = json.dumps(msgData)
            #client.send(json_data)
            mqtt.single(MqttTopic,json_data,hostname=MqttBroker,port=MqttPort,client_id="waveplus_bridge")

            
            
            waveplus.disconnect()
        except Exception as e:
            print("failure:" + str(e))
        
        time.sleep(SamplePeriod)
            
finally:
    waveplus.disconnect()
