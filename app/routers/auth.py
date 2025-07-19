from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.database.connection import get_db
from app.models.user import User
from app.models.transaction import UserTotal

router = APIRouter()

# Pydantic models
class UserCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    phone: Optional[str]

@router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Yeni kullanıcı oluşturma"""
    try:
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            return UserResponse(
                user_id=str(existing_user.id),
                email=existing_user.email,
                name=existing_user.name,
                phone=existing_user.phone
            )
        
        # Create new user
        new_user = User(
            email=user_data.email,
            name=user_data.name,
            phone=user_data.phone,
            password_hash="demo_hash"  # Hackathon için basit
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Create user totals record
        user_total = UserTotal(user_id=new_user.id)
        db.add(user_total)
        await db.commit()
        
        return UserResponse(
            user_id=str(new_user.id),
            email=new_user.email,
            name=new_user.name,
            phone=new_user.phone
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User creation failed: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Kullanıcı bilgilerini getir"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            user_id=str(user.id),
            email=user.email,
            name=user.name,
            phone=user.phone
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        ) 