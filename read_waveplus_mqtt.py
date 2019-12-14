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
import socket
import json
import paho.mqtt.client as mqtt
from Sensors import Sensors
from WavePlus import WavePlus

# ===============================
# Script guards for correct usage
# ===============================
def print_usage():
    print ("USAGE: read_waveplus_mqtt.py SN SERVERADDRESS")
    print ("    where SN is the 10-digit serial number found under the magnetic backplate of your Wave Plus")
    print ("    and SERVERADDRESS specifies the IP-address of the MQTT server you want to post the results to.")
    
if len(sys.argv) < 2:
    print ("ERROR: Missing input argument SN or SERVERADDRESS.")
    print_usage()
    sys.exit(1)

if sys.argv[1].isdigit() is not True or len(sys.argv[1]) != 10:
    print ("ERROR: Invalid SN format.")
    print_usage()
    sys.exit(1)

SerialNumber = int(sys.argv[1])
Broker = sys.argv[2]

try:
    socket.inet_aton(Broker)
    # legal
except socket.error:
    # Not legal
    print ("ERROR: Invalid IP address format:", Broker)
    print_usage()
    sys.exit(1)

#---- Initialize ----#
waveplus = WavePlus(SerialNumber)
waveplus.connect()

# read values
jsonPackage = dict()
sensors = waveplus.read()
client = mqtt.Client()
client.connect(Broker)
for i in range(sensors.NUMBER_OF_SENSORS):
    topic = "waveplus/{0}/{1}".format(SerialNumber, sensors.header[i].replace(' ','_'))
    info = client.publish(topic, sensors.getValue(i), retain=False)
    info.wait_for_publish()
    time.sleep(0.1)
    jsonPackage[sensors.header[i].replace(' ','_')]={'value':sensors.getValue(i), 'notation':sensors.sensor_units[i]}

# Post all values as json object
topic = "waveplus/{0}/".format(SerialNumber)
info = client.publish(topic, json.dumps(jsonPackage), retain=False)
info.wait_for_publish()
time.sleep(0.1)

# End it all
client.disconnect()
waveplus.disconnect()
