from ultralytics import YOLO
import cv2
import inspect

model = YOLO('C:/Users/ADuoirds/Desktop/New/static/model/yolov7.pt')
inner_model = model.model

def wrap_ignore_extra_kwargs(obj, method_name):
    orig_func = getattr(obj, method_name)
    def wrapped(*args, **kwargs):
        sig = inspect.signature(orig_func)
        filtered = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return orig_func(*args, **filtered)
    setattr(obj, method_name, wrapped)

wrap_ignore_extra_kwargs(inner_model, 'forward')
wrap_ignore_extra_kwargs(inner_model, 'fuse')

img = cv2.imread('C:/Users/ADuoirds/Desktop/New/uploads/can (1).jpg')
results = model(img)

print("----- BOX 0 -----")
xyxy = results[0].boxes[0].xyxy[0].cpu().numpy()
conf = float(results[0].boxes[0].conf)
cls = int(results[0].boxes[0].cls)
print(f"xyxy: {xyxy}")
print(f"conf: {conf}")
print(f"cls: {cls}")
