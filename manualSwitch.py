#!/opt/homebrew/bin/python3

from datetime import datetime
from serial.tools import list_ports
from serial import Serial
import sys
import configparser
import os

# For updating the configuation file:
configFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.ini")

try:
    if sys.argv[1] == "On":
        ledOn = True
    else:
        ledOn = False
except:
    print('No argument given to manual sign update, exiting.')
    ledOn = True
    sys.exit()

# Update the config to block automatic sign updates...
thisConfig = list()
if ledOn:
    with open(configFile, "r") as fh_r:
        for thisLine in fh_r:
            if thisLine.find("manual") != -1:
                thisConfig.append("manual = True\n")
            else:
                thisConfig.append(str(thisLine))
else:
    with open(configFile, "r") as fh_r:
        for thisLine in fh_r:
            if thisLine.find("manual") != -1:
                thisConfig.append("manual = False\n")
            else:
                thisConfig.append(str(thisLine))

# Store the new manual configuration
with open(configFile, "w") as fh_w:
    for thisLine in thisConfig:
        fh_w.write(thisLine)

# Read in the current configuration
config = configparser.ConfigParser()
config.read(configFile)

ENABLE_SERIAL_UPDATE = config.getboolean('DEFAULT', 'enableUpdate')
ENABLE_EXTRA_DEBUG = config.getboolean('DEFAULT', 'extraDebug')
thisBaud = config.get('DEFAULT', 'arduinoSerialBaud')

# Update the sign manually
if ENABLE_SERIAL_UPDATE:
    # Get the Serial USB Device
    port = list(list_ports.comports())
    for p in port:
      if(p.usb_description() == 'USB Serial'):
        thisDevice = p.device
        if ENABLE_EXTRA_DEBUG: print("I am attempting to update device: %s..."%(thisDevice))
    
    try:
        # Read in the defined BAUD
        if ENABLE_EXTRA_DEBUG: print("Reading the configuration from the file...")

        # Setup and Write to the Serial Device
        if ENABLE_EXTRA_DEBUG: print("Setting up the Serial device handler...")
        serialIF = Serial(thisDevice, thisBaud, timeout=0.1)
    
        # For this update, set the LED based on the calendar events checked above...
        if ENABLE_EXTRA_DEBUG: print("Writing to the Serial device...")
        if ledOn:
            serialIF.write('M0016000002160100041603000600080007000801050000160305001601160016.\r\n'.encode('raw_unicode_escape'))
        else:
            serialIF.write('A000000.\r\n'.encode('raw_unicode_escape'))

        # Get the response...
        if int(serialIF.read(2).decode('utf-8')) != 0:
            print('uController Failure response.')
            raise ValueError('uController Failure response.')
    
        # Close the IF
        if ENABLE_EXTRA_DEBUG: print("Done, closing the Serial handler...")
        serialIF.close()

        # Print that the update finished successfully
        print("Last updated: %s"%(datetime.now()))
    except Exception as e:
        print(e)
        print("Updating the meeting sign through the USB interface failed...")
