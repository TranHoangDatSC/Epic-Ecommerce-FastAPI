import socket
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import engine, Base
from app.api.v1 import auth, users, categories, products, orders, moderator, cart, admin, system
import os

import logging
import warnings
from sqlalchemy.exc import SAWarning

warnings.filterwarnings("ignore", category=SAWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

logging.getLogger("uvicorn.access").setLevel(logging.WARNING) 
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

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
    Base.metadata.create_all(bind=engine)
    
    local_ip = "127.0.0.1"
    network_ip = get_ip_address()
    port = 8000
    
    # Giao diện khởi động Clean & Pro
    print("\n" + "╔" + "═"*68 + "╗")
    print(f"║  🚀 {settings.PROJECT_NAME.upper()} - BACKEND SERVICES READY".ljust(69) + "║")
    print("╠" + "═"*68 + "╣")
    print(f"║  ▸ Local:    http://{local_ip}:{port}".ljust(69) + "║")
    print(f"║  ▸ Network:  http://{network_ip}:{port}".ljust(69) + "║")
    print(f"║  ▸ API Docs: http://{local_ip}:{port}/api/docs".ljust(69) + "║")
    print(f"║  ▸ Status:   HEALTHY - DEBUG: {settings.DEBUG}".ljust(69) + "║")
    print("╚" + "═"*68 + "╝\n")
    yield

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

# Move and setup media directory
media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")
os.makedirs(media_dir, exist_ok=True)
os.makedirs(os.path.join(media_dir, "products"), exist_ok=True)
os.makedirs(os.path.join(media_dir, "users"), exist_ok=True)

# Mount static files to /media
app.mount("/media", StaticFiles(directory=media_dir), name="media")

# ==================== Middleware ====================

origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

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

# Primary versioned API (used by docs)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(categories.router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(moderator.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(system.router, prefix=settings.API_V1_STR)
app.include_router(cart.router, prefix=settings.API_V1_STR)

# Compatibility routes for clients calling /api/* (no /v1). These are not shown in the OpenAPI schema.
app.include_router(auth.router, prefix="/api", include_in_schema=False)
app.include_router(users.router, prefix="/api", include_in_schema=False)
app.include_router(categories.router, prefix="/api", include_in_schema=False)
app.include_router(products.router, prefix="/api", include_in_schema=False)
app.include_router(orders.router, prefix="/api", include_in_schema=False)
app.include_router(moderator.router, prefix="/api", include_in_schema=False)
app.include_router(admin.router, prefix="/api", include_in_schema=False)
app.include_router(system.router, prefix="/api", include_in_schema=False)
app.include_router(cart.router, prefix="/api", include_in_schema=False)

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