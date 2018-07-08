#!/usr/bin/python
import sys
import Adafruit_DHT
import os
import glob
import time
import requests
import serial, string, time
import RPi.GPIO as GPIO
from time import sleep

ser = serial.Serial('/dev/ttyACM0', 9600)

TRIG = 22
ECHO = 27

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(8,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(7,GPIO.OUT,initial=GPIO.LOW)

def WaterLevelSetup(TRIG,ECHO):
    GPIO.setwarnings(False)
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    GPIO.output(TRIG, False)
    time.sleep(1)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO)==0:
      pulse_start = time.time()
    while GPIO.input(ECHO)==1:
      pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distanceLevel = pulse_duration * 17150
    distanceLevel = round(distanceLevel, 2)
    
    return distanceLevel


while True:

    ser.flushInput()
    humidity, temperature = Adafruit_DHT.read_retry(11, 4)
    read_serial=ser.readline()
    reading = ser.readline()
    moisture1 = int(reading.split(' ')[0])
    moisture2 = int(reading.split(' ')[1].strip('\n'))
    RainLevel = int(reading.split(' ')[2].strip('\n'))

#Water Level

    TankLevel=WaterLevelSetup(TRIG,ECHO)

    #print(tempTurbidity, tempFlowRate, tempVolume)
    if(TankLevel > 100):
        TankLevel=100

    if(RainLevel > 10):
        print("Both Actuator Low since mokka Nagesh\n")
        GPIO.output(8,GPIO.LOW)
        GPIO.output(7,GPIO.LOW)
        GPIO.output(20,GPIO.HIGH)
        GPIO.output(12,GPIO.HIGH)
    else:
        if(moisture1 < 20):
            print("Actuator 1 High")
            GPIO.output(8,GPIO.HIGH)
            GPIO.output(21,GPIO.HIGH)
            GPIO.output(20,GPIO.LOW)
        else:
            print("Actuator 1 Low")
            GPIO.output(8,GPIO.LOW)
            GPIO.output(20,GPIO.HIGH)
            GPIO.output(21,GPIO.LOW)

        if(moisture2 < 20):
            print("Actuator 2 High")
            GPIO.output(7,GPIO.HIGH)
            GPIO.output(16,GPIO.HIGH)
            GPIO.output(12,GPIO.LOW)
        else:
            print("Actuator 2 Low")
            GPIO.output(7,GPIO.LOW)
    		GPIO.output(12,GPIO.HIGH)
    		GPIO.output(16,GPIO.LOW)
    # sending all data
    url = 'http://mounikac16.pythonanywhere.com/sensors/addreading/'
    payload = {'plant1':str(temperature) + ' ' + str(humidity) + ' ' + str(moisture1) + ' ' + str(TankLevel) + ' ' + str(RainLevel)}
    r = requests.post(url, data = payload)
    
    url = 'http://mounikac16.pythonanywhere.com/sensors/addreading/'
    payload = {'plant2':str(temperature) + ' ' + str(humidity) + ' ' + str(moisture2) + ' ' + str(TankLevel) + ' ' + str(RainLevel)}
    r = requests.post(url, data = payload)
        
    print("Humidity "+str(humidity))
    print("Temperature "+str(temperature))
    print("SoilMoisture "+str(moisture1))
    print("SoilMoisture "+str(moisture2))
    print("TankLevel "+str(TankLevel))
    print("RainGuageLevel "+str(RainLevel)+'\n')

