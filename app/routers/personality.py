from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.database.connection import get_db
from app.services.personality_service import PersonalityService

router = APIRouter()

class PersonalityAnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/api/v1/personality/{user_id}/analyze", response_model=PersonalityAnalysisResponse)
async def analyze_user_personality(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    🧬 Kullanıcının Financial DNA analizi yapar
    
    Hackathon-friendly: İstek geldiğinde analiz yapar
    Minimum 7 günlük veri gereklidir
    
    Returns:
    - personality_type: 'akilli_baykus', 'ozgur_kelebegi', etc.
    - personality_name: '🦉 Akıllı Baykuş'
    - confidence_score: 0.0-1.0
    - description: Kişilik açıklaması
    """
    try:
        service = PersonalityService()
        result = await service.analyze_user_personality(db, user_id)
        
        if result['success']:
            return PersonalityAnalysisResponse(
                success=True,
                data=result['data']
            )
        else:
            return PersonalityAnalysisResponse(
                success=False,
                error=result['error']
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Personality analizi hatası: {str(e)}"
        )

@router.get("/api/v1/personality/{user_id}", response_model=PersonalityAnalysisResponse)
async def get_user_personality(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    🎭 Kullanıcının mevcut Financial DNA'sını getirir
    
    Returns:
    - Mevcut personality bilgileri
    - Analysis history
    - Confidence score
    """
    try:
        service = PersonalityService()
        result = await service.get_user_personality(db, user_id)
        
        if result['success']:
            return PersonalityAnalysisResponse(
                success=True,
                data=result['data']
            )
        else:
            return PersonalityAnalysisResponse(
                success=False,
                error=result['error']
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Personality getirme hatası: {str(e)}"
        )

@router.get("/api/v1/personality/types", response_model=Dict)
async def get_personality_types():
    """
    📋 Mevcut tüm personality tiplerini listeler
    
    Returns:
    - Tüm personality tipleri
    - Descriptions
    - Traits
    """
    try:
        service = PersonalityService()
        return {
            "success": True,
            "data": service.personality_types
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Personality types listesi hatası: {str(e)}"
        ) 