from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from pydantic import BaseModel
from typing import Dict, Optional

from app.database.connection import get_db, EXPENSE_CATEGORIES
from app.models.user import User
from app.models.transaction import DailyTransaction, UserTotal
from app.services.score_service import ScoreService

router = APIRouter()
score_service = ScoreService()

# Pydantic models
class UserScoreResponse(BaseModel):
    user_id: str
    total_score: float
    days_in_system: int
    total_income: float
    total_expenses: float
    savings_rate: float

class MonthlyAnalytics(BaseModel):
    year: int
    month: int
    tree_level: int
    score: float
    total_income: float
    total_expenses: float
    savings_rate: float
    category_breakdown: Dict[str, float]

@router.get("/{user_id}/score", response_model=UserScoreResponse)
async def get_user_score(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Kullanıcı skor durumu"""
    try:
        # Get user totals
        result = await db.execute(
            select(UserTotal).where(UserTotal.user_id == user_id)
        )
        user_total = result.scalar_one_or_none()
        
        if not user_total:
            # Create default user total
            user_total = UserTotal(user_id=user_id)
            db.add(user_total)
            await db.commit()
            await db.refresh(user_total)
        
        # Calculate savings rate
        savings_rate = 0.0
        if user_total.total_income > 0:
            savings_rate = (user_total.total_income - user_total.total_expenses) / user_total.total_income
        
        return UserScoreResponse(
            user_id=user_id,
            total_score=float(user_total.total_score),
            days_in_system=user_total.days_in_system,
            total_income=float(user_total.total_income),
            total_expenses=float(user_total.total_expenses),
            savings_rate=savings_rate
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user score: {str(e)}"
        )

@router.get("/{user_id}/monthly/{year}/{month}", response_model=MonthlyAnalytics)
async def get_monthly_summary(
    user_id: str,
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db)
):
    """Aylık özet"""
    try:
        # Get monthly transactions
        result = await db.execute(
            select(DailyTransaction).where(
                DailyTransaction.user_id == user_id,
                extract('year', DailyTransaction.date) == year,
                extract('month', DailyTransaction.date) == month
            )
        )
        transactions = result.scalars().all()
        
        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No transactions found for this month"
            )
        
        # Calculate monthly totals
        total_income = sum(float(t.income or 0) for t in transactions)
        total_expenses = sum(float(t.total_expenses or 0) for t in transactions)
        
        # Calculate category breakdown
        category_breakdown = {}
        for category in EXPENSE_CATEGORIES.keys():
            category_total = sum(float(getattr(t, category, 0) or 0) for t in transactions)
            category_breakdown[category] = category_total
        
        # Get current user score
        user_total_result = await db.execute(
            select(UserTotal).where(UserTotal.user_id == user_id)
        )
        user_total = user_total_result.scalar_one_or_none()
        
        current_score = 50.0  # Default
        tree_level = 1  # Default
        
        if user_total:
            current_score = float(user_total.total_score)
            tree_level = user_total.tree_level
        
        # Calculate savings rate
        savings_rate = 0.0
        if total_income > 0:
            savings_rate = (total_income - total_expenses) / total_income
        
        return MonthlyAnalytics(
            year=year,
            month=month,
            tree_level=tree_level,
            score=current_score,
            total_income=total_income,
            total_expenses=total_expenses,
            savings_rate=savings_rate,
            category_breakdown=category_breakdown
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get monthly summary: {str(e)}"
        ) 