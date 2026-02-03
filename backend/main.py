from dotenv import load_dotenv
import os
load_dotenv()
import sys
from pathlib import Path


# -----------------------
# Ensure project root is on sys.path
# -----------------------
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# V1 routers
from backend.sample_size_calculator.api import router as sample_size_router
from backend.mde_calculator.api import router as mde_router
from fastapi import FastAPI
from backend.api.phase0 import router as phase0_router
from backend.api.inference import router as inference_router

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path


# V2 routers
from backend.v2.api.experiments import router as v2_experiments_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

#drafts

from backend.v2.api.resume import router as resume_router

#dashboard
from backend.v2.api import dashboard



#orchestration layer
from backend.v2.api.orchestration import router as orchestration_router


app = FastAPI(
    title="AB Experiment Design Validator",
    version="0.1",
    description="Phase 0.3 experiment design validation engine"
)

# Fix: Use absolute path for static files
STATIC_DIR = Path(__file__).parent.parent / "Take_inputs"

if not STATIC_DIR.exists():
    print(f"❌ ERROR: Static directory not found at {STATIC_DIR}")
    print(f"   Current working directory: {Path.cwd()}")
else:
    print(f"✅ Static directory found at {STATIC_DIR}")

# Mount Take_inputs directory
app.mount(
    "/Take_inputs",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)

# -----------------------
# Serve public frontend (Learn, Articles, Homepage)
# -----------------------

PUBLIC_DIR = Path(__file__).parent.parent / "public"

if not PUBLIC_DIR.exists():
    print(f"❌ ERROR: Public directory not found at {PUBLIC_DIR}")
else:
    print(f"✅ Public directory found at {PUBLIC_DIR}")

app.mount(
    "/",
    StaticFiles(directory=str(PUBLIC_DIR), html=True),
    name="public",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://sriram788nagarajan.github.io",
        "https://pvalue.net",
        "https://www.pvalue.net",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
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
# V2 – Experiment Framework
# -----------------------
app.include_router(v2_experiments_router)



app.include_router(resume_router)

## Dashboard Router

app.include_router(dashboard.router)



## orchestration layer router

app.include_router(orchestration_router)

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




@app.get("/v2/experiments/create")
def serve_create_experiment():
    # Redirect to static file location
    return RedirectResponse(url="/Take_inputs/v2/experiments/create_experiment.html")


@app.get("/debug/static")
def debug_static():
    """Debug endpoint to verify static file structure"""
    static_dir = Path(__file__).parent.parent / "Take_inputs"
    
    files = []
    if static_dir.exists():
        for file in static_dir.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(static_dir)
                files.append(str(rel_path).replace("\\", "/"))
    
    return {
        "static_dir": str(static_dir),
        "exists": static_dir.exists(),
        "files": sorted(files)[:50],
        "total_files": len(files)
    }


# Debug: Print all registered routes
@app.on_event("startup")
async def startup_debug():
    print("=" * 80)
    print("REGISTERED ROUTES:")
    print("=" * 80)
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"{route.methods} {route.path}")
    print("=" * 80)