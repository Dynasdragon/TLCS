from tracemalloc import start
import pyfirmata
import time
import sys
import pyodbc 
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import queue


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
   print("listening on thread")
   data = request.get_json()
   data = jsonify(data)
   print(data)
   return data
@app.route("/closePort", methods=["GET"])
def closePort():
   print("Closing Port")
   q.put(True)
   global stopPort 
   stopPort = True
   data = jsonify("resp: success")
   return data


q = queue.Queue()
if __name__ == "__main__": 
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

port = 'COM5'
board = pyfirmata.Arduino(port)

it = pyfirmata.util.Iterator(board)
it.start()

#set pin 10 as digital input
board.digital[12].mode = pyfirmata.INPUT

#stallTime = int(sys.argv[1])
#print(stallTime)
#sys.stdout.flush()
while not stopPort:
        
        #reads pin 10   
        sw = board.digital[12].read()
    
        #change pin 13
        if sw is True:
            #print("Setting", flush=True)
            #sys.stdout.flush()
            board.digital[13].write(1)
            #time.sleep(stallTime)
        else:
            #print("Turning off", flush = True)
            #sys.stdout.flush()
            board.digital[13].write(0)
        
#wait 0.1 seconds between iterations
time.sleep(0.1)
print("Done", flush = True)
sys.stdout.flush()
