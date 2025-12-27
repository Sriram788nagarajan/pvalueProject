import sys
from pathlib import Path
from backend.sample_size_calculator.api import router as sample_size_router
from backend.mde_calculator.api import router as mde_router




# -----------------------
# Ensure project root is on sys.path
# -----------------------
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from backend.api.phase0 import router as phase0_router
from backend.api.inference import router as inference_router

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path


app = FastAPI(
    title="AB Experiment Design Validator",
    version="0.1",
    description="Phase 0.3 experiment design validation engine"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://sriram788nagarajan.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Register API routers
# -----------------------

# Phase 0
app.include_router(
    phase0_router,
    prefix="/api",
    tags=["Phase 0"]
)

# Sample Size Calculator
app.include_router(
    sample_size_router,
    prefix="/api",
    tags=["Sample Size Calculator"]
)

# MDE Calculator
app.include_router(
    mde_router,
    prefix="/api",
    tags=["MDE Calculator"]
)


# Phase 3 – Statistical Inference
app.include_router(
    inference_router
)

# -----------------------
# Serve Phase 3 frontend
# -----------------------

@app.get("/inference")
def serve_inference_page():
    html_path = Path(__file__).parent.parent / "Take_inputs" / "inference.html"
    return FileResponse(html_path)

# -----------------------
# Serve Sample Size Calculator frontend
# -----------------------

@app.get("/sample-size-calculator")
def serve_sample_size_calculator():
    html_path = (
        Path(__file__).parent.parent
        / "Take_inputs"
        / "sample_size_calculator"
        / "sample_size.html"
    )
    return FileResponse(html_path)

# -----------------------
# Serve MDE Calculator frontend
# -----------------------

@app.get("/mde-calculator")
def serve_mde_calculator():
    html_path = (
        Path(__file__).parent.parent
        / "Take_inputs"
        / "mde_calculator"
        / "mde.html"
    )
    return FileResponse(html_path)



# -----------------------
# Health check
# -----------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}
