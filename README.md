# Airthings Wave Plus Sensor Reader

This is a project to provide users an interface (```read_waveplus.py```) to read current sensor values from the
[Airthings Wave Plus](https://airthings.com/wave-plus/) devices using a Raspberry Pi 3 
Model B over Bluetooth Low Energy (BLE).

Airthings Wave Plus is a smart IAQ monitor with Radon detection, including sensors for
temperature, air presssure, humidity, TVOCs and CO2.

**Table of contents**

* [Requirements](#requirements)
  * [Setup Raspberry Pi](#setup-Raspberry-pi)
  * [Turn on the BLE interface](#turn-on-the-ble-interface)
  * [Installing linux and python packages](#installing-linux-and-python-packages)
  * [Downloading script](#downloading-script)
* [Usage](#usage)
  * [Printing data to the terminal window](#printing-data-to-the-terminal-window)
  * [Piping data to a text-file](#piping-data-to-a-text-file)
* [Sensor data description](#sensor-data-description)
* [Release notes](#release-notes)  

# Requirements

The following tables shows a compact overview of dependencies for this project.

**List of OS dependencies**

| OS | model/version | Comments |
|-------------|-------------|-------------|
| Raspberry Pi 3 | Model B | Raspbian image
| Linux          | x86 Debian | Should work according to [bluepy](https://github.com/IanHarvey/bluepy)

**List of linux/raspberry dependencies**

| package | version | Comments |
|-------------|-------------|-------------|
| python  | 2.7 | Tested with python 2.7.13
| python-pip | | pip for python2.7
| git        | | To download this project
| libglib2.0-dev  | | For bluepy module

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

In the terminal window on you Raspberry Pi:

```
pi@raspberrypi:~$ bluetoothctl
[bluetooth]# power on
[bluetooth]# show
```

After issuing the command ```show```, a list of bluetooth settings will be printed
to the Raspberry Pi terminal window. Look for “Powered: yes”.

## Installing linux and python packages

> Note: The ```read_waveplus.py``` script is only compatible with Python2.7.

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

Additionally, the ```read_waveplus.py``` script depends on the ```tableprint``` module
to print nicely formated sensor data to the Raspberry Pi terminal at run-time.

```
pi@raspberrypi:~$ sudo pip2 install tableprint==0.8.0
```

> Note: The ```read_waveplus.py``` script has been tested with bluepy==1.2.0 and tableprint==0.8.0. You may download the latest versions at your own risk.

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

```cd``` into the directory where the read_waveplus.py script is located.

```
pi@raspberrypi:~$ cd waveplus-reader
```

## Printing data to the terminal window

Run the Python script ```read_waveplus.py``` in the following way:

```
pi@raspberrypi:~/waveplus-reader $ sudo python2 read_waveplus.py [SN] terminal
```

where you change [SN] with the 10-digit serial number. 

After a short delay, the script will print the current sensor values to the 
Raspberry Pi terminal window. Exit the script using “Ctrl + c”.

## Piping data to a text-file

If you want to pipe the results to a text-file, you can run the script in the following way:

```
pi@raspberrypi:~/waveplus-reader $ sudo python2 read_waveplus.py [SN] pipe > yourfile.txt
```

where you change [SN] with the 10-digit serial number. Exit the script using “Ctrl + c”.

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

# Release notes

Initial release 12-Dec-2018