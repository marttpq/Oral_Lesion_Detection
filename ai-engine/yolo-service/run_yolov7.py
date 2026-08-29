import torch
import cv2
import numpy as np
import os
import sys
import glob
from collections import defaultdict

# --- CONFIGURATION ---
MODEL_PATH = os.getenv("YOLO_V7_MODEL_FILE", "yolov7.pt")
DEFAULT_INPUT = "test_image.jpg"
CONF_THRESHOLD = 0.3  # Temporarily lower to see everything
IOU_THRESHOLD = 0.45
ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.JPG', '.PNG', '.bmp', '.webp')

# MAPPING: Standardize everything to a common key
NAME_MAP = {
    "leukoplakia": "Leukoplakia",
    "lichenplanus": "Lichen planus",
    "lichen planus": "Lichen planus",
    "candidiasis": "Candidiasis",
    "otherwhite": "Linea alba buccalis",
    "other white": "Linea alba buccalis",
    "lineaalbabuccalis": "Linea alba buccalis",
    "linea alba buccalis": "Linea alba buccalis",
    "ulcer": "Ulcer",
}

def standardize(name):
    if not name: return "Unknown"
    clean = str(name).lower().strip().replace("_", "").replace("-", "")
    if clean in NAME_MAP: return NAME_MAP[clean]
    clean_nospace = clean.replace(" ", "")
    if clean_nospace in NAME_MAP: return NAME_MAP[clean_nospace]
    return name

YOLOv7_REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yolov7 - Copy")
if YOLOv7_REPO not in sys.path:
    sys.path.insert(0, YOLOv7_REPO)

def load_yolov7(model_path):
    print(f"--- Loading YOLOv7 Model ---")
    try:
        from models.experimental import attempt_load
        
        device = torch.device("cpu")
        model = attempt_load(model_path, map_location=device)
        model.eval()
        
        # We'll attach necessary attributes for inference to the model object
        model.conf = CONF_THRESHOLD
        model.iou = IOU_THRESHOLD
        
        print(f"Model Labels: {model.names}")
        print("Model loaded successfully via native YOLOv7 code.\n")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_inference(model, image_path, output_dir, ground_truth=None):
    from utils.datasets import letterbox
    from utils.general import non_max_suppression, scale_coords

    img0 = cv2.imread(image_path)
    if img0 is None: return None

    # Preprocess exactly as WongKinYiu detect.py does
    device = torch.device("cpu")
    stride = int(model.stride.max())
    img = letterbox(img0, 640, stride=stride)[0]
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(device).float()
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # Run inference
    with torch.no_grad():
        pred = model(img, augment=False)[0]

    # NMS
    pred = non_max_suppression(pred, CONF_THRESHOLD, IOU_THRESHOLD, classes=None, agnostic=False)
    
    class_names = model.names 

    std_gt = standardize(ground_truth) if ground_truth else None
    
    # GROUPING: Store detections by class
    grouped_detections = defaultdict(lambda: {"count": 0, "confidences": [], "boxes": []})
    
    total_preds = 0
    for i, det in enumerate(pred):
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()
            
            for *xyxy, conf, cls in reversed(det):
                box_coords = [float(c) for c in xyxy]
                conf = float(conf)
                cls_id = int(cls)
                
                label = class_names[cls_id]
                std_label = standardize(label)
                
                grouped_detections[label]["count"] += 1
                grouped_detections[label]["confidences"].append(conf)
                grouped_detections[label]["boxes"].append({"box": box_coords, "std_label": std_label})
                total_preds += 1

    # Find the top overall class for validation
    top_label = "No Detection"
    top_avg_conf = 0.0
    
    print(f" Image: {os.path.basename(image_path)}")
    if not grouped_detections:
        print("   -> [NO DETECTIONS FOUND]")
    
    for label, data in grouped_detections.items():
        avg_conf = sum(data["confidences"]) / data["count"]
        std_label = data["boxes"][0]["std_label"]
        
        print(f"   -> Found: {label} (Avg: {avg_conf:.2f}) - {data['count']} times")
        
        if avg_conf > top_avg_conf:
            top_avg_conf = avg_conf
            top_label = label

    # Check correctness if ground_truth is provided
    is_correct = False
    if std_gt:
        # Check if ANY of our grouped standardized labels match the standard ground truth
        for label, data in grouped_detections.items():
            if data["boxes"][0]["std_label"] == std_gt:
                is_correct = True
                break

    # Visualization
    img_draw = img0.copy()
    for label, data in grouped_detections.items():
        avg_conf = sum(data["confidences"]) / data["count"]
        for box_info in data["boxes"]:
            x1, y1, x2, y2 = map(int, box_info["box"])
            is_det_gt = (std_gt and box_info["std_label"] == std_gt)
            color = (0, 255, 0) if is_det_gt else (0, 0, 255)
            cv2.rectangle(img_draw, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img_draw, f"{label} {avg_conf:.2f}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Save logic
    res_status = "OK" if is_correct else "FAIL"
    sub_folder = "Correct" if is_correct else "Incorrect"
    save_path = os.path.join(output_dir, sub_folder)
    if not os.path.exists(save_path): os.makedirs(save_path)
    cv2.imwrite(os.path.join(save_path, f"{res_status}_{os.path.basename(image_path)}"), img_draw)

    return {"is_correct": is_correct, "total_detections": total_preds}

if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    model = load_yolov7(MODEL_PATH)
    if not model: sys.exit(1)

    output_root = "validation_debug"
    if not os.path.exists(output_root): os.makedirs(output_root)

    stats = {"total": 0, "correct": 0, "by_folder": defaultdict(lambda: {"total": 0, "correct": 0})}

    if os.path.isdir(input_path):
        print(f"Starting Debug Scan on: {input_path}\n")
        
        # Limit to first 5 images per folder for debugging if needed, 
        # but here we'll do all and the user can see the logs
        for root, dirs, files in os.walk(input_path):
            folder_name = os.path.basename(root)
            images = [f for f in files if f.lower().endswith(ALLOWED_EXTENSIONS)]
            if not images: continue

            print(f"\n--- Folder: {folder_name} (GT: {standardize(folder_name)}) ---")
            
            for img_name in images:
                img_path = os.path.join(root, img_name)
                result = run_inference(model, img_path, output_root, ground_truth=folder_name)
                
                if result:
                    stats["total"] += 1
                    stats["by_folder"][folder_name]["total"] += 1
                    if result["is_correct"]:
                        stats["correct"] += 1
                        stats["by_folder"][folder_name]["correct"] += 1

        print("\n" + "="*50)
        print(f" FINAL DEBUG ACCURACY: { (stats['correct']/stats['total']*100) if stats['total']>0 else 0 :.2f}%")
        print("="*50)
    else:
        run_inference(model, input_path, output_root)
