# Automated Fruit Quality Grading and Freshness Classification System using PyTorch, ONNX Runtime, FastAPI, Streamlit, and Docker

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX_Runtime-1.15+-005fed.svg)](https://onnxruntime.ai/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-ff4b4b.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ed.svg)](https://www.docker.com/)

**CPE178P Foundations of AI**

**Group02 FOPI01**

**1T2627**

---

## Executive Summary

Post-harvest fruit inspection and quality grading in agricultural supply chains remain predominantly manual processes. Human visual inspection is labor-intensive, subjective, prone to physical fatigue, and highly inconsistent across operational shifts. Undetected rotten produce packaged alongside fresh fruit releases ethylene gas, rapidly contaminating entire inventory batches during transit and warehouse storage, leading to substantial economic loss and food waste.

This project delivers an **Automated Fruit Quality Grading and Freshness Classification System**—a production-ready, real-time computer vision application that categorizes produce into six distinct fresh or rotten states across three major fruit categories (apples, bananas, and oranges). By leveraging transfer learning with a pre-trained **ResNet-18** CNN backbone, exporting to hardware-agnostic **ONNX Runtime**, serving via a **FastAPI** REST backend, rendering with a **Streamlit** GUI, and orchestrating deployment via **Docker Compose**, the platform provides high-accuracy, objective freshness assessments under 200 ms on CPU hardware.

---

## Key System Features & Objectives

* **Multi-Class Freshness Classification:** Classifies 6 produce categories (`freshapples`, `rottenapples`, `freshbananas`, `rottenbananas`, `freshoranges`, `rottenoranges`) with target validation accuracy $\ge 92\%$ and Macro $F1 \ge 0.90$.
* **Low-Latency CPU Execution:** Achieves end-to-end processing time $< 200\text{ ms}$ per image on standard CPU nodes via ONNX Runtime optimization.
* **Hardware-Agnostic Interoperability:** Exports fine-tuned PyTorch weights to standardized `.onnx` (opset 13), ensuring numerical parity with a maximum absolute logit delta $|\Delta\text{logit}| < 10^{-4}$.
* **Decoupled 3-Tier Architecture:** Clean separation of Presentation (Streamlit), Logic (FastAPI REST service), and Data Access Tiers.
* **Containerized Deployment:** Reproducible, single-command cross-platform orchestration via Docker Compose.

---

##  3-Tier System Architecture

```text
+-----------------------------------------------------------------------------------+
|                                 USER / CLIENT                                     |
|                      (Quality Control Inspector / Operator)                       |
+----------------------------------------+------------------------------------------+
                                         |
                                  Uploads Image / Displays Results
                                         v
+-----------------------------------------------------------------------------------+
| PRESENTATION TIER (Streamlit Web GUI)                                            |
|  - UI & Image Uploader Widget (st.file_uploader)                                  |
|  - Probability Bar Chart & Color-Coded Status Badge (Green=Fresh, Red=Rotten)     |
+----------------------------------------+------------------------------------------+
                                         |
                                  HTTP POST /predict (Image Bytes)
                                         v
+-----------------------------------------------------------------------------------+
| LOGIC TIER (FastAPI REST Service)                                                 |
|  - API Controller & Request Dispatcher (POST /predict)                            |
|  - Image Preprocessor (224x224 Resize, Tensor Conversion, ImageNet Normalization) |
|  - ONNX Runtime Inference Engine (hardware-agnostic graph execution)              |
|  - Post-Processor & Softmax Formatter                                             |
+----------------------------------------+------------------------------------------+
                                         |
                                  Read Model & Labels / Write Audit Logs
                                         v
+-----------------------------------------------------------------------------------+
| DATA ACCESS TIER (Storage & Model Repository)                                     |
|  - ONNX Model Artifact (fruit_model.onnx)                                         |
|  - Class Label Mapping (labels.json)                                              |
|  - System Audit Logs (audit_logs.json)                                            |
+-----------------------------------------------------------------------------------+
```

---

## Dataset Specification & Preprocessing Contract

* **Dataset Source:** Open-source Fresh and Rotten Fruits Dataset (Kaggle / Roboflow), comprising ~13,500 high-resolution RGB images across 6 target classes.
* **Data Partitioning:**
  * **Training Split (70%):** Used for backpropagation parameter optimization with online data augmentation.
  * **Validation Split (15%):** Used for hyperparameter tuning and early stopping monitoring.
  * **Test Split (15%):** Reserved exclusively for final unbiased accuracy and confusion matrix evaluation.
* **Preprocessing Contract:**
  * Spatial transform resize: $224 \times 224$ pixels.
  * ImageNet Standard Normalization: $\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$.
  * Augmentation (Train only): Random horizontal flips, random rotation ($\pm 15^\circ$), and color jitter.

---

## Repository Directory Layout

```text
cpe178p-fopi01-group02-fruit-quality-grading/
├── backend/                  # Logic Tier (FastAPI REST Service)
│   ├── main.py               # REST API endpoints, ONNX inference session, post-processing
│   ├── requirements.txt      # Backend Python dependencies
│   └── Dockerfile            # Container configuration for backend service
├── frontend/                 # Presentation Tier (Streamlit Web GUI)
│   ├── app.py                # Streamlit UI dashboard, image upload, REST client, status badges
│   ├── requirements.txt      # Frontend Python dependencies
│   └── Dockerfile            # Container configuration for frontend service
├── models/                   # Data Access Tier (Model Repository & Configuration)
│   ├── fruit_model.onnx      # Quantized / Exported ONNX model graph (ResNet-18 backbone)
│   ├── labels.json           # JSON mapping of class index to human-readable label
│   └── audit_logs.json       # System execution and latency audit logs
├── docs/                     # Documentation & Architecture Diagrams
│   ├── 3-tier-architecture-diagram-v3.drawio
│   ├── CPE178P_Project_Proposal.pdf
│   └── CPE178P_Project_Schedule.xlsx
├── docker-compose.yml        # Orchestration for multi-container deployment
├── .gitignore                # Git exclusion rules
└── README.md                 # Project documentation
```

---

## Quick Start & Setup Guide

### Option 1: Single-Command Docker Deployment

Ensure [Docker](https://docs.docker.com/get-docker/) and Docker Compose are installed on your system, then run:

```bash
# Clone the repository
git clone https://github.com/rvpsopongco/Fruit-Quality-Grading.git
cd Fruit-Quality-Grading

# Build and launch containers
docker-compose up --build
```

Access the services in your browser:
* **Streamlit Web GUI:** [http://localhost:8501](http://localhost:8501)
* **FastAPI Interactive Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **API Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

### Option 2: Local Manual Setup

#### 1. Backend Service Setup (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scriptsctivate
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Service Setup (Streamlit)
```bash
# Open a new terminal tab
cd frontend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scriptsctivate
pip install -r requirements.txt

# Launch Streamlit app
streamlit run app.py
```

---

## API Endpoint Documentation

### `POST /predict`
Accepts an image file and returns prediction probabilities, top label, and latency metrics.

* **Request:** `multipart/form-data` with key `file` containing RGB image (`.jpg` or `.png`).
* **Response (200 OK):**
```json
{
  "filename": "freshapples_01.jpg",
  "prediction": "Fresh Apple",
  "confidence": 0.9482,
  "status_badge": "FRESH",
  "latency_ms": 42.15,
  "probabilities": {
    "freshapples": 0.9482,
    "freshbananas": 0.0121,
    "freshoranges": 0.0105,
    "rottenapples": 0.0152,
    "rottenbananas": 0.0080,
    "rottenoranges": 0.0060
  }
}
```

### `GET /health`
Returns system health, model load status, and runtime environment details.

---

##  System Test Cases & QA Matrix

| Test ID | Scenario | Test Input | Expected Output | Status |
| :--- | :--- | :--- | :--- | :---: |
| **TC-01** | Fresh Apple Classification | `freshapples_01.jpg` | Label: 'Fresh Apple', Confidence $\ge 90\%$, Green badge | PASS |
| **TC-02** | Rotten Banana Classification | `rottenbananas_12.png` | Label: 'Rotten Banana', Confidence $\ge 90\%$, Red badge | PASS |
| **TC-03** | REST API Batch Payload | Image binary | HTTP 200 OK with valid JSON fields | PASS |
| **TC-04** | Latency Benchmark | 50 sequential requests | Mean end-to-end CPU latency $< 200\text{ ms}$ | PASS |
| **TC-05** | Invalid File Format Handling | `document.txt` | HTTP 400 Bad Request with descriptive error message | PASS |

---

## Development Team

* **Rachel Joy Baldo** — Backend Lead & API Architect
* **Aliyah Kate Wilsen See** — Machine Learning Lead & Model Trainer
* **Richard Von Sopongco** — Frontend & QA Lead

---

## License & Course Attribution

Developed in partial fulfillment of the requirements for CPE178P Foundations of AI at Mapúa University  
AI Disclosure: Consultative AI tools (Gemini) were utilized strictly for structural formatting, architectural diagramming, and schedule drafting per Mapúa Academic Council Resolution No. 2026-06. All code implementation, model training, and technical verifications were conducted independently by the student team.
