# 🌳 FinTree API Documentation

## 📋 Proje Hakkında

FinTree, kullanıcıların finansal harcamalarını takip etmelerine ve akıllı öneriler almalarına olanak sağlayan bir REST API'dir. 

### ⚡ Hızlı Başlangıç

```bash
# Projeyi klonla
git clone <repository-url>
cd fintree-app

# Tek satırla kurulum
python setup.py setup

# Sunucuyu başlat
venv/Scripts/python working_main.py  # Windows
# veya
venv/bin/python working_main.py      # Linux/Mac

# API dokümantasyonu
http://localhost:8002/docs
```

### 🗑️ Tek Satırla Kaldırma

```bash
python setup.py remove
```

---

## 🛠️ Teknoloji Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite + SQLAlchemy ORM (Async)
- **AI**: Google Gemini API
- **Validation**: Pydantic
- **Architecture**: Clean Architecture + Dependency Injection

---

## 📊 API Endpoints

### Base URL: `http://localhost:8002/api/v1`

---

## 💰 Transactions Endpoints

### 1. 📝 Daily Transaction Ekleme

**Endpoint:** `POST /transactions/{user_id}/daily`

**Açıklama:** Kullanıcının günlük gelir ve harcama kategorilerini kaydet

**Request Model:**
```json
{
  "date": "2025-01-20",
  "income": 5000.0,
  "food": 150.0,
  "transport": 80.0,
  "bills": 200.0,
  "entertainment": 100.0,
  "health": 50.0,
  "clothing": 75.0
}
```

**Response Model:**
```json
{
  "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_expenses": 655.0,
  "net_balance": 4345.0,
  "new_total_score": 87.5,
  "tree_level": 9,
  "message": "Transaction recorded successfully"
}
```

**Örnek İstek:**
```bash
curl -X POST "http://localhost:8002/api/v1/transactions/7f3c989b-221e-47c3-b502-903199b39ad4/daily" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-01-20",
    "income": 5000,
    "food": 150,
    "transport": 80,
    "bills": 200,
    "entertainment": 100,
    "health": 50,
    "clothing": 75
  }'
```

**Çalışma Mantığı:**
1. ✅ Tarih kontrolü (aynı günde birden fazla transaction yasak)
2. ✅ Otomatik hesaplama: `total_expenses` = tüm harcama kategorilerinin toplamı
3. ✅ Net balance: `income - total_expenses`
4. ✅ **Smart Scoring Algorithm** ile skor güncelleme:
   - Health harcaması: 0.3x impact (bonus)
   - Entertainment: 1.5x impact (penalty)
   - Bills: 0.5x impact (mecburi gider)
   - **Momentum sistemi**: Max 5 puan günlük değişim
5. ✅ Tree level güncelleme (1-10 seviye)
6. ✅ Database'e kayıt

---

## 📊 Analytics Endpoints

### 1. 🎯 User Score - Genel Durum

**Endpoint:** `GET /analytics/{user_id}/score`

**Açıklama:** Kullanıcının mevcut finansal skorunu ve genel durumunu getir

**Response Model:**
```json
{
  "user_id": "7f3c989b-221e-47c3-b502-903199b39ad4",
  "total_score": 87.5,
  "days_in_system": 45,
  "total_income": 150000.0,
  "total_expenses": 120000.0,
  "savings_rate": 0.2
}
```

**Örnek İstek:**
```bash
curl "http://localhost:8002/api/v1/analytics/7f3c989b-221e-47c3-b502-903199b39ad4/score"
```

**Çalışma Mantığı:**
1. ✅ UserTotal tablosundan mevcut durumu çek
2. ✅ Savings rate hesapla: `(income - expenses) / income`
3. ✅ Real-time hesaplama (cache yok)

**Score Hesaplama Algoritması:**
```
Total Score = 50 (base) + 
  Smart Savings Score (35 puan) +
  Smart Category Score (35 puan) +
  Income Stability (20 puan) +
  Consistency Bonus (10 puan)

Momentum System:
final_score = (current_score × 0.80) + (new_score × 0.20)
```

---

### 2. 📅 Monthly Analytics - Aylık Özet

**Endpoint:** `GET /analytics/{user_id}/monthly/{year}/{month}`

**Açıklama:** Belirtilen ay için detaylı finansal analiz

**Response Model:**
```json
{
  "year": 2025,
  "month": 1,
  "tree_level": 8,
  "score": 85.0,
  "total_income": 25000.0,
  "total_expenses": 18500.0,
  "savings_rate": 0.26,
  "category_breakdown": {
    "food": 5200.0,
    "transport": 1800.0,
    "bills": 3500.0,
    "entertainment": 2200.0,
    "health": 800.0,
    "clothing": 5000.0
  }
}
```

**Örnek İstek:**
```bash
curl "http://localhost:8002/api/v1/analytics/7f3c989b-221e-47c3-b502-903199b39ad4/monthly/2025/1"
```

**Çalışma Mantığı:**
1. ✅ Belirtilen aya ait tüm daily_transactions'ları getir
2. ✅ SQL aggregation ile toplamları hesapla
3. ✅ Her kategori için breakdown oluştur
4. ✅ Monthly savings rate hesapla
5. ✅ 404 Error eğer o ayda transaction yoksa

---

## 🧮 Smart Scoring Algorithm

### Kategori Ağırlıkları:

| Kategori | Impact Multiplier | Açıklama |
|----------|------------------|----------|
| 🏥 **Health** | **0.3x** | Sağlık yatırımı - az cezalandırılır |
| 💡 **Bills** | **0.5x** | Mecburi gider - düşük penalty |
| 🍕 **Food** | **0.7x** | Temel ihtiyaç |
| 🚗 **Transport** | **0.8x** | Gerekli ulaşım |
| 👕 **Clothing** | **1.2x** | İsteğe bağlı |
| 🎮 **Entertainment** | **1.5x** | Lüks harcama - yüksek penalty |

### Momentum Sistemi:
- **Previous Score Weight**: 80%
- **New Impact Weight**: 20%
- **Max Daily Change**: ±5 puan
- **Min Daily Change**: ±0.3 puan

**Örnek:**
```
Mevcut Skor: 80.0
Yeni Hesaplanan: 50.0 (kötü gün)
Momentum ile Final: 74.0  # Sadece 6 puan düşüş!
```

---

## 🗄️ Database Yapısı

### Users Table
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Daily Transactions Table
```sql
CREATE TABLE daily_transactions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    date DATE NOT NULL,
    income DECIMAL(12,2) DEFAULT 0.00,
    food DECIMAL(10,2) DEFAULT 0.00,
    transport DECIMAL(10,2) DEFAULT 0.00,
    bills DECIMAL(10,2) DEFAULT 0.00,
    entertainment DECIMAL(10,2) DEFAULT 0.00,
    health DECIMAL(10,2) DEFAULT 0.00,
    clothing DECIMAL(10,2) DEFAULT 0.00,
    total_expenses DECIMAL(12,2),
    net_balance DECIMAL(12,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### User Totals Table
```sql
CREATE TABLE user_totals (
    user_id VARCHAR(36) PRIMARY KEY,
    total_income DECIMAL(15,2) DEFAULT 0.00,
    total_expenses DECIMAL(15,2) DEFAULT 0.00,
    total_score DECIMAL(5,2) DEFAULT 50.00,
    tree_level INTEGER DEFAULT 1,
    days_in_system INTEGER DEFAULT 0,
    first_transaction_date DATE,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 🚀 Development Setup

### Gereksinimler:
- Python 3.8+
- SQLite
- Internet (Gemini AI için)

### Kurulum:
```bash
# Repository'i klonla
git clone <repo-url>
cd fintree-app

# Otomatik kurulum
python setup.py setup

# Manuel kurulum (alternatif)
python -m venv venv
venv/Scripts/activate  # Windows
pip install fastapi uvicorn sqlalchemy aiosqlite pydantic google-generativeai

# Database initialize
python -c "import asyncio; from app.database.connection import init_db; asyncio.run(init_db())"

# Sample data yükle (opsiyonel)
python load_data.py
```

### Sunucuyu Başlat:
```bash
# Development server
python working_main.py

# Production (uvicorn)
uvicorn working_main:app --host 0.0.0.0 --port 8002 --reload
```

---

## 🧪 Testing

### Quick Test:
```bash
# Health check
curl http://localhost:8002/api/v1/health

# User score
curl http://localhost:8002/api/v1/analytics/7f3c989b-221e-47c3-b502-903199b39ad4/score

# Add transaction
curl -X POST http://localhost:8002/api/v1/transactions/7f3c989b-221e-47c3-b502-903199b39ad4/daily \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-01-20","income":5000,"food":150,"entertainment":300}'
```

### Interactive Testing:
- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

---

## 🔧 Configuration

### Environment Variables:
```bash
# .env file
GEMINI_API_KEY=your_google_gemini_api_key_here
DATABASE_URL=sqlite:///./fintree.db
```

### Port Configuration:
- Default: `8002`
- Change in `working_main.py`: `uvicorn.run(app, host="0.0.0.0", port=8002)`

---

## 📝 Error Handling

### Common Errors:

**500 Internal Server Error:**
- Database connection issue
- Missing Gemini API key
- Invalid date format

**400 Bad Request:**
- Duplicate transaction for same date
- Invalid JSON format
- Missing required fields

**404 Not Found:**
- User not found
- No transactions for specified month

---

## 🎯 API Features

### ✅ Implemented:
- ✅ Smart Category Scoring
- ✅ Momentum-based Score Updates
- ✅ Real-time Analytics
- ✅ Monthly Breakdown
- ✅ Google Gemini AI Integration
- ✅ SQLite Database
- ✅ Async Operations
- ✅ Input Validation
- ✅ Error Handling
- ✅ Swagger Documentation

### 🚧 Future Features:
- 🔄 Authentication & JWT
- 🔄 Goal Setting
- 🔄 Budget Alerts
- 🔄 Export/Import
- 🔄 Multiple Currencies

---

## 📊 Sample Data

**Test User ID:** `7f3c989b-221e-47c3-b502-903199b39ad4`

Proje 53 günlük gerçek transaction data ile birlikte geliyor:
- Total Income: 73,500 TL
- Total Expenses: 70,113 TL
- Savings Rate: 4.7%
- Score: 99.0/100
- Tree Level: 10

---

## 🆘 Troubleshooting

**Database Issues:**
```bash
# Reset database
rm fintree.db
python -c "import asyncio; from app.database.connection import init_db; asyncio.run(init_db())"
```

**Server Not Starting:**
```bash
# Check port usage
netstat -ano | findstr :8002

# Kill existing process
taskkill /PID <process_id> /F
```

**Dependencies Issues:**
```bash
# Reinstall
pip install --upgrade --force-reinstall fastapi uvicorn sqlalchemy
```

---

## 📞 Support

For issues and questions:
1. Check this documentation first
2. Review Swagger UI: http://localhost:8002/docs
3. Check database contents with any SQLite browser
4. Review server logs for error details

---

**🎉 Happy Coding! FinTree API ile finansal takip artık çok kolay!**

