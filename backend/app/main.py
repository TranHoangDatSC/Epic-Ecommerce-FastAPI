import socket
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import engine, Base
from app.api.routes import auth, users, categories, products, orders, moderator

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

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(categories.router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(moderator.router, prefix=settings.API_V1_STR)

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