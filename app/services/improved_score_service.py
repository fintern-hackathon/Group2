from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from app.services.score_service import ScoreService
from app.models.transaction import DailyTransaction, UserTotal

class ImprovedScoreService(ScoreService):
    """Gelişmiş skorlama servisi - mevcut servisi extend eder"""
    
    def __init__(self):
        super().__init__()
        
        # Smart kategori ağırlıkları ve impact multiplier'ları
        self.smart_weights = {
            # TEMEL İHTİYAÇLAR (düşük impact)
            'food': {
                'impact_factor': 0.7,      # %30 daha az etkili
                'is_essential': True
            },
            'bills': {
                'impact_factor': 0.5,      # %50 daha az etkili (mecburi)
                'is_essential': True
            },
            'health': {
                'impact_factor': 0.3,      # %70 daha az etkili (BONUS)
                'is_essential': True,
                'bonus_multiplier': 0.8    # Sağlık harcaması bonus
            },
            'transport': {
                'impact_factor': 0.8,      # %20 daha az etkili
                'is_essential': True
            },
            
            # İSTEĞE BAĞLI (yüksek impact)
            'entertainment': {
                'impact_factor': 1.5,      # %50 daha etkili
                'is_essential': False
            },
            'clothing': {
                'impact_factor': 1.2,      # %20 daha etkili
                'is_essential': False
            }
        }
        
        # Momentum konfigürasyonu
        self.momentum = {
            'previous_weight': 0.80,    # Önceki skorun ağırlığı
            'new_weight': 0.20,         # Yeni günün ağırlığı
            'max_daily_change': 5.0,    # Maksimum günlük değişim
            'min_daily_change': 0.3     # Minimum günlük değişim
        }

    async def update_user_score_with_momentum(self, db: AsyncSession, user_id: str) -> Tuple[float, int]:
        """Momentum ve smart weights ile skor güncelleme"""
        
        # Mevcut skoru al
        current_score = await self.get_current_user_score(db, user_id)
        
        # Base score hesapla (parent class method)
        user_data = await self.get_user_financial_data(db, user_id)
        base_new_score = self.calculate_improved_total_score(user_data)
        
        # Momentum uygula
        final_score = self.apply_momentum_smoothing(current_score, base_new_score, user_data)
        
        # Tree level hesapla
        tree_level = self.calculate_tree_level(final_score)
        
        # Database güncelle
        await self.update_database_score(db, user_id, final_score, tree_level, user_data)
        
        return final_score, tree_level

    async def get_current_user_score(self, db: AsyncSession, user_id: str) -> float:
        """Mevcut kullanıcı skorunu al"""
        result = await db.execute(
            select(UserTotal).where(UserTotal.user_id == user_id)
        )
        user_total = result.scalar_one_or_none()
        return float(user_total.total_score) if user_total else 50.0

    def calculate_improved_total_score(self, user_data: Dict) -> float:
        """Gelişmiş total skor hesaplama"""
        
        if not user_data['transactions']:
            return 50.0
        
        base_score = 50.0
        
        # 1. Smart Tasarruf Skoru (35 puan)
        savings_score = self.calculate_smart_savings_score(user_data)
        
        # 2. Smart Kategori Skoru (35 puan) 
        category_score = self.calculate_smart_category_balance_score(user_data)
        
        # 3. Gelir İstikrarı (20 puan)
        stability_score = self.calculate_income_stability_score(user_data)
        
        # 4. Süreklilik Bonusu (10 puan)
        consistency_score = self.calculate_consistency_bonus(user_data)
        
        total_score = base_score + savings_score + category_score + stability_score + consistency_score
        
        return max(0.0, min(100.0, total_score))

    def calculate_smart_category_balance_score(self, user_data: Dict) -> float:
        """Smart kategori balance scoring"""
        total_expenses = user_data['total_expenses']
        
        if total_expenses <= 0:
            return 15.0  # Neutral score
        
        score = 35.0  # Base category score
        category_totals = user_data['category_totals']
        
        # Gelir seviyesine göre tolerance
        avg_monthly_income = user_data.get('avg_monthly_income', 0)
        income_tolerance = self.get_income_tolerance_factor(avg_monthly_income)
        
        # İdeal oranlar (geliştirilmiş)
        ideal_ratios = {
            'food': 0.28,
            'transport': 0.15,
            'bills': 0.22,
            'entertainment': 0.12,
            'health': 0.13,
            'clothing': 0.10
        }
        
        for category, config in self.smart_weights.items():
            actual_amount = category_totals.get(category, 0)
            actual_ratio = actual_amount / total_expenses
            ideal_ratio = ideal_ratios.get(category, 0.10)
            impact_factor = config['impact_factor']
            
            # Ratio farkı hesapla
            ratio_diff = abs(actual_ratio - ideal_ratio)
            base_tolerance = 0.08  # %8 base tolerance
            adjusted_tolerance = base_tolerance * income_tolerance
            
            if ratio_diff > adjusted_tolerance:
                # Penalty hesapla
                excess = ratio_diff - adjusted_tolerance
                penalty = excess * 200 * impact_factor  # Penalty calculation
                
                # Special cases
                if category == 'health' and actual_ratio > ideal_ratio:
                    # Sağlık harcaması fazlaysa bonus
                    penalty *= config.get('bonus_multiplier', 1.0)
                elif category == 'entertainment' and avg_monthly_income < 15000:
                    # Düşük gelirde eğlence harcaması extra penalty
                    penalty *= 1.8
                
                score -= penalty
        
        return max(5.0, min(35.0, score))

    def calculate_smart_savings_score(self, user_data: Dict) -> float:
        """Gelişmiş tasarruf skorlaması"""
        total_income = user_data['total_income']
        total_expenses = user_data['total_expenses']
        
        if total_income <= 0:
            return 0.0
        
        savings_rate = (total_income - total_expenses) / total_income
        
        # Progressive scoring with smoother transitions
        if savings_rate >= 0.40:    return 35.0   # Excellent
        elif savings_rate >= 0.30:  return 30.0   # Great  
        elif savings_rate >= 0.20:  return 25.0   # Good
        elif savings_rate >= 0.15:  return 20.0   # Fair
        elif savings_rate >= 0.10:  return 15.0   # Acceptable
        elif savings_rate >= 0.05:  return 10.0   # Poor
        elif savings_rate >= 0:     return 5.0    # Barely positive
        elif savings_rate >= -0.05: return 0.0    # Slight deficit
        elif savings_rate >= -0.10: return -10.0  # Deficit
        else:                        return -20.0  # Major deficit

    def get_income_tolerance_factor(self, monthly_income: float) -> float:
        """Gelir seviyesine göre tolerance faktörü"""
        if monthly_income >= 25000:
            return 1.4  # Yüksek gelir = daha tolerant
        elif monthly_income >= 15000:
            return 1.2  # Orta gelir = normal tolerance
        elif monthly_income >= 8000:
            return 1.0  # Düşük gelir = standart
        else:
            return 0.8  # Çok düşük gelir = strict

    def apply_momentum_smoothing(self, current_score: float, new_score: float, user_data: Dict) -> float:
        """Momentum ile skor değişimini yumuşat"""
        
        # Weighted average
        prev_weight = self.momentum['previous_weight']
        new_weight = self.momentum['new_weight']
        
        weighted_score = (current_score * prev_weight) + (new_score * new_weight)
        
        # Change limiting
        score_change = weighted_score - current_score
        max_change = self.momentum['max_daily_change']
        min_change = self.momentum['min_daily_change']
        
        # Ani değişimleri sınırla
        if abs(score_change) > max_change:
            limited_change = max_change if score_change > 0 else -max_change
            final_score = current_score + limited_change
        elif abs(score_change) < min_change and score_change != 0:
            # Çok küçük değişimleri garanti et
            min_change_applied = min_change if score_change > 0 else -min_change
            final_score = current_score + min_change_applied
        else:
            final_score = weighted_score
        
        # Trend bonus (son hafta improve oluyorsa extra boost)
        if self.is_improving_trend(user_data):
            if score_change > 0:
                final_score += 1.0  # Improvement boost
        
        return max(0.0, min(100.0, final_score))

    def is_improving_trend(self, user_data: Dict) -> bool:
        """Son haftada improving trend var mı?"""
        transactions = user_data.get('transactions', [])
        if len(transactions) < 7:
            return False
        
        # Son 7 günün daily expense'lerini al
        recent_expenses = []
        seven_days_ago = datetime.now().date() - timedelta(days=7)
        
        for transaction in transactions:
            if hasattr(transaction, 'date') and transaction.date >= seven_days_ago:
                recent_expenses.append(float(getattr(transaction, 'total_expenses', 0) or 0))
        
        if len(recent_expenses) < 4:
            return False
        
        # Basit trend analizi: son 3 gün vs önceki 3 gün
        mid_point = len(recent_expenses) // 2
        early_avg = sum(recent_expenses[:mid_point]) / mid_point
        later_avg = sum(recent_expenses[mid_point:]) / (len(recent_expenses) - mid_point)
        
        # Expense azalıyorsa improving
        return later_avg < early_avg * 0.95  # %5 improvement threshold

    async def update_database_score(self, db: AsyncSession, user_id: str, score: float, tree_level: int, user_data: Dict):
        """Database'de skorları güncelle"""
        result = await db.execute(
            select(UserTotal).where(UserTotal.user_id == user_id)
        )
        user_total = result.scalar_one_or_none()
        
        if not user_total:
            user_total = UserTotal(user_id=user_id)
            db.add(user_total)
        
        # Update values
        user_total.total_score = score
        user_total.tree_level = tree_level
        user_total.total_income = user_data['total_income']
        user_total.total_expenses = user_data['total_expenses']
        user_total.days_in_system = user_data['days_in_system']
        
        await db.commit()

    # Debugging ve testing için
    def get_score_breakdown(self, user_data: Dict) -> Dict:
        """Skor breakdown'unu döndür (debugging için)"""
        savings_score = self.calculate_smart_savings_score(user_data)
        category_score = self.calculate_smart_category_balance_score(user_data)
        stability_score = self.calculate_income_stability_score(user_data)
        consistency_score = self.calculate_consistency_bonus(user_data)
        
        return {
            'base_score': 50.0,
            'savings_score': savings_score,
            'category_score': category_score,
            'stability_score': stability_score,
            'consistency_score': consistency_score,
            'total': 50.0 + savings_score + category_score + stability_score + consistency_score
        } 