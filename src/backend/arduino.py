import pyfirmata
import time
import sys

port = 'COM5'
board = pyfirmata.Arduino(port)

it = pyfirmata.util.Iterator(board)
print(it)
sys.stdout.flush()
it.start()

#set pin 10 as digital input
board.digital[10].mode = pyfirmata.INPUT

stallTime = int(sys.argv[1])
print(stallTime)
sys.stdout.flush()

#while True:
    #reads pin 10   
    #sw = board.digital[10].read()
    
    #change pin 13
    #if sw is True:
print("Setting", flush=True)
sys.stdout.flush()
board.digital[13].write(1)
time.sleep(stallTime)
    #else:
print("Turning off", flush = True)
sys.stdout.flush()
board.digital[13].write(0)
        
    #wait 0.1 seconds between iterations
time.sleep(0.1)
print("Done", flush = True)
sys.stdout.flush()
