import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List
import os
from datetime import datetime, timedelta

from app.models.transaction import DailyTransaction, UserTotal
from app.services.score_service import ScoreService

class GeminiAIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None
        
        self.score_service = ScoreService()

    async def get_user_financial_context(self, db: AsyncSession, user_id: str) -> Dict:
        """Kullanıcının finansal durumunu AI için hazırla"""
        
        # Get user total score
        result = await db.execute(
            select(UserTotal).where(UserTotal.user_id == user_id)
        )
        user_total = result.scalar_one_or_none()
        
        # Get last 7 days transactions for weekly average
        seven_days_ago = datetime.now().date() - timedelta(days=7)
        recent_result = await db.execute(
            select(DailyTransaction).where(
                DailyTransaction.user_id == user_id,
                DailyTransaction.date >= seven_days_ago
            )
        )
        recent_transactions = recent_result.scalars().all()
        
        # Calculate weekly averages
        weekly_avg = {
            'food': 0.0, 'transport': 0.0, 'bills': 0.0,
            'entertainment': 0.0, 'health': 0.0, 'clothing': 0.0
        }
        
        if recent_transactions:
            for category in weekly_avg.keys():
                category_total = sum(float(getattr(t, category, 0) or 0) for t in recent_transactions)
                weekly_avg[category] = category_total / len(recent_transactions)
        
        # Get full financial data
        user_data = await self.score_service.get_user_financial_data(db, user_id)
        
        context = {
            'days_in_system': user_data['days_in_system'],
            'total_score': float(user_total.total_score) if user_total else 50.0,
            'tree_level': user_total.tree_level if user_total else 1,
            'savings_rate': 0.0,
            'avg_monthly_income': user_data['avg_monthly_income'],
            'weekly_avg': weekly_avg
        }
        
        # Calculate savings rate
        if user_data['total_income'] > 0:
            context['savings_rate'] = (user_data['total_income'] - user_data['total_expenses']) / user_data['total_income']
        
        return context

    def build_daily_suggestion_prompt(self, user_data: Dict) -> str:
        """Günlük öneri prompt'u"""
        prompt = f"""
        Sen bir finansal danışman asistanısın. Kullanıcının finansal ağacını büyütmesine yardım ediyorsun.
        
        Kullanıcı Bilgileri:
        - Sistemde {user_data['days_in_system']} gündür
        - Mevcut skor: {user_data['total_score']}/100
        - Ağaç seviyesi: {user_data['tree_level']}/10
        - Toplam tasarruf oranı: %{user_data['savings_rate'] * 100:.1f}
        - Aylık ortalama gelir: {user_data['avg_monthly_income']:.0f} TL
        
        Son 7 günlük harcama ortalaması:
        - Yemek: {user_data['weekly_avg']['food']:.0f} TL
        - Ulaşım: {user_data['weekly_avg']['transport']:.0f} TL
        - Faturalar: {user_data['weekly_avg']['bills']:.0f} TL
        - Eğlence: {user_data['weekly_avg']['entertainment']:.0f} TL
        - Sağlık: {user_data['weekly_avg']['health']:.0f} TL
        - Giyim: {user_data['weekly_avg']['clothing']:.0f} TL
        
        Lütfen kullanıcıya:
        1. Genel durumu hakkında kısa yorum yap
        2. Bir sonraki hafta için pratik bir tavsiye ver
        3. Ağacının durumunu emoji ile ifade et
        4. Motivasyonel ve samimi ol
        
        Maksimum 150 kelime, Türkçe yazmaını istiyorum.
        """
        return prompt

    async def generate_daily_suggestion(self, user_data: Dict) -> Dict:
        """Günlük öneri üretme"""
        try:
            if self.model is None:
                return self._get_fallback_suggestion(user_data)
            
            prompt = self.build_daily_suggestion_prompt(user_data)
            response = await self.model.generate_content_async(prompt)
            
            return {
                'suggestion_text': response.text,
                'prompt_used': prompt,
                'response_raw': response.text
            }
            
        except Exception as e:
            print(f"Gemini AI error: {e}")
            return self._get_fallback_suggestion(user_data)

    def _get_fallback_suggestion(self, user_data: Dict) -> Dict:
        """AI hata durumunda varsayılan öneri"""
        score = user_data['total_score']
        
        if score >= 70:
            text = f"Harika gidiyorsun! Skorun {score:.1f}. Ağacın güçleneye devam ediyor 🌳💪"
        elif score >= 50:
            text = f"Ortalama bir durum. Skorun {score:.1f}. Biraz daha dikkatli olursan ağacın büyüyecek! 🌳😊"
        else:
            text = f"Dikkat et! Skorun {score:.1f}. Ağacın solmaya başlıyor. Harcamalarını gözden geçir! 🌳😟"
        
        return {
            'suggestion_text': text,
            'prompt_used': 'fallback',
            'response_raw': text
        } 