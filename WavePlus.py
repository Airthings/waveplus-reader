# ===============================
# Class WavePlus
# ===============================

import sys
import struct
from Sensors import Sensors
from bluepy.btle import UUID, Peripheral, Scanner, DefaultDelegate

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
            while self.MacAddr is None and searchCount < 50:
                devices      = scanner.scan(0.1) # 0.1 seconds scan period
                searchCount += 1
                for dev in devices:
                    ManuData = dev.getValueText(255)
                    if ManuData != None:
                        SN = self.parseSerialNumber(ManuData)
                        if (SN == self.SN):
                            self.MacAddr = dev.addr # exits the while loop on next conditional check
                            break # exit for loop
            
            if (self.MacAddr is None):
                print ("ERROR: Could not find device.")
                print ("GUIDE: (1) Please verify the serial number.")
                print ("       (2) Ensure that the device is advertising.")
                print ("       (3) Retry connection.")
                sys.exit(1)
        
        # Connect to device
        if (self.periph is None):
            self.periph = Peripheral(self.MacAddr)
        if (self.curr_val_char is None):
            self.curr_val_char = self.periph.getCharacteristics(uuid=self.uuid)[0]
        
    def read(self):
        if (self.curr_val_char is None):
            print ("ERROR: Devices are not connected.")
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

    # ====================================
    # Utility functions for WavePlus class
    # ====================================

    def parseSerialNumber(self, ManuDataHexStr):
        if (ManuDataHexStr == "None"):
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

