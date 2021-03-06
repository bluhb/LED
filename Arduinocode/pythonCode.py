import serial
import requests
import time
import struct
import sys
import config

from tinydb import TinyDB, Query
import datetime

url = 'http://127.0.0.1:5000/arduinodata'
arduino = serial.Serial('/dev/ttyUSB0', 115200)
time.sleep(2) #wait 2 seconds to initialize the connection
wait = 1
interval = 300 #5 min interval for reading the arduino.
prevMilli = time.time() // 1000000 
now = time.time() // 1000000

def ArduinoWrite():
    global url, wait
    try:
        #req = requests.get(url)
        #json = req.json()
        color = config.color_rgb_arduino
        brightness = config.brightness
        r = int(color['r'] * brightness)
        g = int(color['g'] * brightness)
        b = int(color['b'] * brightness)
        wait = config.wait

        data = struct.pack('>BBB', r,g,b)
    except KeyboardInterrupt:
        Exit()
    except:
        r=0
        g=0
        b=0
        data = struct.pack('>BBB', 0,0,0)
    arduino.write( struct.pack('?', True))
    arduino.write(data)
    return None

def ArduinoRead():
    global sensorData
    try:
        humidTempB = arduino.readline()
        humidTempD = humidTempB.decode()
        humidTemp = humidTempD.rstrip()
        val = humidTemp.split(",")
        json = {'temp':val[0], 'humid':val[1], 'LDR':val[2]}
        config.roomTemp = val[0]
        config.roomHumid = val[1]
        config.roomLDR = val[2]
        sensorData.insert({'time':str(datetime.datetime.now()),'data':json})
        print(json)
    except KeyboardInterrupt:
        Exit()
    except:
        pass
		
    return None

def Exit():
    data = struct.pack('>BBB', 0,0,0)
    arduino.write(struct.pack('?',True))
    arduino.write(data)
    arduino.close()
    print('Quitting the program')

def init():
    global sensorData, db
    print('init')
    for i in range(0,4):
        arduino.write(struct.pack('?', False))
        time.sleep(0.1)
    db = TinyDB('Database.json')
    sensorData = db.table('sensors')
    return None

def main():
    global now, prevMilli
    try:
        now = time.time()
        if now - prevMilli >= interval:
            prevMilli = now
            ArduinoRead()
        
        ArduinoWrite()
        #time.sleep(wait)  
    except KeyboardInterrupt:
        Exit()
    return None

if __name__ == '__main__':
    init()
    while True:
        main()
