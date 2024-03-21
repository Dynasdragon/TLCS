#Object detection using YOLO + coco files from https://pjreddie.com/darknet/yolo/
#Must hv YOLO weights file (yolov3.weights), configuration file (yolov3.cfg), and the COCO names file (coco.names) to test.
#Edit to use our trained models

import cv2
import numpy as np
from flask import Flask, request, Response

app = Flask(__name__)

# Load YOLO
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getUnconnectedOutLayersNames()

@app.route('/upload', methods=['POST'])
def upload():
    # Receive image data from the ESP32-CAM
    image_data = request.data
    nparr = np.frombuffer(image_data, np.uint8)
    
    # Decode the image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Perform object detection
    height, width, _ = img.shape
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(layer_names)

    class_ids = []
    confidences = []
    boxes = []

    # Parse the detection results
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Draw bounding boxes and labels on the image
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]
            color = (0, 255, 0)  # Green
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Save or process the annotated image as needed
    cv2.imwrite("annotated_image.jpg", img)

    return Response(response="Object detection result", status=200)

if __name__ == '__main__':
    # Run the Flask server
    app.run(host='0.0.0.0', port=5000)
