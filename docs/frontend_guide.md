# 🌐 FinTree Frontend Integration Guide

## 🎯 **TEK ENDPOINT - SADECE BUNU KULLAN:**

```
POST /api/v1/mcp-client/daily-suggestion
```

## 📝 **REQUEST (Sadece user_id):**

```json
{
  "user_id": "11111111-1111-1111-1111-111111111111"
}
```

## 📊 **RESPONSE:**

```json
{
  "success": true,
  "suggestion_text": "🌳 FinTree Finansal Analiz\n\nMerhaba! Finansal ağacınızın durumunu analiz ettim...",
  "user_score": 85.5,
  "tree_level": 8,
  "mcp_flow_status": "completed_with_full_analysis"
}
```

## 💻 **JAVASCRIPT EXAMPLE:**

```javascript
async function getDailySuggestion(userId) {
  try {
    const response = await fetch('/api/v1/mcp-client/daily-suggestion', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // AI suggestion ready
      displaySuggestion(data.suggestion_text);
      updateUserScore(data.user_score);
      updateTreeLevel(data.tree_level);
    } else {
      // Handle error
      console.error('AI Error:', data.error);
    }
    
  } catch (error) {
    console.error('Network Error:', error);
  }
}
```

## ⚛️ **REACT EXAMPLE:**

```jsx
import { useState, useEffect } from 'react';

function DailySuggestion({ userId }) {
  const [suggestion, setSuggestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [userScore, setUserScore] = useState(0);
  const [treeLevel, setTreeLevel] = useState(1);

  const fetchSuggestion = async () => {
    setLoading(true);
    
    try {
      const response = await fetch('/api/v1/mcp-client/daily-suggestion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSuggestion(data.suggestion_text);
        setUserScore(data.user_score);
        setTreeLevel(data.tree_level);
      }
      
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="daily-suggestion">
      <button onClick={fetchSuggestion} disabled={loading}>
        {loading ? 'AI Düşünüyor...' : 'Günlük Önerimi Al'}
      </button>
      
      {suggestion && (
        <div className="suggestion-card">
          <div className="user-stats">
            <span>Skor: {userScore}/100</span>
            <span>Ağaç: Level {treeLevel}</span>
          </div>
          <div className="suggestion-text">
            {suggestion}
          </div>
        </div>
      )}
    </div>
  );
}
```

## 🔧 **ERROR HANDLING:**

```javascript
const handleApiResponse = (data) => {
  if (!data.success) {
    if (data.error.includes('quota')) {
      showError('AI servisi geçici olarak kullanılamıyor. Lütfen daha sonra tekrar deneyin.');
    } else if (data.error.includes('function response')) {
      showError('AI analiz sorunu. Tekrar deneyin.');
    } else {
      showError('Beklenmeyen hata: ' + data.error);
    }
    return false;
  }
  return true;
};
```

## 🎨 **CSS STYLING SUGGESTIONS:**

```css
.daily-suggestion {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.suggestion-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 16px;
  margin-top: 16px;
}

.user-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-weight: bold;
}

.suggestion-text {
  white-space: pre-line;
  line-height: 1.6;
}

button {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
```

## 🚀 **DEPLOYMENT:**

1. **Environment Variables:**
   ```bash
   GEMINI_API_KEY=your_api_key_here
   ```

2. **Start Server:**
   ```bash
   python working_main.py
   ```

3. **Test API:**
   ```bash
   python tests/test_api.py
   ```

## ✅ **CHECKLIST:**

- [ ] Server running (port 8004)
- [ ] Gemini API key configured
- [ ] Database initialized
- [ ] Frontend connected
- [ ] Error handling implemented
- [ ] User experience optimized

**🎉 Frontend integration complete!** 