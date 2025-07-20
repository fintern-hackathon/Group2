import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Optional, List
import os
from datetime import datetime, date
import asyncio
import json

from app.models.suggestion import AISuggestion
from app.models.transaction import UserTotal, DailyTransaction

class MCPAIService:
    """MCP Server entegrasyonu için AI servisi"""
    
    def __init__(self):
        # Gemini API setup
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None
        
        # MCP configuration
        self.mcp_config = {
            'prompt_file_path': 'prompts/ai_prompt.txt',
            'max_retries': 3,
            'timeout': 30,
            'backup_prompt': self._get_backup_prompt()
        }

    async def process_mcp_ai_request(self, db: AsyncSession, user_id: str) -> Dict:
        """MCP üzerinden AI isteği işle"""
        try:
            # 1. Prompt dosyasından prompt oku
            prompt_content = await self._read_prompt_file()
            
            # 2. Kullanıcı verilerini hazırla
            user_context = await self._prepare_user_context(db, user_id)
            
            # 3. Gemini'ye istek at
            ai_response = await self._call_gemini_with_context(prompt_content, user_context)
            
            # 4. Sonucu database'e kaydet
            suggestion_record = await self._save_ai_suggestion(db, user_id, ai_response, prompt_content)
            
            return {
                'success': True,
                'suggestion_id': suggestion_record.id,
                'suggestion_text': ai_response['suggestion_text'],
                'generated_at': suggestion_record.created_at.isoformat(),
                'mcp_status': 'processed'
            }
            
        except Exception as e:
            print(f"MCP AI Service Error: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_used': True,
                'mcp_status': 'failed'
            }

    async def _read_prompt_file(self) -> str:
        """Prompt dosyasını oku"""
        try:
            # Prompt dosyası yoksa oluştur
            if not os.path.exists(self.mcp_config['prompt_file_path']):
                await self._create_default_prompt_file()
            
            with open(self.mcp_config['prompt_file_path'], 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if not content:
                return self.mcp_config['backup_prompt']
                
            return content
            
        except Exception as e:
            print(f"Prompt file read error: {e}")
            return self.mcp_config['backup_prompt']

    async def _create_default_prompt_file(self):
        """Varsayılan prompt dosyası oluştur"""
        os.makedirs(os.path.dirname(self.mcp_config['prompt_file_path']), exist_ok=True)
        
        default_prompt = """
Finansal danışman asistanı olarak davran. Kullanıcının finansal ağacını büyütmesine yardım et.

Kullanıcı Verileri:
- Toplam Skor: {total_score}/100
- Ağaç Seviyesi: {tree_level}/10
- Günlerdeki Durumu: {days_in_system} gün
- Tasarruf Oranı: %{savings_rate}
- Aylık Ortalama Gelir: {avg_monthly_income:.0f} TL

Son Harcama Verileri:
{spending_summary}

Lütfen:
1. Kullanıcının durumunu kısaca değerlendir
2. Bir sonraki hafta için pratik tavsiye ver  
3. Ağacının durumunu emoji ile göster
4. Motivasyonel ve samimi ol

Maksimum 150 kelime, Türkçe yaz.
        """.strip()
        
        with open(self.mcp_config['prompt_file_path'], 'w', encoding='utf-8') as f:
            f.write(default_prompt)

    async def _prepare_user_context(self, db: AsyncSession, user_id: str) -> Dict:
        """Kullanıcı context verilerini hazırla"""
        
        # User total score
        result = await db.execute(
            select(UserTotal).where(UserTotal.user_id == user_id)
        )
        user_total = result.scalar_one_or_none()
        
        # Recent transactions (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.now().date() - timedelta(days=7)
        recent_result = await db.execute(
            select(DailyTransaction).where(
                DailyTransaction.user_id == user_id,
                DailyTransaction.date >= seven_days_ago
            )
        )
        recent_transactions = recent_result.scalars().all()
        
        # Calculate context data
        context = {
            'total_score': float(user_total.total_score) if user_total else 50.0,
            'tree_level': user_total.tree_level if user_total else 1,
            'days_in_system': user_total.days_in_system if user_total else 0,
            'avg_monthly_income': float(user_total.total_income or 0) / max(1, (user_total.days_in_system or 1) / 30),
            'savings_rate': 0.0,
            'spending_summary': ''
        }
        
        # Calculate savings rate
        if user_total and user_total.total_income and user_total.total_expenses:
            total_income = float(user_total.total_income)
            total_expenses = float(user_total.total_expenses)
            if total_income > 0:
                context['savings_rate'] = ((total_income - total_expenses) / total_income) * 100
        
        # Recent spending summary
        if recent_transactions:
            categories = ['food', 'transport', 'bills', 'entertainment', 'health', 'clothing']
            spending_lines = []
            for category in categories:
                total = sum(float(getattr(t, category, 0) or 0) for t in recent_transactions)
                if total > 0:
                    spending_lines.append(f"- {category.title()}: {total:.0f} TL")
            context['spending_summary'] = '\n'.join(spending_lines) if spending_lines else "Henüz harcama verisi yok"
        else:
            context['spending_summary'] = "Son 7 günde işlem yok"
            
        return context

    async def _call_gemini_with_context(self, prompt_template: str, context: Dict) -> Dict:
        """Gemini'yi context ile çağır"""
        
        if self.model is None:
            return self._get_fallback_response(context)
        
        try:
            # Format prompt with context data
            formatted_prompt = prompt_template.format(**context)
            
            # Call Gemini
            response = await self.model.generate_content_async(formatted_prompt)
            
            return {
                'suggestion_text': response.text,
                'prompt_used': formatted_prompt,
                'model_response': response.text,
                'source': 'gemini'
            }
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._get_fallback_response(context)

    async def _save_ai_suggestion(self, db: AsyncSession, user_id: str, ai_response: Dict, prompt_content: str) -> AISuggestion:
        """AI sonucunu database'e kaydet"""
        
        suggestion = AISuggestion(
            user_id=user_id,
            date=date.today(),
            suggestion_text=ai_response['suggestion_text'],
            gemini_prompt=prompt_content,
            user_score_at_time=None  # MCP context'ten alınabilir
        )
        
        db.add(suggestion)
        await db.commit()
        await db.refresh(suggestion)
        
        return suggestion

    def _get_backup_prompt(self) -> str:
        """Yedek prompt döndür"""
        return """
Finansal danışman asistanı olarak kullanıcının durumunu değerlendir:

Skor: {total_score}/100
Ağaç Seviyesi: {tree_level}/10
Sistem: {days_in_system} gün
Tasarruf: %{savings_rate}
Gelir: {avg_monthly_income:.0f} TL/ay

Son Harcamalar:
{spending_summary}

Kısa değerlendirme ve tavsiye ver (max 150 kelime, Türkçe).
        """.strip()

    def _get_fallback_response(self, context: Dict) -> Dict:
        """AI çalışmazsa fallback response"""
        score = context['total_score']
        
        if score >= 70:
            text = f"🌳 Harika! Skorunuz {score:.1f}. Ağacınız güçlü büyüyor! Bu tempoda devam edin."
        elif score >= 50:
            text = f"🌿 Skorunuz {score:.1f}. Ağacınız büyüyor ama daha da iyileştirebiliriz!"
        else:
            text = f"🌱 Dikkat! Skorunuz {score:.1f}. Ağacınız solmaya başlıyor, harcamalarınızı gözden geçirin."
        
        return {
            'suggestion_text': text,
            'prompt_used': 'fallback',
            'model_response': text,
            'source': 'fallback'
        }

    async def get_recent_suggestions(self, db: AsyncSession, user_id: str, limit: int = 5) -> List[Dict]:
        """Son AI önerilerini getir (MCP endpoint için)"""
        
        from sqlalchemy import desc
        
        result = await db.execute(
            select(AISuggestion)
            .where(AISuggestion.user_id == user_id)
            .order_by(desc(AISuggestion.created_at))
            .limit(limit)
        )
        
        suggestions = result.scalars().all()
        
        return [
            {
                'id': s.id,
                'text': s.suggestion_text,
                'date': s.date.isoformat() if s.date else None,
                'created_at': s.created_at.isoformat() if s.created_at else None,
                'is_read': s.is_read
            }
            for s in suggestions
        ] 