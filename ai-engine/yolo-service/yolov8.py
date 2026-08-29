from ultralytics import YOLO
import cv2

model = YOLO('static/model/yolov8.pt')
# print(model.names)


img = cv2.imread('uploads/v_can_5.jpg')
# img = cv2.resize(img, (768, 1366))
result = model(img, verbose=True, device='cpu')

Leukoplakia = []
Lichenplanus = []
Candidiasis = []
OtherWhite = []
Ulcer = []

cs_list = []
conf_list = []

for r in result:
    boxes = r.boxes
    for box in boxes:
        b = box.xyxy[0]
        x = int(b[0])
        y = int(b[1])
        x1 = int(b[2])
        y1 = int(b[3])
        cls = int(box.cls)
        confidence = round(float(box.conf), 2)  # ปัดเศษให้เหลือสองตำแหน่ง

        label = model.names[cls] + f' {confidence}'  # เพิ่ม confidence score ใน label

        if model.names[cls] == 'Leukoplakia':
            Leukoplakia.append(((x, y), (x1, y1)))
            cv2.rectangle(img, (x, y), (x1, y1), (0, 255, 0), 1)
            cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cs_list.append(model.names[cls])
            conf_list.append(confidence)
        elif model.names[cls] == 'Lichenplanus':
            Lichenplanus.append(((x, y), (x1, y1)))
            cv2.rectangle(img, (x, y), (x1, y1), (0, 0, 255), 1)
            cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cs_list.append(model.names[cls])
            conf_list.append(confidence)

        elif model.names[cls] == 'Candidiasis':
            Candidiasis.append(((x, y), (x1, y1)))
            cv2.rectangle(img, (x, y), (x1, y1), (255, 0, 0), 1)
            cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            cs_list.append(model.names[cls])
            conf_list.append(confidence)

        elif model.names[cls] == 'OtherWhite':
            OtherWhite.append(((x, y), (x1, y1)))
            cv2.rectangle(img, (x, y), (x1, y1), (128, 128, 128), 1)
            cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (128, 128, 128), 2)
            cs_list.append(model.names[cls])
            conf_list.append(confidence)

        elif model.names[cls] == 'Ulcer':
            Ulcer.append(((x, y), (x1, y1)))
            cv2.rectangle(img, (x, y), (x1, y1), (255, 140, 0), 1)
            cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 140, 0), 2)
            cs_list.append(model.names[cls])
            conf_list.append(confidence)

    print(cs_list)
    print(conf_list)
cv2.imshow('image', img)
cv2.waitKey(0)