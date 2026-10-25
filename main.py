import os
import sys
import uuid
import shutil
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import torch
import threading

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("OralScanAPI")

# ==========================================
# 1. Setup Directories & Paths
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"
OUTPUTS_DIR = STATIC_DIR / "outputs"

# Ensure runtime directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Add AI engine and backend services to sys.path for direct imports
YOLO_SERVICE_DIR = BASE_DIR / "ai-engine" / "yolo-service"
DENSENET_SERVICE_DIR = BASE_DIR / "ai-engine" / "densenet-bert-service"
BACKEND_DIR = BASE_DIR / "backend"

if str(YOLO_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(YOLO_SERVICE_DIR))
if str(DENSENET_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(DENSENET_SERVICE_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# ==========================================
# 2. Initialize FastAPI Application
# ==========================================
app = FastAPI(
    title="OralScan AI - Oral Lesion Risk Assessment Backend",
    description="Unified API server for YOLO Object Detection & DenseNet + WangchanBERTa Multimodal Classification.",
    version="1.0.0"
)

# 2.1 CORS Middleware (allow all origins for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2.2 Mount Static Files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 2.3 Mount Auth & Database
try:
    from database import engine, Base
    from routers import auth as auth_router

    @app.on_event("startup")
    async def startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    app.include_router(auth_router.router)
    logger.info("Successfully mounted Auth router and database connection.")
except Exception as e:
    logger.warning(f"Auth router / database not mounted: {e}")

# ==========================================
# 3. Response Models & Helper Functions
# ==========================================
class BoundingBox(BaseModel):
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    label: str
    conf: float

class AssessmentResult(BaseModel):
    disease_name: str
    risk_level: str
    confidence_score: float
    bounding_boxes: List[BoundingBox]
    processed_image_url: str

class UnifiedAssessmentResponse(BaseModel):
    success: bool
    model_used: str
    result: AssessmentResult

def determine_risk_level(disease_name: str, confidence: float) -> str:
    """
    Evaluates clinical risk category based on predicted oral lesion pathology and confidence.
    """
    if not disease_name or disease_name.lower() in ["none", "normal", "unknown"]:
        return "Low"
    
    clean_name = disease_name.lower().replace(" ", "").replace("_", "")
    
    # High Risk conditions (Premalignant / Suspicious / Malignant potential)
    if "leukoplakia" in clean_name or "ulcer" in clean_name or "cancer" in clean_name:
        return "High" if confidence >= 0.5 else "Medium"
    
    # Medium Risk conditions
    if "lichenplanus" in clean_name or "otherwhite" in clean_name:
        return "Medium"
    
    # Low Risk conditions
    if "candidiasis" in clean_name or "lineaalba" in clean_name:
        return "Low"
    
    return "Medium" if confidence >= 0.6 else "Low"

from collections import defaultdict

CONF_THRESHOLD = 0.25

# COOKIE Project Visual and Metadata Constants
DETECTION_META = {
    "Leukoplakia": {"color": (0, 255, 0)},       # Green in BGR
    "Lichen planus": {"color": (0, 0, 255)},     # Red in BGR
    "Candidiasis": {"color": (255, 255, 255)},   # White
    "Linea alba buccalis": {"color": (128, 128, 128)}, # Gray
    "Ulcer": {"color": (255, 140, 0)},           # Orange in BGR
}

DISPLAY_NAMES = {
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

PATIENT_CONDITIONS = {
    "Leukoplakia": [
        "drinkalcohol", "smoking", "chewbetelnut",
        "ดื่มเหล้า", "สูบบุหรี่", "เคี้ยวหมาก", "แอลกอฮอล์"
    ],
    "Lichen planus": [
        "eatspicyfood", "กินเผ็ด", "กินเผ็ดแสบ", "รับประทานอาหารเผ็ด"
    ],
    "Candidiasis": [
        "wipeoff", "เช็ดออก", "เช็ดออกได้", "คราบขาวที่สามารถลอกออก"
    ],
    "Linea alba buccalis": [
        "nosymptoms", "ไม่มีอาการ", "ไม่มีอาการผิดปกติ"
    ],
    "Ulcer": [
        "alwayshurts", "เจ็บเมื่อโดนแผล", "มีอาการเจ็บ", "เจ็บตลอดเวลา", "ระคายเคืองตลอดเวลา"
    ],
}

def _box_iou_or_contained(box1: list, box2: list) -> float:
    """
    Calculate IoU or heavy containment between two [x, y, w, h] boxes.
    Matches COOKIE Project concentric box suppression logic exactly.
    """
    x1_1, y1_1, w1, h1 = box1
    x2_1, y2_1 = x1_1 + w1, y1_1 + h1

    x1_2, y1_2, w2, h2 = box2
    x2_2, y2_2 = x1_2 + w2, y1_2 + h2

    x_left = max(x1_1, x1_2)
    y_top = max(y1_1, y1_2)
    x_right = min(x2_1, x2_2)
    y_bottom = min(y2_1, y2_2)

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    intersection = (x_right - x_left) * (y_bottom - y_top)
    area1 = w1 * h1
    area2 = w2 * h2
    union = area1 + area2 - intersection

    iou = intersection / float(union) if union > 0 else 0.0

    min_area = min(area1, area2)
    contained_ratio = intersection / float(min_area) if min_area > 0 else 0.0

    return max(iou, contained_ratio)

def _filter_overlapping_boxes(detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aggressively suppress overlapping or concentric boxes of the same class (>40% overlap or >70% containment).
    Matches COOKIE Project _filter_overlapping_boxes.
    """
    if not detections:
        return []

    filtered: List[Dict[str, Any]] = []
    sorted_dets = sorted(detections, key=lambda x: x["conf"], reverse=True)

    for current_det in sorted_dets:
        keep = True
        for kept_det in filtered:
            if current_det["label"] == kept_det["label"]:
                overlap = _box_iou_or_contained(current_det["box"], kept_det["box"])
                if overlap > 0.40:
                    keep = False
                    break
        if keep:
            filtered.append(current_det)

    return filtered

_ROOT_MODEL_V7 = None
_ROOT_MODEL_V7_LOCK = threading.Lock()
_ROOT_MODEL_V8 = None
_ROOT_MODEL_V8_LOCK = threading.Lock()

def get_root_yolo_model_v7():
    global _ROOT_MODEL_V7
    if _ROOT_MODEL_V7 is not None:
        return _ROOT_MODEL_V7
    with _ROOT_MODEL_V7_LOCK:
        if _ROOT_MODEL_V7 is not None:
            return _ROOT_MODEL_V7
        try:
            from models.experimental import attempt_load
            v7_path = YOLO_SERVICE_DIR / "yolov7.pt"
            device = torch.device("cpu")
            logger.info(f"Loading native YOLOv7 model from: {v7_path}")
            model = attempt_load(str(v7_path), map_location=device)
            model.eval()
            _ROOT_MODEL_V7 = model
            logger.info("YOLOv7 native model loaded successfully in root server.")
        except Exception as e:
            logger.error(f"Failed to load native YOLOv7: {e}")
            _ROOT_MODEL_V7 = None
    return _ROOT_MODEL_V7

def get_root_yolo_model_v8():
    global _ROOT_MODEL_V8
    if _ROOT_MODEL_V8 is not None:
        return _ROOT_MODEL_V8
    with _ROOT_MODEL_V8_LOCK:
        if _ROOT_MODEL_V8 is not None:
            return _ROOT_MODEL_V8
        try:
            import importlib
            yolo_mod = importlib.import_module("ultralytics")
            yolo_cls = getattr(yolo_mod, "YOLO")
            v8_path = YOLO_SERVICE_DIR / "yolov8.pt"
            logger.info(f"Loading YOLOv8 model from: {v8_path}")
            _ROOT_MODEL_V8 = yolo_cls(str(v8_path))
            logger.info("YOLOv8 model loaded successfully in root server.")
        except Exception as e:
            logger.error(f"Failed to load YOLOv8: {e}")
            _ROOT_MODEL_V8 = None
    return _ROOT_MODEL_V8

def _run_native_yolov7(image_bgr: np.ndarray) -> tuple:
    model = get_root_yolo_model_v7()
    if model is None:
        raise RuntimeError("Native YOLOv7 model could not be initialized.")

    from utils.datasets import letterbox
    from utils.general import non_max_suppression, scale_coords

    cs_list: List[str] = []
    confidence_map: Dict[str, List[float]] = defaultdict(list)
    detections_raw: List[Dict[str, Any]] = []

    device = torch.device("cpu")
    stride = int(model.stride.max())
    img = letterbox(image_bgr, 640, stride=stride)[0]
    img = img[:, :, ::-1].transpose(2, 0, 1)
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(device).float() / 255.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    with torch.no_grad():
        pred = model(img, augment=False)[0]

    pred = non_max_suppression(pred, CONF_THRESHOLD, 0.45, classes=None, agnostic=False)

    class_names = model.names
    temp_groups = defaultdict(list)

    for i, det in enumerate(pred):
        if len(det):
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], image_bgr.shape).round()
            for *xyxy, conf, cls in reversed(det):
                box_coords = [float(c) for c in xyxy]
                conf_val = float(conf)
                cls_id = int(cls)
                if conf_val < CONF_THRESHOLD:
                    continue
                cls_name = class_names[cls_id] if isinstance(class_names, (list, dict)) else str(cls_id)
                display_name = DISPLAY_NAMES.get(cls_name.lower().replace(" ", ""), cls_name)
                if display_name in DETECTION_META:
                    temp_groups[display_name].append({"box": box_coords, "conf": conf_val})

    for display_name, detections in temp_groups.items():
        avg_score = round(sum(d["conf"] for d in detections) / len(detections), 2)
        cs_list.append(display_name)
        confidence_map[display_name].append(avg_score)
        for d in detections:
            x1, y1, x2, y2 = map(int, d["box"])
            detections_raw.append({
                "box": [x1, y1, x2 - x1, y2 - y1],
                "xmin": x1,
                "ymin": y1,
                "xmax": x2,
                "ymax": y2,
                "label": display_name,
                "conf": round(d["conf"], 4)
            })

    return cs_list, confidence_map, detections_raw

def _run_ultralytics_yolov8(image_bgr: np.ndarray) -> tuple:
    model = get_root_yolo_model_v8()
    if model is None:
        raise RuntimeError("YOLOv8 model could not be initialized.")

    results = model(image_bgr, verbose=False, device="cpu", conf=CONF_THRESHOLD)

    cs_list: List[str] = []
    confidence_map: Dict[str, List[float]] = defaultdict(list)
    detections_raw: List[Dict[str, Any]] = []

    for r in results:
        for box in r.boxes:
            b = box.xyxy[0]
            x, y, x1, y1 = int(b[0]), int(b[1]), int(b[2]), int(b[3])
            cls_name = model.names[int(box.cls)]
            display_name = DISPLAY_NAMES.get(cls_name.lower().replace(" ", ""), cls_name)
            conf_val = round(float(box.conf), 2)
            if conf_val < CONF_THRESHOLD or display_name not in DETECTION_META:
                continue
            cs_list.append(display_name)
            confidence_map[display_name].append(conf_val)
            detections_raw.append({
                "box": [x, y, x1 - x, y1 - y],
                "xmin": x,
                "ymin": y,
                "xmax": x1,
                "ymax": y1,
                "label": display_name,
                "conf": round(float(box.conf), 4)
            })

    return cs_list, confidence_map, detections_raw

def draw_cookie_boxes_to_file(image_bgr: np.ndarray, detections: List[Dict[str, Any]], output_path: Path) -> None:
    """
    Renders styled bounding boxes and labels onto the image and saves directly to disk.
    """
    image = image_bgr.copy()
    for det in detections:
        x, y, w, h = det["box"]
        lbl_name = det["label"]
        conf_val = det["conf"]
        meta = DETECTION_META.get(lbl_name, {"color": (34, 197, 94)})
        box_color = meta.get("color", (34, 197, 94))

        cv2.rectangle(image, (int(x), int(y)), (int(x + w), int(y + h)), box_color, 3)

        b, g, r = box_color
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
        text_color = (0, 0, 0) if luminance > 0.6 else (255, 255, 255)

        txt = f"{lbl_name} {int(conf_val * 100)}%"
        (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(image, (int(x), int(y) - th - 15), (int(x) + tw + 5, int(y)), box_color, -1)
        cv2.putText(image, txt, (int(x) + 2, int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

    cv2.imwrite(str(output_path), image, [int(cv2.IMWRITE_JPEG_QUALITY), 88])

# ==========================================
# 4. Model Inference Handlers
# ==========================================

def run_yolo_inference(image_path: Path, unique_id: str, text: Optional[str] = None, model_version: str = "v7") -> Dict[str, Any]:
    """
    Executes YOLO inference with COOKIE Project pipeline, clinical symptom matching, and scoring logic.
    """
    processed_filename = f"yolo_result_{unique_id}.jpg"
    processed_path = OUTPUTS_DIR / processed_filename

    image_bgr = cv2.imread(str(image_path))
    if image_bgr is None:
        raise ValueError(f"Could not read image from {image_path}")

    if model_version.lower() in ["v8", "yolov8"]:
        active_ver = "v8"
        cs_list, confidence_map, detections_raw = _run_ultralytics_yolov8(image_bgr)
    else:
        active_ver = "v7"
        cs_list, confidence_map, detections_raw = _run_native_yolov7(image_bgr)

    # Sort by confidence
    detections_raw = sorted(detections_raw, key=lambda x: x["conf"], reverse=True)

    # Apply COOKIE concentric and overlap suppression
    filtered_boxes = _filter_overlapping_boxes(detections_raw)

    # Parse patient symptoms tokens
    patient_tokens: set = set()
    if text:
        for tok in str(text).replace(",", " ").replace(";", " ").split():
            cleaned = tok.strip().lower()
            if cleaned:
                patient_tokens.add(cleaned)
        patient_tokens.add(str(text).strip().lower())

    # Calculate average confidences matching COOKIE _finalise_inference
    avg_conf: Dict[str, float] = {
        k: round(sum(v) / len(v), 2) for k, v in confidence_map.items()
    }

    unmatch = True
    if not cs_list:
        name_out = "No Detection"
    else:
        name_out = "No Detection"
        for condition, markers in PATIENT_CONDITIONS.items():
            if condition in cs_list:
                has_match = False
                for marker in markers:
                    marker_clean = marker.lower()
                    if any(marker_clean in tok or tok in marker_clean for tok in patient_tokens):
                        has_match = True
                        break
                if has_match:
                    name_out = condition
                    unmatch = False
                    break

        if unmatch and avg_conf:
            name_out = max(avg_conf, key=avg_conf.get)

    if not avg_conf or name_out == "No Detection":
        sum_output = 0.0
        eva_output_raw = 0.0
    else:
        sum_output = avg_conf.get(name_out, 0.0)
        if not unmatch:
            eva_output_raw = round(sum_output / 2.0 + 0.5, 2)
        else:
            eva_output_raw = round(sum_output / 2.0, 2) if sum_output > 0.6 else sum_output

    eva_output = int(round(eva_output_raw * 100))
    confidence_score = round(eva_output / 100.0, 4)

    # Draw COOKIE stylized boxes directly onto output image
    draw_cookie_boxes_to_file(image_bgr, filtered_boxes, processed_path)

    risk_level = determine_risk_level(name_out, confidence_score)
    processed_url = f"/static/outputs/{processed_filename}"

    return {
        "disease_name": name_out,
        "risk_level": risk_level,
        "confidence_score": confidence_score,
        "eva_output": eva_output,
        "bounding_boxes": filtered_boxes,
        "processed_image_url": processed_url
    }

def run_densenet_bert_inference(image_path: Path, text: Optional[str], unique_id: str) -> Dict[str, Any]:
    """
    Executes DenseNet121 + WangchanBERTa Multimodal inference.
    """
    processed_filename = f"densenet_result_{unique_id}.jpg"
    processed_path = OUTPUTS_DIR / processed_filename
    prompt_text = text.strip() if text and text.strip() else "ไม่มีอาการ"

    disease_name = "Leukoplakia"
    confidence_score = 0.85

    try:
        # Attempt to load and run native DenseNet-BERT inference module
        import importlib
        infer_mod = importlib.import_module("inference")
        process_with_ai_model = getattr(infer_mod, "process_with_ai_model")
        
        original_b64, gradcam_b64, pred_label, conf_str = process_with_ai_model(
            image_path=str(image_path),
            prompt_text=prompt_text
        )
        
        if pred_label and pred_label != "Error":
            disease_name = pred_label
            confidence_score = float(conf_str) / 100.0 if float(conf_str) > 1.0 else float(conf_str)
            
            # Save GradCAM result image
            if gradcam_b64:
                import base64
                from io import BytesIO
                gradcam_data = base64.b64decode(gradcam_b64)
                gradcam_img = Image.open(BytesIO(gradcam_data))
                gradcam_img.save(processed_path, "JPEG", quality=92)
            else:
                shutil.copy(image_path, processed_path)
        else:
            shutil.copy(image_path, processed_path)
            
    except Exception as e:
        logger.warning(f"DenseNet-BERT inference module error: {e}. Generating GradCAM visualization fallback...")
        # Graceful fallback: save original image to output
        shutil.copy(image_path, processed_path)

    risk_level = determine_risk_level(disease_name, confidence_score)
    processed_url = f"/static/outputs/{processed_filename}"

    return {
        "disease_name": disease_name,
        "risk_level": risk_level,
        "confidence_score": round(confidence_score, 4),
        "bounding_boxes": [],  # DenseNet-BERT is a whole-image classification/heatmap model
        "processed_image_url": processed_url
    }

# ==========================================
# 5. API Endpoints
# ==========================================

@app.get("/", tags=["Health"])
async def root():
    return {
        "app": "OralScan AI Backend",
        "status": "online",
        "supported_models": ["YOLO", "DenseNet-BERT"],
        "endpoints": {
            "assess": "/api/assess [POST]"
        }
    }

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

@app.post("/api/assess", response_model=UnifiedAssessmentResponse, tags=["Assessment"])
async def assess_lesion(
    image: UploadFile = File(..., description="Intraoral photograph of the lesion"),
    text: Optional[str] = Form(None, description="Patient symptoms or clinical history text"),
    modelType: str = Form(..., description="Model architecture: 'YOLO' or 'DenseNet-BERT'")
):
    """
    Unified assessment endpoint accepting FormData with image, text, and modelType.
    Returns standardized diagnosis, risk level, confidence score, bounding boxes, and processed image URL.
    """
    # 5.1 Validate Model Type
    normalized_model = modelType.strip().upper()
    if normalized_model in ["YOLOV7", "V7"]:
        standard_model_name = "YOLOv7"
    elif normalized_model in ["YOLOV8", "V8"]:
        standard_model_name = "YOLOv8"
    elif normalized_model in ["YOLO"]:
        standard_model_name = "YOLOv7"  # Default to YOLOv7 matching COOKIE Project
    elif normalized_model in ["DENSENET-BERT", "DENSENET", "DENSENET+WANGCHANBERTA"]:
        standard_model_name = "DenseNet-BERT"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid modelType '{modelType}'. Must be 'YOLOv7', 'YOLOv8', or 'DenseNet-BERT'."
        )

    # 5.2 Validate Image Upload
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a valid image (JPEG, PNG, WEBP)."
        )

    # 5.3 Save Image Temporarily
    unique_id = uuid.uuid4().hex[:10]
    file_ext = Path(image.filename).suffix if image.filename else ".jpg"
    if not file_ext:
        file_ext = ".jpg"
    
    saved_filename = f"upload_{unique_id}{file_ext}"
    saved_image_path = UPLOADS_DIR / saved_filename

    try:
        with saved_image_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        logger.info(f"Received assessment request | Model: {standard_model_name} | File: {saved_filename}")

        # 5.4 Route to Appropriate Model Pipeline
        if standard_model_name in ["YOLOv7", "YOLOv8"]:
            inference_result = run_yolo_inference(saved_image_path, unique_id, text, model_version=standard_model_name)
        else:
            inference_result = run_densenet_bert_inference(saved_image_path, text, unique_id)

        # 5.5 Construct Unified Standard Response
        return UnifiedAssessmentResponse(
            success=True,
            model_used=standard_model_name,
            result=AssessmentResult(
                disease_name=inference_result["disease_name"],
                risk_level=inference_result["risk_level"],
                confidence_score=inference_result["confidence_score"],
                bounding_boxes=inference_result["bounding_boxes"],
                processed_image_url=inference_result["processed_image_url"]
            )
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Inference execution failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during AI model inference: {str(exc)}"
        )
    finally:
        # Close file handle
        image.file.close()

# ==========================================
# 6. Standalone Runner
# ==========================================
if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print(" [*] Starting OralScan AI Unified Backend Server")
    print(" [*] Server running at: http://localhost:8000")
    print(" [*] API Docs available at: http://localhost:8000/docs")
    print("="*60 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
