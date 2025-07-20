from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import statistics
import math

from app.models.personality import UserFinancialPersonality
from app.models.transaction import DailyTransaction
from app.database.connection import EXPENSE_CATEGORIES

class PersonalityService:
    """Financial Personality Analysis Service"""
    
    def __init__(self):
        # Kişilik tipleri ve özellikleri
        self.personality_types = {
            'akilli_baykus': {
                'name': '🦉 Akıllı Baykuş',
                'description': 'Planlı, uzun vadeli düşünen, güvenli adımlar',
                'traits': {
                    'planning_score': {'min': 0.7, 'weight': 0.3},
                    'savings_consistency': {'min': 0.6, 'weight': 0.25},
                    'risk_aversion': {'min': 0.7, 'weight': 0.2},
                    'essential_focus': {'min': 0.6, 'weight': 0.15},
                    'variance_low': {'max': 0.3, 'weight': 0.1}
                }
            },
            'caliskan_sincap': {
                'name': '🐿️ Çalışkan Sincap',
                'description': 'Çok biriktiren ama kendine harcamayı unutan',
                'traits': {
                    'high_savings': {'min': 0.4, 'weight': 0.4},
                    'low_entertainment': {'max': 0.08, 'weight': 0.25},
                    'low_clothing': {'max': 0.05, 'weight': 0.15},
                    'consistency_high': {'min': 0.7, 'weight': 0.15},
                    'essential_only': {'min': 0.8, 'weight': 0.05}
                }
            },
            'ozgur_kelebegi': {
                'name': '🦋 Özgür Kelebeği',
                'description': 'Spontan, keyifli, anlık harcama kararları',
                'traits': {
                    'high_entertainment': {'min': 0.15, 'weight': 0.3},
                    'high_variance': {'min': 0.4, 'weight': 0.25},
                    'weekend_multiplier': {'min': 1.8, 'weight': 0.2},
                    'spontaneous_spending': {'min': 0.6, 'weight': 0.15},
                    'flexible_budget': {'min': 0.5, 'weight': 0.1}
                }
            },
            'sabit_kaplumbaga': {
                'name': '🐢 Sabit Kaplumbağa',
                'description': 'Tutarlı, değişimi sevmeyen, düzenli',
                'traits': {
                    'ultra_consistency': {'min': 0.8, 'weight': 0.4},
                    'low_variance': {'max': 0.2, 'weight': 0.25},
                    'routine_spending': {'min': 0.7, 'weight': 0.2},
                    'stable_categories': {'min': 0.8, 'weight': 0.1},
                    'predictable_timing': {'min': 0.7, 'weight': 0.05}
                }
            },
            'cesur_aslan': {
                'name': '🦁 Cesur Aslan',
                'description': 'Risk alan, büyük hedefli, cesur harcamalar',
                'traits': {
                    'high_variance': {'min': 0.6, 'weight': 0.3},
                    'big_transactions': {'min': 0.5, 'weight': 0.25},
                    'risk_taking': {'min': 0.6, 'weight': 0.2},
                    'goal_oriented': {'min': 0.6, 'weight': 0.15},
                    'bold_categories': {'min': 0.4, 'weight': 0.1}
                }
            },
            'konfor_koala': {
                'name': '🐨 Konfor Koala',
                'description': 'Konforu seven, yaşam kalitesi odaklı',
                'traits': {
                    'high_food': {'min': 0.25, 'weight': 0.25},
                    'high_health': {'min': 0.12, 'weight': 0.2},
                    'comfort_spending': {'min': 0.6, 'weight': 0.2},
                    'quality_over_quantity': {'min': 0.5, 'weight': 0.2},
                    'lifestyle_focus': {'min': 0.6, 'weight': 0.15}
                }
            }
        }

    async def analyze_user_personality(self, db: AsyncSession, user_id: str) -> Dict:
        """Kullanıcının financial personality'sini analiz et"""
        
        # Mevcut personality kaydını al
        existing = await self.get_existing_personality(db, user_id)
        
        # User transaction data al
        user_data = await self.get_user_transaction_data(db, user_id)
        
        # DEBUG: Transaction sayısını logla
        transaction_count = len(user_data['transactions']) if user_data['transactions'] else 0
        print(f"🔍 DEBUG: User {user_id} için {transaction_count} transaction bulundu")
        
        if not user_data['transactions'] or len(user_data['transactions']) < 7:
            return {
                'success': False,
                'error': f'Personality analizi için en az 7 günlük veri gerekli (şu an: {transaction_count})',
                'data': None
            }
        
        # Pattern analysis yap
        patterns = self.calculate_spending_patterns(user_data)
        
        # Personality scoring
        personality_scores = self.calculate_personality_scores(patterns)
        
        # En yüksek skorlu personality'yi seç
        best_personality = max(personality_scores.items(), key=lambda x: x[1]['total_score'])
        personality_type = best_personality[0]
        confidence = best_personality[1]['total_score']
        
        # Database güncelle
        await self.update_personality_record(
            db, user_id, personality_type, confidence, 
            personality_scores, patterns, existing
        )
        
        # AI Prompt için context oluştur
        ai_context = self.generate_ai_context(personality_type, patterns, personality_scores, confidence)
        
        return {
            'success': True,
            'data': {
                'personality_type': personality_type,
                'personality_name': self.personality_types[personality_type]['name'],
                'confidence_score': confidence,
                'description': self.personality_types[personality_type]['description'],
                'all_scores': personality_scores,
                'patterns': patterns,
                'is_new_analysis': existing is None,
                'ai_context': ai_context  # AI prompt için
            }
        }

    async def get_existing_personality(self, db: AsyncSession, user_id: str) -> Optional[UserFinancialPersonality]:
        """Mevcut personality kaydını al"""
        result = await db.execute(
            select(UserFinancialPersonality).where(UserFinancialPersonality.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_transaction_data(self, db: AsyncSession, user_id: str) -> Dict:
        """Kullanıcının transaction verilerini al"""
        # HACKATHON: Tarih filtresi kaldırıldı - tüm transaction'lar
        
        result = await db.execute(
            select(DailyTransaction)
            .where(DailyTransaction.user_id == user_id)
            .order_by(DailyTransaction.date.desc())
        )
        transactions = result.scalars().all()
        
        if not transactions:
            return {'transactions': [], 'total_income': 0, 'total_expenses': 0}
        
        total_income = sum(float(t.income or 0) for t in transactions)
        total_expenses = sum(float(t.total_expenses or 0) for t in transactions)
        
        return {
            'transactions': transactions,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'days_count': len(transactions)
        }

    def calculate_spending_patterns(self, user_data: Dict) -> Dict:
        """Detaylı harcama pattern analizi"""
        transactions = user_data['transactions']
        
        if not transactions:
            return {}
        
        # Basic calculations
        daily_expenses = [float(t.total_expenses or 0) for t in transactions]
        total_expenses = sum(daily_expenses)
        avg_daily = total_expenses / len(daily_expenses) if daily_expenses else 0
        
        # Variance calculation
        variance = statistics.variance(daily_expenses) if len(daily_expenses) > 1 else 0
        variance_coefficient = (variance ** 0.5) / avg_daily if avg_daily > 0 else 0
        
        # Category analysis
        category_ratios = {}
        for category in EXPENSE_CATEGORIES.keys():
            category_total = sum(float(getattr(t, category, 0) or 0) for t in transactions)
            category_ratios[category] = category_total / total_expenses if total_expenses > 0 else 0
        
        # Timing patterns
        weekend_expenses = [float(t.total_expenses or 0) for t in transactions if t.date.weekday() >= 5]
        weekday_expenses = [float(t.total_expenses or 0) for t in transactions if t.date.weekday() < 5]
        
        weekend_avg = sum(weekend_expenses) / len(weekend_expenses) if weekend_expenses else 0
        weekday_avg = sum(weekday_expenses) / len(weekday_expenses) if weekday_expenses else 1
        weekend_multiplier = weekend_avg / weekday_avg if weekday_avg > 0 else 1
        
        # Savings rate
        total_income = user_data['total_income']
        savings_rate = (total_income - total_expenses) / total_income if total_income > 0 else 0
        
        # Consistency score
        consistency_score = 1 - min(variance_coefficient, 1.0)
        
        # Big transaction analysis
        big_transactions = [exp for exp in daily_expenses if exp > avg_daily * 2]
        big_transaction_ratio = len(big_transactions) / len(daily_expenses) if daily_expenses else 0
        
        return {
            'variance_coefficient': variance_coefficient,
            'category_ratios': category_ratios,
            'weekend_multiplier': weekend_multiplier,
            'savings_rate': savings_rate,
            'consistency_score': consistency_score,
            'big_transaction_ratio': big_transaction_ratio,
            'avg_daily_expense': avg_daily,
            'total_days': len(transactions)
        }

    def calculate_personality_scores(self, patterns: Dict) -> Dict:
        """Her personality type için skor hesapla"""
        scores = {}
        
        for personality_type, config in self.personality_types.items():
            trait_scores = {}
            total_score = 0.0
            
            for trait_name, trait_config in config['traits'].items():
                trait_score = self.calculate_trait_score(trait_name, trait_config, patterns)
                trait_scores[trait_name] = trait_score
                total_score += trait_score * trait_config['weight']
            
            scores[personality_type] = {
                'total_score': total_score,
                'trait_scores': trait_scores,
                'name': config['name'],
                'description': config['description']
            }
        
        return scores

    def calculate_trait_score(self, trait_name: str, trait_config: Dict, patterns: Dict) -> float:
        """Belirli bir trait için skor hesapla"""
        
        # Her trait için özel hesaplama
        if trait_name == 'planning_score':
            # Düzenli harcama + tasarruf
            return min(patterns.get('consistency_score', 0) + patterns.get('savings_rate', 0), 1.0)
        
        elif trait_name == 'savings_consistency':
            return patterns.get('savings_rate', 0)
        
        elif trait_name == 'risk_aversion':
            return 1 - patterns.get('variance_coefficient', 0)
        
        elif trait_name == 'essential_focus':
            essential_categories = ['food', 'bills', 'health', 'transport']
            essential_ratio = sum(patterns.get('category_ratios', {}).get(cat, 0) for cat in essential_categories)
            return essential_ratio
        
        elif trait_name == 'variance_low':
            return 1 - patterns.get('variance_coefficient', 0)
        
        elif trait_name == 'high_savings':
            return patterns.get('savings_rate', 0)
        
        elif trait_name == 'low_entertainment':
            return 1 - patterns.get('category_ratios', {}).get('entertainment', 0)
        
        elif trait_name == 'low_clothing':
            return 1 - patterns.get('category_ratios', {}).get('clothing', 0)
        
        elif trait_name == 'consistency_high':
            return patterns.get('consistency_score', 0)
        
        elif trait_name == 'essential_only':
            essential_categories = ['food', 'bills', 'health', 'transport']
            essential_ratio = sum(patterns.get('category_ratios', {}).get(cat, 0) for cat in essential_categories)
            return essential_ratio
        
        elif trait_name == 'high_entertainment':
            return patterns.get('category_ratios', {}).get('entertainment', 0)
        
        elif trait_name == 'high_variance':
            return patterns.get('variance_coefficient', 0)
        
        elif trait_name == 'weekend_multiplier':
            multiplier = patterns.get('weekend_multiplier', 1)
            return min(multiplier / 2.0, 1.0)  # Normalize to 0-1
        
        elif trait_name == 'spontaneous_spending':
            return patterns.get('big_transaction_ratio', 0)
        
        elif trait_name == 'ultra_consistency':
            return patterns.get('consistency_score', 0)
        
        elif trait_name == 'big_transactions':
            return patterns.get('big_transaction_ratio', 0)
        
        elif trait_name == 'high_food':
            return patterns.get('category_ratios', {}).get('food', 0)
        
        elif trait_name == 'high_health':
            return patterns.get('category_ratios', {}).get('health', 0)
        
        # Default calculation for other traits
        else:
            return 0.5  # Neutral score
    
    async def update_personality_record(self, db: AsyncSession, user_id: str, 
                                      personality_type: str, confidence: float,
                                      all_scores: Dict, patterns: Dict, 
                                      existing: Optional[UserFinancialPersonality]):
        """Personality kaydını güncelle"""
        
        if existing:
            # Mevcut kaydı güncelle
            existing.personality_type = personality_type
            existing.personality_name = self.personality_types[personality_type]['name']
            existing.confidence_score = confidence
            existing.set_pattern_analysis(patterns)
            existing.analysis_count += 1
            existing.last_analysis_date = datetime.utcnow()
            existing.updated_at = datetime.utcnow()
        else:
            # Yeni kayıt oluştur
            new_personality = UserFinancialPersonality(
                user_id=user_id,
                personality_type=personality_type,
                personality_name=self.personality_types[personality_type]['name'],
                confidence_score=confidence,
                analysis_count=1,
                last_analysis_date=datetime.utcnow()
            )
            new_personality.set_pattern_analysis(patterns)
            new_personality.set_traits(all_scores)
            db.add(new_personality)
        
        await db.commit()

    async def get_user_personality(self, db: AsyncSession, user_id: str) -> Dict:
        """Kullanıcının mevcut personality'sini getir"""
        personality = await self.get_existing_personality(db, user_id)
        
        if not personality:
            return {
                'success': False,
                'error': 'Henüz personality analizi yapılmamış',
                'data': None
            }
        
        return {
            'success': True,
            'data': personality.to_dict()
        }

    def generate_ai_context(self, personality_type: str, patterns: Dict, all_scores: Dict, confidence: float) -> str:
        """AI prompt için kullanıcının financial personality context'ini oluştur"""
        
        personality_info = self.personality_types[personality_type]
        
        # Ana karakter özellikleri
        context_parts = [
            f"Kullanıcı tipi: {personality_info['name']} - {personality_info['description']}",
            f"Güven skoru: {confidence:.2f} (ne kadar yüksekse o kadar kesin)"
        ]
        
        # Harcama pattern'leri
        savings_rate = patterns.get('savings_rate', 0)
        variance = patterns.get('variance_coefficient', 0)
        consistency = patterns.get('consistency_score', 0)
        weekend_mult = patterns.get('weekend_multiplier', 1)
        
        if savings_rate < -1:
            context_parts.append("ÇOK FAZLA HARCAMA YAPIYOR, tasarruf etmiyor")
        elif savings_rate < 0:
            context_parts.append("Gelirinden fazla harcıyor")
        elif savings_rate > 0.3:
            context_parts.append("İyi tasarruf yapıyor")
        
        if variance > 3:
            context_parts.append("Harcamaları çok değişken, tutarsız")
        elif variance < 0.5:
            context_parts.append("Harcamaları çok düzenli ve tutarlı")
        
        if weekend_mult > 1.5:
            context_parts.append("Hafta sonları çok daha fazla harcıyor")
        elif weekend_mult < 0.7:
            context_parts.append("Hafta sonları daha az harcıyor")
        
        # Kategori analizi
        category_ratios = patterns.get('category_ratios', {})
        dominant_category = max(category_ratios.items(), key=lambda x: x[1]) if category_ratios else None
        
        if dominant_category and dominant_category[1] > 0.5:
            category_name = dominant_category[0]
            percentage = dominant_category[1] * 100
            
            category_meanings = {
                'entertainment': 'eğlence ve sosyal aktivitelere',
                'food': 'yemek ve beslenmeye', 
                'transport': 'ulaşım ve seyahate',
                'health': 'sağlık ve kişisel bakıma',
                'clothing': 'giyim ve aksesuvara',
                'bills': 'faturalar ve zorunlu ödemelere'
            }
            
            meaning = category_meanings.get(category_name, category_name)
            context_parts.append(f"Harcamalarının %{percentage:.0f}'i {meaning} odaklı")
        
        # Alternatif personalities
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1]['total_score'], reverse=True)
        if len(sorted_scores) > 1:
            second_personality = sorted_scores[1]
            second_name = second_personality[1]['name']
            context_parts.append(f"İkinci en yakın tip: {second_name}")
        
        # Final context
        ai_context = ". ".join(context_parts) + "."
        
        return ai_context 