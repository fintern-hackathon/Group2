from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import statistics

from app.models.transaction import DailyTransaction, UserTotal
from app.database.connection import EXPENSE_CATEGORIES

class ScoreService:
    def __init__(self):
        pass

    async def update_user_score(self, db: AsyncSession, user_id: str) -> Tuple[float, int]:
        """Kullanıcının total skorunu güncelle"""
        
        # Get user financial data
        user_data = await self.get_user_financial_data(db, user_id)
        
        # Calculate total score
        total_score = self.calculate_total_score(user_data)
        
        # Calculate tree level
        tree_level = self.calculate_tree_level(total_score)
        
        # Update user totals
        result = await db.execute(
            select(UserTotal).where(UserTotal.user_id == user_id)
        )
        user_total = result.scalar_one_or_none()
        
        if not user_total:
            user_total = UserTotal(user_id=user_id)
            db.add(user_total)
        
        user_total.total_score = total_score
        user_total.tree_level = tree_level
        user_total.total_income = user_data['total_income']
        user_total.total_expenses = user_data['total_expenses']
        user_total.days_in_system = user_data['days_in_system']
        
        await db.commit()
        
        return total_score, tree_level

    async def get_user_financial_data(self, db: AsyncSession, user_id: str) -> Dict:
        """Kullanıcının finansal verilerini topla"""
        
        # Get all transactions
        result = await db.execute(
            select(DailyTransaction).where(DailyTransaction.user_id == user_id)
        )
        transactions = result.scalars().all()
        
        if not transactions:
            return {
                'transactions': [],
                'total_income': 0.0,
                'total_expenses': 0.0,
                'days_in_system': 0,
                'category_totals': {},
                'monthly_incomes': [],
                'avg_monthly_income': 0.0
            }
        
        # Calculate totals
        total_income = sum(float(t.income or 0) for t in transactions)
        total_expenses = sum(float(t.total_expenses or 0) for t in transactions)
        
        # Calculate category totals
        category_totals = {}
        for category in EXPENSE_CATEGORIES.keys():
            category_total = sum(float(getattr(t, category, 0) or 0) for t in transactions)
            category_totals[category] = category_total
        
        # Calculate monthly incomes (for stability calculation)
        monthly_incomes = {}
        for transaction in transactions:
            month_key = f"{transaction.date.year}-{transaction.date.month:02d}"
            if month_key not in monthly_incomes:
                monthly_incomes[month_key] = 0.0
            monthly_incomes[month_key] += float(transaction.income or 0)
        
        monthly_income_list = list(monthly_incomes.values())
        avg_monthly_income = sum(monthly_income_list) / len(monthly_income_list) if monthly_income_list else 0.0
        
        return {
            'transactions': transactions,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'days_in_system': len(transactions),
            'category_totals': category_totals,
            'monthly_incomes': monthly_income_list,
            'avg_monthly_income': avg_monthly_income
        }

    def calculate_total_score(self, user_data: Dict) -> float:
        """Total skor hesaplama algoritması"""
        
        if not user_data['transactions']:
            return 50.0  # Başlangıç skoru
        
        base_score = 50.0
        
        # 1. Tasarruf Oranı Skoru (40 puan)
        savings_score = self.calculate_savings_score(user_data)
        
        # 2. Kategori Dengesi Skoru (30 puan)
        balance_score = self.calculate_category_balance_score(user_data)
        
        # 3. Gelir İstikrarı Skoru (20 puan)
        stability_score = self.calculate_income_stability_score(user_data)
        
        # 4. Süreklilik Bonusu (10 puan)
        consistency_bonus = self.calculate_consistency_bonus(user_data)
        
        total_score = base_score + savings_score + balance_score + stability_score + consistency_bonus
        
        return max(0.0, min(100.0, total_score))

    def calculate_savings_score(self, user_data: Dict) -> float:
        """Tasarruf oranı skoru (40 puan)"""
        total_income = user_data['total_income']
        total_expenses = user_data['total_expenses']
        
        if total_income <= 0:
            return -20.0
        
        savings_rate = (total_income - total_expenses) / total_income
        
        if savings_rate >= 0.4:      # %40+ tasarruf
            return 40.0
        elif savings_rate >= 0.3:    # %30-40 tasarruf
            return 30.0
        elif savings_rate >= 0.2:    # %20-30 tasarruf
            return 20.0
        elif savings_rate >= 0.1:    # %10-20 tasarruf
            return 10.0
        elif savings_rate >= 0:      # Pozitif
            return 0.0
        else:                        # Negatif
            return -20.0

    def calculate_category_balance_score(self, user_data: Dict) -> float:
        """Kategori dengesi skoru (30 puan)"""
        total_expenses = user_data['total_expenses']
        
        if total_expenses <= 0:
            return 0.0
        
        # İdeal kategoriler ve oranları
        ideal_ratios = {
            'food': 0.30,
            'transport': 0.15,
            'bills': 0.25,
            'entertainment': 0.10,
            'health': 0.15,
            'clothing': 0.05
        }
        
        score = 30.0
        category_totals = user_data['category_totals']
        
        for category, ideal_ratio in ideal_ratios.items():
            actual_amount = category_totals.get(category, 0)
            actual_ratio = actual_amount / total_expenses
            ratio_diff = abs(actual_ratio - ideal_ratio)
            
            # Gelir seviyesine göre esneklik
            income_factor = min(user_data['avg_monthly_income'] / 15000, 2.0)  # 15K TL baz
            
            # Eğlence harcaması gelire göre değerlendir
            if category == 'entertainment' and user_data['avg_monthly_income'] > 20000:
                # Yüksek gelirli için eğlence harcaması daha tolere edilebilir
                ratio_diff *= 0.7
            
            # Sapma cezası
            if ratio_diff > 0.15:
                score -= (8.0 / income_factor)
            elif ratio_diff > 0.10:
                score -= (5.0 / income_factor)
            elif ratio_diff > 0.05:
                score -= (2.0 / income_factor)
        
        return max(-15.0, score)

    def calculate_income_stability_score(self, user_data: Dict) -> float:
        """Gelir istikrarı skoru (20 puan)"""
        monthly_incomes = user_data['monthly_incomes']
        
        if len(monthly_incomes) < 2:
            return 10.0  # İlk aylar için bonus
        
        # Aylık gelir varyasyonunu hesapla
        avg_income = sum(monthly_incomes) / len(monthly_incomes)
        if avg_income == 0:
            return 5.0
        
        variance = sum((x - avg_income) ** 2 for x in monthly_incomes) / len(monthly_incomes)
        cv = (variance ** 0.5) / avg_income  # Coefficient of variation
        
        if cv < 0.1:      # %10'dan az varyasyon
            return 20.0
        elif cv < 0.2:    # %20'den az varyasyon
            return 15.0
        elif cv < 0.4:    # %40'tan az varyasyon
            return 10.0
        else:             # Yüksek varyasyon
            return 5.0

    def calculate_consistency_bonus(self, user_data: Dict) -> float:
        """Süreklilik bonusu (10 puan)"""
        days_in_system = user_data['days_in_system']
        
        # Günlük veri girme sürekliliği
        if days_in_system >= 30:
            return 10.0
        elif days_in_system >= 14:
            return 7.0
        elif days_in_system >= 7:
            return 5.0
        else:
            return 2.0

    def calculate_tree_level(self, total_score: float) -> int:
        """Ağaç seviyesi belirleme (1-10)"""
        if total_score >= 95:   return 10  # Legendary Tree 🌳✨
        elif total_score >= 90: return 9   # Master Tree 🌳👑
        elif total_score >= 80: return 8   # Expert Tree 🌳🏆
        elif total_score >= 70: return 7   # Advanced Tree 🌳💪
        elif total_score >= 60: return 6   # Good Tree 🌳😊
        elif total_score >= 50: return 5   # Average Tree 🌳😐
        elif total_score >= 40: return 4   # Weak Tree 🌳😟
        elif total_score >= 30: return 3   # Sick Tree 🌳🤒
        elif total_score >= 20: return 2   # Dying Tree 🌳💀
        else:                   return 1   # Dead Tree 🪦

    def get_tree_visual_data(self, tree_level: int) -> Dict[str, str]:
        """Ağaç görsel verisi"""
        visual_data = {
            10: {"emoji": "🌳✨", "color": "#00FF00", "description": "Efsanevi Ağaç"},
            9:  {"emoji": "🌳👑", "color": "#32CD32", "description": "Usta Ağaç"},
            8:  {"emoji": "🌳🏆", "color": "#228B22", "description": "Uzman Ağaç"},
            7:  {"emoji": "🌳💪", "color": "#90EE90", "description": "Güçlü Ağaç"},
            6:  {"emoji": "🌳😊", "color": "#98FB98", "description": "İyi Ağaç"},
            5:  {"emoji": "🌳😐", "color": "#ADFF2F", "description": "Ortalama Ağaç"},
            4:  {"emoji": "🌳😟", "color": "#FFFF00", "description": "Zayıf Ağaç"},
            3:  {"emoji": "🌳🤒", "color": "#FFA500", "description": "Hasta Ağaç"},
            2:  {"emoji": "🌳💀", "color": "#FF4500", "description": "Ölmekte Olan Ağaç"},
            1:  {"emoji": "🪦", "color": "#8B4513", "description": "Ölü Ağaç"}
        }
        return visual_data.get(tree_level, visual_data[1]) 