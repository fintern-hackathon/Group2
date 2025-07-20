from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.transactions import router as transactions_router
from app.routers.analytics import router as analytics_router
from app.routers.mcp_tools import router as mcp_tools_router
from app.routers.mcp_client import router as mcp_client_router
from app.routers.personality import router as personality_router
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
app.include_router(mcp_tools_router, prefix="/api/v1/mcp", tags=["mcp-tools"])
app.include_router(mcp_client_router, prefix="/api/v1/mcp-client", tags=["mcp-client"])
app.include_router(personality_router, tags=["personality"])  # NEW: Financial DNA

# Startup event
@app.on_event("startup")
async def startup():
    await init_db()
    print("✅ Working API started!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 