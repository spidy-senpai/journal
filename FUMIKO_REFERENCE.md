# 🤖 FUMIKO AI - QUICK REFERENCE CARD

## 3 Endpoints - 3 Functions

### 1️⃣ Chat with Fumiko
```
POST /api/fumiko-chat

Request:
  { "message": "text", "chat_id": "default" }

Response:
  { "success": true, "response": "...", "context_provided": {...} }

Time: 2-5 seconds
```

### 2️⃣ Get Context Info
```
GET /api/fumiko-context

Response:
  { 
    "current_entry": "...",
    "past_entries_count": 7,
    "virtual_profile": {...},
    "chat_history_count": 5
  }

Time: <1 second
```

### 3️⃣ Get Chat History
```
GET /api/fumiko-history?limit=50

Response:
  { "messages": [{timestamp, sender, message, response}, ...] }

Time: <1 second
```

---

## 5 Context Datasets

```
1. Current Entry    → Your latest diary
2. Past 7 Days      → Last 7 diary entries
3. Virtual Profile  → Your personality insights
4. Chat History     → Last 5 conversations
5. Fumiko Persona   → Her character (fumiko.txt)
```

---

## Fumiko's Vocabulary

| Phrase | Meaning |
|--------|---------|
| Haan haan | Agreement/acknowledgment |
| Accha | Understood/what? |
| Kya hua | What happened? |
| Koi nhi | Don't worry |
| Umm | Thinking |
| Woah | Impressive |
| Mst | Great |
| Noice | Nice |

---

## Data Saved Per Chat

```
✅ User message
✅ Timestamp
✅ Chat ID
✅ Fumiko's response
✅ Response timestamp
✅ Sender (user/fumiko)
```

---

## Frontend Example - Minimal

```html
<input id="msg" placeholder="Chat with Fumiko">
<button onclick="chat()">Send</button>
<div id="response"></div>

<script>
async function chat() {
  const msg = document.getElementById('msg').value;
  const res = await fetch('/api/fumiko-chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: msg, chat_id: 'default'})
  });
  const data = await res.json();
  document.getElementById('response').textContent = data.response;
}
</script>
```

---

## Testing

```bash
# 1. Create diary entry first
# 2. Run test suite
python test_fumiko.py

# 3. Or curl test
curl -b cookies.txt -X POST \
  http://localhost:5000/api/fumiko-chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hi"}'
```

---

## Database Path

```
/artifacts/
  default-journal-app-id/
    users/
      {uid}/
        chat_history/
          {auto_id}: {message, response, timestamp}
```

---

## Performance

| Operation | Time |
|-----------|------|
| Chat | 2-5s |
| Context | <1s |
| History | <1s |

---

## How It Works (Simple)

```
User Message
    ↓
Fetch 5 Datasets
    ↓
Build Prompt
    ↓
Gemini API
    ↓
Get Response
    ↓
Save to DB
    ↓
Return Response
```

---

## Requirements

✅ GEMINI_API_KEY in .env
✅ Logged in (session cookie)
✅ Diary entry exists
✅ Firestore permissions set

---

## Files

| File | Purpose |
|------|---------|
| app.py | Implementation (+200 lines) |
| FUMIKO_INTEGRATION.md | Full docs |
| FUMIKO_QUICK_START.md | Code examples |
| test_fumiko.py | Test suite |

---

## Common Errors & Fixes

| Error | Fix |
|-------|-----|
| No response | Check API key |
| Empty entries | Create entry first |
| Empty profile | Run /api/analyze-now |
| 401 Error | Login first |

---

## Context Awareness Example

**User today**: "Feeling anxious"
**Fumiko checks**:
- Did you feel anxious before? (past 7 days)
- What's your personality? (virtual profile)
- Did we talk about anxiety? (chat history)
- What's different now? (current entry)

**Response**: "Haan haan, I see anxiety 3 times this week... 
This time it's about work though. What's different?"

---

## Fumiko's 3-Step Response

```
1. Validate
   "I hear you, that sounds tough"

2. Recall
   "Like when you mentioned X..."

3. Guide
   "What if you...? What do you think?"
```

---

## Character Consistency

Fumiko:
- 🗣️ Uses her unique vocabulary
- 🎭 Maintains her personality
- 💭 Follows her emotional patterns
- 📚 References your past entries
- 👤 Respects your personality type

---

## What Fumiko CAN'T do

❌ Make real-world decisions for you
❌ Replace professional help
❌ Share your data
❌ Judge you
❌ Break character

---

## What Fumiko CAN do

✅ Listen without judgment
✅ Spot patterns in your life
✅ Ask thoughtful questions
✅ Remember your conversations
✅ Tailor advice to your personality
✅ Help you find clarity

---

## Next: Build UI

```javascript
// Add to your dashboard.html

function initFumikoChat() {
  const input = document.getElementById('fumiko-input');
  const btn = document.getElementById('fumiko-send');
  
  btn.onclick = async () => {
    const msg = input.value;
    const res = await fetch('/api/fumiko-chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: msg, chat_id: 'default'})
    });
    
    const data = await res.json();
    displayMessage('fumiko', data.response);
    input.value = '';
  };
}
```

---

**🎉 Everything is ready. Start building the UI!**
