from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date

from app.database.connection import get_db
from app.services.mcp_ai_service import MCPAIService

router = APIRouter()
mcp_ai_service = MCPAIService()

# Pydantic Models
class MCPAIRequest(BaseModel):
    user_id: str
    force_regenerate: Optional[bool] = False

class MCPAIResponse(BaseModel):
    success: bool
    suggestion_id: Optional[str] = None
    suggestion_text: Optional[str] = None
    generated_at: Optional[str] = None
    mcp_status: str
    error: Optional[str] = None

class SuggestionItem(BaseModel):
    id: str
    text: str
    date: Optional[str]
    created_at: Optional[str]
    is_read: bool

class SuggestionsResponse(BaseModel):
    suggestions: List[SuggestionItem]
    total_count: int
    mcp_status: str

# MCP AI Endpoints
@router.post("/{user_id}/generate", response_model=MCPAIResponse)
async def generate_mcp_ai_suggestion(
    user_id: str,
    force_regenerate: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    MCP üzerinden AI öneri üret
    
    Bu endpoint:
    1. prompts/ai_prompt.txt dosyasından prompt okur
    2. Kullanıcı verilerini hazırlar
    3. Gemini AI'ya istek gönderir  
    4. Sonucu database'e kaydeder
    5. MCP server için uygun formatta döner
    """
    try:
        # Check if today's suggestion already exists
        if not force_regenerate:
            existing = await mcp_ai_service.get_recent_suggestions(db, user_id, limit=1)
            if existing and existing[0]['date'] == date.today().isoformat():
                return MCPAIResponse(
                    success=True,
                    suggestion_id=existing[0]['id'],
                    suggestion_text=existing[0]['text'],
                    generated_at=existing[0]['created_at'],
                    mcp_status='existing_used'
                )
        
        # Generate new suggestion
        result = await mcp_ai_service.process_mcp_ai_request(db, user_id)
        
        return MCPAIResponse(
            success=result['success'],
            suggestion_id=result.get('suggestion_id'),
            suggestion_text=result.get('suggestion_text'),
            generated_at=result.get('generated_at'),
            mcp_status=result.get('mcp_status', 'processed'),
            error=result.get('error')
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MCP AI generation failed: {str(e)}"
        )

@router.get("/{user_id}/suggestions", response_model=SuggestionsResponse)
async def get_mcp_ai_suggestions(
    user_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    MCP için AI önerilerini getir
    
    Frontend'in bu endpoint'i kullanarak
    kullanıcının AI önerilerini çekebilir
    """
    try:
        suggestions = await mcp_ai_service.get_recent_suggestions(db, user_id, limit)
        
        suggestion_items = [
            SuggestionItem(
                id=s['id'],
                text=s['text'],
                date=s['date'],
                created_at=s['created_at'],
                is_read=s['is_read']
            )
            for s in suggestions
        ]
        
        return SuggestionsResponse(
            suggestions=suggestion_items,
            total_count=len(suggestion_items),
            mcp_status='success'
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get MCP suggestions: {str(e)}"
        )

@router.get("/prompt/status")
async def get_prompt_file_status():
    """
    Prompt dosyasının durumunu kontrol et
    
    MCP server kurulmadan önce
    prompt dosyasının var olup olmadığını kontrol eder
    """
    try:
        import os
        prompt_path = 'prompts/ai_prompt.txt'
        
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            return {
                'exists': True,
                'file_path': prompt_path,
                'content_length': len(content),
                'has_content': bool(content),
                'mcp_status': 'ready'
            }
        else:
            return {
                'exists': False,
                'file_path': prompt_path,
                'content_length': 0,
                'has_content': False,
                'mcp_status': 'waiting_for_prompt'
            }
            
    except Exception as e:
        return {
            'exists': False,
            'error': str(e),
            'mcp_status': 'error'
        }

@router.post("/prompt/create")
async def create_default_prompt():
    """
    Varsayılan prompt dosyasını oluştur
    
    Geliştiricinin prompt dosyasını manuel oluşturması
    için kullanılabilir
    """
    try:
        await mcp_ai_service._create_default_prompt_file()
        
        return {
            'success': True,
            'message': 'Default prompt file created',
            'file_path': 'prompts/ai_prompt.txt',
            'mcp_status': 'prompt_created'
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create prompt file: {str(e)}"
        )

# Health check for MCP
@router.get("/health")
async def mcp_ai_health():
    """MCP AI servisinin sağlık durumu"""
    try:
        import os
        
        # Check Gemini API key
        has_gemini_key = bool(os.getenv("GEMINI_API_KEY"))
        
        # Check prompt file
        prompt_exists = os.path.exists('prompts/ai_prompt.txt')
        
        return {
            'status': 'healthy',
            'gemini_api_configured': has_gemini_key,
            'prompt_file_exists': prompt_exists,
            'mcp_ready': has_gemini_key and prompt_exists,
            'service': 'mcp_ai_service'
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'mcp_ready': False
        } 