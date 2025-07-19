# 🌳 FinTree API

**Akıllı Finansal Takip ve Analiz API'si**

FinTree, kullanıcıların günlük harcamalarını takip etmelerine, akıllı skorlama sistemi ile finansal durumlarını analiz etmelerine ve AI destekli öneriler almalarına olanak sağlayan modern bir REST API'dir.

## ⚡ Hızlı Başlangıç

```bash
# Repository'i klonla
git clone https://github.com/yourusername/fintree-app.git
cd fintree-app

# Tek satırla kurulum
python setup.py setup

# Sunucuyu başlat
venv/Scripts/python working_main.py  # Windows
# veya
venv/bin/python working_main.py      # Linux/Mac
```

🎉 **API Documentation**: http://localhost:8002/docs

## ✨ Özellikler

- 🧮 **Smart Scoring Algorithm**: Kategori-bazlı akıllı puanlama
- ⚡ **Momentum System**: Ani skor değişimlerini önleyen yumuşak geçiş
- 🤖 **AI Integration**: Google Gemini ile kişiselleştirilmiş öneriler
- 📊 **Real-time Analytics**: Anlık finansal analiz ve raporlama
- 🗄️ **SQLite Database**: Kolay kurulum, taşınabilir veritabanı
- 🚀 **FastAPI**: Modern, hızlı ve otomatik API dokümantasyonu
- 📱 **RESTful Design**: Clean ve tutarlı endpoint yapısı

## 🎯 Ana Endpoint'ler

### 💰 Transactions
```http
POST /api/v1/transactions/{user_id}/daily
```
Günlük gelir ve harcamaları kaydet

### 📊 Analytics
```http
GET /api/v1/analytics/{user_id}/score          # Genel skor durumu
GET /api/v1/analytics/{user_id}/monthly/{year}/{month}  # Aylık detay
```

## 🧮 Smart Scoring System

| Kategori | Impact | Açıklama |
|----------|--------|----------|
| 🏥 Health | **0.3x** | Sağlık yatırımı (bonus) |
| 💡 Bills | **0.5x** | Mecburi gider |
| 🍕 Food | **0.7x** | Temel ihtiyaç |
| 🎮 Entertainment | **1.5x** | Lüks harcama (penalty) |

**Momentum Sistemi**: Günlük maksimum ±5 puan değişim ile ani skor dalgalanmalarını önler.

## 🛠️ Teknoloji Stack

- **Backend**: FastAPI (Python 3.8+)
- **Database**: SQLite + SQLAlchemy ORM (Async)
- **AI**: Google Gemini API
- **Validation**: Pydantic
- **Documentation**: Swagger UI + ReDoc

## 📋 Kurulum Gereksinimleri

- Python 3.8 veya üzeri
- Internet bağlantısı (AI özellikler için)

## 📚 Detaylı Dokümantasyon

Kapsamlı API dokümantasyonu için [`document.md`](document.md) dosyasına bakın.

## 🗑️ Projeyi Kaldırma

Tek satırla tam temizlik:

```bash
python setup.py remove
```

Bu komut tüm proje dosyalarını, sanal ortamı ve veritabanını tamamen kaldırır.

## 🧪 Test

```bash
# Health check
curl http://localhost:8002/api/v1/health

# Interactive testing
http://localhost:8002/docs
```

## 📊 Sample Data

Proje 53 günlük gerçek finansal veri ile birlikte geliyor:
- 💰 Toplam Gelir: 73,500 TL
- 💸 Toplam Gider: 70,113 TL  
- 📊 Tasarruf Oranı: %4.7
- 🎯 Skor: 99.0/100

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim

Sorularınız için:
- 📚 [Dokümantasyon](document.md)
- 🔧 [Swagger UI](http://localhost:8002/docs)
- 🐛 Issues sekmesi

---

**🌳 FinTree ile finansal geleceğinizi bugünden planlayın!** 