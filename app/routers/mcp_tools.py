from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.database.connection import get_db
from app.mcp_server import mcp_server, MCPSuggestionSave, MCPToolResponse

router = APIRouter()

# Request Models for MCP Tools
class MCPToolRequest(BaseModel):
    user_id: str
    parameters: Optional[Dict[str, Any]] = {}

class MCPSaveRequest(BaseModel):
    user_id: str
    suggestion_text: str
    user_score_at_time: Optional[float] = None

# MCP Tool Endpoints - Gemini AI'nın çağıracağı

@router.post("/get_user_financial_data", response_model=MCPToolResponse)
async def mcp_get_user_financial_data(
    request: MCPToolRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    MCP Tool: Kullanıcının tüm finansal verilerini getir
    
    Gemini AI bu tool'u kullanarak:
    - Kullanıcının toplam skorunu
    - Ağaç seviyesini  
    - Gelir/gider durumunu
    - Kategori bazlı harcama dağılımını öğrenir
    """
    return await mcp_server.get_user_financial_data(db, request.user_id)

@router.post("/get_user_score", response_model=MCPToolResponse)
async def mcp_get_user_score(
    request: MCPToolRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    MCP Tool: Kullanıcının sadece skor bilgilerini getir
    
    Gemini AI bu tool'u kullanarak:
    - Mevcut total skoru
    - Ağaç seviyesini
    - Sistemdeki gün sayısını öğrenir
    """
    return await mcp_server.get_user_score(db, request.user_id)

@router.post("/get_recent_transactions", response_model=MCPToolResponse)
async def mcp_get_recent_transactions(
    request: MCPToolRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    MCP Tool: Son günlerin işlemlerini getir
    
    Gemini AI bu tool'u kullanarak:
    - Son 7 günün harcamalarını
    - Harcama trendini
    - Kategori bazlı dağılımı öğrenir
    """
    days = request.parameters.get('days', 7)
    return await mcp_server.get_recent_transactions(db, request.user_id, days)

@router.post("/get_spending_analysis", response_model=MCPToolResponse)
async def mcp_get_spending_analysis(
    request: MCPToolRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    MCP Tool: Detaylı harcama analizi
    
    Gemini AI bu tool'u kullanarak:
    - Kategori bazlı yüzde dağılımları
    - Otomatik öneriler
    - Harcama paternleri hakkında bilgi alır
    """
    return await mcp_server.get_spending_analysis(db, request.user_id)

@router.post("/save_ai_suggestion", response_model=MCPToolResponse)
async def mcp_save_ai_suggestion(
    request: MCPSaveRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    MCP Tool: AI önerisini database'e kaydet
    
    Gemini AI bu tool'u kullanarak:
    - Ürettiği önerileri database'e kaydeder
    - Öneri ID'sini alır
    - Başarı durumunu kontrol eder
    """
    suggestion_data = MCPSuggestionSave(
        user_id=request.user_id,
        suggestion_text=request.suggestion_text,
        user_score_at_time=request.user_score_at_time
    )
    return await mcp_server.save_ai_suggestion(db, suggestion_data)

# MCP Info Endpoints

# Sadece temel tool endpoints kaldı - MCP Client bunları çağırır 