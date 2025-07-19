from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import date
from typing import Optional
from sqlalchemy import select

from app.database.connection import get_db
from app.models.user import User
from app.models.transaction import DailyTransaction
from app.services.score_service import ScoreService

router = APIRouter()
score_service = ScoreService()

# Pydantic models
class DailyTransactionCreate(BaseModel):
    date: date
    income: float = 0.0
    food: float = 0.0
    transport: float = 0.0
    bills: float = 0.0
    entertainment: float = 0.0
    health: float = 0.0
    clothing: float = 0.0

class DailyTransactionResponse(BaseModel):
    transaction_id: str
    total_expenses: float
    net_balance: float
    new_total_score: float
    tree_level: int
    message: str

@router.post("/{user_id}/daily", response_model=DailyTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_daily_transaction(
    user_id: str,
    transaction_data: DailyTransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Günlük işlem ekleme"""
    try:
        # Check if transaction already exists for this date
        existing_transaction = await db.execute(
            select(DailyTransaction).where(
                DailyTransaction.user_id == user_id,
                DailyTransaction.date == transaction_data.date
            )
        )
        existing = existing_transaction.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction already exists for this date"
            )
        
        # Create new transaction
        new_transaction = DailyTransaction(
            user_id=user_id,
            date=transaction_data.date,
            income=transaction_data.income,
            food=transaction_data.food,
            transport=transaction_data.transport,
            bills=transaction_data.bills,
            entertainment=transaction_data.entertainment,
            health=transaction_data.health,
            clothing=transaction_data.clothing
        )
        
        # Calculate totals
        new_transaction.calculate_totals()
        
        # Save to database
        db.add(new_transaction)
        await db.commit()
        await db.refresh(new_transaction)
        
        # Update user total score with improved algorithm
        try:
            from app.services.improved_score_service import ImprovedScoreService
            improved_service = ImprovedScoreService()
            new_total_score, tree_level = await improved_service.update_user_score_with_momentum(db, user_id)
        except Exception as e:
            # Fallback to standard scoring
            new_total_score, tree_level = await score_service.update_user_score(db, user_id)
        
        return DailyTransactionResponse(
            transaction_id=str(new_transaction.id),
            total_expenses=float(new_transaction.total_expenses),
            net_balance=float(new_transaction.net_balance),
            new_total_score=new_total_score,
            tree_level=tree_level,
            message="Transaction recorded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create transaction: {str(e)}"
        ) 