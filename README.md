# Airthings Wave Plus Sensor Reader

This is a project to provide users an interface (```read_waveplus.py```) to read current sensor values from the
[Airthings Wave Plus](https://airthings.com/wave-plus/) devices using a Raspberry Pi 3 
Model B over Bluetooth Low Energy (BLE).

Airthings Wave Plus is a smart IAQ monitor with Radon detection, including sensors for
temperature, air pressure, humidity, TVOCs and CO2.

**Table of contents**

* [Requirements](#requirements)
  * [Setup Raspberry Pi](#setup-Raspberry-pi)
  * [Turn on the BLE interface](#turn-on-the-ble-interface)
  * [Installing linux and python packages](#installing-linux-and-python-packages)
  * [Downloading script](#downloading-script)
* [Usage](#usage)
  * [Printing data to the terminal window](#printing-data-to-the-terminal-window)
  * [Piping data to a text-file](#piping-data-to-a-text-file)
  * [Posting regularly to MQTT Server](#posting-regularly-to-mqtt-server)
* [Sensor data description](#sensor-data-description)
* [Contribution](#contribution)
* [Release notes](#release-notes)

# Requirements

The following tables shows a compact overview of dependencies for this project.

**List of OS dependencies**

| OS | Device/model/version | Comments |
|-------------|-------------|-------------|
| Raspbian | Raspberry Pi 3 Model B | Used in this project.
| Linux    | x86 Debian             | Should work according to [bluepy](https://github.com/IanHarvey/bluepy)

**List of linux/raspberry dependencies**

| package | version | Comments |
|-------------|-------------|-------------|
| python         | 2.7 or 3.6 | Tested with python 2.7.13 and 3.6.5
| python-pip     |     | pip for python 2.7 or python 3.6
| git            |     | To download this project
| libglib2.0-dev |     | For bluepy module

**List of Python dependencies**

| module | version | Comments |
|-------------|-------------|-------------|
| bluepy      | 1.2.0 | Newer versions have not been tested.
| tableprint  | 0.8.0 | Newer versions have not been tested.

## Setup Raspberry Pi

The first step is to setup the Raspberry Pi with Raspbian. An installation guide for 
Raspbian can be found on the [Raspberry Pi website](https://www.raspberrypi.org/downloads/raspbian/).
In short: download the Raspbian image and write it to a micro SD card.

To continue, you need access to the Raspberry Pi using either a monitor and keyboard, or 
by connecting through WiFi or ethernet from another computer. The latter option does not 
require an external screen or keyboard and is called “headless” setup. To access a headless 
setup, you must first activate SSH on the Pi. This can be done by creating a file named ssh 
in the boot partition of the SD card. Connect to the Pi using SSH from a command line 
interface (terminal):

```
$ ssh pi@raspberrypi.local
```

The default password for the “pi” user is “raspberry”.

## Turn on the BLE interface

In the terminal window on your Raspberry Pi:

```
pi@raspberrypi:~$ bluetoothctl
[bluetooth]# power on
[bluetooth]# show
```

After issuing the command ```show```, a list of bluetooth settings will be printed
to the Raspberry Pi terminal window. Look for ```Powered: yes```.

## Installing linux and python packages

> **Note:** The ```read_waveplus.py``` script is only compatible with Python2.7.

The next step is to install the bluepy Python library for talking to the BLE stack. 
For the current released version for Python 2.7:

```
pi@raspberrypi:~$ sudo apt-get install python-pip libglib2.0-dev
pi@raspberrypi:~$ sudo pip2 install bluepy==1.2.0
```

Make sure your Raspberry Pi has git installed

```
pi@raspberrypi:~$ git --version
```

or install git to be able to clone this repo.

```
pi@raspberrypi:~$ sudo apt-get install git
```

Additionally, the ```read_waveplus.py``` script depends on the ```tableprint``` module to print nicely formated sensor data to the Raspberry Pi terminal at run-time and the ```paho.mqtt``` module for communication with an MQTT server.

```
pi@raspberrypi:~$ sudo pip install tableprint==0.8.0
pi@raspberrypi:~$ sudo pip install paho-mqtt

```

> **Note:** The ```read_waveplus.py``` script has been tested with bluepy==1.2.0 and tableprint==0.8.0. You may download the latest versions at your own risk.

## Downloading script

Downloading using git:

```
pi@raspberrypi:~$ sudo git clone https://github.com/Airthings/waveplus-reader.git
```

Downloading using wget:

```
pi@raspberrypi:~$ wget https://raw.githubusercontent.com/Airthings/waveplus-reader/master/read_waveplus.py
```

# Usage

To read the sensor data from the Airthings Wave Plus using the ```read_waveplus.py``` script,
you need the 10-digit serial number of the device. This can be found under the magnetic backplate 
of your Airthings Wave Plus.

If your device is paired and connected to e.g. a phone, you may need to turn off bluetooth on
your phone while using this script.

```cd``` into the directory where the ```read_waveplus.py``` script is located if you cloned the repo.

The general format for calling the ```read_waveplus.py``` script is as follows:

```
read_waveplus.py SN SAMPLE-PERIOD [pipe > yourfilename.txt]
```

where the input arguments are:

| input argument | example | Comments |
|-------------|-------------|-------------|
| SN            | 0123456789              | 10-digit number. Can be found under the magnetic backplate of your Airthings Wave Plus.
| SAMPLE-PERIOD | 60                      | Read sensor values every 60 seconds. Must be larger than zero.
| pipe          | pipe > yourfilename.txt | Optional. Since tableprint is incompatible with piping, we use a third optional input argument "pipe".

> **Note on choosing a sample period:** 
Except for the radon measurements, the Wave Plus updates its current sensor values once every 5 minutes.
Radon measurements are updated once every hour.

## Printing data to the terminal window

By default, the ```read_waveplus.py``` script will print the current sensor values to the Rasberry Pi terminal.
Run the Python script in the following way:

```
pi@raspberrypi:~/waveplus-reader $ sudo python2 read_waveplus.py SN SAMPLE-PERIOD
```

where you change ```SN``` with the 10-digit serial number, and change ```SAMPLE-PERIOD``` to a numerical value of your choice.

After a short delay, the script will print the current sensor values to the 
Raspberry Pi terminal window. Exit the script using ```Ctrl+C```.

## Piping data to a text-file

If you want to pipe the results to a text-file, you can run the script in the following way:

```
pi@raspberrypi:~/waveplus-reader $ sudo python2 read_waveplus.py SN SAMPLE-PERIOD pipe > yourfilename.txt
```

where you change ```SN``` with the 10-digit serial number, and change ```SAMPLE-PERIOD``` to a numerical value of your choice.

Exit the script using ```Ctrl+C```.

## Posting regularly to MQTT Server

If you need the data available on an home automation system, you can set up the script to post data read from the Airthings Wave plus to an MQTT server (like mosquitto). Invoking the read_waveplus.py with 
```
pi@raspberrypi:~/waveplus-reader $ sudo python3 read_waveplus.py SN SAMPLE-PERIOD mqtt SERVER_ADDRESS
```
will read values from Airthings Wave Plus and post all values on the given mqtt server, assuming there is no login required. 
```SN``` should be the serial number of your device, ```SAMPLE_PERIOD``` is ignored and ```SERVER_ADDRESS``` is the ip-address of the mqtt server you want your data posted to.

The values wil be posted as the following topics:
```
waveplus/SN/MEASUREMENT_TYPE
```
```MEASUREMENT_TYPE``` would be modified name of the measurements. Examples of topics would be 
```
waveplus/2930002359/Humidity 
waveplus/2930002359/Radon_ST_avg 
...
waveplus/2930002359/VOC_level
```

Practical setup would be to add a line to your cron table:
```
pi@raspberrypi:~ $ sudo crontab -e
```
The following line will make a read and post every 5 minutes from your Raspberry Pi to the mqtt server located at ```192.168.0.16```:
 
```
*/5 * * * *  sudo python3 /home/pi/waveplus-reader/read_waveplus.py 2930002359 60 mqtt 192.168.0.16
```


# Sensor data description

| sensor | units | Comments |
|-------------|-------------|-------------|
| Humidity                      | %rH | 
| Temperature                   | &deg;C |
| Radon short term average      | Bq/m3 | First measurement available 1 hour after inserting batteries
| Radon long term average       | Bq/m3 | First measurement available 1 hour after inserting batteries
| Relative atmospheric pressure | hPa |
| CO2 level                     | ppm |
| TVOC level                    | ppb | Total volatile organic compounds level

# Contribution

Let us know how it went! If you want contribute, you can do so by posting issues or suggest enhancement
[here](https://github.com/Airthings/waveplus-reader/issues), or you can open a pull request for review
[here](https://github.com/Airthings/waveplus-reader/pulls).

# Release notes

Release dated 14-Dec-2018

* Added SAMPLE-PERIOD as an input argument.

Initial release 12-Dec-2018