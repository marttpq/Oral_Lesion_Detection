import os
import sys
import inspect
import importlib
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent

try:
    yolo_mod = importlib.import_module("ultralytics")
    YOLO = getattr(yolo_mod, "YOLO")
except Exception as e:
    print(f"Could not load ultralytics: {e}")
    sys.exit(1)

try:
    cv2 = importlib.import_module("cv2")
except Exception:
    cv2 = None

v8_path = BASE_DIR / "yolov8.pt"
v7_path = BASE_DIR / "yolov7.pt"
model_path = v8_path if v8_path.exists() else v7_path

print(f"Loading YOLO from: {model_path}")
model = YOLO(str(model_path))
inner_model = getattr(model, "model", model)

def wrap_ignore_extra_kwargs(obj, method_name):
    orig_func = getattr(obj, method_name, None)
    if orig_func is None:
        return
    def wrapped(*args, **kwargs):
        sig = inspect.signature(orig_func)
        filtered = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return orig_func(*args, **filtered)
    setattr(obj, method_name, wrapped)

wrap_ignore_extra_kwargs(inner_model, 'forward')
wrap_ignore_extra_kwargs(inner_model, 'fuse')

# Test image resolution
img_path = BASE_DIR.parent.parent / "static" / "uploads"
img_files = list(img_path.glob("*.jpg")) if img_path.exists() else []

if img_files and cv2 is not None:
    test_img = cv2.imread(str(img_files[0]))
else:
    # Use dummy image tensor/array for testing inference
    test_img = np.zeros((640, 640, 3), dtype=np.uint8)

results = model(test_img)

print("\n===== YOLO TEST RESULTS =====")
if results and len(results) > 0 and getattr(results[0], "boxes", None) is not None:
    boxes = results[0].boxes
    if len(boxes) > 0:
        box = boxes[0]
        xyxy = box.xyxy[0].cpu().numpy().tolist()
        conf = float(box.conf[0].cpu().numpy())
        cls_idx = int(box.cls[0].cpu().numpy())
        print(f"Box 0 xyxy: {xyxy}")
        print(f"Box 0 conf: {conf:.4f}")
        print(f"Box 0 cls : {cls_idx}")
    else:
        print("Model inference succeeded: 0 objects detected.")
else:
    print("Model inference executed.")
print("=============================\n")
