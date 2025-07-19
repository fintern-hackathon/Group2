from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel
from datetime import date
from typing import List, Optional

from app.database.connection import get_db
from app.models.user import User
from app.models.suggestion import AISuggestion
from app.services.ai_service import GeminiAIService

router = APIRouter()
ai_service = GeminiAIService()

# Pydantic models
class SuggestionResponse(BaseModel):
    suggestion_id: str
    suggestion_text: str
    created_at: str

class SuggestionListItem(BaseModel):
    id: str
    text: str
    is_read: bool
    created_at: str

class SuggestionListResponse(BaseModel):
    suggestions: List[SuggestionListItem]
    unread_count: int

@router.post("/{user_id}/suggestion", response_model=SuggestionResponse)
async def generate_ai_suggestion(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """AI öneri alma"""
    try:
        # Get user financial data for AI context
        user_data = await ai_service.get_user_financial_context(db, user_id)
        
        # Generate suggestion using Gemini
        suggestion_result = await ai_service.generate_daily_suggestion(user_data)
        
        # Save suggestion to database
        new_suggestion = AISuggestion(
            user_id=user_id,
            date=date.today(),
            suggestion_text=suggestion_result['suggestion_text'],
            gemini_prompt=suggestion_result.get('prompt_used'),
            user_score_at_time=user_data.get('total_score')
        )
        
        db.add(new_suggestion)
        await db.commit()
        await db.refresh(new_suggestion)
        
        return SuggestionResponse(
            suggestion_id=str(new_suggestion.id),
            suggestion_text=new_suggestion.suggestion_text,
            created_at=new_suggestion.created_at.isoformat()
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestion: {str(e)}"
        )

@router.get("/{user_id}/suggestions", response_model=SuggestionListResponse)
async def get_user_suggestions(
    user_id: str,
    suggestion_date: Optional[date] = None,
    unread_only: bool = False,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Günlük öneriler listesi"""
    try:
        # Build query
        query = select(AISuggestion).where(AISuggestion.user_id == user_id)
        
        if suggestion_date:
            query = query.where(AISuggestion.date == suggestion_date)
        
        if unread_only:
            query = query.where(AISuggestion.is_read == False)
        
        query = query.order_by(desc(AISuggestion.created_at)).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        suggestions = result.scalars().all()
        
        # Get unread count
        unread_query = select(func.count(AISuggestion.id)).where(
            AISuggestion.user_id == user_id,
            AISuggestion.is_read == False
        )
        unread_result = await db.execute(unread_query)
        unread_count = unread_result.scalar()
        
        # Format response
        suggestion_items = [
            SuggestionListItem(
                id=str(s.id),
                text=s.suggestion_text,
                is_read=s.is_read,
                created_at=s.created_at.isoformat()
            )
            for s in suggestions
        ]
        
        return SuggestionListResponse(
            suggestions=suggestion_items,
            unread_count=unread_count or 0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )

@router.patch("/{user_id}/suggestions/{suggestion_id}/read")
async def mark_suggestion_as_read(
    user_id: str,
    suggestion_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Öneri okundu olarak işaretleme"""
    try:
        # Get suggestion
        result = await db.execute(
            select(AISuggestion).where(
                AISuggestion.id == suggestion_id,
                AISuggestion.user_id == user_id
            )
        )
        suggestion = result.scalar_one_or_none()
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )
        
        # Mark as read
        suggestion.is_read = True
        await db.commit()
        
        return {"marked_as_read": True}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark suggestion as read: {str(e)}"
        ) 