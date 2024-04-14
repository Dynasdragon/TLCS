#Traffic Light Control System
The traffic light control system is a database management system that receives images and related data of a model traffic light system and dispalys it for users to see. The system also initiates the traffic light system with the latest uploaded parameters (eg. light switching timers), and allows for real-time changes to these parameters. This project was created to design and build a new innovative traffic light control system that uses AI learning to detect objects like pedestrians, cars, and license plates. The program's frontend was made using Electron and React. While the backend was created using python and C++, in Arduino's IDE.

The system communicates to each physical components through TCP connections, while the frontend and backend communicate using FastAPI. The program also deploys a YOLOv5-based object detection and Tesseract optical text recognition software to find and read license plates, then storing it into the database.

#Installation

react-notications
torch (pytorch)
pytesseract
ultralytics

download tesseract
add tesseract to path environment
update tesseract_cmd's path in detect.py to wherever tesseract.exe is
