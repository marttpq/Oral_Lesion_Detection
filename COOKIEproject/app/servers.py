from flask import Flask, request, render_template
import cv2
import numpy as np
import json
from ultralytics import YOLO
import os


app = Flask(__name__)

# ฟังก์ชันสำหรับการอัพโหลดไฟล์
def upload_file(file):

    filename = file.filename

    file.save("uploads/" + filename)

    filename = "uploads/" + filename

    return filename

# ฟังก์ชันสำหรับการประมวลผลภาพ
def process_image(image):
    # Load the YOLOv8 model
    model = YOLO("static/model/yolov8.pt")
    # Perform object detection with YOLO
    result = model(image, verbose=True, device='cpu')
    # Initialize empty lists for lesion categories
    Leukoplakia = []
    Lichenplanus = []
    Candidiasis = []
    OtherWhite = []
    Ulcer = []

    # Process each detected object
    for r in result:
        boxes = r.boxes
        for box in boxes:
            b = box.xyxy[0]
            x = int(b[0])
            y = int(b[1])
            x1 = int(b[2])
            y1 = int(b[3])
            cls = int(box.cls)
            confidence = round(float(box.conf), 2)
            label = model.names[cls] + f" {confidence}"
            if model.names[cls] == 'Leukoplakia':
                Leukoplakia.append(((x, y), (x1, y1)))
                cv2.rectangle(image, (x, y), (x1, y1), (0, 255, 0), 1)
                cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            elif model.names[cls] == 'Lichenplanus':
                Lichenplanus.append(((x, y), (x1, y1)))
                cv2.rectangle(image, (x, y), (x1, y1), (0, 0, 255), 1)
                cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            elif model.names[cls] == 'Candidiasis':
                Candidiasis.append(((x, y), (x1, y1)))
                cv2.rectangle(image, (x, y), (x1, y1), (255, 0, 0), 1)
                cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            elif model.names[cls] == 'OtherWhite':
                OtherWhite.append(((x, y), (x1, y1)))
                cv2.rectangle(image, (x, y), (x1, y1), (128, 128, 128), 1)
                cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (128, 128, 128), 2)
            elif model.names[cls] == 'Ulcer':
                Ulcer.append(((x, y), (x1, y1)))
                cv2.rectangle(image, (x, y), (x1, y1), (255, 140, 0), 1)
                cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 140, 0), 2)

    # Save processed image
    cv2.imwrite("static/output/processed.jpg", image)
    image_output = "/static/output/processed.jpg"

    # Save to results folder
    output_folder = "results/"
    file_extension = ".jpg"
    count = 1
    while os.path.exists(f"{output_folder}{count}{file_extension}"):
        count += 1
    filenames = f"{output_folder}{count}{file_extension}"
    cv2.imwrite(filenames, image)
    return image_output, label


@app.route("/")

def index():
    return render_template("index.html")


@app.route("/uploaded", methods=["POST"])
def uploaded():
    file = request.files["file"]
    filename = upload_file(file)
    image = cv2.imread(filename)
    image_output, label = process_image(image)
    return render_template("index.html", image_output=image_output, label=label)


if __name__ == "__main__":
    app.run()