import pyfirmata
import time
import sys

port = 'COM6'
board = pyfirmata.Arduino(port)

it = pyfirmata.util.Iterator(board)
it.start()

#set pin 10 as digital input
board.digital[10].mode = pyfirmata.INPUT

#while True:
    #reads pin 10   
    #sw = board.digital[10].read()
    
    #change pin 13
    #if sw is True:
print("Setting", flush=True)
sys.stdout.flush()
board.digital[13].write(1)
time.sleep(5)
    #else:
print("Turning off", flush = True)
sys.stdout.flush()
board.digital[13].write(0)
        
    #wait 0.1 seconds between iterations
time.sleep(0.1)
print("Done", flush = True)
sys.stdout.flush()
