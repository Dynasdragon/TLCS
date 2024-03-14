from pyfirmata import Arduino, util
import time

# Define pin numbers for output
stcp_Pin = 4
shcp_Pin = 3
ds_Pin = 2

dataPin = 11
latchPin = 12
clockPin = 13
buttonPin = 10

#red led on pin 9
#green led on pin 10
#blue led on pin 11
PIN_RED = 5
PIN_GREEN = 6
PIN_BLUE = 7

# Define intervals for each state
defaultLightsInterval = 1.5
way1Interval = 1.5
greenLightInterval = 1
segmentDisplayInterval = 1.5

td = 5
tdreset = 5

active = 0
buttonValue = 0

# Define LED patterns
values = [
    int('11110110', 2),  # num 9
    int('11111110', 2),  # num 8
    int('11100000', 2),  # num 7
    int('10111110', 2),  # num 6
    int('10110110', 2),  # num 5
    int('01100110', 2),  # num 4
    int('11110010', 2),  # num 3
    int('11011010', 2),  # num 2
    int('01100000', 2),  # num 1
    int('11111101', 2)   # num 0
]

valuesnew = [
    int('10111110', 2),  # num 6
    int('10110110', 2),  # num 5
    int('01100110', 2),  # num 4
    int('11110010', 2),  # num 3
    int('11011010', 2),  # num 2
    int('01100000', 2),  # num 1
    int('11111101', 2)   # num 0
]

# Initialize Arduino board
board = Arduino('COM6')  # Replace 'COM6' with the port connected to your Arduino
iterator = util.Iterator(board)
iterator.start()

# Set pin modes
board.digital[stcp_Pin].mode = board.digital[buttonPin].INPUT
board.digital[shcp_Pin].mode = board.digital[buttonPin].INPUT
board.digital[ds_Pin].mode = board.digital[buttonPin].INPUT

board.digital[latchPin].mode = board.OUTPUT
board.digital[dataPin].mode = board.OUTPUT
board.digital[clockPin].mode = board.OUTPUT
board.digital[PIN_RED].mode = board.OUTPUT
board.digital[PIN_GREEN].mode = board.OUTPUT 
board.digital[PIN_BLUE].mode = board.OUTPUT


def button1():
    global buttonValue
    buttonValue += 1
    print(buttonValue)


def default_lights():
    global active, td, tdreset
    currentTime = time.time()

    if currentTime - lastUpdateTime >= defaultLightsInterval:
        lastUpdateTime = currentTime

        if board.digital[buttonPin].read() == 1:
            active = 1

        waitStartTime = time.time()
        while time.time() - waitStartTime <= td:
            board.digital[stcp_Pin].write(0)
            board.shiftOut(ds_Pin, shcp_Pin, board.LSBFIRST, 0B00011000)
            board.digital[stcp_Pin].write(1)
            if board.digital[buttonPin].read() == 1:
                active = 1

        if board.digital[buttonPin].read() == 1:
            active = 1

        waitStartTime = time.time()
        while time.time() - waitStartTime <= (td / 2):
            board.digital[stcp_Pin].write(0)
            board.shiftOut(ds_Pin, shcp_Pin, board.LSBFIRST, 0B00010100)
            board.digital[stcp_Pin].write(1)
            if board.digital[buttonPin].read() == 1:
                active = 1

        if board.digital[buttonPin].read() == 1:
            active = 1

        waitStartTime = time.time()
        while time.time() - waitStartTime <= (td / 3):
            board.digital[stcp_Pin].write(0)
            board.shiftOut(ds_Pin, shcp_Pin, board.LSBFIRST, 0B00010001)
            board.digital[stcp_Pin].write(1)
            if board.digital[buttonPin].read() == 1:
                active = 1

        if board.digital[buttonPin].read() == 1:
            active = 1

        waitStartTime = time.time()
        while time.time() - waitStartTime <= td:
            board.digital[stcp_Pin].write(0)
            board.shiftOut(ds_Pin, shcp_Pin, board.LSBFIRST, 0B01000001)
            board.digital[stcp_Pin].write(1)
            lights_way1(tdreset, active)

        active = 0

        if board.digital[buttonPin].read() == 1:
            active = 1

        waitStartTime = time.time()
        while time.time() - waitStartTime <= (td / 2):
            board.digital[stcp_Pin].write(0)
            board.shiftOut(ds_Pin, shcp_Pin, board.LSBFIRST, 0B00100001)
            board.digital[stcp_Pin].write(1)
            if board.digital[buttonPin].read() == 1:
                active = 1

        if board.digital[buttonPin].read() == 1:
            active = 1

        waitStartTime = time.time()
        while time.time() - waitStartTime <= (td / 3):
            board.digital[stcp_Pin].write(0)
            board.shiftOut(ds_Pin, shcp_Pin, board.LSBFIRST, 0B00010001)
            board.digital[stcp_Pin].write(1)
            if board.digital[buttonPin].read() == 1:
                active = 1

        td = tdreset


def lights_way1(read, active1):
    board.digital[PIN_GREEN].write(1)
    board.digital[PIN_RED].write(0)
    startTime = time.time()
    while time.time() - startTime <= (read / 2):
        pass

    startTime = time.time()
    while time.time() - startTime <= (read / 4):
        pass

    startTime = time.time()
    while time.time() - startTime <= 1:
        pass

    if active1 == 1:
        for i in range(10):
            board.digital[latchPin].write(0)
            board.shiftOut(dataPin, clockPin, board.MSBFIRST, values[i])
            board.digital[latchPin].write(1)
            startTime = time.time()
            while time.time() - startTime <= 1:
                pass

            if i == 9:
                board.digital[PIN_GREEN].write(0)
                board.digital[buttonPin].write(1)
                board.shiftOut(dataPin, clockPin, board.MSBFIRST, 0B00000000)

    elif active1 == 0:
        for i in range(7):
            board.digital[latchPin].write(0)
            board.shiftOut(dataPin, clockPin, board.MSBFIRST, valuesnew[i])
            board.digital[latchPin].write(1)
            startTime = time.time()
            while time.time() - startTime <= 1000:
                pass
            j = 6
            if i == j:
                board.digital[PIN_GREEN].write(0)
                board.digital[buttonPin].write(1)
                board.shiftOut(dataPin, clockPin, board.MSBFIRST, 0B00000000)
        board.digital[PIN_GREEN].write(0)
        board.digital[PIN_RED].write(1)
        board.digital[buttonPin].write(0)
        active = 0

def loop():
    default_lights()
                    
                