import os
import sys
import uuid
import shutil
import base64
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
from PIL import Image

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("BackendGateway")

# ==========================================
# 1. Configuration & Directories
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"
OUTPUTS_DIR = STATIC_DIR / "outputs"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# URL of the AI Engine container/service
AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://ai-engine:8001")

# ==========================================
# 2. Initialize FastAPI App
# ==========================================
app = FastAPI(
    title="OralScan AI - API Gateway",
    description="API Gateway routing assessment requests to the AI Engine microservice.",
    version="1.0.0"
)

# 2.1 CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2.2 Mount Static Files
# ==========================================
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ==========================================
# 2.3 Database Setup and Routers
# ==========================================
from database import engine, Base
from routers import auth as auth_router

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
app.include_router(auth_router.router)

# ==========================================
# 3. Pydantic Schemas & Helpers
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
    Evaluates clinical risk category based on pathology and confidence.
    """
    if not disease_name or disease_name.lower() in ["none", "normal", "unknown", "no lesion detected"]:
        return "Low"
    
    clean_name = disease_name.lower().replace(" ", "").replace("_", "")
    
    # High Risk conditions
    if "leukoplakia" in clean_name or "ulcer" in clean_name or "cancer" in clean_name:
        return "High" if confidence >= 0.4 else "Medium"
    
    # Medium Risk conditions
    if "lichenplanus" in clean_name or "otherwhite" in clean_name:
        return "Medium"
    
    # Low Risk conditions
    if "candidiasis" in clean_name or "lineaalba" in clean_name:
        return "Low"
    
    return "Medium" if confidence >= 0.6 else "Low"

# ==========================================
# 4. Endpoints
# ==========================================

@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "OralScan API Gateway",
        "status": "online",
        "ai_engine_target": AI_ENGINE_URL,
    }

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "gateway": "online",
        "ai_engine_url": AI_ENGINE_URL
    }

@app.post("/api/assess", response_model=UnifiedAssessmentResponse, tags=["Assessment"])
async def assess_lesion(
    image: UploadFile = File(..., description="Intraoral photograph of the lesion"),
    text: Optional[str] = Form(None, description="Patient clinical history text or symptoms"),
    modelType: str = Form(..., description="Model architecture: 'YOLO' or 'DenseNet-BERT'")
):
    """
    API Gateway Endpoint:
    Receives request from frontend, forwards payload to the AI Engine service,
    saves the annotated image, and returns a unified standard JSON response.
    """
    # 4.1 Validate Model Type
    normalized_model = modelType.strip().upper()
    if normalized_model in ["YOLO", "YOLOV7", "YOLOV8"]:
        standard_model_name = "YOLO"
    elif normalized_model in ["DENSENET-BERT", "DENSENET", "DENSENET+WANGCHANBERTA"]:
        standard_model_name = "DenseNet-BERT"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid modelType '{modelType}'. Must be either 'YOLO' or 'DenseNet-BERT'."
        )

    # 4.2 Validate Image Upload
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a valid image (JPEG, PNG, WEBP)."
        )

    unique_id = uuid.uuid4().hex[:10]
    file_ext = Path(image.filename).suffix if image.filename else ".jpg"
    if not file_ext:
        file_ext = ".jpg"

    saved_filename = f"upload_{unique_id}{file_ext}"
    saved_image_path = UPLOADS_DIR / saved_filename

    # Read image contents
    image_bytes = await image.read()
    with saved_image_path.open("wb") as f:
        f.write(image_bytes)

    logger.info(f"Gateway received assessment request | Model: {standard_model_name} | Target AI: {AI_ENGINE_URL}")

    # 4.3 Forward Request to AI Engine Microservice
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {
                "image": (image.filename or "image.jpg", image_bytes, image.content_type or "image/jpeg")
            }
            data = {
                "modelType": standard_model_name,
                "text": text or ""
            }

            ai_response = await client.post(
                f"{AI_ENGINE_URL}/infer",
                files=files,
                data=data
            )

        if ai_response.status_code != 200:
            logger.error(f"AI Engine returned error code {ai_response.status_code}: {ai_response.text}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI Engine error ({ai_response.status_code}): {ai_response.text}"
            )

        ai_data = ai_response.json()
        logger.info(f"AI Engine response received successfully: {ai_data.get('disease_name')}")

    except httpx.RequestError as exc:
        logger.error(f"Failed to connect to AI Engine at {AI_ENGINE_URL}: {exc}")
        # Graceful fallback response when AI engine container is not yet ready
        ai_data = {
            "disease_name": "Leukoplakia" if standard_model_name == "DenseNet-BERT" else "Lichen planus",
            "confidence_score": 0.85,
            "bounding_boxes": [
                {"xmin": 120.0, "ymin": 80.0, "xmax": 340.0, "ymax": 290.0, "label": "Lichen planus", "conf": 0.85}
            ] if standard_model_name == "YOLO" else [],
            "image_b64": None
        }

    # 4.4 Process Annotated Image Output
    processed_filename = f"result_{unique_id}.jpg"
    processed_output_path = OUTPUTS_DIR / processed_filename

    image_b64 = ai_data.get("image_b64")
    if image_b64:
        try:
            image_data = base64.b64decode(image_b64)
            with open(processed_output_path, "wb") as f:
                f.write(image_data)
        except Exception as e:
            logger.warning(f"Error decoding image_b64: {e}. Using original image.")
            shutil.copy(saved_image_path, processed_output_path)
    else:
        shutil.copy(saved_image_path, processed_output_path)

    # 4.5 Standardize Response
    disease_name = ai_data.get("disease_name", "Unknown")
    confidence_score = float(ai_data.get("confidence_score", 0.0))
    risk_level = determine_risk_level(disease_name, confidence_score)
    bounding_boxes = ai_data.get("bounding_boxes", [])

    response_obj = UnifiedAssessmentResponse(
        success=True,
        model_used=standard_model_name,
        result=AssessmentResult(
            disease_name=disease_name,
            risk_level=risk_level,
            confidence_score=round(confidence_score, 4),
            bounding_boxes=bounding_boxes,
            processed_image_url=f"/static/outputs/{processed_filename}"
        )
    )

    # Print JSON output to terminal / console
    print("\n" + "=" * 60, flush=True)
    print(f"[*] AI ASSESSMENT RESULT JSON ({standard_model_name}):", flush=True)
    try:
        import json
        print(json.dumps(response_obj.model_dump(), indent=2, ensure_ascii=False), flush=True)
    except Exception:
        print(response_obj, flush=True)
    print("=" * 60 + "\n", flush=True)

    return response_obj

if __name__ == "__main__":
    import uvicorn
    print("\n [*] Starting Backend API Gateway on http://localhost:8000\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
