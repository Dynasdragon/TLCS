from asyncio.windows_events import NULL
from ctypes.wintypes import FLOAT
from re import L
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
from pyfirmata import DIGITAL, ArduinoMega, serial, util, Arduino

paramPath = 'C:\\Users\\xdark\\source\\repos\\TLCS\\src\\assets\\param.json'
# Opening JSON file
f = open(paramPath)

# returns JSON object as a dictionary
paramData = json.load(f)

#Set up Flask
app = Flask(__name__)
#Set up Flask to bypass CORS
cors = CORS(app);
stopPort = False


def startApp():
    app.run()

#Create the receiver API POST endpoint
@app.route("/receiver", methods=["POST"])
def postME():
    global td, td2, tdreset
    print("listening on thread")
    data = request.get_json()
    with open(paramPath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
   
    newParams = []
    for i in data:
        newParams.append(data[i])
   
    td = newParams[0]
    td2 = newParams[0]
    tdreset = newParams[0]
    
        
    print(data)
    return data

@app.route("/closePort", methods=["GET"])
def closePort():
   print("Closing Port")
   global stopPort 
   stopPort = True
   data = jsonify("resp: success")
   f.close()
   return data

if __name__ == "__main__": 
    print("Starting Flask")
    thread1 = threading.Thread(target=startApp, args=[])
    thread1.setDaemon(True)
    thread1.start()
    
cnxn = pyodbc.connect("Driver={SQL Server};"
                      "Server=Eddys-Laptop\\SQLEXPRESS;"
                      "Database=TLCS;"
                      "uid=TLCS;"
                      "pwd=trafficlight;")


cursor = cnxn.cursor()
cursor.execute('SELECT * FROM Intersection')

for row in cursor:
    print('row = %r' % (row,))

port = 'COM6'

# pins are output for red light
stcp_Pin = 4
shcp_Pin = 3
ds_Pin = 2

# pins for 7hc for 7 segment
dataPin = 5
latchPin = 6
clockPin = 7

# pins for 7hc for 2nd 7 segment
dataPin2 = 12
latchPin2 = 11
clockPin2 = 9

speakerPin = 48
lightChange = 42
redLightViolated = 40

buttonPin = 10 #side1
buttonPin2 = 8 #side2

#starts the counter at 0
buttonValue = 0
buttonValue2 = 0

#red led on pin 9
#green led on pin 10
#blue led on pin 11
PIN_RED = 25
PIN_GREEN = 29
PIN_BLUE = 27

params = []
# Iterating through the json list
for i in paramData:
    params.append(paramData[i])
# Define intervals for each state
defaultLightsInterval =1.5
way1Interval = 1.5
greenLightInterval = 1
segmentDisplayInterval = 1.5
last_update_time = 0

td = params[0] | 5
tdreset = params[0] | 5
td2 = params[0] | 5
leds = 0

# if crossing button is pressed
active = 0
active2 = 0

# for when sensors detect cars incoming
carPresent = 0
carPresent2 = 0

note_freq = {
    'C4': 261.63,
    'C#4': 277.18,
    'D4': 293.66,
    'D#4': 311.13,
    'E4': 329.63,
    'F4': 349.23,
    'F#4': 369.99,
    'G4': 392.00,
    'G#4': 415.30,
    'A4': 440.00,
    'A#4': 466.16,
    'B4': 493.88
}

# Define LED patterns
values = [
    [0,1,1,1,1,1,1,0],  # num 9
    [1,1,1,1,1,1,1,1],  # num 8
    [0,1,1,0,0,1,1,0],  # num 7
    [1,1,1,1,1,1,0,1],  # num 6
    [1,1,1,1,1,1,0,0],  # num 5
    [0,1,1,1,1,0,1,0],  # num 4
    [1,1,1,1,0,1,1,0],  # num 3
    [1,0,1,1,0,1,1,1],  # num 2
    [0,1,1,0,0,0,1,0],  # num 1
    [1,1,1,0,1,1,1,1]   # num 0
]

valuesnew = [
    [1,1,1,1,1,1,0,1],  # num 6
    [1,1,1,1,1,1,0,0],  # num 5
    [0,1,1,1,1,0,1,0],  # num 4
    [1,1,1,1,0,1,1,0],  # num 3
    [1,0,1,1,0,1,1,1],  # num 2
    [0,1,1,0,0,0,1,0],  # num 1
    [1,1,1,0,1,1,1,1]   # num 0
]

values2 = [
    [1,0,0,1,1,1,1,1], # num 9
    [1,1,1,1,1,1,1,1], # num 8
    [1,0,0,1,1,0,0,1], # num 7
    [1,1,1,0,1,1,1,1], # num 6
    [1,1,0,0,1,1,1,1], # num 5
    [1,0,0,1,0,1,1,1], # num 4
    [1,1,0,1,1,0,1,1], # num 3
    [0,1,1,1,1,0,1,1], # num 2
    [1,0,0,1,0,0,0,1], # num 1
    [1,1,1,1,1,1,0,1]  # num 0
  ] 

valuesnew2 = [
    [1,1,1,0,1,1,1,1], # num 6
    [1,1,0,0,1,1,1,1], # num 5
    [1,0,0,1,0,1,1,1], # num 4
    [1,1,0,1,1,0,1,1], # num 3
    [0,1,1,1,1,0,1,1], # num 2
    [1,0,0,1,0,0,0,1], # num 1
    [1,1,1,1,1,1,0,1]  # num 0
]

# Initialize Arduino board
board = ArduinoMega(port)  # Replace 'COM6' with the port connected to your Arduino
iterator = util.Iterator(board)
iterator.start()
#speaker pin
#tone_pin = board.get_pin('d:48:output')

# Set pin modes
def setup():
    board.digital[stcp_Pin].mode = pyfirmata.OUTPUT
    board.digital[shcp_Pin].mode = pyfirmata.OUTPUT
    board.digital[ds_Pin].mode = pyfirmata.OUTPUT
    board.digital[stcp_Pin].write(0)
    board.digital[shcp_Pin].write(0)
    board.digital[ds_Pin].write(0)

    board.digital[latchPin].mode = pyfirmata.OUTPUT
    board.digital[dataPin].mode = pyfirmata.OUTPUT
    board.digital[clockPin].mode = pyfirmata.OUTPUT
    board.digital[latchPin].write(0)
    board.digital[dataPin].write(0)
    board.digital[clockPin].write(0)
    
    
    board.digital[latchPin2].mode = pyfirmata.OUTPUT
    board.digital[dataPin2].mode = pyfirmata.OUTPUT
    board.digital[clockPin2].mode = pyfirmata.OUTPUT    
    board.digital[latchPin2].write(0)
    board.digital[dataPin2].write(0)
    board.digital[clockPin2].write(0)
    
    board.digital[buttonPin].mode = pyfirmata.INPUT
    board.digital[buttonPin].when_activated = button1()
    
    board.digital[buttonPin2].mode = pyfirmata.INPUT
    board.digital[buttonPin2].when_activated = button2()
    
    board.digital[PIN_BLUE].mode = pyfirmata.OUTPUT
    board.digital[PIN_GREEN].mode = pyfirmata.OUTPUT
    board.digital[PIN_RED].mode = pyfirmata.OUTPUT
    board.digital[speakerPin].mode = pyfirmata.OUTPUT
    board.digital[lightChange].mode = pyfirmata.OUTPUT
    board.digital[redLightViolated].mode = pyfirmata.INPUT
    

    
   


def button1():
    global buttonValue
    buttonValue += 1
    #print(buttonValue)

def button2():
    global buttonValue2
    buttonValue2 += 1
    #print(buttonValue2)


def default_lights():
    global last_update_time, active, active2, td
    current_time = time.time()
    
    board.digital[latchPin].write(0)
    shiftOut(dataPin, clockPin, 'MSBFIRST', [0,0,0,0,0,0,0,0])
    board.digital[latchPin].write(1)

    board.digital[latchPin2].write(0)
    shiftOut(dataPin2, clockPin2, 'MSBFIRST', [0,0,0,0,0,0,0,0])
    board.digital[latchPin2].write(1)

    if current_time - last_update_time >= defaultLightsInterval:
        last_update_time = current_time

        if board.digital[buttonPin].read() == 1:
            active = 1;

        if board.digital[buttonPin2].read() == 1:
            active2 = 1;
        
        isViolated()
            
        #print("Entering td")
        wait_start_time = time.time()
        while time.time() - wait_start_time <= td:
            board.digital[stcp_Pin].write(0)
            shiftOut(ds_Pin, shcp_Pin, 'LSBFIRST', [0,0,0,1,1,0,0,0])
            board.digital[stcp_Pin].write(1)
            active = lights_way2(tdreset, active2)
            if board.digital[buttonPin].read() == 1:
                active = 1
        
            isViolated()
        active2 = 0

        # Check buttons again before proceeding
        if board.digital[buttonPin].read() == 1:
            active = 1
        if board.digital[buttonPin2].read() == 1:
            active2 = 1
        isViolated()
            
            

        #print("Entering td1/2")
        wait_start_time = time.time()
        while time.time() - wait_start_time <= (td / 2):
            board.digital[stcp_Pin].write(0)
            shiftOut(ds_Pin, shcp_Pin, 'LSBFIRST', [0,0,0,1,0,1,0,0])
            board.digital[stcp_Pin].write(1)
            if board.digital[buttonPin].read() == 1:
                active = 1
        
            isViolated()
                
                
                
        # Check buttons again before proceeding
        if board.digital[buttonPin].read():
            active = 1
        if board.digital[buttonPin2].read():
            active2 = 1
        
        isViolated()
            
            

        #print("Entering td1/3")
        board.digital[lightChange].write(0)
        wait_start_time = time.time()
        while time.time() - wait_start_time <= (td / 3):
            board.digital[stcp_Pin].write(0)
            shiftOut(ds_Pin, shcp_Pin, 'LSBFIRST', [0,0,0,1,0,0,0,1])
            board.digital[stcp_Pin].write(1)
            if board.digital[buttonPin].read() == 1:
                active = 1
        
            isViolated()
                
                

        # Check buttons again before proceeding
        if board.digital[buttonPin].read():
            active = 1
        if board.digital[buttonPin2].read():
            active2 = 1
        
        isViolated()
            
            
            
        #print("Entering td2")

        wait_start_time = time.time()
        while time.time() - wait_start_time <= td:
            #print("entered 4th loop")
            board.digital[stcp_Pin].write(0)
            shiftOut(ds_Pin, shcp_Pin, 'LSBFIRST', [0,1,0,0,0,0,0,1])
            board.digital[stcp_Pin].write(1)
            active2 = lights_way1(tdreset, active)
            if board.digital[buttonPin2].read() == 1:
                active2 = 1
            isViolated()
                
                

        active = 0

        # Check buttons again before proceeding
        if board.digital[buttonPin].read():
            active = 1
        if board.digital[buttonPin2].read():
            active2 = 1
        
        isViolated()
            
            
        
        #print("Entering td2/2")
        wait_start_time = time.time()
        while time.time() - wait_start_time <= (td / 2):
            board.digital[stcp_Pin].write(0)
            shiftOut(ds_Pin, shcp_Pin, 'LSBFIRST', [0,0,1,0,0,0,0,1])
            board.digital[stcp_Pin].write(1)
            if board.digital[buttonPin].read() == 1:
                active = 1
        
            isViolated()
                
                

        # Check buttons again before proceeding
        if board.digital[buttonPin].read():
            active = 1
        if board.digital[buttonPin2].read():
            active2 = 1
        
        isViolated()
            
            
            
        board.digital[lightChange].write(1)
        #print("Entering td2/3")
        wait_start_time = time.time()
        while time.time() - wait_start_time <= (td / 3):
            board.digital[stcp_Pin].write(0)
            shiftOut(ds_Pin, shcp_Pin, 'LSBFIRST', [0,0,0,1,0,0,0,1])
            board.digital[stcp_Pin].write(1)
            if board.digital[buttonPin].read() == 1:
                active = 1
        
            isViolated()
                
                
        
        td = tdreset
    #print("Done Method")


def lights_way2(read, active3):
    active = 0
    board.digital[PIN_GREEN].write(1)
    board.digital[PIN_RED].write(0)
    startTime = time.time()
    while time.time() - startTime <= 1:
        tone(2500)
        if board.digital[buttonPin].read() == 1:    
            active = 1
        isViolated()
            
            

    startTime = time.time()
    while time.time() - startTime <= (read / 2):
        if board.digital[buttonPin].read() == 1:    
            active = 1
        isViolated()
            
            

    if board.digital[buttonPin].read() == 1:    
        active = 1
    
    isViolated()
        
    board.digital[stcp_Pin].write(1)

    startTime = time.time()
    while time.time() - startTime <= (read / 4):
        if board.digital[buttonPin].read() == 1:    
            active = 1
        isViolated()
            
            

    if board.digital[buttonPin].read() == 1:    
        active = 1
    isViolated()
        
        

    startTime = time.time()
    while time.time() - startTime <= 1:
        if board.digital[buttonPin].read() == 1:    
            active = 1
        isViolated()
            
            

    if board.digital[buttonPin].read() == 1:    
        active = 1
    isViolated()
        
        

    if active3 == 1:
        #print("active == 1")
        for i in range(10):
            board.digital[latchPin2].write(0)
            shiftOut(dataPin2, clockPin2, 'MSBFIRST', values2[i])
            board.digital[latchPin2].write(1)
            startTime = time.time()
            while time.time() - startTime <= 1:
                if board.digital[buttonPin].read() == 1:    
                    active = 1
                isViolated()
            if i == 9:
                board.digital[PIN_GREEN].write(0)
                board.digital[latchPin2].write(0)
                shiftOut(dataPin2, clockPin2, 'MSBFIRST', [0,0,0,0,0,0,0,0])
                board.digital[latchPin2].write(1)

    elif active3 == 0:
        for i in range(7):
            board.digital[latchPin2].write(0)
            shiftOut(dataPin2, clockPin2, 'MSBFIRST', valuesnew2[i])
            board.digital[latchPin2].write(1)
            startTime = time.time()
            while time.time() - startTime <= 1:
                if board.digital[buttonPin].read() == 1:    
                    active = 1
                isViolated()
                    
            j = 6
            if i == j:
                board.digital[PIN_GREEN].write(0)
                board.digital[latchPin2].write(0)
                shiftOut(dataPin2, clockPin2, 'MSBFIRST', [0,0,0,0,0,0,0,0])
                board.digital[latchPin2].write(1)
    
    startTime = time.time()
    while time.time() - startTime <= 1:
        tone( 5000)
        if board.digital[buttonPin2].read == 1:    
            active2 = 1          
        isViolated()
            
              

    board.digital[PIN_GREEN].write(0)
    board.digital[PIN_RED].write(1)
    #print("return active == 0")
    return active

def lights_way1(read, active1):
    active2 = 0
    board.digital[PIN_GREEN].write(1)
    board.digital[PIN_RED].write(0)
    
    startTime = time.time()

    while time.time() - startTime <= 1:
        tone(500)
        if board.digital[buttonPin2].read() == 1:    
            active2 = 1
        isViolated()
            
            
        
    startTime = time.time()
    while time.time() - startTime <= (read):
        if board.digital[buttonPin2].read() == 1:    
            active2 = 1
        isViolated()
            
            

    if board.digital[buttonPin2].read() == 1:    
        active2 = 1
    isViolated()
        
        

    board.digital[stcp_Pin].write(1)

    startTime = time.time()
    while time.time() - startTime <= (read / 4):
        if board.digital[buttonPin2].read() == 1:    
            active2 = 1
        isViolated()
            
            

    if board.digital[buttonPin2].read() == 1:    
        active2 = 1
    isViolated()
        
        

    startTime = time.time()
    while time.time() - startTime <= 1:
        if board.digital[buttonPin2].read() == 1:    
            active2 = 1
        isViolated()
            
            

    if board.digital[buttonPin2].read() == 1:    
        active2 = 1
    isViolated()
        
        

    if active1 == 1:
        for i in range(10):
            board.digital[latchPin].write(0)
            shiftOut(dataPin, clockPin, 'MSBFIRST', values[i])
            board.digital[latchPin].write(1)
            startTime = time.time()
            while time.time() - startTime <= 1:
                if board.digital[buttonPin2].read() == 1:    
                    active2 = 1
                isViolated()
            if i == 9:
                board.digital[latchPin].write(0)
                shiftOut(dataPin, clockPin, 'MSBFIRST', [0,0,0,0,0,0,0,0])
                board.digital[latchPin].write(1)

    elif active1 == 0:
        #print("active1==0")
        for i in range(7):
            board.digital[latchPin].write(0)
            shiftOut(dataPin, clockPin, 'MSBFIRST', valuesnew[i])
            board.digital[latchPin].write(1)
            startTime = time.time()
            while time.time() - startTime <= 1:
                if board.digital[buttonPin2].read() == 1:    
                    active2 = 1
                isViolated()
 
            j = 6
            if i == j:
                board.digital[PIN_GREEN].write(0)
                board.digital[latchPin].write(0)
                shiftOut(dataPin, clockPin, 'MSBFIRST', [0,0,0,0,0,0,0,0])
                board.digital[latchPin].write(1)

    startTime = time.time()                
    while time.time() - startTime <= 1:
        tone(1000)

    board.digital[PIN_GREEN].write(0)
    board.digital[PIN_RED].write(1)
    return active2

def shiftOut(dataPin, clockPin, bitOrder, val):
    bits = val
    if bitOrder == 'LSBFIRST':
        bits = val[::-1]
        
    for bit in bits:
        # Write each bit to the data pin
        board.digital[dataPin].write(bit)
        # Pulse the clock pin to shift the next bit
        board.digital[clockPin].write(1)
        time.sleep(.01)
        board.digital[clockPin].write(0)
        time.sleep(.01)

def tone( frequency):
    """
    Generate a tone of specified frequency and duration on the given pin.
    """
    #print(frequency)
    pinStatus = 0;
    startTime = time.time()
    period = (1/(frequency/10))
    half_period = period/2
    cycles = int(frequency*10)
    previousTime = time.time()
    #print(time.time()-startTime)
    while time.time() - startTime < 1:
        if time.time() - previousTime >= half_period:
            previousTime = time.time()
            if pinStatus == 0:
                board.digital[speakerPin].write(1) 
                pinStatus = 1
            else:
                board.digital[speakerPin].write(0)  # Turn off tone
                pinStatus = 0
        
def isViolated():
    if board.digital[redLightViolated].read() == 1:
            print("Violated!")
            tone(10000)

while True:
    print("Starting Default: " + str(tdreset))
    setup()
    default_lights()