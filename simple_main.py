from fastapi import FastAPI
from app.database.connection import init_db, get_db
from app.routers.auth import router as auth_router

app = FastAPI(title="FinTree Debug API")

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    await init_db()
    print("✅ Database ready")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 