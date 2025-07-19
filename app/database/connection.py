from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from typing import AsyncGenerator

# SQLite Database path
DATABASE_PATH = "fintree.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

# SQLAlchemy setup
Base = declarative_base()
metadata = MetaData()

# Async engine
async_engine = None
AsyncSessionLocal = None

async def init_db():
    """SQLite database bağlantısını başlat"""
    global async_engine, AsyncSessionLocal
    
    try:
        # SQLite async engine
        async_engine = create_async_engine(
            DATABASE_URL,
            echo=True if os.getenv("DEBUG") == "True" else False,
            future=True
        )
        
        # Create async session factory
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ SQLite database initialized")
        
    except Exception as e:
        print(f"❌ SQLite database connection failed: {e}")
        raise e

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Expense categories (static)
EXPENSE_CATEGORIES = {
    'food': {'name': 'Yemek & İçecek', 'icon': '🍽️', 'ideal_percentage': 30.0},
    'transport': {'name': 'Ulaşım', 'icon': '🚗', 'ideal_percentage': 15.0},
    'bills': {'name': 'Faturalar', 'icon': '📄', 'ideal_percentage': 25.0},
    'entertainment': {'name': 'Eğlence', 'icon': '🎬', 'ideal_percentage': 10.0},
    'health': {'name': 'Sağlık', 'icon': '🏥', 'ideal_percentage': 15.0},
    'clothing': {'name': 'Giyim', 'icon': '👕', 'ideal_percentage': 5.0}
} 