from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta, date
import statistics
import math

from app.models.transaction import DailyTransaction, UserTotal
from app.database.connection import EXPENSE_CATEGORIES

class AdvancedScoreService:
    def __init__(self):
        # Smart kategori ağırlıkları
        self.category_weights = {
            # TEMEL İHTİYAÇLAR (düşük ceza)
            'food': {
                'impact_multiplier': 0.7,  # Daha az etkili
                'ideal_ratio': 0.25,
                'tolerance': 0.10,
                'description': 'Temel ihtiyaç'
            },
            'bills': {
                'impact_multiplier': 0.5,  # En az etkili (mecburi)
                'ideal_ratio': 0.20,
                'tolerance': 0.05,
                'description': 'Mecburi gider'
            },
            'health': {
                'impact_multiplier': 0.4,  # Health harcaması bonus
                'ideal_ratio': 0.10,
                'tolerance': 0.15,  # Yüksek tolerans
                'description': 'Sağlık yatırımı'
            },
            'transport': {
                'impact_multiplier': 0.8,
                'ideal_ratio': 0.15,
                'tolerance': 0.08,
                'description': 'Gerekli ulaşım'
            },
            
            # İSTEĞE BAĞLI (yüksek ceza)
            'entertainment': {
                'impact_multiplier': 1.5,  # Çok etkili
                'ideal_ratio': 0.10,
                'tolerance': 0.05,
                'description': 'Eğlence harcaması'
            },
            'clothing': {
                'impact_multiplier': 1.2,
                'ideal_ratio': 0.08,
                'tolerance': 0.07,
                'description': 'Giyim harcaması'
            }
        }
        
        # Score momentum faktörleri
        self.momentum_config = {
            'previous_weight': 0.85,  # Geçmiş skorun ağırlığı
            'new_impact_weight': 0.15,  # Yeni transaction'ın ağırlığı
            'trend_multiplier': 0.1,   # Trend etkisi
            'min_change': 0.5,         # Minimum değişim
            'max_change': 8.0          # Maksimum günlük değişim
        }

    async def update_user_score_advanced(self, db: AsyncSession, user_id: str) -> Tuple[float, int]:
        """Gelişmiş skorlama algoritması"""
        
        # Mevcut skoru al
        current_score = await self.get_current_score(db, user_id)
        
        # User financial data al
        user_data = await self.get_comprehensive_user_data(db, user_id)
        
        # Yeni skor hesapla
        new_base_score = self.calculate_advanced_total_score(user_data)
        
        # Weighted update uygula
        final_score = self.apply_weighted_update(current_score, new_base_score, user_data)
        
        # Tree level hesapla
        tree_level = self.calculate_tree_level(final_score)
        
        # Database güncelle
        await self.update_user_totals(db, user_id, final_score, tree_level, user_data)
        
        return final_score, tree_level

    async def get_current_score(self, db: AsyncSession, user_id: str) -> float:
        """Mevcut kullanıcı skorunu al"""
        result = await db.execute(
            select(UserTotal).where(UserTotal.user_id == user_id)
        )
        user_total = result.scalar_one_or_none()
        return float(user_total.total_score) if user_total else 50.0

    async def get_comprehensive_user_data(self, db: AsyncSession, user_id: str) -> Dict:
        """Kapsamlı kullanıcı verisi toplama"""
        
        # Tüm transactions
        result = await db.execute(
            select(DailyTransaction)
            .where(DailyTransaction.user_id == user_id)
            .order_by(DailyTransaction.date.desc())
        )
        transactions = result.scalars().all()
        
        if not transactions:
            return self.get_empty_user_data()
        
        # Son 30 günlük data (trend analysis için)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_transactions = [t for t in transactions if t.date >= thirty_days_ago]
        
        # Son 7 günlük data (momentum için)
        seven_days_ago = datetime.now().date() - timedelta(days=7)
        weekly_transactions = [t for t in transactions if t.date >= seven_days_ago]
        
                 # Base calculations
        total_income = sum(float(t.income or 0) for t in transactions)
        total_expenses = sum(float(t.total_expenses or 0) for t in transactions)
        
        return {
            'transactions': list(transactions),
            'recent_transactions': recent_transactions,
            'weekly_transactions': weekly_transactions,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'days_in_system': len(transactions),
            'category_totals': self.calculate_category_totals(list(transactions)),
            'recent_category_totals': self.calculate_category_totals(recent_transactions),
            'weekly_spending_trend': self.calculate_weekly_trend(weekly_transactions),
            'income_stability': self.calculate_income_stability_value(list(transactions)),
            'spending_patterns': self.analyze_spending_patterns(recent_transactions)
        }

    def calculate_advanced_total_score(self, user_data: Dict) -> float:
        """Gelişmiş total skor hesaplama"""
        
        if not user_data['transactions']:
            return 50.0
        
        # Base components
        savings_score = self.calculate_advanced_savings_score(user_data)
        category_score = self.calculate_smart_category_score(user_data)
        stability_score = self.calculate_income_stability_score(user_data)
        pattern_score = self.calculate_spending_pattern_score(user_data)
        trend_score = self.calculate_trend_score(user_data)
        consistency_score = self.calculate_consistency_score(user_data)
        
        # Weighted combination
        total_score = (
            savings_score * 0.30 +      # Tasarruf %30
            category_score * 0.25 +     # Smart kategori %25
            stability_score * 0.15 +    # Gelir istikrarı %15
            pattern_score * 0.15 +      # Spending pattern %15
            trend_score * 0.10 +        # Trend momentum %10
            consistency_score * 0.05    # Süreklilik %5
        )
        
        return max(0.0, min(100.0, total_score))

    def calculate_smart_category_score(self, user_data: Dict) -> float:
        """Smart kategori skorlaması"""
        total_expenses = user_data['total_expenses']
        
        if total_expenses <= 0:
            return 50.0
        
        score = 75.0  # Base score
        category_totals = user_data['category_totals']
        
        # Income-based thresholds
        avg_monthly_income = self.calculate_avg_monthly_income(user_data)
        income_tier = self.get_income_tier(avg_monthly_income)
        
        for category, config in self.category_weights.items():
            actual_amount = category_totals.get(category, 0)
            actual_ratio = actual_amount / total_expenses
            ideal_ratio = config['ideal_ratio']
            tolerance = config['tolerance']
            impact_multiplier = config['impact_multiplier']
            
            # Income tier'a göre tolerance ayarla
            adjusted_tolerance = tolerance * income_tier['tolerance_multiplier']
            
            # Ratio difference hesapla
            ratio_diff = abs(actual_ratio - ideal_ratio)
            
            if ratio_diff > adjusted_tolerance:
                # Penalty hesapla
                excess_ratio = ratio_diff - adjusted_tolerance
                penalty = excess_ratio * 100 * impact_multiplier
                
                # Special bonuses
                if category == 'health' and actual_ratio > ideal_ratio:
                    penalty *= 0.3  # Health bonus
                elif category == 'entertainment' and avg_monthly_income < 15000:
                    penalty *= 1.5  # Low income entertainment penalty
                
                score -= penalty
        
        return max(30.0, min(100.0, score))

    def calculate_spending_pattern_score(self, user_data: Dict) -> float:
        """Spending pattern analizi"""
        patterns = user_data['spending_patterns']
        score = 50.0
        
        # Consistency bonus
        if patterns['variance_score'] < 0.3:
            score += 15.0  # Consistent spending
        elif patterns['variance_score'] > 0.7:
            score -= 10.0  # Erratic spending
        
        # Essential vs discretionary ratio
        essential_ratio = patterns['essential_ratio']
        if essential_ratio > 0.7:
            score += 10.0  # Good priority
        elif essential_ratio < 0.5:
            score -= 15.0  # Poor priority
        
        # Weekend vs weekday spending
        if patterns['weekend_multiplier'] > 2.0:
            score -= 8.0  # Excessive weekend spending
        
        return max(20.0, min(80.0, score))

    def calculate_trend_score(self, user_data: Dict) -> float:
        """Trend momentum hesaplama"""
        trend = user_data['weekly_spending_trend']
        score = 50.0
        
        # Improving trend bonus
        if trend['direction'] == 'improving':
            score += trend['strength'] * 20
        elif trend['direction'] == 'declining':
            score -= trend['strength'] * 15
        
        # Consistency in improvement
        if trend['consistency'] > 0.8:
            score += 10.0
        
        return max(20.0, min(80.0, score))

    def apply_weighted_update(self, current_score: float, new_base_score: float, user_data: Dict) -> float:
        """Ağırlıklı skor güncellemesi - ani değişimleri önler"""
        
        # Momentum config
        prev_weight = self.momentum_config['previous_weight']
        new_weight = self.momentum_config['new_impact_weight']
        max_change = self.momentum_config['max_change']
        min_change = self.momentum_config['min_change']
        
        # Base weighted score
        weighted_score = (current_score * prev_weight) + (new_base_score * new_weight)
        
        # Change limitation
        score_change = weighted_score - current_score
        
        if abs(score_change) > max_change:
            # Limit extreme changes
            score_change = max_change if score_change > 0 else -max_change
            weighted_score = current_score + score_change
        elif abs(score_change) < min_change:
            # Ensure minimum sensitivity
            score_change = min_change if new_base_score > current_score else -min_change
            weighted_score = current_score + score_change
        
        # Trend momentum
        trend = user_data['weekly_spending_trend']
        if trend['direction'] == 'improving' and score_change > 0:
            weighted_score += trend['strength'] * 2  # Boost improvement
        elif trend['direction'] == 'declining' and score_change < 0:
            weighted_score += trend['strength'] * 1  # Soften decline
        
        return max(0.0, min(100.0, weighted_score))

    # Helper methods
    def get_income_tier(self, monthly_income: float) -> Dict:
        """Gelir seviyesi tier'ını belirle"""
        if monthly_income >= 30000:
            return {'tier': 'high', 'tolerance_multiplier': 1.5}
        elif monthly_income >= 15000:
            return {'tier': 'medium', 'tolerance_multiplier': 1.2}
        else:
            return {'tier': 'low', 'tolerance_multiplier': 0.8}

    def analyze_spending_patterns(self, transactions: List) -> Dict:
        """Spending pattern analizi"""
        if not transactions:
            return {'variance_score': 0.5, 'essential_ratio': 0.7, 'weekend_multiplier': 1.0}
        
        # Variance calculation
        daily_expenses = [float(t.total_expenses or 0) for t in transactions]
        avg_expense = sum(daily_expenses) / len(daily_expenses) if daily_expenses else 0
        variance = sum((x - avg_expense) ** 2 for x in daily_expenses) / len(daily_expenses) if daily_expenses else 0
        variance_score = min(variance / (avg_expense ** 2) if avg_expense > 0 else 0, 1.0)
        
        # Essential vs discretionary
        total_expenses = sum(daily_expenses)
        essential_expenses = sum(
            float(getattr(t, cat, 0) or 0) 
            for t in transactions 
            for cat in ['food', 'bills', 'health', 'transport']
        )
        essential_ratio = essential_expenses / total_expenses if total_expenses > 0 else 0.7
        
        # Weekend spending
        weekend_expenses = [
            float(t.total_expenses or 0) for t in transactions 
            if t.date.weekday() >= 5  # Saturday, Sunday
        ]
        weekday_expenses = [
            float(t.total_expenses or 0) for t in transactions 
            if t.date.weekday() < 5
        ]
        
        weekend_avg = sum(weekend_expenses) / len(weekend_expenses) if weekend_expenses else 0
        weekday_avg = sum(weekday_expenses) / len(weekday_expenses) if weekday_expenses else 1
        weekend_multiplier = weekend_avg / weekday_avg if weekday_avg > 0 else 1.0
        
        return {
            'variance_score': variance_score,
            'essential_ratio': essential_ratio,
            'weekend_multiplier': weekend_multiplier
        }

    def calculate_weekly_trend(self, weekly_transactions: List) -> Dict:
        """Haftalık trend analizi"""
        if len(weekly_transactions) < 3:
            return {'direction': 'stable', 'strength': 0.0, 'consistency': 0.5}
        
        # Daily expenses
        daily_data = {}
        for t in weekly_transactions:
            daily_data[t.date] = float(t.total_expenses or 0)
        
        # Trend calculation
        dates = sorted(daily_data.keys())
        expenses = [daily_data[d] for d in dates]
        
        if len(expenses) < 3:
            return {'direction': 'stable', 'strength': 0.0, 'consistency': 0.5}
        
        # Linear trend
        n = len(expenses)
        x_vals = list(range(n))
        x_mean = sum(x_vals) / n
        y_mean = sum(expenses) / n
        
        numerator = sum((x_vals[i] - x_mean) * (expenses[i] - y_mean) for i in range(n))
        denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Direction and strength
        if slope < -10:  # Improving (expenses decreasing)
            direction = 'improving'
            strength = min(abs(slope) / 50, 1.0)
        elif slope > 10:  # Declining (expenses increasing)
            direction = 'declining'
            strength = min(slope / 50, 1.0)
        else:
            direction = 'stable'
            strength = 0.0
        
        # Consistency (R-squared approximation)
        y_pred = [x_mean + slope * (x - x_mean) for x in x_vals]
        ss_res = sum((expenses[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((expenses[i] - y_mean) ** 2 for i in range(n))
        consistency = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.5
        
        return {
            'direction': direction,
            'strength': strength,
            'consistency': max(0.0, min(1.0, consistency))
        }

    # Standard calculation methods (improved versions)
    def calculate_advanced_savings_score(self, user_data: Dict) -> float:
        """Gelişmiş tasarruf skorlaması"""
        total_income = user_data['total_income']
        total_expenses = user_data['total_expenses']
        
        if total_income <= 0:
            return 20.0
        
        savings_rate = (total_income - total_expenses) / total_income
        
        # Progressive scoring
        if savings_rate >= 0.5:     return 100.0  # Excellent
        elif savings_rate >= 0.4:  return 90.0   # Great
        elif savings_rate >= 0.3:  return 80.0   # Good
        elif savings_rate >= 0.2:  return 65.0   # Fair
        elif savings_rate >= 0.1:  return 50.0   # Acceptable
        elif savings_rate >= 0:    return 35.0   # Poor but positive
        elif savings_rate >= -0.1: return 20.0   # Slight overspend
        else:                       return 5.0    # Serious overspend

    # ... (diğer hesaplama methodları)

    def get_empty_user_data(self) -> Dict:
        """Boş user data"""
        return {
            'transactions': [],
            'recent_transactions': [],
            'weekly_transactions': [],
            'total_income': 0.0,
            'total_expenses': 0.0,
            'days_in_system': 0,
            'category_totals': {},
            'recent_category_totals': {},
            'weekly_spending_trend': {'direction': 'stable', 'strength': 0.0, 'consistency': 0.5},
            'income_stability': 0.5,
            'spending_patterns': {'variance_score': 0.5, 'essential_ratio': 0.7, 'weekend_multiplier': 1.0}
        }

    async def update_user_totals(self, db: AsyncSession, user_id: str, score: float, tree_level: int, user_data: Dict):
        """User totals güncelle"""
        result = await db.execute(
            select(UserTotal).where(UserTotal.user_id == user_id)
        )
        user_total = result.scalar_one_or_none()
        
        if not user_total:
            user_total = UserTotal(user_id=user_id)
            db.add(user_total)
        
                 user_total.total_score = float(score)
        user_total.tree_level = int(tree_level)
        user_total.total_income = float(user_data['total_income'])
        user_total.total_expenses = float(user_data['total_expenses'])
        user_total.days_in_system = int(user_data['days_in_system'])
        
        await db.commit()

    def calculate_tree_level(self, score: float) -> int:
        """Tree level hesaplama"""
        return max(1, min(10, int(score / 10) + 1))

    def calculate_category_totals(self, transactions: List) -> Dict:
        """Kategori totalları"""
        totals = {}
        for category in self.category_weights.keys():
            totals[category] = sum(float(getattr(t, category, 0) or 0) for t in transactions)
        return totals

    def calculate_avg_monthly_income(self, user_data: Dict) -> float:
        """Ortalama aylık gelir"""
        transactions = user_data['transactions']
        if not transactions:
            return 0.0
        
        monthly_incomes = {}
        for t in transactions:
            month_key = f"{t.date.year}-{t.date.month:02d}"
            if month_key not in monthly_incomes:
                monthly_incomes[month_key] = 0.0
            monthly_incomes[month_key] += float(t.income or 0)
        
        return sum(monthly_incomes.values()) / len(monthly_incomes) if monthly_incomes else 0.0

    def calculate_income_stability_score(self, user_data: Dict) -> float:
        """Gelir istikrarı skoru"""
        stability_value = user_data.get('income_stability', 0.5)
        
        # Stability value'yu score'a çevir (0-1 range'den 0-100'e)
        if stability_value >= 0.9:
            return 80.0
        elif stability_value >= 0.7:
            return 65.0
        elif stability_value >= 0.5:
            return 50.0
        elif stability_value >= 0.3:
            return 35.0
        else:
            return 20.0

    def calculate_income_stability_value(self, transactions: List) -> float:
        """Gelir istikrarı değeri hesapla (0-1 range)"""
        if len(transactions) < 2:
            return 0.7  # Default for new users
        
        # Monthly income'ları hesapla
        monthly_incomes = {}
        for t in transactions:
            month_key = f"{t.date.year}-{t.date.month:02d}"
            if month_key not in monthly_incomes:
                monthly_incomes[month_key] = 0.0
            monthly_incomes[month_key] += float(t.income or 0)
        
        if len(monthly_incomes) < 2:
            return 0.7
        
        income_values = list(monthly_incomes.values())
        avg_income = sum(income_values) / len(income_values)
        
        if avg_income == 0:
            return 0.3
        
        # Coefficient of variation hesapla
        variance = sum((x - avg_income) ** 2 for x in income_values) / len(income_values)
        cv = (variance ** 0.5) / avg_income
        
        # CV'yi 0-1 stability score'a çevir
        if cv < 0.1:
            return 0.95
        elif cv < 0.2:
            return 0.8
        elif cv < 0.4:
            return 0.6
        elif cv < 0.6:
            return 0.4
        else:
            return 0.2

    def calculate_consistency_score(self, user_data: Dict) -> float:
        """Süreklilik skoru"""
        days = user_data['days_in_system']
        if days >= 30: return 80.0
        elif days >= 14: return 60.0
        elif days >= 7: return 40.0
        else: return 20.0 