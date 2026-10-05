import io
import json
import numpy as np
from PIL import Image, ImageOps
from fastapi import FastAPI, File, UploadFile, HTTPException
import onnxruntime as ort

# 1. Initialize FastAPI App
app = FastAPI(
    title="Fruit Quality Classification API",
    description="Backend API for classifying fruit freshness using ONNX Runtime",
    version="1.0.0"
)

# 2. Load ONNX Model and Class Labels
MODEL_PATH = "models/fruit_model.onnx"
LABELS_PATH = "models/labels.json"

try:
    ort_session = ort.InferenceSession(MODEL_PATH)
    with open(LABELS_PATH, "r") as f:
        labels_map = json.load(f)
    print("ONNX Model and Labels loaded successfully.")
except Exception as e:
    print(f"Warning: Could not load model or labels from {MODEL_PATH}: {e}")

# 3. Helper Functions: Preprocessing & Softmax
def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Resize preserving aspect ratio, center crop, normalize, and format into (1, 3, 224, 224)."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # Preserves aspect ratio, scales shortest edge, and center crops to exact (224, 224)
    image = ImageOps.fit(image, (224, 224), method=Image.Resampling.BILINEAR)
    
    # Scale to [0.0, 1.0]
    img_array = np.array(image).astype(np.float32) / 255.0
    
    # ImageNet Mean & Std Normalization
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_array = (img_array - mean) / std
    
    # Transpose from (224, 224, 3) -> (3, 224, 224)
    img_array = img_array.transpose(2, 0, 1)
    
    # Add batch dimension -> (1, 3, 224, 224)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def softmax(x: np.ndarray) -> np.ndarray:
    """Compute Softmax probabilities from raw model output logits."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=1, keepdims=True)

# 4. API Endpoints
@app.get("/")
def root():
    return {"status": "online", "message": "Fruit Quality Grading API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": MODEL_PATH}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Validate file format
    if file.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Please upload JPG or PNG.")
    
    # Read and preprocess image
    image_bytes = await file.read()
    input_tensor = preprocess_image(image_bytes)
    
    # Run ONNX Inference Engine
    input_name = ort_session.get_inputs()[0].name
    raw_outputs = ort_session.run(None, {input_name: input_tensor})[0]
    print(f"DEBUG RAW LOGITS: {raw_outputs}")
    
    # Calculate Softmax Probabilities
    probabilities = softmax(raw_outputs)[0]
    predicted_idx = int(np.argmax(probabilities))
    confidence = float(probabilities[predicted_idx])
    
    # Direct list lookup using integer indices
    predicted_class = labels_map[predicted_idx]
    
    # Format all class probabilities for output
    all_scores = {labels_map[i]: float(prob) for i, prob in enumerate(probabilities)}

    return {
        "filename": file.filename,
        "prediction": predicted_class,
        "confidence": round(confidence * 100, 2),
        "is_fresh": predicted_class.startswith("fresh"),
        "probabilities": all_scores
    }