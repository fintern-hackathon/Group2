#!/usr/bin/env python3
"""
🔄 MCP Client Router
Frontend → MCP Host → Gemini AI → MCP Server → Database
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, Dict, Any
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration
import requests
import os
from datetime import datetime
import time
import logging
import json

from app.database.connection import get_db
from app.mcp_server import mcp_server  # Internal call için ekle
from app.services.personality_service import PersonalityService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router setup
router = APIRouter()

# Request/Response Models
class MCPRequest(BaseModel):
    user_id: str

class MCPResponse(BaseModel):
    success: bool
    suggestion_text: Optional[str] = None
    suggestion: Optional[str] = None  # Frontend compatibility
    suggestion_id: Optional[str] = None
    user_score: Optional[float] = None
    tree_level: Optional[int] = None
    mcp_flow_status: str
    error: Optional[str] = None

# MCP Configuration
MCP_BASE_URL = "http://192.168.1.16:8006/api/v1/mcp"
GEMINI_API_KEY = "AIzaSyA5uWgtk7rejkcY5FFXITOweB_zRhJaxEY"

# Gemini AI Function Definitions (DOĞRU FORMAT)
def create_mcp_functions():
    """Gemini AI için doğru formatta function definitions oluştur"""
    return [
        FunctionDeclaration(
            name="get_user_financial_data",
            description="Kullanıcının tam finansal verilerini al (skor, gelir, gider, kategori dağılımı)",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "user_id": {
                        "type": "STRING", 
                        "description": "Kullanıcının UUID'si"
                    }
                },
                "required": ["user_id"]
            }
        ),
        FunctionDeclaration(
            name="get_user_score",
            description="Kullanıcının mevcut finansal skorunu ve ağaç seviyesini al",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "user_id": {
                        "type": "STRING", 
                        "description": "Kullanıcının UUID'si"
                    }
                },
                "required": ["user_id"]
            }
        ),
        FunctionDeclaration(
            name="get_recent_transactions", 
            description="Kullanıcının son işlemlerini ve harcama trendlerini al",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "user_id": {
                        "type": "STRING", 
                        "description": "Kullanıcının UUID'si"
                    },
                    "days": {
                        "type": "INTEGER",
                        "description": "Kaç günlük geçmişe bakılacak"
                    }
                },
                "required": ["user_id"]
            }
        ),
        FunctionDeclaration(
            name="get_spending_analysis",
            description="Detaylı harcama analizi ve kategori yüzdeleri", 
            parameters={
                "type": "OBJECT",
                "properties": {
                    "user_id": {
                        "type": "STRING",
                        "description": "Kullanıcının UUID'si"
                    }
                },
                "required": ["user_id"]
            }
        ),
        FunctionDeclaration(
            name="save_ai_suggestion",
            description="AI tarafından üretilen finansal öneriyi database'e kaydet",
            parameters={
                "type": "OBJECT", 
                "properties": {
                    "user_id": {
                        "type": "STRING",
                        "description": "Kullanıcının UUID'si"
                    },
                    "suggestion_text": {
                        "type": "STRING",
                        "description": "AI'nın ürettiği öneri metni"
                    },
                    "user_score_at_time": {
                        "type": "NUMBER",
                        "description": "Öneri anındaki kullanıcı skoru"
                    }
                },
                "required": ["user_id", "suggestion_text"]
            }
        )
    ]

# MCP Functions instance
MCP_FUNCTIONS = create_mcp_functions()

class MCPClient:
    """MCP Protocol Client - Gemini AI ile MCP Server arasında köprü"""
    
    def __init__(self):
        # Gemini AI Configuration
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',  # Stable model - proven to work
            tools=MCP_FUNCTIONS
        )
        
        # System Prompt for FinTree
        self.system_prompt = """
        🌳 FinTree Finansal Danışman Asistanısın!
        
        MCP PROTOCOL: 
        PHASE 1: Hangi verilere ihtiyacın var? MCP tool'ları çağır!
        PHASE 2: Verileri topla ve analiz et
        PHASE 3: Anlamlı finansal öneri üret
        
        AVAILABLE MCP TOOLS:
        1. get_user_financial_data - Tam finansal durum (skor, gelir, gider, kategori dağılımı)
        2. get_user_score - Sadece skor ve ağaç seviyesi  
        3. get_recent_transactions - Son harcamalar ve trendler
        4. get_spending_analysis - Detaylı harcama analizi ve yüzdeler
        
        STRATEGY:
        - İLK önce get_user_financial_data veya get_user_score çağır
        - Sonra get_recent_transactions veya get_spending_analysis çağır
        - Verileri analiz edip DETAYLI öneri üret
        
        ÖNERİ KRİTERLERİ:
        📊 Skor analizi (0-100 arası)
        🌳 Ağaç seviyesi motivasyonu (1-10 seviye)
        💰 Kategorilere özel tavsiyeler (food, transport, bills, entertainment, health, clothing)
        📈 Trend analizi (yükseliş/düşüş)
        🎯 Kısa/orta/uzun vadeli hedefler
        💡 Actionable, spesifik adımlar
        
        KONUŞMA STİLİ:
        - Türkçe ve samimi
        - Ağaç metaforları kullan 🌳🌿🌱🍃
        - Motivasyonel ama gerçekçi
        - Sayısal verilerle destekle
        - Emoji kullan ama abartma
        """

    async def call_mcp_tool(self, tool_name: str, db: AsyncSession, **kwargs) -> Dict[str, Any]:
        """MCP Server'a tool çağrısı yap (internal call)"""
        try:
            # Internal call mapping
            if tool_name == "get_user_score":
                result = await mcp_server.get_user_score(db, kwargs.get("user_id"))
            elif tool_name == "get_user_financial_data":
                result = await mcp_server.get_user_financial_data(db, kwargs.get("user_id"))
            elif tool_name == "get_recent_transactions":
                result = await mcp_server.get_recent_transactions(db, kwargs.get("user_id"), kwargs.get("days", 30))
            elif tool_name == "get_spending_analysis":
                result = await mcp_server.get_spending_analysis(db, kwargs.get("user_id"), kwargs.get("days", 30))
            elif tool_name == "save_ai_suggestion":
                from app.mcp_server import MCPSuggestionSave
                suggestion_data = MCPSuggestionSave(
                    user_id=kwargs.get("user_id"),
                    suggestion_text=kwargs.get("suggestion_text"),
                    user_score_at_time=kwargs.get("user_score_at_time")
                )
                result = await mcp_server.save_ai_suggestion(db, suggestion_data)
            else:
                return {"success": False, "error": f"Tool {tool_name} not implemented"}
            # MCPToolResponse tipinde döner, dict'e çevir
            return result.dict() if hasattr(result, 'dict') else dict(result)
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def process_mcp_request(self, user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """
        MCP Protocol Ana Akışı - FIXED VERSION
        AI çalışmazsa HATA döner, fake response YOK!
        """
        logger.info(f"🚀 STEP 1: MCP Flow Started for User: {user_id}")
        
        try:
            # Otomatik prompt oluştur
            auto_query = "Günlük finansal durumumu analiz et ve kişiselleştirilmiş öneriler ver."
            full_message = f"{self.system_prompt}\n\nKullanıcı ID: {user_id}\nİstek: {auto_query}"
            
            logger.info(f"📝 STEP 2: Auto Query Generated: {auto_query}")
            
            # STEP 2.5: Personality verisini çek
            personality_service = PersonalityService()
            personality_result = await personality_service.get_user_personality(db, user_id)
            personality_block = ""
            if personality_result.get('success') and personality_result['data']:
                pdata = personality_result['data']
                personality_block = f"""
=== KULLANICI KİŞİLİK PROFİLİ ===\n{pdata.get('personality_name', '')} (Güven: {pdata.get('confidence_score', 0):.2f})\nAçıklama: {pdata.get('description', '')}\n"""
                # AI context varsa ekle
                if pdata.get('ai_context'):
                    personality_block += f"{pdata['ai_context']}\n"
                # Öne çıkan traitleri ekle (isteğe bağlı)
                traits = pdata.get('traits', {})
                if traits:
                    # traits_json: personality tiplerine göre AI'nın kullandığı skorlar ve öne çıkan özelliklerdir.
                    personality_block += "Aşağıda kullanıcının kişilik analizine göre öne çıkan trait skorları (0-1 arası) yer almaktadır.\n"
                    trait_lines = []
                    for t_name, t_val in traits.items():
                        if isinstance(t_val, dict) and 'total_score' in t_val:
                            score = t_val['total_score']
                            trait_lines.append(f"- {t_val.get('name', t_name)}: {score:.2f}")
                        elif isinstance(t_val, (float, int)):
                            trait_lines.append(f"- {t_name}: {t_val:.2f}")
                    if trait_lines:
                        personality_block += "\n".join(trait_lines) + "\n"
                    personality_block += "Bilge Baykuş tipi kullanıcı, planlı hareket eder, uzun vadeli düşünür. Harcamalarında genellikle düzenli bir tasarruf modeli izler, riskten kaçar ve genellikle faturalar ile gıda gibi temel ihtiyaçlara odaklanır.Meşgul Sincap tipi kullanıcı, aşırı derecede tasarruf yapar ancak keyif almayı ihmal eder. Gelirinin %40’ından fazlasını biriktirir ve eğlence ya da giyim gibi alanlara çok az harcama yapar.Özgür Kelebek tipi kullanıcı, anlık kararlar alır, spontane yaşar ve hayatın tadını çıkarmayı sever. Eğlence harcamaları yüksektir ve harcama davranışları değişkendir.Sabit Kaplumbağa tipi kullanıcı, düzenli ve tutarlıdır. Harcama kalıplarında çok az değişkenlik görülür ve genellikle aynı miktarlarda harcama yapar. Değişikliklerden hoşlanmaz.Cesur Aslan tipi kullanıcı, risk almayı sever, büyük harcamalar yapar ve finansal hedeflere odaklanır. Harcamalarında büyük dalgalanmalar olabilir.Konfor Koala tipi kullanıcı, yaşam kalitesine önem verir ve rahatlığı ön planda tutar. Gıda, sağlık ve eğlence gibi alanlarda yüksek harcama eğilimindedir.Bu trait skorları, kullanıcının harcama alışkanlıklarından çıkarılan kişilik özelliklerini ve finansal davranışlarını yansıtır.\n"
            else:
                personality_block = ""

            logger.info(f"🔧 STEP 3: Personality Block: {personality_block}")
            # STEP 3: Veri toplama (AI olmadan)
            logger.info("🔧 STEP 3: Collecting user data from MCP tools...")
            
            collected_data = {}
            tools_used = []
            
            # Akıllı veri toplama - Son 30 gün odaklı
            data_collection_tools = [
                ("get_user_score", {}),  # Mevcut skor
                ("get_recent_transactions", {"days": 30}),  # Son 1 ay işlemler
                ("get_spending_analysis", {"days": 30})  # Son 1 ay analiz
            ]
            
            for tool_name, params in data_collection_tools:
                try:
                    logger.info(f"🔧 Calling {tool_name}...")
                    result = await self.call_mcp_tool(tool_name, db, user_id=user_id, **params)
                    
                    if result.get('success'):
                        collected_data[tool_name] = result.get('data', {})
                        tools_used.append(tool_name)
                        logger.info(f"✅ {tool_name}: SUCCESS")
                    else:
                        logger.warning(f"⚠️ {tool_name}: FAILED - {result.get('error', 'Unknown')}")
                        
                except Exception as e:
                    logger.error(f"❌ {tool_name}: ERROR - {e}")
            
            logger.info(f"📊 STEP 4: Data collection complete. Tools used: {tools_used}")
            
            if not collected_data:
                logger.error("❌ STEP 4: No data collected from any tool!")
                return {
                    "success": False,
                    "error": "Veri toplama başarısız. Database bağlantısı kontrol edin.",
                    "mcp_flow_status": "data_collection_failed"
                }
            
            # STEP 5: AI'ya veri ve prompt gönder (SINGLED REQUEST)
            logger.info("🤖 STEP 5: Sending data to Gemini AI...")
            
            # MOBİL BANKACILIK UYGULAMASI PROMPT
            enhanced_prompt = f"""
            Sen FinTree mobil bankacılık uygulamasının AI asistanısın. 📱🌳

=== KULLANICI KİŞİLİK PROFİLİ ===
{personality_block}

=== VERİ ANALİZİ (Son 30 gün odaklı) ===
{json.dumps(collected_data, indent=2, ensure_ascii=False)}

=== YAZIM KURALLARI ===
✅ Doğrudan kullanıcıya hitap et ("Sen", "Siz")
✅ FinTree uygulamasından bahset
✅ Kısa ve öz (20-30 kelime ideal). 30 kelimeyi asla aşmasın.
✅ Mobil ekranda rahat okunabilir
✅ Motivasyonel ve pozitif ton
✅ Spesifik sayısal öneriler ver
✅ Eylem odaklı tavsiyelerde bulun
❌ Personality isimleriyle (Cesur Aslan, Bilge Baykuş gibi) veya başka bir hitap şekliyle asla hitap etme
❌ Harcamaları artırmaya teşvik eden öneriler verme
❌ Merhaba gibi ifadeleri kullanma

=== ÇIKTI FORMATI ===
Sadece öneri metnini yaz. Başlık, açıklama vs. yok.
Örnek: "Bu ay kahve harcaman %15 arttı! ☕ Günde 2 kahve yerine 1 içersen aylık 180₺ tasarruf edebilirsin. 💰"

=== ÖZEL TALİMATLAR ===
Kullanıcının gerçek finansal verilerine ve kişilik profiline göre kişisel, spesifik ve uygulanabilir öneriler ver! 🎯
"Son 30 gün", "merhaba" veya kişilik isimleriyle (cesur aslan gibi) hitaplarda bulunma çünkü bu bir günlük tavsiye alanıdır.
Harcamaları azaltmaya, tasarruf sağlamaya ya da mevcut bütçeyi daha verimli kullanmaya yönelik pozitif öneriler sun. ✨ """
            logger.info(f"🔧 STEP 6: Enhanced Prompt: {enhanced_prompt}")
            try:
                logger.info("⏳ STEP 6: Rate limiting...")
                time.sleep(2)
                
                # TEK REQUEST - Function calling YOK
                logger.info("🤖 STEP 7: Calling Gemini AI (single request)...")
                ai_response = self.model.generate_content(enhanced_prompt)
                
                if ai_response and ai_response.text:
                    suggestion_text = ai_response.text.strip()
                    logger.info(f"✅ STEP 7: AI Response received ({len(suggestion_text)} chars)")
                    logger.info(f"📝 Preview: {suggestion_text[:100]}...")
                else:
                    logger.error("❌ STEP 7: AI returned empty response")
                    return {
                        "success": False,
                        "error": "AI boş response döndü",
                        "mcp_flow_status": "ai_empty_response"
                    }
                
            except Exception as ai_error:
                logger.error(f"❌ STEP 7: Gemini AI Error: {ai_error}")
                
                # Quota check
                if "429" in str(ai_error) or "quota" in str(ai_error).lower():
                    return {
                        "success": False,
                        "error": "Gemini API quota aşıldı",
                        "mcp_flow_status": "quota_exceeded"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"AI hatası: {str(ai_error)}",
                        "mcp_flow_status": "ai_error"
                    }
            
            # STEP 8: Öneriyi database'e kaydet
            logger.info("💾 STEP 8: Saving suggestion to database...")
            
            user_score = 0
            if 'get_user_score' in collected_data:
                user_score = collected_data['get_user_score'].get('score', 0)
            
            try:
                save_result = await self.call_mcp_tool(
                    "save_ai_suggestion",
                    db,
                    user_id=user_id,
                    suggestion_text=suggestion_text[:1000],
                    user_score_at_time=user_score
                )
                
                save_success = save_result.get('success', False)
                logger.info(f"💾 STEP 8: Save result: {save_success}")
                
            except Exception as save_error:
                logger.error(f"❌ STEP 8: Save error: {save_error}")
                save_success = False
            
            # STEP 9: Final response
            logger.info("🎉 STEP 9: MCP Flow completed successfully!")
            
            return {
                "success": True,
                "suggestion_text": suggestion_text,
                "user_score": user_score,
                "tree_level": int(user_score // 10) if user_score > 0 else 1,
                "mcp_flow_status": "completed_successfully",
                "tools_called": ", ".join(tools_used),
                "data_processed": True,
                "suggestion_saved": save_success
            }
            
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR in MCP Flow: {e}")
            return {
                "success": False,
                "error": str(e),
                "mcp_flow_status": "critical_error"
            }

# Global MCP Client instance
mcp_client = MCPClient()

# =============================================================================
# 🔄 MCP ENDPOINTS - Frontend Interface
# =============================================================================

@router.post("/daily-suggestion", response_model=MCPResponse)
async def get_daily_suggestion(
    request: MCPRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    🎯 ANA MCP ENDPOINT 
    
    Frontend sadece user_id gönderir
    MCP Protocol ile tüm akış otomatik çalışır
    
    Flow: Frontend → MCP Host → Gemini AI → MCP Server → Database → Frontend
    """
    try:
        print(f"🌳 FinTree MCP Request: {request.user_id}")
        
        # MCP Protocol Full Flow
        mcp_result = await mcp_client.process_mcp_request(user_id=request.user_id, db=db)
        
        if mcp_result.get("success"):
            suggestion_text = mcp_result.get("suggestion_text")
            return MCPResponse(
                success=True,
                suggestion_text=suggestion_text,
                suggestion=suggestion_text,  # Frontend compatibility
                user_score=mcp_result.get("user_score"),
                tree_level=int(mcp_result.get("user_score", 0) // 10) if mcp_result.get("user_score") else 1,
                mcp_flow_status=mcp_result.get("mcp_flow_status", "completed")
            )
        else:
            return MCPResponse(
                success=False,
                error=mcp_result.get("error", "Unknown MCP error"),
                mcp_flow_status="error"
            )
            
    except Exception as e:
        print(f"❌ MCP Endpoint Error: {e}")
        return MCPResponse(
            success=False,
            error=str(e),
            mcp_flow_status="endpoint_error"
        )

 