# 🧮 FinTree Matematiksel Algoritmalar ve Rule-Based Sistemler

## 📋 İçindekiler
- [Genel Bakış](#genel-bakış)
- [Skorlama Algoritmaları](#skorlama-algoritmaları)
- [Personality Belirleme Sistemi](#personality-belirleme-sistemi)
- [Trend Analizi](#trend-analizi)
- [Momentum Smoothing](#momentum-smoothing)
- [Kategori Ağırlıklandırma](#kategori-ağırlıklandırma)
- [Gelir Adaptasyonu](#gelir-adaptasyonu)
- [Ağaç Seviye Hesaplama](#ağaç-seviye-hesaplama)

---

## 🎯 Genel Bakış

FinTree, finansal davranışları analiz eden rule-based bir sistemdir. Tüm kararlar matematiksel formüller ve kurallar üzerine kurulmuştur.

### Temel Prensipler
- **Deterministik Algoritmalar**: Aynı girdi her zaman aynı çıktıyı verir
- **Ağırlıklı Sistemler**: Farklı faktörler farklı ağırlıklarla değerlendirilir
- **Adaptif Kurallar**: Gelir seviyesine göre kurallar değişir
- **Momentum Koruma**: Ani değişimler sınırlandırılır

---

## 📊 Skorlama Algoritmaları

### Temel Skor Formülü

```python
total_score = base_score + savings_score + category_score + stability_score + consistency_bonus
```

**Bileşenler:**
- `base_score = 50.0` (Başlangıç skoru)
- `savings_score` (0-40 puan)
- `category_score` (0-30 puan)
- `stability_score` (0-20 puan)
- `consistency_bonus` (0-10 puan)

### 1. Tasarruf Skoru Hesaplama

```python
def calculate_savings_score(total_income, total_expenses):
    if total_income <= 0:
        return -20.0
    
    savings_rate = (total_income - total_expenses) / total_income
    
    if savings_rate >= 0.4:      return 40.0  # %40+ tasarruf
    elif savings_rate >= 0.3:    return 30.0  # %30-40 tasarruf
    elif savings_rate >= 0.2:    return 20.0  # %20-30 tasarruf
    elif savings_rate >= 0.1:    return 10.0  # %10-20 tasarruf
    elif savings_rate >= 0:      return 0.0   # Pozitif
    else:                        return -20.0 # Negatif
```

**Matematiksel Mantık:**
- **Tasarruf Oranı**: `savings_rate = (gelir - gider) / gelir`
- **Progressive Scoring**: Yüksek tasarruf oranları daha fazla puan
- **Negatif Ceza**: Gelirinden fazla harcayanlar ceza alır

### 2. Kategori Dengesi Skoru

```python
def calculate_category_balance_score(category_totals, total_expenses, avg_monthly_income):
    ideal_ratios = {
        'food': 0.30,        # Yemek %30
        'transport': 0.15,   # Ulaşım %15
        'bills': 0.25,       # Faturalar %25
        'entertainment': 0.10, # Eğlence %10
        'health': 0.15,      # Sağlık %15
        'clothing': 0.05     # Giyim %5
    }
    
    score = 30.0  # Başlangıç skoru
    
    for category, ideal_ratio in ideal_ratios.items():
        actual_amount = category_totals.get(category, 0)
        actual_ratio = actual_amount / total_expenses
        ratio_diff = abs(actual_ratio - ideal_ratio)
        
        # Gelir seviyesine göre esneklik
        income_factor = min(avg_monthly_income / 15000, 2.0)
        
        # Sapma cezası
        if ratio_diff > 0.15:    score -= (8.0 / income_factor)
        elif ratio_diff > 0.10:  score -= (5.0 / income_factor)
        elif ratio_diff > 0.05:  score -= (2.0 / income_factor)
    
    return max(-15.0, score)
```

**Matematiksel Kurallar:**
- **İdeal Oranlar**: Her kategori için hedef yüzde
- **Sapma Cezası**: İdeal orandan uzaklaştıkça puan düşer
- **Gelir Adaptasyonu**: Yüksek gelirli daha esnek kurallar

### 3. Gelir İstikrarı Skoru

```python
def calculate_income_stability_score(monthly_incomes):
    if len(monthly_incomes) < 2:
        return 10.0
    
    avg_income = sum(monthly_incomes) / len(monthly_incomes)
    if avg_income == 0:
        return 5.0
    
    # Coefficient of Variation hesaplama
    variance = sum((x - avg_income) ** 2 for x in monthly_incomes) / len(monthly_incomes)
    cv = (variance ** 0.5) / avg_income
    
    if cv < 0.1:      return 20.0  # %10'dan az varyasyon
    elif cv < 0.2:    return 15.0  # %20'den az varyasyon
    elif cv < 0.4:    return 10.0  # %40'tan az varyasyon
    else:             return 5.0   # Yüksek varyasyon
```

**İstatistiksel Hesaplamalar:**
- **Ortalama**: `μ = Σxᵢ / n`
- **Varyans**: `σ² = Σ(xᵢ - μ)² / n`
- **Coefficient of Variation**: `CV = σ / μ`

### 4. Süreklilik Bonusu

```python
def calculate_consistency_bonus(days_in_system):
    if days_in_system >= 30: return 10.0
    elif days_in_system >= 14: return 7.0
    elif days_in_system >= 7: return 5.0
    else: return 2.0
```

---

## 🧠 Personality Belirleme Sistemi

### Pattern Analizi

```python
def calculate_spending_patterns(transactions):
    daily_expenses = [float(t.total_expenses or 0) for t in transactions]
    total_expenses = sum(daily_expenses)
    avg_daily = total_expenses / len(daily_expenses) if daily_expenses else 0
    
    # Varyasyon katsayısı
    variance = statistics.variance(daily_expenses) if len(daily_expenses) > 1 else 0
    variance_coefficient = (variance ** 0.5) / avg_daily if avg_daily > 0 else 0
    
    # Kategori oranları
    category_ratios = {}
    for category in EXPENSE_CATEGORIES.keys():
        category_total = sum(float(getattr(t, category, 0) or 0) for t in transactions)
        category_ratios[category] = category_total / total_expenses if total_expenses > 0 else 0
    
    # Hafta sonu analizi
    weekend_expenses = [float(t.total_expenses or 0) for t in transactions if t.date.weekday() >= 5]
    weekday_expenses = [float(t.total_expenses or 0) for t in transactions if t.date.weekday() < 5]
    
    weekend_avg = sum(weekend_expenses) / len(weekend_expenses) if weekend_expenses else 0
    weekday_avg = sum(weekday_expenses) / len(weekday_expenses) if weekday_expenses else 1
    weekend_multiplier = weekend_avg / weekday_avg if weekday_avg > 0 else 1
    
    # Tasarruf oranı
    total_income = sum(float(t.income or 0) for t in transactions)
    savings_rate = (total_income - total_expenses) / total_income if total_income > 0 else 0
    
    # Tutarlılık skoru
    consistency_score = 1 - min(variance_coefficient, 1.0)
    
    # Büyük işlem analizi
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
```

### Trait Scoring Sistemi

```python
def calculate_trait_score(trait_name, trait_config, patterns):
    if trait_name == 'planning_score':
        return min(patterns.get('consistency_score', 0) + patterns.get('savings_rate', 0), 1.0)
    
    elif trait_name == 'savings_consistency':
        return patterns.get('savings_rate', 0)
    
    elif trait_name == 'risk_aversion':
        return 1 - patterns.get('variance_coefficient', 0)
    
    elif trait_name == 'essential_focus':
        essential_categories = ['food', 'bills', 'health', 'transport']
        essential_ratio = sum(patterns.get('category_ratios', {}).get(cat, 0) for cat in essential_categories)
        return essential_ratio
    
    elif trait_name == 'high_entertainment':
        return patterns.get('category_ratios', {}).get('entertainment', 0)
    
    elif trait_name == 'weekend_multiplier':
        multiplier = patterns.get('weekend_multiplier', 1)
        return min(multiplier / 2.0, 1.0)  # Normalize to 0-1
    
    elif trait_name == 'big_transactions':
        return patterns.get('big_transaction_ratio', 0)
    
    # ... diğer trait'ler
```

### Personality Seçim Algoritması

```python
def calculate_personality_scores(patterns):
    scores = {}
    
    for personality_type, config in personality_types.items():
        trait_scores = {}
        total_score = 0.0
        
        for trait_name, trait_config in config['traits'].items():
            trait_score = calculate_trait_score(trait_name, trait_config, patterns)
            trait_scores[trait_name] = trait_score
            total_score += trait_score * trait_config['weight']
        
        scores[personality_type] = {
            'total_score': total_score,
            'trait_scores': trait_scores,
            'name': config['name'],
            'description': config['description']
        }
    
    return scores

# En yüksek skorlu personality'yi seç
best_personality = max(personality_scores.items(), key=lambda x: x[1]['total_score'])
```

---

## 📈 Trend Analizi

### Haftalık Trend Hesaplama

```python
def calculate_weekly_trend(transactions):
    if len(transactions) < 14:  # En az 2 hafta gerekli
        return {'direction': 'stable', 'strength': 0.0, 'consistency': 0.5}
    
    # Son 2 haftayı al
    recent_transactions = transactions[-14:]
    
    # Haftalık gruplar
    week1 = recent_transactions[:7]
    week2 = recent_transactions[7:]
    
    week1_avg = sum(float(t.total_expenses or 0) for t in week1) / 7
    week2_avg = sum(float(t.total_expenses or 0) for t in week2) / 7
    
    # Trend yönü
    if week2_avg < week1_avg * 0.9:  # %10'dan fazla azalma
        direction = 'improving'
        strength = (week1_avg - week2_avg) / week1_avg
    elif week2_avg > week1_avg * 1.1:  # %10'dan fazla artma
        direction = 'declining'
        strength = (week2_avg - week1_avg) / week1_avg
    else:
        direction = 'stable'
        strength = 0.0
    
    # Tutarlılık hesaplama
    daily_changes = []
    for i in range(1, len(recent_transactions)):
        prev = float(recent_transactions[i-1].total_expenses or 0)
        curr = float(recent_transactions[i].total_expenses or 0)
        if prev > 0:
            change = (curr - prev) / prev
            daily_changes.append(change)
    
    # Trend tutarlılığı
    if direction == 'improving':
        consistent_changes = sum(1 for c in daily_changes if c < 0)
    elif direction == 'declining':
        consistent_changes = sum(1 for c in daily_changes if c > 0)
    else:
        consistent_changes = len(daily_changes) // 2
    
    consistency = consistent_changes / len(daily_changes) if daily_changes else 0.5
    
    return {
        'direction': direction,
        'strength': min(strength, 1.0),
        'consistency': consistency
    }
```

---

## 🔄 Momentum Smoothing

### Ağırlıklı Güncelleme

```python
def apply_weighted_update(current_score, new_base_score, user_data):
    # Momentum konfigürasyonu
    prev_weight = 0.85  # Geçmiş skorun ağırlığı
    new_weight = 0.15   # Yeni transaction'ın ağırlığı
    max_change = 8.0    # Maksimum günlük değişim
    min_change = 0.5    # Minimum günlük değişim
    
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
```

### Momentum Konfigürasyonu

```python
momentum_config = {
    'previous_weight': 0.85,  # Geçmiş skorun ağırlığı
    'new_impact_weight': 0.15,  # Yeni transaction'ın ağırlığı
    'trend_multiplier': 0.1,   # Trend etkisi
    'min_change': 0.5,         # Minimum değişim
    'max_change': 8.0          # Maksimum günlük değişim
}
```

---

## ⚖️ Kategori Ağırlıklandırma

### Smart Kategori Sistemi

```python
category_weights = {
    # TEMEL İHTİYAÇLAR (düşük ceza)
    'food': {
        'impact_multiplier': 0.7,  # %30 daha az etkili
        'ideal_ratio': 0.25,
        'tolerance': 0.10,
        'description': 'Temel ihtiyaç'
    },
    'bills': {
        'impact_multiplier': 0.5,  # %50 daha az etkili (mecburi)
        'ideal_ratio': 0.20,
        'tolerance': 0.05,
        'description': 'Mecburi gider'
    },
    'health': {
        'impact_multiplier': 0.4,  # %60 daha az etkili (BONUS)
        'ideal_ratio': 0.10,
        'tolerance': 0.15,  # Yüksek tolerans
        'description': 'Sağlık yatırımı'
    },
    'transport': {
        'impact_multiplier': 0.8,  # %20 daha az etkili
        'ideal_ratio': 0.15,
        'tolerance': 0.08,
        'description': 'Gerekli ulaşım'
    },
    
    # İSTEĞE BAĞLI (yüksek ceza)
    'entertainment': {
        'impact_multiplier': 1.5,  # %50 daha etkili
        'ideal_ratio': 0.10,
        'tolerance': 0.05,
        'description': 'Eğlence harcaması'
    },
    'clothing': {
        'impact_multiplier': 1.2,  # %20 daha etkili
        'ideal_ratio': 0.08,
        'tolerance': 0.07,
        'description': 'Giyim harcaması'
    }
}
```

### Kategori Skor Hesaplama

```python
def calculate_smart_category_score(user_data):
    total_expenses = user_data['total_expenses']
    if total_expenses <= 0:
        return 50.0
    
    score = 75.0  # Base score
    category_totals = user_data['category_totals']
    
    # Income-based thresholds
    avg_monthly_income = calculate_avg_monthly_income(user_data)
    income_tier = get_income_tier(avg_monthly_income)
    
    for category, config in category_weights.items():
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
```

---

## 💰 Gelir Adaptasyonu

### Gelir Seviyesi Belirleme

```python
def get_income_tier(monthly_income):
    if monthly_income >= 30000:
        return {'tier': 'high', 'tolerance_multiplier': 1.5}
    elif monthly_income >= 15000:
        return {'tier': 'medium', 'tolerance_multiplier': 1.2}
    else:
        return {'tier': 'low', 'tolerance_multiplier': 0.8}
```

### Gelir Tabanlı Tolerans

```python
def get_income_tolerance_factor(monthly_income):
    if monthly_income >= 25000:
        return 1.4  # Yüksek gelir = daha tolerant
    elif monthly_income >= 15000:
        return 1.2  # Orta gelir = normal tolerance
    elif monthly_income >= 8000:
        return 1.0  # Düşük gelir = standart
    else:
        return 0.8  # Çok düşük gelir = strict
```

---

## 🌳 Ağaç Seviye Hesaplama

### Seviye Belirleme Algoritması

```python
def calculate_tree_level(score):
    # 0-100 arası skoru 1-10 arası seviyeye çevir
    return max(1, min(10, int(score / 10) + 1))
```

### Ağaç Görseli Seçimi

```python
def get_tree_image(score):
    # 0-100 arası skoru 1-10 arası ağaç indeksine çevir
    tree_index = Math.min(Math.max(Math.ceil((score / 100) * 10), 1), 10)
    
    # Tüm ağaç fotoğraflarını önceden tanımla
    tree_images = {
        1: require('@/assets/images/1.png'),   # En küçük ağaç
        2: require('@/assets/images/2.png'),
        3: require('@/assets/images/3.png'),
        4: require('@/assets/images/4.png'),
        5: require('@/assets/images/5.png'),
        6: require('@/assets/images/6.png'),
        7: require('@/assets/images/7.png'),
        8: require('@/assets/images/8.png'),
        9: require('@/assets/images/9.png'),
        10: require('@/assets/images/10.png')  # En büyük ağaç
    }
    
    return tree_images[tree_index]
```

### Seviye Aralıkları

```
Seviye 1:  0-10   puan  → Fidan aşaması
Seviye 2:  11-20  puan  → Küçük fidan
Seviye 3:  21-30  puan  → Küçük ağaç
Seviye 4:  31-40  puan  → Orta boy ağaç
Seviye 5:  41-50  puan  → Büyük ağaç
Seviye 6:  51-60  puan  → Gelişmiş ağaç
Seviye 7:  61-70  puan  → Olgun ağaç
Seviye 8:  71-80  puan  → Büyük olgun ağaç
Seviye 9:  81-90  puan  → Tam gelişmiş ağaç
Seviye 10: 91-100 puan  → Mükemmel ağaç
```

---

## 🔧 Matematiksel Sabitler

### Sistem Sabitleri

```python
# Skorlama sabitleri
BASE_SCORE = 50.0
MAX_SCORE = 100.0
MIN_SCORE = 0.0

# Momentum sabitleri
PREVIOUS_WEIGHT = 0.85
NEW_WEIGHT = 0.15
MAX_DAILY_CHANGE = 8.0
MIN_DAILY_CHANGE = 0.5

# Kategori sabitleri
FOOD_IMPACT = 0.7
BILLS_IMPACT = 0.5
HEALTH_IMPACT = 0.4
TRANSPORT_IMPACT = 0.8
ENTERTAINMENT_IMPACT = 1.5
CLOTHING_IMPACT = 1.2

# Personality sabitleri
MIN_TRANSACTIONS_FOR_ANALYSIS = 7
CONFIDENCE_THRESHOLD = 0.6
VARIANCE_THRESHOLD = 0.3
WEEKEND_MULTIPLIER_THRESHOLD = 1.8
```

### Eşik Değerleri

```python
# Tasarruf oranı eşikleri
SAVINGS_EXCELLENT = 0.4  # %40+
SAVINGS_GREAT = 0.3      # %30-40
SAVINGS_GOOD = 0.2       # %20-30
SAVINGS_FAIR = 0.1       # %10-20
SAVINGS_POOR = 0.0       # %0-10

# Gelir istikrarı eşikleri
STABILITY_EXCELLENT = 0.1  # %10'dan az varyasyon
STABILITY_GOOD = 0.2       # %20'den az varyasyon
STABILITY_FAIR = 0.4       # %40'tan az varyasyon

# Kategori sapma eşikleri
CATEGORY_MAJOR_DEVIATION = 0.15  # %15'ten fazla sapma
CATEGORY_MODERATE_DEVIATION = 0.10  # %10'dan fazla sapma
CATEGORY_MINOR_DEVIATION = 0.05   # %5'ten fazla sapma
```

---

## 📐 İstatistiksel Hesaplamalar

### Varyasyon Katsayısı

```python
def calculate_coefficient_of_variation(values):
    if not values or len(values) < 2:
        return 0.0
    
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_deviation = variance ** 0.5
    
    return std_deviation / mean
```

### Hareketli Ortalama

```python
def calculate_moving_average(values, window_size=7):
    if len(values) < window_size:
        return values
    
    moving_averages = []
    for i in range(window_size - 1, len(values)):
        window = values[i - window_size + 1:i + 1]
        average = sum(window) / window_size
        moving_averages.append(average)
    
    return moving_averages
```

### Trend Analizi

```python
def calculate_trend_slope(x_values, y_values):
    if len(x_values) != len(y_values) or len(x_values) < 2:
        return 0.0
    
    n = len(x_values)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x ** 2 for x in x_values)
    
    # Linear regression slope
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    
    return slope
```

---

## 🎯 Rule-Based Karar Ağaçları

### Personality Seçim Ağacı

```
1. Tasarruf Oranı > %40?
   ├─ Evet → Çalışkan Sincap (Yüksek tasarruf)
   └─ Hayır → 2. Adım

2. Eğlence Harcaması > %15?
   ├─ Evet → Özgür Kelebeği (Yüksek eğlence)
   └─ Hayır → 3. Adım

3. Sağlık Harcaması > %12?
   ├─ Evet → Konfor Koala (Sağlık odaklı)
   └─ Hayır → 4. Adım

4. Varyasyon Katsayısı > %60?
   ├─ Evet → Cesur Aslan (Yüksek değişkenlik)
   └─ Hayır → 5. Adım

5. Tutarlılık Skoru > %80?
   ├─ Evet → Sabit Kaplumbağa (Aşırı tutarlı)
   └─ Hayır → Akıllı Baykuş (Planlı)
```

### Skor Güncelleme Ağacı

```
1. Yeni transaction var mı?
   ├─ Hayır → Mevcut skoru koru
   └─ Evet → 2. Adım

2. Base score hesapla
   ├─ Tasarruf skoru (40 puan)
   ├─ Kategori skoru (30 puan)
   ├─ İstikrar skoru (20 puan)
   └─ Süreklilik bonusu (10 puan)

3. Momentum uygula
   ├─ Ağırlıklı ortalama (85% eski + 15% yeni)
   ├─ Değişim sınırlama (±8 puan)
   └─ Trend bonus/ceza

4. Final skoru hesapla
   ├─ 0-100 arası sınırla
   └─ Ağaç seviyesini güncelle
```

---

## 🔍 Hata Kontrolü ve Validasyon

### Veri Validasyonu

```python
def validate_transaction_data(transaction):
    # Gelir kontrolü
    if transaction.income < 0:
        raise ValueError("Gelir negatif olamaz")
    
    # Gider kontrolü
    if transaction.total_expenses < 0:
        raise ValueError("Gider negatif olamaz")
    
    # Kategori kontrolü
    for category in EXPENSE_CATEGORIES:
        amount = getattr(transaction, category, 0)
        if amount < 0:
            raise ValueError(f"{category} kategorisi negatif olamaz")
    
    # Tarih kontrolü
    if transaction.date > datetime.now().date():
        raise ValueError("Gelecek tarih olamaz")
```

### Skor Sınırlama

```python
def clamp_score(score):
    """Skoru 0-100 arası sınırla"""
    return max(0.0, min(100.0, score))

def validate_personality_score(score):
    """Personality skorunu 0-1 arası sınırla"""
    return max(0.0, min(1.0, score))
```

---

**Son Güncelleme**: 2024  
**Versiyon**: 1.0.0
