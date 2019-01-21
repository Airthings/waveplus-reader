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

import sys
import time
import tableprint
import paho.mqtt.client as mqtt
from Sensors import Sensors
from WavePlus import WavePlus

# ===============================
# Script guards for correct usage
# ===============================
def print_usage():
    print ("USAGE: read_waveplus.py SN SAMPLE-PERIOD [pipe > yourfile.txt]")
    print ("    where SN is the 10-digit serial number found under the magnetic backplate of your Wave Plus.")
    print ("    where SAMPLE-PERIOD is the time in seconds between reading the current values.")
    print ("    where [pipe > yourfile.txt] is optional and specifies that you want to pipe your results to yourfile.txt.")
    
if len(sys.argv) < 3:
    print ("ERROR: Missing input argument SN or SAMPLE-PERIOD.")
    print_usage()
    sys.exit(1)

if sys.argv[1].isdigit() is not True or len(sys.argv[1]) != 10:
    print ("ERROR: Invalid SN format.")
    print_usage()
    sys.exit(1)

if sys.argv[2].isdigit() is not True or int(sys.argv[2])<0:
    print ("ERROR: Invalid SAMPLE-PERIOD. Must be a numerical value larger than zero.")
    print_usage()
    sys.exit(1)

if len(sys.argv) > 3:
    Mode = sys.argv[3].lower()
    if Mode == 'mqtt':
        Broker = sys.argv[4]
    else:
        Broker = None
else:
    Mode = 'terminal' # (default) print to terminal 

if Mode!='pipe' and Mode!='terminal':
    print ("ERROR: Invalid piping method.")
    print_usage()
    sys.exit(1)

SerialNumber = int(sys.argv[1])
SamplePeriod = int(sys.argv[2])


try:
    #---- Initialize ----#
    waveplus = WavePlus(SerialNumber)
    
    if (Mode=='terminal'):
        print ("\nPress ctrl+C to exit program\n")
    
    header = ['Humidity', 'Radon ST avg', 'Radon LT avg', 'Temperature', 'Pressure', 'CO2 level', 'VOC level']
    
    print ("Device serial number: %s" %(SerialNumber))
    
    if (Mode=='terminal'):
        print (tableprint.header(header, width=12))
    elif (Mode=='pipe'):
        print (header)


    while True:
        sensors = None
        waveplus.connect()
        
        # read values
        sensors = waveplus.read()

        # extract
        humidity     = str(sensors.getValue(sensors.SENSOR_IDX_HUMIDITY))             + " " + str(sensors.getUnit(sensors.SENSOR_IDX_HUMIDITY))
        radon_st_avg = str(sensors.getValue(sensors.SENSOR_IDX_RADON_SHORT_TERM_AVG)) + " " + str(sensors.getUnit(sensors.SENSOR_IDX_RADON_SHORT_TERM_AVG))
        radon_lt_avg = str(sensors.getValue(sensors.SENSOR_IDX_RADON_LONG_TERM_AVG))  + " " + str(sensors.getUnit(sensors.SENSOR_IDX_RADON_LONG_TERM_AVG))
        temperature  = str(sensors.getValue(sensors.SENSOR_IDX_TEMPERATURE))          + " " + str(sensors.getUnit(sensors.SENSOR_IDX_TEMPERATURE))
        pressure     = str(sensors.getValue(sensors.SENSOR_IDX_REL_ATM_PRESSURE))     + " " + str(sensors.getUnit(sensors.SENSOR_IDX_REL_ATM_PRESSURE))
        CO2_lvl      = str(sensors.getValue(sensors.SENSOR_IDX_CO2_LVL))              + " " + str(sensors.getUnit(sensors.SENSOR_IDX_CO2_LVL))
        VOC_lvl      = str(sensors.getValue(sensors.SENSOR_IDX_VOC_LVL))              + " " + str(sensors.getUnit(sensors.SENSOR_IDX_VOC_LVL))
        
        # Print data
        data = [humidity, radon_st_avg, radon_lt_avg, temperature, pressure, CO2_lvl, VOC_lvl]
        
        if (Mode=='terminal'):
            print (tableprint.row(data, width=12))
        elif (Mode=='pipe'):
            print (data)
            
        waveplus.disconnect()
        time.sleep(SamplePeriod)
            
finally:
    waveplus.disconnect()