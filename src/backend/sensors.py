from ctypes.wintypes import FLOAT
from sys import byteorder
from tkinter import BUTT
import pyfirmata
import json
import time
import sys
import pyodbc 
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import queue
from pyfirmata import DIGITAL, ArduinoMega, util, Arduino

distance1 = 0
distance2 = 0 
distance3 = 0
distance4 = 0
speed1 = 0
speed2 = 0
speed3 = 0
speed4 = 0

carPresenceNorth = False
carPresenceSouth = False
carPresenceWest = False
carPresenceEast = False

hallSensorPin2 = 2
hallSensorPin3 = 3
hallSensorPin4 = 4
indSensor = 5

port='COM6'
board = ArduinoMega(port)  # Replace 'COM6' with the port connected to your Arduino
iterator = util.Iterator(board)
iterator.start()

def setup():
    board.digital[hallSensorPin2].mode(pyfirmata.INPUT)
    board.digital[hallSensorPin3].mode(pyfirmata.INPUT)
    board.digital[hallSensorPin4].mode(pyfirmata.INPUT)
    board.digital[indSensor].mode(pyfirmata.INPUT)
    
def loop():
    sensorValue1 = board.digital[hallSensorPin2].read()
    sensorValue2 = board.digital[hallSensorPin3].read()
    sensorValue3 = board.digital[hallSensorPin4].read()
    indSensorValue = board.digital[indSensor].read()
    
    if sensorValue1 == 1:
        carPresenceNorth = True
    else:
        carPresenceNorth = False
        
    if sensorValue2 == 1:
        carPresenceSouth = True
    else:
        carPresenceSouth = False
        
    if sensorValue3 == 1:
        carPresenceEast = True
    else:
        carPresenceEast = False
        
    if indSensorValue == 1:
        carPresenceWest = True
    else:
        carPresenceWest = False
    