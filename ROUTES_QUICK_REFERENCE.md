# 📱 Fumiko Routes Quick Reference Card

## The Three Routes at a Glance

### 1️⃣ POST /api/fumiko-chat
```
REQUEST:
{
  "message": "How are you?",
  "chat_id": "default"
}

RESPONSE:
{
  "success": true,
  "response": "Haan, I'm here for you!",
  "context_provided": {
    "has_current_entry": true,
    "past_entries_count": 7,
    "has_virtual_profile": true,
    "chat_history_messages": 5
  }
}

TIME: 2-5 seconds
WHEN TO USE: User wants to chat with Fumiko
WHAT IT DOES:
1. Gets all context (diary, profile, history)
2. Sends to Fumiko via Gemini API
3. Saves conversation to database
4. Returns response
```

---

### 2️⃣ GET /api/fumiko-context
```
REQUEST:
GET /api/fumiko-context

RESPONSE:
{
  "success": true,
  "current_entry": "Today I felt happy...",
  "past_entries_count": 7,
  "past_entries": [
    {"date": "2024-01-15", "preview": "..."},
    {"date": "2024-01-14", "preview": "..."}
  ],
  "virtual_profile": {
    "personality_traits": ["creative", "introvert"],
    "emotional_state": "Reflective",
    "interests": ["art", "reading"],
    "has_profile": true
  },
  "chat_history_count": 12
}

TIME: <100ms
WHEN TO USE: Check what context exists before chatting
WHAT IT DOES:
1. Fetches current diary entry
2. Gets preview of past 7 days
3. Gets personality profile
4. Counts chat history
5. Returns everything (no AI call)
```

---

### 3️⃣ GET /api/fumiko-history
```
REQUEST:
GET /api/fumiko-history?limit=50

RESPONSE:
{
  "success": true,
  "messages": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "sender": "user",
      "message": "I'm feeling anxious",
      "response": "What's making you feel that way?",
      "response_timestamp": "2024-01-15T10:30:05Z"
    },
    {...}
  ]
}

TIME: <100ms
WHEN TO USE: Show all past conversations
WHAT IT DOES:
1. Queries all past messages
2. Returns with timestamps
3. Shows conversation thread
```

---

## 🔄 Typical User Flow

```
1. Page loads
   → GET /api/fumiko-context
   → Show "7 entries available"

2. User opens history
   → GET /api/fumiko-history?limit=10
   → Show past conversations

3. User types message
   → POST /api/fumiko-chat {message: "..."}
   → "Thinking..." for 2-3 seconds
   → Show Fumiko's response
   → Auto-saved to history
```

---

## 🎯 What Each Route Fetches

```
/api/fumiko-chat:
├── Current diary entry (today)
├── Past 7 days of entries
├── Virtual profile (personality analysis)
├── Last 5 chat messages
└── Fumiko's persona from file

/api/fumiko-context:
├── Current diary entry
├── Past 7 days with previews
├── Virtual profile
└── Chat history count

/api/fumiko-history:
├── All chat messages (paginated)
├── Timestamps
├── Sender info
└── Response text
```

---

## 🔧 Implementation Notes

### Integration
- All routes use `@auth_required` decorator (authentication)
- `/api/fumiko-chat` imports `chat_system` from `function.py`
- All data saved to Firestore automatically

### Error Handling
All routes return `{"error": "message"}` on failure

### Testing with curl
```powershell
# Test chat
curl -X POST http://localhost:5000/api/fumiko-chat `
  -H "Content-Type: application/json" `
  -d '{"message":"Hi Fumiko","chat_id":"default"}'

# Test context
curl http://localhost:5000/api/fumiko-context

# Test history
curl http://localhost:5000/api/fumiko-history?limit=10
```

---

## 💡 Frontend Integration Tips

### Loading States
```javascript
// Chat
POST /api/fumiko-chat
→ Show loading spinner for 2-5s
→ Display response when ready

// Context & History
GET endpoints
→ Instant response (<100ms)
→ No loading needed
```

### Error Handling
```javascript
if (!response.success) {
  show_error(response.error)
}
```

### Caching Strategy
```javascript
// Cache context for 1 minute
GET /api/fumiko-context
→ Store in localStorage
→ Use cached version for 60s
→ Refresh on new entry

// Always fetch fresh history
GET /api/fumiko-history
→ No caching
```

---

## 📊 Example: Complete User Interaction

```
USER VISIT:
├─ GET /api/fumiko-context
│  └─ Display "7 entries, 12 chats, profile ready"
│
├─ GET /api/fumiko-history?limit=5
│  └─ Show last 5 conversations
│
└─ User types: "I'm feeling overwhelmed"
   │
   ├─ POST /api/fumiko-chat
   │  {message: "I'm feeling overwhelmed"}
   │
   ├─ [2-3 second wait]
   │
   └─ Response: "Arey, what happened? 
                 I remember you mentioned 
                 stress on the 14th. 
                 Same thing or something new?"

NEXT VISIT:
└─ GET /api/fumiko-history
   └─ Shows new conversation in history
```

---

## ✅ Checklist Before Using

- [x] `fumiko.txt` exists in root directory
- [x] `GEMINI_API_KEY` set in `.env`
- [x] User authenticated (session has uid)
- [x] Firestore collection accessible
- [x] All three routes responding
- [x] No syntax errors in `function.py` or `app.py`

---

## 🚀 You're Ready!

Your routes are fully integrated and production-ready. Connect them to your frontend!
