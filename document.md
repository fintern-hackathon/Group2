# 🌳 Fintree App - API Dokümantasyonu

## 📋 İçindekiler
- [Genel Bilgiler](#genel-bilgiler)
- [Kurulum ve Çalıştırma](#kurulum-ve-çalıştırma)  
- [Transactions API](#transactions-api)
- [Analytics API](#analytics-api)
- [MCP AI System](#mcp-ai-system)
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

## 🤖 MCP AI System

**MCP (Model Context Protocol) AI System**, AI ile database arasında köprü görevi gören gelişmiş yapıdır. Prompt dosyasından özel prompt'lar okur, Gemini AI'ya gönderir ve sonuçları database'e kaydeder.

### 🏗️ MCP AI Mimarisi

```
Frontend → MCP AI Endpoint → Prompt File → Gemini AI → Database → Frontend
```

### 📁 Prompt Sistemi

MCP AI, `prompts/ai_prompt.txt` dosyasından prompt template'ini okur:

```txt
prompts/
  └── ai_prompt.txt  # Özel AI prompt template'i
```

### 🛠️ MCP AI Endpoints

**Base URL**: `/api/v1/mcp-ai`

#### 🤖 AI Öneri Üretme

**Endpoint**: `POST /mcp-ai/{user_id}/generate`

**Açıklama**: MCP üzerinden AI öneri üretir
1. `prompts/ai_prompt.txt` dosyasından prompt okur
2. Kullanıcı verilerini hazırlar
3. Gemini AI'ya istek gönderir
4. Sonucu database'e kaydeder

#### 📝 Request Parameters
```json
{
  "force_regenerate": false  // Optional: Aynı gün için yeniden üret
}
```

#### 📊 Response Model - MCPAIResponse
```json
{
  "success": true,
  "suggestion_id": "uuid-string",
  "suggestion_text": "AI önerisi metni...",
  "generated_at": "2024-01-15T14:30:00",
  "mcp_status": "processed",
  "error": null
}
```

#### 📋 AI Önerilerini Getirme

**Endpoint**: `GET /mcp-ai/{user_id}/suggestions`

**Açıklama**: Kullanıcının AI önerilerini listeler

#### 📊 Response Model - SuggestionsResponse
```json
{
  "suggestions": [
    {
      "id": "uuid-string",
      "text": "AI öneri metni...",
      "date": "2024-01-15",
      "created_at": "2024-01-15T14:30:00",
      "is_read": false
    }
  ],
  "total_count": 5,
  "mcp_status": "success"
}
```

### 🔧 MCP Utility Endpoints

#### 🏥 MCP Health Check

**Endpoint**: `GET /mcp-ai/health`

**Açıklama**: MCP AI sisteminin sağlık durumunu kontrol eder

#### 📊 Response
```json
{
  "status": "healthy",
  "gemini_api_configured": true,
  "prompt_file_exists": true,
  "mcp_ready": true,
  "service": "mcp_ai_service"
}
```

#### 📄 Prompt Durumu

**Endpoint**: `GET /mcp-ai/prompt/status`

**Açıklama**: Prompt dosyasının varlığını ve durumunu kontrol eder

#### 📊 Response
```json
{
  "exists": true,
  "file_path": "prompts/ai_prompt.txt",
  "content_length": 456,
  "has_content": true,
  "mcp_status": "ready"
}
```

#### 📝 Varsayılan Prompt Oluştur

**Endpoint**: `POST /mcp-ai/prompt/create`

**Açıklama**: Varsayılan prompt dosyasını oluşturur

### 🎯 MCP AI Kullanım Örneği

```bash
# 1. MCP Health Check
curl http://localhost:8002/api/v1/mcp-ai/health

# 2. Prompt Durumu Kontrol
curl http://localhost:8002/api/v1/mcp-ai/prompt/status

# 3. AI Öneri Üret
curl -X POST http://localhost:8002/api/v1/mcp-ai/11111111-1111-1111-1111-111111111111/generate

# 4. Önerileri Getir
curl http://localhost:8002/api/v1/mcp-ai/11111111-1111-1111-1111-111111111111/suggestions
```

### 🧪 MCP AI Test

```bash
python test_mcp_ai.py
```

Bu test:
- ✅ MCP AI health durumunu kontrol eder
- ✅ Prompt dosyası varlığını test eder
- ✅ AI öneri üretimini test eder
- ✅ Öneri listelemeyi test eder

### 🔑 MCP Konfigürasyonu

```env
# .env dosyasında
GEMINI_API_KEY=your_gemini_api_key_here
```

### 📝 Custom Prompt Template

`prompts/ai_prompt.txt` dosyasını düzenleyerek AI'nın nasıl yanıt vereceğini özelleştirebilirsiniz:

```txt
Sen bir finansal danışman asistanısın...

=== KULLANICI VERİLERİ ===
- Toplam Skor: {total_score}/100
- Ağaç Seviyesi: {tree_level}/10
- Sistemde: {days_in_system} gün
- Tasarruf Oranı: %{savings_rate:.1f}
- Aylık Ortalama Gelir: {avg_monthly_income:.0f} TL

=== SON HARCAMA DETAYLARI ===
{spending_summary}

=== GÖREVIN ===
1. Durumu değerlendir
2. Pratik tavsiye ver
3. Emoji ile durumu göster
4. Motivasyonel ol
```

### 🌊 MCP Integration Flow

1. **Frontend Request** → `/mcp-ai/{user_id}/generate`
2. **Prompt Read** → `prompts/ai_prompt.txt` okunur
3. **Data Preparation** → Kullanıcı verileri hazırlanır
4. **AI Request** → Gemini AI'ya formatted prompt gönderilir
5. **Database Save** → AI yanıtı database'e kaydedilir
6. **Response** → Frontend'e sonuç döner

### 🔄 MCP vs Normal AI

| Özellik | Normal AI | MCP AI |
|---------|-----------|--------|
| **Prompt Source** | Hardcoded | External File |
| **Customization** | Code Change | File Edit |
| **Scalability** | Limited | High |
| **MCP Ready** | ❌ | ✅ |
| **Hot Reload** | ❌ | ✅ |

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
