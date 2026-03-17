import socket
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.config import get_settings
from app.database import engine, Base
from app.api.v1.api import api_router
import os

# --- Helper để lấy IP Network ---
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# ==================== Lifespan (Startup/Shutdown) ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # Khởi tạo tables (Chỉ dùng nếu không dùng Alembic)
    Base.metadata.create_all(bind=engine)
    
    # Banner Terminal theo phong cách HEMIS
    local_ip = "127.0.0.1"
    network_ip = get_ip_address()
    port = 8000
    
    print("\n" + "="*70)
    print(f"  {settings.PROJECT_NAME.upper()} API Server")
    print("="*70)
    print(f"  Local:   http://{local_ip}:{port}")
    print(f"  Network: http://{network_ip}:{port}")
    print(f"  Docs:    http://{local_ip}:{port}/api/docs")
    print(f"  ReDoc:   http://{local_ip}:{port}/api/redoc")
    print("="*70 + "\n")
    
    yield
    print(f"\n--- Shutting down {settings.PROJECT_NAME} ---")

# ==================== Initialize App ====================

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="FastAPI Backend for OldShop E-commerce Platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# ==================== Static Files ====================

# Create uploads directory structure at root level (next to backend folder)
# Get the project root: backend > parent > uploads
project_root = Path(__file__).parent.parent.parent  # Go from app/main.py to root
uploads_dir = project_root / "uploads"
products_dir = uploads_dir / "products"

# Ensure directories exist with proper permissions
uploads_dir.mkdir(exist_ok=True, parents=True)
products_dir.mkdir(exist_ok=True, parents=True)

print(f"📁 Static files directory: {uploads_dir}")
print(f"📁 Products images path: {products_dir}")

# Mount static files
app.mount("/static", StaticFiles(directory=str(uploads_dir)), name="static")

# ==================== Middleware ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Base Routes ====================

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/api/docs")

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION
    }

# ==================== API Routes ====================

# Include all v1 API endpoints with /api/v1 prefix
# The api_router already includes the prefix from v1/api.py
app.include_router(api_router)

# ==================== Error Handlers ====================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "Internal server error"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )