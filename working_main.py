from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.transactions import router as transactions_router
from app.routers.analytics import router as analytics_router
from app.routers.ai import router as ai_router
from app.database.connection import init_db

# Create FastAPI app
app = FastAPI(
    title="FinTree API - Complete Version",
    description="Gamified Financial App - Finansal Ağaç Büyütme Uygulaması",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "database": "connected"}

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(transactions_router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])

# Startup event
@app.on_event("startup")
async def startup():
    await init_db()
    print("✅ Working API started!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 