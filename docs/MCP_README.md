# 🔧 FinTree MCP System

**Model Context Protocol (MCP) mimarisi** ile FinTree AI sisteminin doğru implementasyonu.

## 🎯 MCP Mimarisi

```
Frontend ←→ Gemini AI ←→ MCP Server ←→ Database
```

### 🔄 Doğru Flow:
1. **Frontend** → **Gemini AI**'ya mesaj gönderir
2. **Gemini AI** → **MCP Tool**'ları çağırır (function calling)
3. **MCP Server** → **Database**'den veri getirir
4. **MCP Server** → **Gemini AI**'ya veri döner
5. **Gemini AI** → Bu verilerle yanıt üretir
6. **Gemini AI** → **Frontend**'e nihai yanıt gönderir

## 🛠️ MCP Tools

### 📊 Available Tools:

| Tool | Endpoint | Description |
|------|----------|-------------|
| `get_user_financial_data` | `POST /mcp/get_user_financial_data` | Kullanıcının tam finansal verisi |
| `get_user_score` | `POST /mcp/get_user_score` | Sadece skor ve ağaç seviyesi |
| `get_recent_transactions` | `POST /mcp/get_recent_transactions` | Son N günün işlemleri |
| `get_spending_analysis` | `POST /mcp/get_spending_analysis` | Detaylı harcama analizi |
| `save_ai_suggestion` | `POST /mcp/save_ai_suggestion` | AI önerisini database'e kaydet |

### 🔧 Tool Usage:

```python
# Gemini AI bu tool'ları şöyle çağırır:
{
    "name": "get_user_financial_data",
    "parameters": {
        "user_id": "11111111-1111-1111-1111-111111111111"
    }
}
```

## 🚀 Kurulum ve Test

### 1. 🏃‍♂️ Sunucuyu Başlat:
```bash
python working_main.py
```

### 2. 🧪 MCP Tools Test:
```bash
python test_mcp_system.py
```

### 3. 🤖 Gemini AI Test:
```bash
# GEMINI_API_KEY environment variable'ını set et
export GEMINI_API_KEY="your_key_here"

python gemini_mcp_config.py
```

## 📝 MCP Tool Examples

### Tool 1: Get Financial Data
```bash
curl -X POST http://localhost:8002/api/v1/mcp/get_user_financial_data \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "11111111-1111-1111-1111-111111111111",
    "parameters": {}
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "11111111-1111-1111-1111-111111111111",
    "total_score": 99.0,
    "tree_level": 10,
    "days_in_system": 53,
    "total_income": 73500.0,
    "total_expenses": 70113.95,
    "savings_rate": 0.047,
    "avg_monthly_income": 41571.43,
    "category_breakdown": {
      "food": 28537.45,
      "transport": 13208.50,
      "bills": 18967.00,
      "entertainment": 4701.00,
      "health": 2850.00,
      "clothing": 1850.00
    }
  },
  "tool_name": "get_user_financial_data"
}
```

### Tool 2: Get Recent Transactions
```bash
curl -X POST http://localhost:8002/api/v1/mcp/get_recent_transactions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "11111111-1111-1111-1111-111111111111",
    "parameters": {"days": 7}
  }'
```

### Tool 3: Save AI Suggestion
```bash
curl -X POST http://localhost:8002/api/v1/mcp/save_ai_suggestion \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "11111111-1111-1111-1111-111111111111",
    "suggestion_text": "Ağacınız mükemmel durumda! 🌳✨ Bu tasarruf oranını korumanız harika.",
    "user_score_at_time": 99.0
  }'
```

## 🤖 Gemini AI Integration

### Function Definitions:
Gemini AI şu function'ları kullanacak şekilde konfigüre edilmeli:

```python
MCP_FUNCTIONS = [
    {
        "name": "get_user_financial_data",
        "description": "Get complete financial data for a user including score, income, expenses, and category breakdown",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User's UUID"}
            },
            "required": ["user_id"]
        }
    }
    # ... other functions
]
```

### Usage Example:
```python
# Gemini AI ile chat
client = FinTreeMCPClient(gemini_api_key)
response = await client.chat_with_mcp(
    user_id="11111111-1111-1111-1111-111111111111",
    message="Finansal durumumu nasıl buluyorsun?"
)
```

## 🔍 Debug ve Test

### MCP Health Check:
```bash
curl http://localhost:8002/api/v1/mcp/health
```

### Tools List:
```bash
curl http://localhost:8002/api/v1/mcp/tools
```

### Individual Tool Test:
```bash
curl -X POST http://localhost:8002/api/v1/mcp/test_tool/get_user_score \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "11111111-1111-1111-1111-111111111111",
    "parameters": {}
  }'
```

## 📊 API Documentation

### Swagger UI:
- **URL**: http://localhost:8002/docs
- **Tag**: `mcp-tools`

### Available Endpoints:
- `GET /api/v1/mcp/health` - MCP health check
- `GET /api/v1/mcp/tools` - List all tools
- `POST /api/v1/mcp/get_user_financial_data` - Financial data tool
- `POST /api/v1/mcp/get_user_score` - Score tool
- `POST /api/v1/mcp/get_recent_transactions` - Transactions tool
- `POST /api/v1/mcp/get_spending_analysis` - Analysis tool
- `POST /api/v1/mcp/save_ai_suggestion` - Save suggestion tool
- `POST /api/v1/mcp/test_tool/{tool_name}` - Test any tool

## 🌐 Frontend Integration

### Frontend ←→ Gemini AI:
Frontend artık direkt Gemini AI ile konuşacak:

```javascript
// Frontend code example
const response = await geminiClient.chat({
    user_id: "11111111-1111-1111-1111-111111111111",
    message: "Bu hafta harcamalarım nasıl?",
    functions: MCP_FUNCTIONS
});
```

### Gemini AI ←→ MCP Server:
Gemini AI otomatik olarak MCP tool'larını çağıracak:

```
Gemini AI: "Kullanıcının son harcamalarını öğrenmek için get_recent_transactions tool'unu çağırıyorum..."
```

## 🔑 Environment Variables

```bash
# .env dosyasında
GEMINI_API_KEY=your_gemini_api_key_here
```

## 🚦 MCP Status Codes

| Status | Description |
|--------|-------------|
| `success: true` | Tool başarıyla çalıştı |
| `success: false` | Tool hata verdi |
| `mcp_status: ready` | MCP server hazır |
| `mcp_status: error` | MCP server hatası |

## 🎯 Best Practices

1. **Always check tool success**: Her tool response'unda `success` field'ını kontrol et
2. **Handle errors gracefully**: Tool hataları için fallback stratejisi oluştur
3. **Use appropriate tools**: İhtiyacınız olan veri için en uygun tool'u seçin
4. **Save suggestions**: AI'nın ürettiği önerileri mutlaka `save_ai_suggestion` ile kaydedin

## ✅ Clean MCP System

Sadece MCP sistemi kaldı - gereksiz AI dosyaları temizlendi:

| Silinen | Açıklama |
|---------|----------|
| `app/routers/ai.py` | Eski AI router |
| `app/routers/mcp_ai.py` | Gereksiz MCP AI router |
| `app/services/ai_service.py` | Eski AI service |
| `app/services/mcp_ai_service.py` | Gereksiz MCP AI service |
| `prompts/ai_prompt.txt` | Artık function calling var |

## 🎉 Ready to Go!

MCP sistem tamamen hazır! 

**Test et:**
```bash
python test_mcp_system.py
```

**Gemini AI ile entegre et:**
```bash
python gemini_mcp_config.py
```

**Frontend'den kullan:**
Gemini AI SDK'sını kullanarak MCP function'larını çağır! 