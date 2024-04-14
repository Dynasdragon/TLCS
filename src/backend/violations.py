import io
import json
import socket
import time

import numpy as np
from PIL import Image
import pyodbc

socket_port = 80
buffer_size = 4096


serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# address '0.0.0.0' or '' work to allow connections from other machines.  'localhost' disallows external connections.
# see https://www.raspberrypi.org/forums/viewtopic.php?t=62108
serv.bind(('', socket_port))
serv.listen(5)
print(socket.gethostname())
print("Ready to accept 5 connections")
cnxn = pyodbc.connect("Driver={SQL Server};"
                      "Server=Eddys-Laptop\\SQLEXPRESS;"
                      "Database=TLCS;"
                      "uid=TLCS;"
                      "pwd=trafficlight;")


cursor = cnxn.cursor()
violations = []

def create_image_from_bytes(image_bytes) -> Image.Image:
    stream = io.BytesIO(image_bytes)
    return Image.open(stream)


while True:

    conn, addr = serv.accept()
    array_from_client = bytearray()
    chunks_received = 0
    start = time.time()
    shape_string = ''
    while True:
        # print('waiting for data')
        # Try 4096 if unsure what buffer size to use. Large transfer chunk sizes (which require large buffers) can cause corrupted results
        data = conn.recv(buffer_size)
        if not data or data == b'tx_complete':
            break
        else:
            shape_string += data.decode("utf-8")
            # Find the end of the line.  An index other than -1 will be returned if the end has been found because
            # it has been received
            if shape_string.find('\r\n') != -1:
                sender_index = shape_string.find('Client:')
                sender_end = shape_string.find('|')
                sender = shape_string[sender_index + len('Client:'): sender_end]
                print(sender)
                if sender == "Sensor":
                    speeding_index = shape_string.find('Speeding:')
                    speed_index = shape_string.find('Speed:')
                    light_index = shape_string.find('Light:')
                    time_index = shape_string.find('Time:')
                    series_index = shape_string.find('Series:')

                    speeding = shape_string[speeding_index + len('Speeding:'): speed_index]
                    speed = shape_string[speed_index + len('Speed:'): light_index]
                    light = shape_string[light_index + len('Light:'): time_index]
                    vtime = shape_string[time_index + len('Time:'):series_index]
                    series = shape_string[series_index + len('Series:'):shape_string.find('\r\n')]
                    row = {'id': series}
                    if speeding == "1":
                        row['speed'] = int(speed)
                    else:
                        row['speed'] = -1
                    if light == "1":
                        row['time'] = int(vtime)
                    else:
                        row['time'] = -1
                    row["imgPath"] = ""
                    print(speeding)
                    print(speed)
                    print(light)
                    print(vtime)
                    print(series)
                    print(row)
                    violations.append(row)
                elif sender == "Camera":
                    path_index = shape_string.find('Path:')
                    series_index = shape_string.find('Series:')
                    imagePath = shape_string[path_index + len("Path:"):series_index]
                    series = shape_string[series_index + len('Series:'):shape_string.find('\r\n')]
                    print(imagePath)
                    print(series)
                    print(violations)
                    #Look to find matching series
                    for v in violations:
                        if(v['id'] == series):
                            v['imgPath'] = imagePath
                            print(v)
                            f = open('../assets/lp.txt', 'r')
                            lp = f.readline()
                            print(lp)
                            f.close()
                            cursor.execute("SELECT IDENT_CURRENT('Violations')")
                            last_id = cursor.fetchone()[0]
                            print(last_id + 1)
                            cursor.execute(f'INSERT INTO Violations (date, intersectionID, carColour, licensePlate, imageID) VALUES (\'{time.strftime("%Y-%m-%d %H:%M")}\', 1, \'Red\', \'{lp}\', {last_id + 1})')
                            cursor.commit()
                            cursor.execute(f'INSERT INTO image (imageID, ImagePath) VALUES ({last_id+1},\'{imagePath}\')')
                            if v['speed'] != -1:
                                cursor.execute(f'INSERT INTO Speed (speedID, speed) VALUES ({last_id + 1},{int(v["speed"])})')
                            if v['time'] != -1:
                                cursor.execute(f'INSERT INTO redLight (redLightID, timeElapsed) VALUES ({last_id + 1},{int(v["time"])})')
                            cursor.commit()
                            violations.remove(v)
        #conn.sendall(b'ack')
        # print("sent acknowledgement")
    conn.close()
    print('client disconnected')