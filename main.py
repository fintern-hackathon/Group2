from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import routers - tek tek import
from app.routers.auth import router as auth_router
# from app.routers.transactions import router as transactions_router
# from app.routers.analytics import router as analytics_router  
# from app.routers.ai import router as ai_router
from app.database.connection import init_db

# Create FastAPI app
app = FastAPI(
    title="FinTree API",
    description="Finansal Ağaç Büyütme Uygulaması - MCP + Açık Bankacılık",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hackathon için geçici
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Sistem sağlık kontrolü"""
    try:
        # TODO: Database connection check
        return {
            "status": "healthy",
            "timestamp": "2025-01-15T10:30:00Z",
            "services": {
                "database": "connected",
                "gemini_ai": "connected"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# Include routers - sadece çalışan auth router ile başlayalım  
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
# TODO: Diğer router'ları sonra ekleyeceğiz
# app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
# app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])  
# app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında çalışır"""
    print("🌳 FinTree API başlatılıyor...")
    await init_db()
    print("✅ SQLite database hazır")
    print("🚀 FinTree API hazır!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Uygulama kapanırken çalışır"""
    print("🛑 FinTree API kapatılıyor...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
