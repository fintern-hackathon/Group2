# 🌳 Fintree App - API Dokümantasyonu

## 📋 İçindekiler
- [Genel Bilgiler](#genel-bilgiler)
- [Kurulum ve Çalıştırma](#kurulum-ve-çalıştırma)  
- [Transactions API](#transactions-api)
- [Analytics API](#analytics-api)
- [Uygulamayı Kaldırma](#uygulamayı-kaldırma)

---

## 🎯 Genel Bilgiler

**Fintree App**, kullanıcıların finansal durumlarına göre sanal bir ağacın büyümesini veya solmasını gözlemleyebildikleri gamified finans uygulamasıdır.

### 🏗️ Teknoloji Stack
- **Backend**: FastAPI
- **Database**: SQLite (fintree.db)
- **ORM**: SQLAlchemy (Async)
- **AI**: Google Gemini API
- **Port**: 8002

### 🔗 Base URL
```
http://localhost:8002/api/v1
```

---

## 🚀 Kurulum ve Çalıştırma

### 1. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 2. Sunucuyu Başlat
```bash
python working_main.py
```

### 3. API Dokümantasyonu
- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

---

## 💳 Transactions API

### 📝 Günlük İşlem Ekleme

**Endpoint**: `POST /transactions/{user_id}/daily`

**Açıklama**: Kullanıcı için günlük gelir ve gider verilerini ekler. Bu endpoint aynı zamanda kullanıcının skor hesaplamasını otomatik olarak günceller.

#### 📊 Request Model - DailyTransactionCreate
```json
{
  "date": "2024-01-15",
  "income": 5000.0,
  "food": 300.0,
  "transport": 150.0,
  "bills": 800.0,
  "entertainment": 200.0,
  "health": 100.0,
  "clothing": 250.0
}
```

#### 📈 Response Model - DailyTransactionResponse
```json
{
  "transaction_id": "uuid-string",
  "total_expenses": 1800.0,
  "net_balance": 3200.0,
  "new_total_score": 75.5,
  "tree_level": 3,
  "message": "İşlem başarıyla eklendi!"
}
```

#### 🔄 Çalışma Mantığı
1. **Tarih Kontrolü**: Aynı tarih için işlem var mı kontrol edilir
2. **Işlem Oluşturma**: Yeni DailyTransaction oluşturulur
3. **Hesaplama**: Toplam gider ve net balans hesaplanır
4. **Skor Güncelleme**: Gelişmiş skor algoritması ile toplam skor güncellenir
5. **Response**: İşlem sonucu ve yeni skor döndürülür

#### 🧮 Skor Algoritması Özellikleri
- **Kategori Ağırlıkları**: Sağlık harcamaları (-0.5), eğlence harcamaları (-1.5)
- **Momentum Smoothing**: Günlük skor değişimi maksimum %20 ile sınırlı
- **Trend Analizi**: Son 7 günlük trend hesaplanır
- **Gelir Tabanlı Tolerans**: Yüksek gelirde harcama toleransı artar

#### 📋 Örnek İstek
```bash
curl -X POST "http://localhost:8002/api/v1/transactions/user123/daily" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-15",
    "income": 5000.0,
    "food": 300.0,
    "transport": 150.0,
    "bills": 800.0,
    "entertainment": 200.0,
    "health": 100.0,
    "clothing": 250.0
  }'
```

#### ✅ Başarılı Response (201)
```json
{
  "transaction_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "total_expenses": 1800.0,
  "net_balance": 3200.0,
  "new_total_score": 78.5,
  "tree_level": 3,
  "message": "İşlem başarıyla eklendi ve skor güncellendi!"
}
```

#### ❌ Hata Response (400)
```json
{
  "detail": "Transaction already exists for this date"
}
```

---

## 📊 Analytics API

### 📈 Kullanıcı Skor Durumu

**Endpoint**: `GET /analytics/{user_id}/score`

**Açıklama**: Kullanıcının güncel skor durumunu, toplam gelir/gider bilgilerini ve sistem içinde geçirdiği gün sayısını döndürür.

#### 📊 Response Model - UserScoreResponse
```json
{
  "user_id": "string",
  "total_score": 0.0,
  "days_in_system": 0,
  "total_income": 0.0,
  "total_expenses": 0.0,
  "savings_rate": 0.0
}
```

#### 🔄 Çalışma Mantığı
1. **UserTotal Sorgusu**: Kullanıcının toplam verilerini getirir
2. **Otomatik Oluşturma**: Eğer veri yoksa default UserTotal oluşturur
3. **Tasarruf Oranı**: `(gelir - gider) / gelir` formülü ile hesaplanır
4. **Response**: Tüm finansal özet bilgileri döndürülür

#### 📋 Örnek İstek
```bash
curl -X GET "http://localhost:8002/api/v1/analytics/user123/score"
```

#### ✅ Başarılı Response (200)
```json
{
  "user_id": "user123",
  "total_score": 78.5,
  "days_in_system": 45,
  "total_income": 150000.0,
  "total_expenses": 89500.0,
  "savings_rate": 0.4033
}
```

### 📅 Aylık Özet

**Endpoint**: `GET /analytics/{user_id}/monthly/{year}/{month}`

**Açıklama**: Belirtilen ay için kullanıcının detaylı finansal analizini ve kategori bazında harcama dağılımını döndürür.

#### 📊 Response Model - MonthlyAnalytics
```json
{
  "year": 2024,
  "month": 1,
  "tree_level": 3,
  "score": 78.5,
  "total_income": 15000.0,
  "total_expenses": 8500.0,
  "savings_rate": 0.433,
  "category_breakdown": {
    "food": 2500.0,
    "transport": 1200.0,
    "bills": 3000.0,
    "entertainment": 800.0,
    "health": 500.0,
    "clothing": 500.0
  }
}
```

#### 🔄 Çalışma Mantığı
1. **Tarih Filtreleme**: Belirtilen yıl ve ay için işlemler filtrelenir
2. **Kategori Toplama**: Her harcama kategorisi için toplam hesaplanır
3. **Skor Hesaplama**: Aylık veriler ile ortalama skor hesaplanır
4. **Ağaç Seviyesi**: Skor bazında ağaç seviyesi belirlenir
5. **Response**: Detaylı aylık analiz döndürülür

#### 📋 Örnek İstek
```bash
curl -X GET "http://localhost:8002/api/v1/analytics/user123/monthly/2024/1"
```

#### ✅ Başarılı Response (200)
```json
{
  "year": 2024,
  "month": 1,
  "tree_level": 3,
  "score": 78.5,
  "total_income": 15000.0,
  "total_expenses": 8500.0,
  "savings_rate": 0.433,
  "category_breakdown": {
    "food": 2500.0,
    "transport": 1200.0,
    "bills": 3000.0,
    "entertainment": 800.0,
    "health": 500.0,
    "clothing": 500.0
  }
}
```

#### ❌ Hata Response (404)
```json
{
  "detail": "No data found for the specified month"
}
```

---

## 🗑️ Uygulamayı Kaldırma

### Tek Satırla Kaldırma
```bash
python uninstall.py
```

Bu komut şunları yapar:
1. ⚠️ Kullanıcıdan onay ister
2. 🔄 Çalışan Python processlerini durdurur
3. 📁 Tüm proje klasörünü siler
4. ✅ Kaldırma işlemini tamamlar

### 🔧 Manuel Kaldırma
Eğer uninstall.py çalışmazsa:
1. Çalışan sunucuyu durdurun (Ctrl+C)
2. Proje klasörünü manuel olarak silin

---

## 📚 Ek Notlar

### 🔐 Authentication
- Şu anda API'ler user_id parametresi ile çalışır
- Gerçek production ortamında JWT token kullanılmalıdır

### 💾 Database
- SQLite database (`fintree.db`) development için GitHub'a dahil edilir
- Production'da PostgreSQL önerilir

### 🎮 Test Kullanıcısı
```
Test User ID: 7f3c989b-221e-47c3-b502-903199b39ad4
```

### 🔄 API Status Codes
- **200**: Başarılı GET istekleri
- **201**: Başarılı POST istekleri (oluşturma)
- **400**: Yanlış istek formatı
- **404**: Veri bulunamadı
- **500**: Sunucu hatası

---

## 🤝 Geliştirme

### Katkıda Bulunma
1. Repo'yu fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request açın

### 🔧 Debugging
- Sunucu logları: Console output
- Database browsing: SQLite browser tools
- API testing: Swagger UI (`/docs`)

---

**Son Güncelleme**: 2024
**Versiyon**: 1.0.0
