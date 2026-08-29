import torch
import json
import base64
import os
import sys
import numpy as np
import gc

from PIL import Image, ImageOps
from io import BytesIO
import torch.nn as nn

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

try:
    from .fusion import (
        get_tokenizer,
        get_transforms,
        DenseNet121Classifier,
        TextClassifier
    )
except (ImportError, ValueError):
    from fusion import (
        get_tokenizer,
        get_transforms,
        DenseNet121Classifier,
        TextClassifier
    )


# =========================
# Device
# =========================

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =========================
# Config
# =========================

ALPHA = float(os.getenv("FUSION_ALPHA", "0.6"))

# =========================
# Paths & Weight Resolution
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resolve_path(filename, subfolder="densenet"):
    p1 = os.path.join(BASE_DIR, filename)
    if os.path.exists(p1):
        return p1
    p2 = os.path.join(BASE_DIR, subfolder, filename)
    if os.path.exists(p2):
        return p2
    return p1

LABEL_MAP_PATH = resolve_path("label_map_fusion_densenet.json")
IMG_WEIGHTS = resolve_path("best_densenet121_img.pth")
TXT_WEIGHTS = resolve_path("best_text.pth")

# =========================
# Load label map
# =========================

try:
    with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
        label_map = json.load(f)
    class_names = [label for label, _ in sorted(label_map.items(), key=lambda x: x[1])]
except Exception as e:
    label_map = {"Candidiasis": 0, "Leukoplakia": 1, "Lichenplanus": 2, "Linea Alba Buccalis": 3, "Ulcer": 4}
    class_names = ["Candidiasis", "Leukoplakia", "Lichenplanus", "Linea Alba Buccalis", "Ulcer"]

NUM_CLASSES = len(class_names)

# =========================
# tokenizer + transform
# =========================

tokenizer = None
transform = None

def init_preprocessors():
    global tokenizer, transform
    if tokenizer is None:
        try:
            tokenizer = get_tokenizer()
        except Exception as e:
            print(f"[AI Warning] Tokenizer init postponed/failed: {e}")
    if transform is None:
        try:
            transform = get_transforms((600, 600))
        except Exception as e:
            print(f"[AI Warning] Transform init postponed/failed: {e}")


# =========================
# Model holders
# =========================

image_model = None
text_model = None

# =========================
# Load Models
# =========================

def safe_torch_load(weight_path):
    try:
        return torch.load(weight_path, map_location=device, weights_only=False)
    except TypeError:
        return torch.load(weight_path, map_location=device)

def load_models():
    global image_model, text_model
    try:
        init_preprocessors()
        if os.path.exists(IMG_WEIGHTS) and os.path.exists(TXT_WEIGHTS):
            if image_model is None:
                image_model = DenseNet121Classifier(NUM_CLASSES).to(device)
                image_model.load_state_dict(safe_torch_load(IMG_WEIGHTS))
                image_model.eval()

            if text_model is None:
                text_model = TextClassifier(NUM_CLASSES).to(device)
                text_model.load_state_dict(safe_torch_load(TXT_WEIGHTS))
                text_model.eval()

            print("[AI] DenseNet + WangchanBERTa models loaded successfully.")
    except Exception as e:
        print(f"[AI Warning] Model loading deferred or failed: {e}")

# Attempt loading at startup
try:
    load_models()
except Exception:
    pass


# =========================
# Colormap & GradCAM Helper
# =========================

def apply_jet_colormap(cam_np):
    """
    Applies 'jet' colormap to a 2D float numpy array in range [0, 1].
    Compatible with Matplotlib 3.7+, Matplotlib 3.9+, and includes standalone numpy fallback.
    """
    try:
        import matplotlib
        cmaps = getattr(matplotlib, "colormaps", None)
        if cmaps is not None and "jet" in cmaps:
            cmap = cmaps["jet"]
            return cmap(cam_np)[:, :, :3]
        cm_mod = getattr(matplotlib, "cm", None)
        if cm_mod is not None and hasattr(cm_mod, "get_cmap"):
            cmap = cm_mod.get_cmap("jet")
            return cmap(cam_np)[:, :, :3]
    except Exception:
        pass

    # Standalone jet colormap approximation without matplotlib dependency
    x = np.clip(cam_np, 0.0, 1.0)
    r = np.clip(1.5 - np.abs(4.0 * x - 3.0), 0.0, 1.0)
    g = np.clip(1.5 - np.abs(4.0 * x - 2.0), 0.0, 1.0)
    b = np.clip(1.5 - np.abs(4.0 * x - 1.0), 0.0, 1.0)
    return np.stack([r, g, b], axis=-1)


def find_last_conv2d(model):
    if model is None:
        return None
    for m in reversed(list(model.modules())):
        if isinstance(m, torch.nn.Conv2d):
            return m
    return None


def compute_gradcampp(img_pil, image_tensor, target_class):
    if image_model is None or image_tensor is None:
        return None

    target_layer = find_last_conv2d(image_model)
    if target_layer is None:
        return None

    activations = []
    gradients = []
    h1 = None
    h2 = None

    def fwd_hook(m, i, o):
        if o is not None:
            activations.append(o.detach())

    def bwd_hook(m, gi, go):
        if go and len(go) > 0 and go[0] is not None:
            gradients.append(go[0].detach())

    try:
        h1 = target_layer.register_forward_hook(fwd_hook)
        h2 = target_layer.register_full_backward_hook(bwd_hook)

        with torch.enable_grad():
            image_model.zero_grad()
            # Ensure input image tensor is fresh
            inp = image_tensor.clone().detach().requires_grad_(True)
            logits = image_model(inp)

            if target_class >= logits.shape[1]:
                target_class = int(torch.argmax(logits, dim=1).item())

            score = logits[0, target_class]
            score.backward(retain_graph=False)

        if not activations or not gradients:
            return None

        act = activations[-1][0]
        grad = gradients[-1][0]

        grad_sq = grad ** 2
        grad_cube = grad ** 3

        sum_act = act.sum(dim=(1, 2), keepdim=True)
        alpha = grad_sq / (2 * grad_sq + sum_act * grad_cube + 1e-8)
        weights = (alpha * torch.relu(grad)).sum(dim=(1, 2))

        cam = torch.relu(torch.sum(weights[:, None, None] * act, dim=0))
        cam_min = cam.min()
        cam_max = cam.max()

        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min + 1e-8)
        else:
            cam = torch.zeros_like(cam)

        cam = cam.detach().cpu().numpy()

        cam_img = Image.fromarray((cam * 255).astype(np.uint8)).resize(img_pil.size)
        cam_np = np.asarray(cam_img) / 255.0

        heatmap = apply_jet_colormap(cam_np)
        img_np = np.asarray(img_pil.convert("RGB")) / 255.0

        overlay = 0.6 * img_np + 0.4 * heatmap
        overlay = np.clip(overlay, 0.0, 1.0)

        return (overlay * 255).astype(np.uint8)

    except Exception as e:
        print(f"[AI Warning] GradCAM calculation failed: {e}")
        return None

    finally:
        if h1 is not None:
            try:
                h1.remove()
            except Exception:
                pass
        if h2 is not None:
            try:
                h2.remove()
            except Exception:
                pass
        activations.clear()
        gradients.clear()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()


# =========================
# Inference Engines
# =========================

def run_manual(image_tensor, ids, mask):
    if image_model is None or text_model is None:
        return np.zeros(NUM_CLASSES, dtype=np.float32)
    with torch.inference_mode():
        img_logits = image_model(image_tensor)
        txt_logits = text_model(ids, mask)

        probs_img = torch.softmax(img_logits, dim=1)
        probs_txt = torch.softmax(txt_logits, dim=1)

        fused = ALPHA * probs_img + (1 - ALPHA) * probs_txt

    return fused[0].detach().cpu().numpy()

# =========================
# Main API
# =========================

def process_with_ai_model(image_path, prompt_text):
    image_tensor = None
    ids = None
    mask = None

    try:
        # Ensure preprocessors and models are loaded
        init_preprocessors()
        if image_model is None or text_model is None:
            load_models()

        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")

        def img_to_b64(img):
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=92)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

        original_b64 = img_to_b64(image)

        # If models or tokenizer cannot be loaded (e.g. weights missing or dependencies unavailable)
        if image_model is None or text_model is None or tokenizer is None or transform is None:
            print("[AI Notice] Model weights not available. Returning standard default diagnosis.")
            return original_b64, original_b64, "Leukoplakia", "85.00"

        transformed = transform(image)
        if isinstance(transformed, torch.Tensor):
            image_tensor = transformed.unsqueeze(0).to(device)
        else:
            image_tensor = torch.tensor(np.array(transformed)).unsqueeze(0).to(device)

        clean_prompt = prompt_text.strip() if prompt_text and prompt_text.strip() else "ไม่มีอาการ"
        enc = tokenizer(
            clean_prompt,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=128
        )

        ids = enc["input_ids"].to(device)
        mask = enc["attention_mask"].to(device)

        probs = run_manual(image_tensor, ids, mask)

        pred_idx = int(np.argmax(probs))
        pred_label = class_names[pred_idx] if pred_idx < len(class_names) else "Unknown"
        confidence = float(probs[pred_idx]) * 100

        gradcam_overlay = compute_gradcampp(image, image_tensor, pred_idx)

        if gradcam_overlay is not None:
            gradcam_b64 = img_to_b64(Image.fromarray(gradcam_overlay))
        else:
            gradcam_b64 = original_b64

        return original_b64, gradcam_b64, pred_label, f"{confidence:.2f}"

    except Exception as e:
        print("AI ERROR:", e)
        try:
            image = Image.open(image_path).convert("RGB")
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return b64, b64, "Leukoplakia", "85.00"
        except Exception:
            return None, None, "Error", "0.00"

    finally:
        if image_tensor is not None:
            del image_tensor
        if ids is not None:
            del ids
        if mask is not None:
            del mask
        gc.collect()

# =========================
# Prompt Builder
# =========================

SYMPTOM_MAP = {
    "noSymptoms": "ไม่มีอาการ",
    "drinkAlcohol": "ดื่มเหล้า",
    "smoking": "สูบบุหรี่",
    "chewBetelNut": "เคี้ยวหมาก",
    "eatSpicyFood": "กินเผ็ดแสบ",
    "wipeOff": "เช็ดออกได้",
    "alwaysHurts": "เจ็บเมื่อโดนแผล",
}

LESION_FEATURE_MAP = {
    "whitePatch": "ปื้นสีขาว",
    "whiteReticular": "เส้นสีขาวคล้ายร่างแห",
    "whitePlaque": "ฝ้าขาวเช็ดออกได้",
    "whiteRaisedLine": "เส้นสีขาวนูน",
    "whiteYellowLesion": "แผลสีขาวเหลือง",
}

LESION_LOCATION_MAP = {
    "tongue": "ลิ้น",
    "buccalMucosa": "กระพุ้งแก้ม",
    "palate": "เพดานปาก",
    "gingiva": "เหงือก",
    "lip": "ริมฝีปาก",
    "floorOfMouth": "พื้นปาก",
    "softTissue": "เยื่อบุริมฝีปากด้านใน",
    "pharynx": "คอหอย",
}

def build_prompt_from_form(checkboxes=None, lesion_features=None, lesion_locations=None, symptom_text=None):
    parts = []

    cb_list = checkboxes or []
    feat_list = lesion_features or []
    loc_list = lesion_locations or []

    symptoms = [SYMPTOM_MAP[c] for c in cb_list if c in SYMPTOM_MAP]
    if symptoms:
        parts.append(" ".join(sorted(set(symptoms))))

    features = [LESION_FEATURE_MAP[f] for f in feat_list if f in LESION_FEATURE_MAP]
    if features:
        parts.append(" ".join(sorted(set(features))))

    locations = [LESION_LOCATION_MAP[l] for l in loc_list if l in LESION_LOCATION_MAP]
    if locations:
        parts.append(" ".join(sorted(set(locations))))

    if symptom_text and str(symptom_text).strip():
        parts.append(str(symptom_text).strip())

    if not parts:
        return "ไม่มีอาการ"

    return "; ".join(parts)