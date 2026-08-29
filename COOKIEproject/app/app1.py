"""
app1.py – Oral Lesion Detection Web App + LINE Bot
Improvements:
  - YOLOv7 + YOLOv8 model singletons loaded once at startup
  - Redis + RQ for true background inference queue (falls back to thread queue)
  - Gunicorn + gevent worker support (set in start.sh)
  - CPU thread limits for 1-2 vCPU / 2 GB RAM environments
  - Replaced Pyrebase4 with direct Firebase REST API
  - Proper logging, file validation, structured error handling
"""

import gc
import hashlib
import json
import logging
import os
import sys
import queue
import tempfile
import threading
import time
import uuid
from collections import defaultdict
from functools import wraps
from io import BytesIO

import cv2
import firebase_admin
import numpy as np
import requests
from dotenv import load_dotenv
from flask import (
    Flask, abort, flash, jsonify, redirect,
    render_template, request, send_from_directory,
    session, url_for,
)
from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient as LineApiClient,
    Configuration as LineConfiguration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage as LineTextMessage,
    ImageMessage as LineImageMessage,
    TemplateMessage,
    ButtonsTemplate,
    PostbackAction,
)
from linebot.v3.webhooks import (
    MessageEvent,
    PostbackEvent,
    ImageMessageContent,
    TextMessageContent,
)
import torch
from PIL import Image
from ultralytics import YOLO
from firebase_admin import auth as firebase_auth
from werkzeug.middleware.proxy_fix import ProxyFix

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Low-RAM / low-vCPU tuning  (must happen before any torch/cv2 work)
# Limits CPU thread pools so a single inference job doesn't peg all cores.
# ---------------------------------------------------------------------------
try:
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
except Exception:
    pass
try:
    import cv2 as _cv2_early
    _cv2_early.setNumThreads(1)
except Exception:
    pass

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Firebase Admin (server-side verification)
# ---------------------------------------------------------------------------
try:
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    logger.info("Firebase Admin initialized.")
except Exception as _fb_err:
    logger.warning("Firebase Admin not initialized (no credentials): %s", _fb_err)


# ---------------------------------------------------------------------------
# Firebase Auth REST API (replaces Pyrebase4)
# ---------------------------------------------------------------------------
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
FIREBASE_AUTH_BASE = "https://identitytoolkit.googleapis.com/v1/accounts"


def firebase_sign_in(email: str, password: str) -> dict:
    """Sign in with email/password via Firebase REST API."""
    url = f"{FIREBASE_AUTH_BASE}:signInWithPassword?key={FIREBASE_API_KEY}"
    resp = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def firebase_get_account_info(id_token: str) -> dict:
    """Fetch account info (includes emailVerified) via Firebase REST API."""
    url = f"{FIREBASE_AUTH_BASE}:lookup?key={FIREBASE_API_KEY}"
    resp = requests.post(url, json={"idToken": id_token}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def firebase_create_user(email: str, password: str) -> dict:
    """Create a new user via Firebase REST API."""
    url = f"{FIREBASE_AUTH_BASE}:signUp?key={FIREBASE_API_KEY}"
    resp = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def firebase_send_verification(id_token: str) -> None:
    """Send email verification via Firebase REST API."""
    url = f"{FIREBASE_AUTH_BASE}:sendOobCode?key={FIREBASE_API_KEY}"
    requests.post(url, json={"requestType": "VERIFY_EMAIL", "idToken": id_token}, timeout=10)


def firebase_send_password_reset(email: str) -> None:
    """Send password reset email via Firebase REST API."""
    url = f"{FIREBASE_AUTH_BASE}:sendOobCode?key={FIREBASE_API_KEY}"
    requests.post(url, json={"requestType": "PASSWORD_RESET", "email": email}, timeout=10)


# ---------------------------------------------------------------------------
# Flask App Setup
# ---------------------------------------------------------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, 
            static_folder=os.path.join(base_dir, 'static'),
            template_folder=os.path.join(base_dir, 'templates'))
            
app.secret_key = os.getenv("SECRET_KEY", "change_me_in_production")
# Tell Flask it is behind a proxy (Railway) so it knows it is using HTTPS
# This fixes issues where `url_for` generates `http://` links for CSS/JS
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# ---------------------------------------------------------------------------
# LINE Bot v3
# ---------------------------------------------------------------------------
_line_config = LineConfiguration(access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN", ""))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET", ""))

def _line_api() -> MessagingApi:
    """Return a MessagingApi client (context-managed per call)."""
    return MessagingApi(LineApiClient(_line_config))

# ---------------------------------------------------------------------------
# Google OAuth config
# ---------------------------------------------------------------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")
GOOGLE_AUTHORIZATION_URL = os.getenv("GOOGLE_AUTHORIZATION_URL", "https://accounts.google.com/o/oauth2/auth")
SCOPES = os.getenv("GOOGLE_SCOPES", "openid email profile")

# ---------------------------------------------------------------------------
# Directory setup
# ---------------------------------------------------------------------------
for _d in ["uploads", "static/output", "static/images", "results"]:
    os.makedirs(_d, exist_ok=True)

# ---------------------------------------------------------------------------
# YOLO model singletons — loaded ONCE at startup, shared across all requests
# ---------------------------------------------------------------------------
logger.info("Loading YOLO models …")
_MODEL_V8: YOLO | None = None
_MODEL_V7 = None          # torch model loaded via torch.hub
_MODEL_V7_LOCK = threading.Lock()


def _resolve_model_path(filename: str, download_env_var: str) -> str:
    """Return local path to model file, downloading if necessary."""
    for candidate in [os.path.join("static", "model", filename), filename]:
        if os.path.exists(candidate):
            logger.info("Using local model file: %s", os.path.abspath(candidate))
            return candidate
    download_url = os.getenv(download_env_var)
    if download_url:
        logger.info("Downloading %s from %s …", filename, download_env_var)
        import urllib.request
        urllib.request.urlretrieve(download_url, filename)
        logger.info("Downloaded %s.", filename)
        return filename
    raise RuntimeError(
        f"Model file '{filename}' not found and {download_env_var} is not set. "
        "Set this env var to a direct download URL."
    )


def get_model_v8() -> YOLO:
    global _MODEL_V8
    if _MODEL_V8 is not None:
        return _MODEL_V8
        
    # Optimization: if this is the web process and a worker is already handle tasks,
    # skip loading the heavy model in the web RAM.
    if not os.getenv("IS_WORKER") and _has_active_workers():
        logger.info("Skipping YOLOv8 load in web process (worker detected).")
        return None

    model_filename = os.getenv("YOLO_V8_MODEL_FILE", "yolov8.pt")
    model_path = _resolve_model_path(model_filename, "MODEL_DOWNLOAD_URL")
    gc.collect()  # clear RAM before loading big model
    _MODEL_V8 = YOLO(model_path)
    logger.info("YOLOv8 model loaded from %s.", model_path)
    return _MODEL_V8


# YOLOv7 repository folders (models/ and utils/) are located in the project root.
# Imports like 'from models.experimental import attempt_load' will work natively.

def get_model_v7():
    """Load YOLOv7 from yolov7.pt using WongKinYiu/yolov7 repo directly."""
    global _MODEL_V7
    if _MODEL_V7 is not None:
        return _MODEL_V7
        
    with _MODEL_V7_LOCK:
        if _MODEL_V7 is not None:
            return _MODEL_V7
            
        # Optimization: skip loading in web process if workers exist
        if not os.getenv("IS_WORKER") and _has_active_workers():
            logger.info("Skipping YOLOv7 load in web process (worker detected).")
            return None

        try:
            model_filename = os.getenv("YOLO_V7_MODEL_FILE", "yolov7.pt")
            model_path = _resolve_model_path(model_filename, "MODEL_V7_DOWNLOAD_URL")
            logger.info("Loading YOLOv7 from %s ...", model_path)
            
            gc.collect()
            from models.experimental import attempt_load
            device = torch.device("cpu")
            model = attempt_load(model_path, map_location=device)
            model.eval()

            _MODEL_V7 = model
            logger.info("YOLOv7 model loaded successfully via native YOLOv7 code.")
        except Exception as exc:
            logger.warning(
                "YOLOv7 load failed (%s). Falling back to YOLOv8 for v7 requests.", exc
            )
            _MODEL_V7 = "fallback_v8"
    return _MODEL_V7


# ---------------------------------------------------------------------------
# Inference constants
# ---------------------------------------------------------------------------
CONF_THRESHOLD = 0.25
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

DETECTION_META = {
    "Leukoplakia":        {"color": (0, 255, 0)},
    "Lichen planus":      {"color": (0, 0, 255)},
    "Candidiasis":        {"color": (255, 255, 255)},
    "Linea alba buccalis":{"color": (128, 128, 128)},
    "Ulcer":              {"color": (255, 140, 0)},
}

DISPLAY_NAMES = {
    "leukoplakia":  "Leukoplakia",
    "lichenplanus": "Lichen planus",
    "candidiasis":  "Candidiasis",
    "otherwhite":   "Linea alba buccalis",
    "other white":  "Linea alba buccalis",
    "ulcer":        "Ulcer",
}

PATIENT_CONDITIONS = {
    "Leukoplakia":         ["drinkAlcohol", "smoking", "chewBetelNut"],
    "Lichen planus":       ["eatSpicyFood"],
    "Candidiasis":         ["wipeOff"],
    "Linea alba buccalis": ["noSymptoms"],
    "Ulcer":               ["alwaysHurts"],
}

# ---------------------------------------------------------------------------
# Inference queue  — Redis/RQ if available, else in-process thread queue
#
# Why queue at all?
#   YOLO inference is CPU-bound and takes ~1-5 s on a 1-vCPU container.
#   Without a queue, 5 concurrent uploads hammer the CPU at 100 % and the
#   process can OOM or get killed by Railway's memory limit.
#   A single worker processes one image at a time; others wait in the queue.
# ---------------------------------------------------------------------------
_INFERENCE_TIMEOUT = 120   # seconds to wait for a result
_MAX_QUEUE_DEPTH  = 2      # reject uploads when queue is already this long

# ---- Try to connect to Redis -----------------------------------------------
_rq_queue = None
_redis_conn = None
try:
    import redis as _redis_lib
    from rq import Queue as _RQ_Queue
    _redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    _redis_conn = _redis_lib.from_url(_redis_url, socket_connect_timeout=3)
    _redis_conn.ping()          # raises if Redis is unreachable
    _rq_queue = _RQ_Queue("inference-tasks", connection=_redis_conn)
    logger.info("Redis queue backend connected at %s", _redis_url)
except Exception as _rq_err:
    logger.info("Redis unavailable (%s). Using in-process thread queue.", _rq_err)
    _rq_queue = None
    _redis_conn = None

# ---- In-process fallback queue (used when Redis is not available) -----------
_inference_queue: queue.Queue = queue.Queue()


class _InferenceTask:
    """Container for the in-process thread queue."""
    def __init__(self, model_version: str, image: np.ndarray, patient_info: list, user_email: str | None):
        self.model_version = model_version
        self.image = image
        self.patient_info = patient_info
        self.user_email = user_email
        self.result: tuple | None = None
        self.error: Exception | None = None
        self.done = threading.Event()


def _inference_worker() -> None:
    """Background daemon thread — only runs when Redis is NOT available."""
    logger.info("In-process inference worker thread started.")
    while True:
        task: _InferenceTask = _inference_queue.get()
        try:
            task.result = _run_inference(
                task.image, task.patient_info, task.user_email, task.model_version
            )
        except Exception as exc:
            logger.exception("Inference worker error: %s", exc)
            task.error = exc
        finally:
            task.done.set()
            _inference_queue.task_done()


_worker_thread = threading.Thread(
    target=_inference_worker, daemon=True, name="inference-worker"
)
_worker_thread.start()


def _has_active_workers() -> bool:
    if _rq_queue is None:
        return False
    try:
        from rq.worker import Worker as _RQ_Worker
        return len(_RQ_Worker.all(connection=_rq_queue.connection)) > 0
    except Exception:
        return False


def _queue_depth() -> int:
    """Return current pending job count across whichever backend is active."""
    if _has_active_workers():
        try:
            return len(_rq_queue)
        except Exception:
            return 0
    return _inference_queue.qsize()


def submit_inference(
    image: np.ndarray,
    patient_info: list,
    user_email: str | None,
    model_version: str = "v8",
) -> tuple:
    """Submit an inference job and block until done (or timeout).

    Raises RuntimeError if queue is too deep (prevents OOM on small VMs).
    """
    depth = _queue_depth()
    if depth >= _MAX_QUEUE_DEPTH:
        raise RuntimeError(
            f"Server queue full ({depth}/{_MAX_QUEUE_DEPTH}). "
            "Please try again in a moment."
        )

    if _has_active_workers():
        # ---- Redis/RQ path ------------------------------------------------
        # Save image to a temp file so the RQ worker (separate process) can
        # read it without passing numpy arrays over the wire.
        tmp = tempfile.NamedTemporaryFile(
            suffix=".jpg", delete=False, dir="uploads"
        )
        cv2.imwrite(tmp.name, image)
        tmp.close()
        try:
            job = _rq_queue.enqueue(
                _run_inference_from_path,
                tmp.name,
                patient_info,
                user_email,
                model_version,
                job_timeout=_INFERENCE_TIMEOUT,
            )
            deadline = time.monotonic() + _INFERENCE_TIMEOUT
            while time.monotonic() < deadline:
                job.refresh()
                if job.is_finished:
                    res = job.result
                    if isinstance(res, tuple) and len(res) == 4:
                        return res + ([],)
                    return res
                if job.is_failed:
                    raise RuntimeError(f"RQ job failed: {job.exc_info}")
                time.sleep(0.4)
            raise TimeoutError("Inference timed out (RQ). Server may be under load.")
        finally:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
    else:
        # ---- In-process thread queue path ----------------------------------
        task = _InferenceTask(model_version, image, patient_info, user_email)
        _inference_queue.put(task)
        finished = task.done.wait(timeout=_INFERENCE_TIMEOUT)
        if not finished:
            raise TimeoutError("Inference timed out. The server may be under heavy load.")
        if task.error:
            raise task.error
        
        # Ensure we always return a 5-tuple: (image_output, label, name_out, eva_output, detections_raw)
        res = task.result
        if isinstance(res, tuple) and len(res) == 4:
            # Fallback for old 4-tuple tasks just in case
            return res + ([],)
        return res


# ---------------------------------------------------------------------------
# Core inference functions & Post-Processing
# ---------------------------------------------------------------------------

def _box_iou_or_contained(box1: list[int], box2: list[int]) -> float:
    """Calculate IoU or heavy containment between two [x, y, w, h] boxes."""
    x1_1, y1_1, w1, h1 = box1
    x2_1, y2_1 = x1_1 + w1, y1_1 + h1
    
    x1_2, y1_2, w2, h2 = box2
    x2_2, y2_2 = x1_2 + w2, y1_2 + h2
    
    # Intersections
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
    
    # If one box is heavily contained inside the other (>70% of the smaller box's area is inside)
    # This specifically catches the "concentric" boxes YOLOv7 outputs
    min_area = min(area1, area2)
    contained_ratio = intersection / float(min_area) if min_area > 0 else 0.0
    
    return max(iou, contained_ratio)
    
def _filter_overlapping_boxes(detections: list[dict]) -> list[dict]:
    """Aggressively suppress overlapping or concentric boxes of the same class."""
    if not detections:
        return []
        
    filtered = []
    # Sort detections by confidence, highest first
    sorted_dets = sorted(detections, key=lambda x: x["conf"], reverse=True)
    
    for current_det in sorted_dets:
        keep = True
        for kept_det in filtered:
            # If same class label and heavily overlapping/concentric
            if current_det["label"] == kept_det["label"]:
                overlap = _box_iou_or_contained(current_det["box"], kept_det["box"])
                if overlap > 0.40: # Aggressive union/containment threshold
                    keep = False
                    break
        if keep:
            filtered.append(current_det)
            
    return filtered

def _run_inference_v8(
    image: np.ndarray,
    patient_info: list,
    user_email: str | None,
) -> tuple:
    """YOLOv8 (Ultralytics) inference path."""
    model = get_model_v8()
    result = model(image, verbose=False, device="cpu", conf=CONF_THRESHOLD)

    cs_list: list[str] = []
    confidence_map: dict[str, list[float]] = defaultdict(list)
    detections_raw: list[dict] = []

    for r in result:
        for box in r.boxes:
            b = box.xyxy[0]
            x, y, x1, y1 = int(b[0]), int(b[1]), int(b[2]), int(b[3])
            cls_name = model.names[int(box.cls)]
            display_name = DISPLAY_NAMES.get(cls_name.lower().replace(" ", ""), cls_name)
            conf = round(float(box.conf), 2)
            if conf < CONF_THRESHOLD or display_name not in DETECTION_META:
                continue
            # Server-side drawing removed for cleaner interactive overlays
            cs_list.append(display_name)
            confidence_map[display_name].append(conf)
            detections_raw.append({
                "box": [x, y, x1 - x, y1 - y],
                "label": display_name,
                "conf": conf
            })

    del result
    gc.collect()

    return cs_list, confidence_map, detections_raw

def _run_inference_v7(
    image: np.ndarray,
    patient_info: list,
    user_email: str | None,
) -> tuple:
    """YOLOv7 inference path using original codebase.

    Returns same (cs_list, confidence_map) tuple as v8 path.
    Falls back transparently to v8 if the v7 model wasn't loaded.
    """
    model = get_model_v7()
    if model == "fallback_v8":
        logger.warning("YOLOv7 unavailable — using YOLOv8 fallback.")
        return _run_inference_v8(image, patient_info, user_email)

    from utils.datasets import letterbox
    from utils.general import non_max_suppression, scale_coords

    cs_list: list[str] = []
    confidence_map: dict[str, list[float]] = defaultdict(list)
    detections_raw: list[dict] = []

    # Preprocess exactly as WongKinYiu detect.py does
    device = torch.device("cpu")
    stride = int(model.stride.max())
    img = letterbox(image, 640, stride=stride)[0]
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(device).float()
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # Run prediction
    with torch.no_grad():
        model.eval() # Ensure eval mode
        pred = model(img, augment=False)[0]

    # NMS
    pred = non_max_suppression(pred, CONF_THRESHOLD, 0.45, classes=None, agnostic=False)


    # Free large tensors early if possible
    
    class_names = model.names 

    # Temporary storage to group by class for averaging
    temp_groups = defaultdict(list)
    
    for i, det in enumerate(pred):
        if len(det):
            # Rescale boxes from img_size to original image size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], image.shape).round()
            
            for *xyxy, conf, cls in reversed(det):
                box_coords = [float(c) for c in xyxy]
                conf = float(conf)
                cls_id = int(cls)
                
                if conf < CONF_THRESHOLD:
                    continue
                cls_name = class_names[cls_id]
                display_name = DISPLAY_NAMES.get(cls_name.lower().replace(" ", ""), cls_name)
                if display_name in DETECTION_META:
                    temp_groups[display_name].append({"box": box_coords, "conf": conf})

    # Finalize detections with averaged confidence
    for display_name, detections in temp_groups.items():
        avg_score = round(sum(d["conf"] for d in detections) / len(detections), 2)
        cs_list.append(display_name)
        confidence_map[display_name].append(avg_score)
        
        for d in detections:
            x1, y1, x2, y2 = map(int, d["box"])
            detections_raw.append({
                "box": [x1, y1, x2 - x1, y2 - y1],
                "label": display_name,
                "conf": d["conf"]  # Reverted to individual raw confidence as requested
            })

    # Cleanup large tensors
    del img
    del pred
    gc.collect()

    return cs_list, confidence_map, detections_raw

def _finalise_inference(
    image: np.ndarray,
    cs_list: list,
    confidence_map: dict,
    patient_info: list,
    user_email: str | None,
    model_version: str,
    detections_raw: list[dict],
) -> tuple:
    """Common post-processing: compute winning class, confidence, save image."""
    avg_conf: dict[str, float] = {
        k: round(sum(v) / len(v), 2) for k, v in confidence_map.items()
    }
    logger.debug("class_output: %s", avg_conf)

    unmatch = True
    if not cs_list:
        name_out = "No Detection"
    else:
        name_out = "No Detection"
        for condition, markers in PATIENT_CONDITIONS.items():
            if condition in cs_list and any(m in patient_info for m in markers):
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
        eva_output_raw = (
            round(sum_output / 2 + 0.5, 2)
            if not unmatch
            else (round(sum_output / 2, 2) if sum_output > 0.6 else sum_output)
        )

    eva_output = int(round(eva_output_raw * 100))
    logger.info("Inference[%s]: name=%s confidence=%s%%", model_version, name_out, eva_output)

    label = f"{name_out} {eva_output}" if sum_output != 0 else "No Detection"

    # --- Draw boxes on image for static sharing (LINE/Download) ---
    for det in detections_raw:
        x, y, w, h = det["box"]
        lbl_name = det["label"]
        conf_val = det["conf"]
        
        meta = DETECTION_META.get(lbl_name, {"color": (34, 197, 94)}) # Fallback to green
        box_color = meta.get("color", (34, 197, 94))
        
        # Draw Box
        cv2.rectangle(image, (int(x), int(y)), (int(x + w), int(y + h)), box_color, 3)
        
        # Decide text color based on background brightness (perceived luminosity)
        # (b, g, r) -> 0.299*R + 0.587*G + 0.114*B
        b, g, r = box_color
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
        text_color = (0, 0, 0) if luminance > 0.6 else (255, 255, 255)
        
        # Draw Label Banner
        txt = f"{lbl_name} {int(conf_val*100)}%"
        (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(image, (int(x), int(y) - th - 15), (int(x) + tw + 5, int(y)), box_color, -1)
        cv2.putText(image, txt, (int(x) + 2, int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

    # --- Save processed image (with optimization for loading speed) ---
    save_params = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
    if user_email:
        email_hash = hashlib.md5(user_email.encode()).hexdigest()[:10]
        user_dir = os.path.join("static", "output", email_hash)
        os.makedirs(user_dir, exist_ok=True)
        # Use a unique filename to avoid caching issues
        image_path = os.path.join(user_dir, f"proc_{int(time.time() * 1000 % 10000)}.jpg")
        cv2.imwrite(image_path, image, save_params)
        image_output = "/" + os.path.relpath(image_path).replace("\\", "/")

        results_dir = os.path.join("results", email_hash)
        os.makedirs(results_dir, exist_ok=True)
        count = 1
        while os.path.exists(os.path.join(results_dir, f"{count}.jpg")):
            count += 1
        cv2.imwrite(os.path.join(results_dir, f"{count}.jpg"), image, save_params)
    else:
        ts = int(time.time())
        image_path = f"static/output/{ts}.jpg"
        cv2.imwrite(image_path, image, save_params)
        image_output = "/" + image_path

    return image_output, label, name_out, eva_output, detections_raw


def _run_inference(
    image: np.ndarray,
    patient_info: list,
    user_email: str | None,
    model_version: str = "v8",
) -> tuple:
    """Route to correct YOLO version and return unified result tuple."""
    if model_version == "v7":
        cs_list, confidence_map, detections_raw = _run_inference_v7(image, patient_info, user_email)
    else:
        cs_list, confidence_map, detections_raw = _run_inference_v8(image, patient_info, user_email)
        
    # Sort by confidence
    detections_raw = sorted(detections_raw, key=lambda x: x["conf"], reverse=True)
    
    # Apply overlap filter
    detections_raw = _filter_overlapping_boxes(detections_raw)
    
    result = _finalise_inference(image, cs_list, confidence_map, patient_info, user_email, model_version, detections_raw)
    
    # Explicitly clear memory for low-RAM environments
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()
    
    return result


def _run_inference_from_path(
    image_path: str,
    patient_info: list,
    user_email: str | None,
    model_version: str = "v8",
) -> tuple:
    """RQ worker entry point: loads image from disk, runs inference."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image at {image_path}")
    return _run_inference(img, patient_info, user_email, model_version)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def _validate_upload(file) -> str | None:
    """Return an error string if the file is invalid, else None."""
    if not file or file.filename == "":
        return "No file selected."
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return f"File type '{ext}' is not allowed. Please upload a JPG, PNG, BMP, or WEBP image."
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_UPLOAD_BYTES:
        return f"File is too large ({size // (1024*1024)} MB). Maximum allowed size is 10 MB."
    return None


def _get_user_image_path(email: str) -> str:
    email_hash = hashlib.md5(email.encode()).hexdigest()[:10]
    user_dir = os.path.join("static", "output", email_hash)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, "processed23.jpg")


def _save_line_image(user_id: str, message_id: str, content: bytes) -> str:
    image_path = f"static/images/{user_id}_{message_id}.jpg"
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    with open(image_path, "wb") as f:
        f.write(content)
    return image_path


def _safe_upload(file) -> str:
    filename = file.filename
    dest = os.path.join("uploads", filename)
    file.save(dest)
    return dest


# ---------------------------------------------------------------------------
# Flask hooks
# ---------------------------------------------------------------------------
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# LINE Bot webhook
# ---------------------------------------------------------------------------
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    logger.info("LINE webhook received")
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature.", 400
    return "OK", 200


# ---------------------------------------------------------------------------
# LINE: user state manager
# ---------------------------------------------------------------------------
class UserStateManager:
    def __init__(self):
        self._states: dict = {}
        self._images: dict = {}
        self._started: set = set()
        self._lock = threading.Lock()

    def get_state(self, uid): 
        with self._lock: return self._states.get(uid)

    def set_state(self, uid, state):
        with self._lock: self._states[uid] = state

    def get_image(self, uid):
        with self._lock: return self._images.get(uid)

    def set_image(self, uid, path):
        with self._lock: self._images[uid] = path

    def start(self, uid):
        with self._lock: self._started.add(uid)

    def has_started(self, uid):
        with self._lock: return uid in self._started

    def clear(self, uid):
        with self._lock:
            self._states.pop(uid, None)
            self._images.pop(uid, None)
            self._started.discard(uid)


state_manager = UserStateManager()

SYMPTOMS = {
    "1": "drinkAlcohol",
    "2": "eatSpicyFood",
    "3": "wipeOff",
    "4": "alwaysHurts",
}

SYMPTOM_LABELS = {
    "drinkAlcohol": "Drink Alcohol",
    "eatSpicyFood":  "Eat Spicy Food",
    "wipeOff":       "Wipe Off",
    "alwaysHurts":   "Always Hurts",
}


def _line_send_result(event, user_id: str, patient_info: list):
    """Run inference for a LINE user and reply with the result."""
    user_image = state_manager.get_image(user_id)
    api = _line_api()
    if not user_image or not os.path.exists(user_image):
        api.reply_message(ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[LineTextMessage(type="text", text="No image found. Please upload an image first.")]
        ))
        return

    try:
        image = cv2.imread(user_image)
        if image is None:
            raise ValueError("Could not read image file.")

        # Always use v7 for LINE as requested for higher accuracy, fallback to v8 if needed
        try:
            image_output, label, name_out, eva_output, _dets = submit_inference(image, patient_info, None, model_version="v7")
        except Exception:
            logger.warning("YOLOv7 failed in LINE bot. Trying YOLOv8 fallback.")
            image_output, label, name_out, eva_output, _dets = submit_inference(image, patient_info, None, model_version="v8")

        # Get just the filename (e.g., '12345.jpg') because serve_line_image expects it
        filename_only = os.path.basename(image_output)

        # Construct image URL for LINE (must be public HTTPS and bypass web session)
        base_url = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
        if not base_url:
            base_url = f"https://{request.host}"
            
        # Use the /line/images/ public route instead of /static/output/
        full_image_url = f"{base_url}/line/images/{filename_only}"
        logger.info("LINE Image URL: %s", full_image_url)

        api.reply_message(ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                LineTextMessage(
                    type="text",
                    text=(
                        f"Detection Result\n"
                        f"------------------------\n"
                        f"Confidence: {eva_output}%\n"
                        f"Lesion Detected: {name_out}\n"
                        f"------------------------"
                    ),
                ),
                LineImageMessage(
                    type="image",
                    original_content_url=full_image_url,
                    preview_image_url=full_image_url,
                ),
            ],
        ))
        state_manager.clear(user_id)

    except TimeoutError:
        api.reply_message(ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[LineTextMessage(type="text", text="Server is busy. Please try again in a moment.")]
        ))
    except Exception as exc:
        logger.exception("LINE inference error for user %s: %s", user_id, exc)
        try:
            api.reply_message(ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[LineTextMessage(type="text", text=f"Error: {str(exc)}")]
            ))
        except Exception:
            pass


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    try:
        text = event.message.text.lower().strip()
        user_id = event.source.user_id
        api = _line_api()

        if text == "start":
            state_manager.start(user_id)
            api.reply_message(ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[LineTextMessage(type="text", text="You can start sending your image now.")]
            ))
        elif text in ("contactus", "howtouse"):
            pass  # handled by LINE rich menu
        else:
            api.reply_message(ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[LineTextMessage(type="text", text="Please type 'start' to begin using the service.")]
            ))
    except Exception as exc:
        logger.exception("handle_text_message error: %s", exc)


@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    try:
        user_id = event.source.user_id
        api = _line_api()

        if not state_manager.has_started(user_id):
            api.reply_message(ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[LineTextMessage(type="text", text="Please type 'start' first before sending an image.")]
            ))
            return

        # Download image content using requests + Bearer token
        img_resp = requests.get(
            f"https://api-data.line.me/v2/bot/message/{event.message.id}/content",
            headers={"Authorization": f"Bearer {os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')}"},
            timeout=15,
        )
        file_path = _save_line_image(user_id, event.message.id, img_resp.content)
        state_manager.set_image(user_id, file_path)

        template_msg = TemplateMessage(
            alt_text="Symptoms Choice",
            template=ButtonsTemplate(
                title="Symptoms Selection",
                text="Do you have any symptoms?",
                actions=[
                    PostbackAction(label="Yes, I have symptoms", display_text="I have symptoms", data="have_symptoms"),
                    PostbackAction(label="No symptoms",           display_text="No symptoms",    data="no_symptoms"),
                ],
            ),
        )
        api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[template_msg]))
    except Exception as exc:
        logger.exception("handle_image_message error: %s", exc)
        try:
            _line_api().reply_message(ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[LineTextMessage(type="text", text="Sorry, there was an error. Please try again.")]
            ))
        except Exception:
            pass


@handler.add(PostbackEvent)
def handle_postback(event):
    try:
        user_id = event.source.user_id
        api = _line_api()

        if not state_manager.has_started(user_id):
            api.reply_message(ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[LineTextMessage(type="text", text="Please type 'start' first.")]
            ))
            return

        data = event.postback.data

        if data == "have_symptoms":
            state_manager.set_state(user_id, {"state": "selecting_symptoms", "symptoms": set()})
            actions = [
                PostbackAction(label=SYMPTOM_LABELS[code][:20], display_text=SYMPTOM_LABELS[code], data=f"symptom_{code}")
                for code in list(SYMPTOMS.values())[:4]
            ]
            api.reply_message(ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TemplateMessage(
                    alt_text="Select Symptoms",
                    template=ButtonsTemplate(title="Select Symptoms", text="Please select your symptoms:", actions=actions),
                )]
            ))

        elif data == "no_symptoms":
            _line_send_result(event, user_id, ["noSymptoms"])

        elif data.startswith("symptom_"):
            symptom_code = data.replace("symptom_", "")
            user_state = state_manager.get_state(user_id) or {"state": "selecting_symptoms", "symptoms": set()}
            user_state["symptoms"].add(symptom_code)
            state_manager.set_state(user_id, user_state)

            if len(user_state["symptoms"]) >= len(SYMPTOMS):
                _line_send_result(event, user_id, list(user_state["symptoms"]))
            else:
                api.reply_message(ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TemplateMessage(
                        alt_text="Confirm Selection",
                        template=ButtonsTemplate(
                            title="Confirm",
                            text="Process now or select more symptoms?",
                            actions=[
                                PostbackAction(label="Process Image", display_text="Process image", data="process_image"),
                                PostbackAction(label="Select More",   display_text="Select more",   data="select_more"),
                            ],
                        ),
                    )]
                ))

        elif data == "process_image":
            user_state = state_manager.get_state(user_id)
            if user_state:
                _line_send_result(event, user_id, list(user_state.get("symptoms", [])))

        elif data == "select_more":
            user_state = state_manager.get_state(user_id)
            if not user_state:
                return
            selected = user_state.get("symptoms", set())
            remaining = {code: SYMPTOM_LABELS[code] for code in SYMPTOMS.values() if code not in selected}
            if not remaining:
                _line_send_result(event, user_id, list(selected))
                return
            actions = [
                PostbackAction(label=label[:20], display_text=label, data=f"symptom_{code}")
                for code, label in list(remaining.items())[:4]
            ]
            api.reply_message(ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TemplateMessage(
                    alt_text="Select More Symptoms",
                    template=ButtonsTemplate(title="Select More Symptoms", text="Select additional symptoms:", actions=actions),
                )]
            ))

    except Exception as exc:
        logger.exception("handle_postback error: %s", exc)
        try:
            _line_api().reply_message(ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[LineTextMessage(type="text", text="Sorry, there was an error. Please try again.")]
            ))
        except Exception:
            pass

@app.route("/health")
def health():
    depth = _queue_depth()
    return jsonify({
        "status": "ok",
        "queue_backend": "redis" if _has_active_workers() else "thread",
        "queue_depth": depth,
        "queue_max": _MAX_QUEUE_DEPTH,
        "queue_busy": depth > 0,
        "redis_connected": _redis_conn is not None,
    }), 200



@app.route("/", methods=["GET", "POST"])
def index():
    if "user" in session:
        return redirect("/home")

    error_message = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            user_data = firebase_sign_in(email, password)
            account_info = firebase_get_account_info(user_data["idToken"])
            if not account_info["users"][0].get("emailVerified", False):
                error_message = "Please verify your email before logging in."
                return render_template("login.html", error=error_message)
            session["user"] = email
            return redirect("/home")
        except requests.HTTPError as exc:
            logger.warning("Login failed for %s: %s", email, exc)
            error_message = "Email or password is incorrect."
        except Exception as exc:
            logger.exception("Unexpected login error: %s", exc)
            error_message = "Login failed. Please try again."

    return render_template("login.html", user=session.get("user"), error=error_message)


@app.route("/login")
def login():
    # Fetch env vars at request time to ensure Railway passes them properly
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    auth_url = os.getenv("GOOGLE_AUTHORIZATION_URL", "https://accounts.google.com/o/oauth2/auth")
    scopes = os.getenv("GOOGLE_SCOPES", "openid email profile")
    
    # Dynamically generate the redirect URI based on the current host
    # This ensures it works both locally and on Railway without changing .env
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")  # Read from .env
    return redirect(
        f"{auth_url}?response_type=code&client_id={client_id}"
        f"&redirect_uri={redirect_uri}&scope={scopes}"
    )


@app.route("/google_auth_callback")
def google_auth_callback():
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    code = request.args.get("code")
    if not code:
        return "Authorization failed. No code provided.", 400

    # We must use exactly the redirect_uri used in /login
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    logger.info("OAuth Callback: code received, using redirect_uri=%s", redirect_uri)

    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )
    token_info = token_resp.json()
    if "access_token" not in token_info:
        logger.error("OAuth token exchange failed: %s", token_info)
        return f"Failed to retrieve access token: {token_info.get('error_description', 'Unknown error')}", 500

    # Try v2 userinfo which is modern and stable
    user_info_resp = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {token_info['access_token']}"},
        timeout=10,
    )
    user_info = user_info_resp.json()
    logger.info("OAuth user_info received: %s", user_info)
    
    # Google sometimes returns 'email' and sometimes 'id' or other fields
    email = user_info.get("email")
    if not email:
        logger.error("OAuth email missing in userinfo: %s", user_info)
        return f"Failed to retrieve email from Google. Data received: {user_info}", 500

    session["user"] = email
    os.makedirs(os.path.join("static", "output", hashlib.md5(email.encode()).hexdigest()[:10]), exist_ok=True)
    return redirect("/home")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        email_error = password_error = None

        if len(password) < 6:
            password_error = "Password should be at least 6 characters long."

        if not password_error:
            try:
                user_data = firebase_create_user(email, password)
                firebase_send_verification(user_data["idToken"])
                return "A verification email has been sent. Please verify it before logging in."
            except requests.HTTPError as exc:
                body = exc.response.json() if exc.response else {}
                err = body.get("error", {}).get("message", "")
                if "EMAIL_EXISTS" in err:
                    email_error = "This email is already registered."
                elif "WEAK_PASSWORD" in err:
                    password_error = "Password is too weak."
                else:
                    return "Failed to sign up. Please try again."

        return render_template("signup.html", email=email, email_error=email_error, password_error=password_error)

    return render_template("signup.html")


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        try:
            firebase_send_password_reset(email)
            flash("Password reset email sent. Please check your inbox.", "success")
        except Exception:
            flash("Failed to send password reset email. Please try again.", "error")
    return render_template("forgot_password.html")


# ---------------------------------------------------------------------------
# Main app routes
# ---------------------------------------------------------------------------
@app.route("/home")
@login_required
def home():
    return render_template("index.html", user=session["user"])


@app.route("/detect")
@login_required
def detect():
    return render_template(
        "detect.html",
        user=session.get("user"),
        image_output=None,
        label=None,
        name_out=None,
        eva_output=None,
        model_version=None,
        detections_raw=[]
    )


@app.route("/test")
@login_required
def test():
    return render_template("ContactSW.html", user=session["user"])


@app.route("/Newmain")
@login_required
def Newmain():
    return render_template("ContactSW.html", user=session["user"])


@app.route("/learn-more")
@login_required
def learn():
    from data import get_cards  # type: ignore
    cards = get_cards()
    return render_template("learn-more.html", user=session["user"], cards=cards)


@app.route("/card-detail/<card_id>")
@login_required
def card_detail(card_id):
    from data import get_cards  # type: ignore
    cards = get_cards()
    card = next((c for c in cards if c["id"] == card_id), None)
    if not card:
        abort(404)
    return render_template("card-detail.html", user=session["user"], card=card)


# ---------------------------------------------------------------------------
# File serving
# ---------------------------------------------------------------------------
@app.route("/static/output/<path:filename>")
def serve_image(filename):
    if "user" not in session:
        return "Unauthorized", 401
    email_hash = hashlib.md5(session["user"].encode()).hexdigest()[:10]
    if not filename.startswith(email_hash):
        return "Unauthorized", 403
    return send_from_directory("static/output", filename)


@app.route("/line/images/<path:filename>")
def serve_line_image(filename):
    return send_from_directory("static/output", filename)


# ---------------------------------------------------------------------------
# Inference route
# ---------------------------------------------------------------------------
@app.route("/uploaded", methods=["POST"])
@login_required
def uploaded():
    user_email = session["user"]
    file = request.files.get("file")

    # Validate
    err = _validate_upload(file)
    if err:
        flash(err, "error")
        return redirect(url_for("detect"))

    file_path = _safe_upload(file)
    image = cv2.imread(file_path)
    if image is None:
        flash("Could not read the uploaded image. Please try a different file.", "error")
        return redirect(url_for("detect"))

    patient_info = request.form.getlist("checkboxes[]")
    # Read model version from the radio button (v7 or v8); default to env var or v8
    model_version = request.form.get(
        "model_version",
        os.getenv("YOLO_MODEL_VERSION", "v8")
    ).strip().lower()
    if model_version not in ("v7", "v8"):
        model_version = "v8"
    logger.info("Upload from %s — patient_info=%s model=%s", user_email, patient_info, model_version)

    try:
        image_output, label, name_out, eva_output, detections_raw = submit_inference(
            image, patient_info, user_email, model_version=model_version
        )
    except TimeoutError:
        msg = "The server is busy. Please try again in a moment."
        if request.headers.get("Accept") == "application/json":
            return jsonify({"success": False, "error": msg}), 503
        flash(msg, "error")
        return redirect(url_for("detect"))
    except RuntimeError as exc:
        msg = str(exc)
        if request.headers.get("Accept") == "application/json":
            return jsonify({"success": False, "error": msg}), 503
        flash(msg, "error")
        return redirect(url_for("detect"))
    except Exception as exc:
        logger.exception("Inference failed: %s", exc)
        msg = "An error occurred during analysis. Please try again."
        if request.headers.get("Accept") == "application/json":
            return jsonify({"success": False, "error": msg}), 500
        flash(msg, "error")
        return redirect(url_for("detect"))

    session["model_version"] = model_version
    session["image_output"] = image_output
    session["label"] = label
    session["name_out"] = name_out
    session["eva_output"] = eva_output
    session["detections_raw"] = detections_raw

    if request.headers.get("Accept") == "application/json":
        return jsonify({
            "success": True,
            "image_output": image_output,
            "label": label,
            "name_out": name_out,
            "eva_output": eva_output,
            "model_version": model_version,
            "detections_raw": detections_raw
        })
        
    return redirect(url_for("show_results"))


@app.route("/results")
@login_required
def show_results():
    image_output = session.get("image_output")
    if not image_output:
        return redirect(url_for("detect"))
    return render_template(
        "detect.html",
        user=session.get("user"),
        image_output=image_output,
        label=session.get("label"),
        name_out=session.get("name_out"),
        eva_output=session.get("eva_output"),
        model_version=session.get("model_version"),
        detections_raw=session.get("detections_raw")
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)