# 🌳 FinTree Backend Dokümantasyonu

## 📋 Genel Bakış

FinTree, kullanıcıların finansal davranışlarını gamification ile takip eden bir mobil uygulama. Backend FastAPI ile geliştirilmiş ve SQLite veritabanı kullanıyor.

## 🏗️ Teknoloji Stack

- **Framework**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy (Async)
- **AI**: Google Gemini API
- **Port**: 8006

## 🧠 AI Sistemi

### MCP (Model Context Protocol) Yapısı
- AI ile veritabanı arası köprü görevi görür
- Prompt dosyasından özel prompt'lar okur
- Gemini AI'ya gönderir ve sonuçları veritabanına kaydeder

### Öneri Sistemi
- Kullanıcının finansal verilerini analiz eder
- Kişiselleştirilmiş öneriler üretir
- Günlük öneri sistemi ile sürekli motivasyon sağlar

## 👤 Personality Sistemi

### Personality Tipleri
- **Cesur Aslan**: Risk alır, büyük harcamalar, hedef odaklı
- **Çalışkan Sincap**: Çok tasarruf eden ama keyif almayı unutan
- **Özgür Kelebeği**: Spontan, keyifli, anlık kararlar
- **Sabit Kaplumbağa**: Tutarlı, güvenli, değişim sevmeyen
- **Konfor Koala**: Konfor odaklı, rahat yaşam
- **Akıllı Baykuş**: Planlı, uzun vadeli düşünen

### Personality Belirleme
- Kullanıcının harcama alışkanlıkları analiz edilir
- AI algoritması ile personality tipi belirlenir
- Emoji ve açıklama ile görselleştirilir

## 🧠 Karar Mekanizmaları

### 📊 Puanlama Algoritması

#### Temel Prensipler
- **0-100 arası skor sistemi**
- **Kategori ağırlıkları**: Sağlık (-0.5), eğlence (-1.5)
- **Momentum smoothing**: Günlük değişim maksimum %20
- **Trend analizi**: Son 7 günlük trend hesaplanır
- **Gelir tabanlı tolerans**: Yüksek gelirde harcama toleransı artar

#### Detaylı Skor Hesaplama

**Temel Skor Bileşenleri:**
```python
total_score = base_score + savings_score + category_score + stability_score + consistency_bonus
```

**1. Tasarruf Skoru (40 puan)**
```python
savings_rate = (total_income - total_expenses) / total_income

if savings_rate >= 0.4:      return 40.0  # %40+ tasarruf
elif savings_rate >= 0.3:    return 30.0  # %30-40 tasarruf
elif savings_rate >= 0.2:    return 20.0  # %20-30 tasarruf
elif savings_rate >= 0.1:    return 10.0  # %10-20 tasarruf
elif savings_rate >= 0:      return 0.0   # Pozitif
else:                        return -20.0 # Negatif
```

**2. Kategori Dengesi Skoru (30 puan)**
```python
# İdeal kategori oranları
ideal_ratios = {
    'food': 0.30,        # Yemek %30
    'transport': 0.15,   # Ulaşım %15
    'bills': 0.25,       # Faturalar %25
    'entertainment': 0.10, # Eğlence %10
    'health': 0.15,      # Sağlık %15
    'clothing': 0.05     # Giyim %5
}

# Her kategori için sapma cezası
ratio_diff = abs(actual_ratio - ideal_ratio)
if ratio_diff > 0.15:    score -= 8.0
elif ratio_diff > 0.10:  score -= 5.0
elif ratio_diff > 0.05:  score -= 2.0
```

**3. Gelir İstikrarı Skoru (20 puan)**
```python
# Coefficient of variation hesaplama
cv = std_deviation / average_income

if cv < 0.1:      return 20.0  # %10'dan az varyasyon
elif cv < 0.2:    return 15.0  # %20'den az varyasyon
elif cv < 0.4:    return 10.0  # %40'tan az varyasyon
else:             return 5.0   # Yüksek varyasyon
```

**4. Süreklilik Bonusu (10 puan)**
```python
if days_in_system >= 30: return 10.0
elif days_in_system >= 14: return 7.0
elif days_in_system >= 7: return 5.0
else: return 2.0
```

#### Gelişmiş Skorlama Algoritması (Advanced)

**Smart Kategori Ağırlıkları:**
```python
category_weights = {
    'food': {'impact_multiplier': 0.7, 'ideal_ratio': 0.25},      # Temel ihtiyaç
    'bills': {'impact_multiplier': 0.5, 'ideal_ratio': 0.20},     # Mecburi gider
    'health': {'impact_multiplier': 0.4, 'ideal_ratio': 0.10},    # Sağlık bonus
    'transport': {'impact_multiplier': 0.8, 'ideal_ratio': 0.15}, # Gerekli ulaşım
    'entertainment': {'impact_multiplier': 1.5, 'ideal_ratio': 0.10}, # Yüksek ceza
    'clothing': {'impact_multiplier': 1.2, 'ideal_ratio': 0.08}   # Orta ceza
}
```

**Momentum Smoothing:**
```python
# Ağırlıklı güncelleme
weighted_score = (current_score * 0.85) + (new_score * 0.15)

# Değişim sınırlama
max_change = 8.0  # Maksimum günlük değişim
min_change = 0.5  # Minimum günlük değişim

if abs(score_change) > max_change:
    score_change = max_change if score_change > 0 else -max_change
```

**Gelir Tabanlı Tolerans:**
```python
# Gelir seviyesine göre tolerance faktörü
if monthly_income >= 25000: tolerance_factor = 1.4  # Yüksek gelir
elif monthly_income >= 15000: tolerance_factor = 1.2  # Orta gelir
elif monthly_income >= 8000: tolerance_factor = 1.0   # Düşük gelir
else: tolerance_factor = 0.8  # Çok düşük gelir
```

### 🎯 Personality Belirleme Algoritması

#### Analiz Faktörleri
- **Harcama Dağılımı**: Kategoriler arası oranlar
- **Tasarruf Oranı**: Gelir-gider farkı
- **Tutarlılık**: Günlük harcama varyasyonu
- **Risk Profili**: Yüksek tutarlı harcamalar
- **Planlama**: Düzenli vs spontan harcamalar

#### Personality Tipleri ve Trait'leri

**🦉 Akıllı Baykuş**
- `planning_score`: Düzenli harcama + tasarruf (min: 0.7, weight: 0.3)
- `savings_consistency`: Tasarruf oranı (min: 0.6, weight: 0.25)
- `risk_aversion`: Düşük varyasyon (min: 0.7, weight: 0.2)
- `essential_focus`: Temel ihtiyaçlara odaklanma (min: 0.6, weight: 0.15)
- `variance_low`: Düşük harcama değişkenliği (max: 0.3, weight: 0.1)

**🐿️ Çalışkan Sincap**
- `high_savings`: Yüksek tasarruf oranı (min: 0.4, weight: 0.4)
- `low_entertainment`: Düşük eğlence harcaması (max: 0.08, weight: 0.25)
- `low_clothing`: Düşük giyim harcaması (max: 0.05, weight: 0.15)
- `consistency_high`: Yüksek tutarlılık (min: 0.7, weight: 0.15)
- `essential_only`: Sadece temel ihtiyaçlar (min: 0.8, weight: 0.05)

**🦋 Özgür Kelebeği**
- `high_entertainment`: Yüksek eğlence harcaması (min: 0.15, weight: 0.3)
- `high_variance`: Yüksek harcama değişkenliği (min: 0.4, weight: 0.25)
- `weekend_multiplier`: Hafta sonu harcama artışı (min: 1.8, weight: 0.2)
- `spontaneous_spending`: Spontan büyük harcamalar (min: 0.6, weight: 0.15)
- `flexible_budget`: Esnek bütçe (min: 0.5, weight: 0.1)

**🐢 Sabit Kaplumbağa**
- `ultra_consistency`: Aşırı tutarlılık (min: 0.8, weight: 0.4)
- `low_variance`: Düşük değişkenlik (max: 0.2, weight: 0.25)
- `routine_spending`: Rutin harcamalar (min: 0.7, weight: 0.2)
- `stable_categories`: Kararlı kategori dağılımı (min: 0.8, weight: 0.1)
- `predictable_timing`: Öngörülebilir zamanlama (min: 0.7, weight: 0.05)

**🦁 Cesur Aslan**
- `high_variance`: Yüksek değişkenlik (min: 0.6, weight: 0.3)
- `big_transactions`: Büyük işlemler (min: 0.5, weight: 0.25)
- `risk_taking`: Risk alma (min: 0.6, weight: 0.2)
- `goal_oriented`: Hedef odaklı (min: 0.6, weight: 0.15)
- `bold_categories`: Cesur kategori seçimleri (min: 0.4, weight: 0.1)

**🐨 Konfor Koala**
- `high_food`: Yüksek yemek harcaması (min: 0.25, weight: 0.25)
- `high_health`: Yüksek sağlık harcaması (min: 0.12, weight: 0.2)
- `comfort_spending`: Konfor odaklı harcamalar (min: 0.6, weight: 0.2)
- `quality_over_quantity`: Kalite odaklı (min: 0.5, weight: 0.2)
- `lifestyle_focus`: Yaşam tarzı odaklı (min: 0.6, weight: 0.15)

#### Trait Hesaplama Formülleri

```python
# Tasarruf Oranı
savings_rate = (total_income - total_expenses) / total_income

# Varyasyon Katsayısı
variance_coefficient = std_deviation / average_daily_expense

# Tutarlılık Skoru
consistency_score = 1 - min(variance_coefficient, 1.0)

# Hafta Sonu Çarpanı
weekend_multiplier = weekend_avg / weekday_avg

# Büyük İşlem Oranı
big_transaction_ratio = big_transactions_count / total_days

# Kategori Oranları
category_ratio = category_total / total_expenses
```

#### Personality Seçim Algoritması
1. **Pattern Analizi**: 7+ günlük veri ile harcama pattern'leri çıkarılır
2. **Trait Scoring**: Her personality tipi için trait skorları hesaplanır
3. **Weighted Scoring**: Trait skorları ağırlıklarıyla çarpılır
4. **Confidence Calculation**: En yüksek skorlu personality seçilir
5. **Database Update**: Sonuç veritabanına kaydedilir

### 🤖 AI Öneri Sistemi

#### Veri Analizi
- **Finansal Durum**: Skor, gelir, gider oranları
- **Harcama Alışkanlıkları**: Kategori bazında analiz
- **Trend Verileri**: Son 30 günlük değişim
- **Personality Profili**: Kullanıcı tipine özel yaklaşım

#### Öneri Kategorileri
1. **Tasarruf Önerileri**: Düşük skorlu kullanıcılar için
2. **Yatırım Tavsiyeleri**: Yüksek tasarruf oranı olanlar için
3. **Harcama Optimizasyonu**: Kategori bazında iyileştirmeler
4. **Motivasyonel Mesajlar**: Personality tipine uygun

#### Prompt Mühendisliği
- **Context Injection**: Kullanıcı verileri prompt'a eklenir
- **Personality Adaptation**: Her tip için farklı ton
- **Actionable Advice**: Somut, uygulanabilir öneriler
- **Emotional Intelligence**: Motivasyonel ve destekleyici

### 🌳 Ağaç Görselleştirme Algoritması

#### Seviye Belirleme
- **1-10 arası seviye sistemi**
- **Skor bazlı mapping**: Her 10 puan = 1 seviye
- **Minimum seviye**: 1 (0-10 puan)
- **Maksimum seviye**: 10 (90-100 puan)

#### Görsel Değişim Mantığı
```
Seviye 1-2:  Fidan aşaması
Seviye 3-4:  Küçük ağaç
Seviye 5-6:  Orta boy ağaç
Seviye 7-8:  Büyük ağaç
Seviye 9-10: Tam gelişmiş ağaç
```

### 📈 Trend Analizi

#### Momentum Hesaplama
- **7 günlük hareketli ortalama**
- **Standart sapma hesaplama**
- **Trend yönü belirleme** (artış/azalış)
- **Anomali tespiti** (aşırı harcamalar)

#### Adaptif Öğrenme
- **Kullanıcı davranış kalıpları**
- **Sezonsal değişimler**
- **Yaşam tarzı değişiklikleri**
- **Hedef bazlı öneriler**

### 🔄 Gerçek Zamanlı Karar Sistemi

#### Veri İşleme Pipeline
1. **Veri Toplama**: Günlük işlemler
2. **Temizleme**: Hatalı verilerin filtrelenmesi
3. **Analiz**: Çok boyutlu analiz
4. **Karar**: Algoritma bazlı karar verme
5. **Aksiyon**: Skor güncelleme ve öneri üretimi

#### Performans Optimizasyonu
- **Caching**: Sık kullanılan hesaplamalar
- **Batch Processing**: Toplu veri işleme
- **Async Operations**: Paralel işlemler
- **Memory Management**: Verimli bellek kullanımı

### Ağaç Görselleştirme
- **1-10 arası ağaç seviyeleri**
- Skor arttıkça ağaç büyür
- 10 farklı ağaç görseli (1.png - 10.png)

## 🗄️ Veritabanı Yapısı

### Ana Tablolar
- **users**: Kullanıcı bilgileri
- **transactions**: Günlük işlemler
- **user_totals**: Toplam skor ve istatistikler
- **personalities**: Personality verileri
- **suggestions**: AI önerileri

### İlişkiler
- Her kullanıcının günlük işlemleri
- Toplam skor otomatik güncellenir
- Personality verisi kullanıcıya bağlı

## 🔄 API Endpoints

### Transactions
- `POST /transactions/{user_id}/daily`: Günlük işlem ekleme
- `GET /transactions/{user_id}`: İşlem geçmişi

### Analytics
- `GET /analytics/{user_id}/score`: Kullanıcı skoru
- `GET /analytics/{user_id}/monthly/{year}/{month}`: Aylık analiz

### Personality
- `GET /personality/{user_id}`: Kullanıcı personality'si

### MCP AI
- `POST /mcp-client/daily-suggestion`: Günlük öneri
- `GET /mcp-ai/{user_id}/suggestions`: Öneri geçmişi

## 🚀 Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Sunucuyu başlat
python working_main.py
```

## 🔧 Konfigürasyon

### Environment Variables
```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///fintree.db
```

### Prompt Dosyası
`prompts/ai_prompt.txt` dosyası AI'nın nasıl yanıt vereceğini belirler.

## 📈 Sistem Akışı

1. **Kullanıcı İşlem Girişi** → Transaction API
2. **Skor Hesaplama** → Puanlama algoritması
3. **Personality Analizi** → AI ile personality belirleme
4. **Öneri Üretimi** → MCP AI sistemi
5. **Görselleştirme** → Ağaç seviyesi güncelleme

## 🎯 Özellikler

- **Gamification**: Ağaç büyütme sistemi
- **AI Destekli**: Kişiselleştirilmiş öneriler
- **Personality Sistemi**: Kullanıcı tipi analizi
- **Gerçek Zamanlı**: Anlık skor güncelleme
- **Mobil Uyumlu**: React Native frontend

## 🔍 Debugging

- **Loglar**: Console output
- **Database**: SQLite browser
- **API Test**: Swagger UI (`/docs`)

---

**Versiyon**: 1.0.0  
**Son Güncelleme**: 2024
