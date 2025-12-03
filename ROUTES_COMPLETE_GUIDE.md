# 🎯 Fumiko Routes Explained - Complete Guide

## Quick Reference

| Route | Method | Purpose | Time |
|-------|--------|---------|------|
| `/api/fumiko-chat` | POST | Chat with Fumiko | 2-5s |
| `/api/fumiko-context` | GET | Get available context | <1s |
| `/api/fumiko-history` | GET | Get chat history | <1s |

---

## 🔵 Route 1: POST /api/fumiko-chat

**The Main Conversation Endpoint**

### Purpose
User sends a message → System fetches all diary/profile context → Fumiko responds staying in character

### Request
```json
{
    "message": "I'm feeling anxious about the exam",
    "chat_id": "default"
}
```

### Response
```json
{
    "success": true,
    "response": "Arrey, exam tension? I remember you mentioned this is your third attempt. What makes THIS exam different? Is it the stakes, or is it something inside you that's changed?",
    "context_provided": {
        "has_current_entry": true,
        "past_entries_count": 7,
        "has_virtual_profile": true,
        "chat_history_messages": 3
    }
}
```

### What Happens Behind the Scenes

```
USER MESSAGE
    ↓
[/api/fumiko-chat handler]
    ↓
1. Extract uid from session (authenticated user)
2. Get current diary entry (today's thoughts)
3. Get past 7 days of entries (for pattern recognition)
4. Get virtual profile (personality, emotions, interests)
5. Get last 5 chat messages (conversation context)
    ↓
[Format all data as strings]
    ↓
[Create chat_system instance with context]
    system = chat_system(
        current_entry = "Today I wrote...",
        old_entries = "Day 1: ...\nDay 2: ...",
        chat_history = "User: ...\nFumiko: ...",
        virtual_profile = "Traits: introspective, creative..."
    )
    ↓
[Call chat_fumiko(message)]
    response = system.chat_fumiko("I'm feeling anxious...")
    ↓
[Inside chat_system.chat_fumiko()]
    1. Load fumiko.txt (3000+ word persona)
    2. Build system prompt with:
       - Fumiko's identity & voice
       - User's personality profile
       - All past diary entries
       - Current thoughts
       - Previous conversations
       - User's message
    3. Send to Gemini API
    4. Get response staying in character
    ↓
[Save to Firestore]
    Save to: /artifacts/{app_id}/users/{uid}/chat_history
    ↓
FUMIKO'S RESPONSE
```

### Why This Order?
- **Validate emotion** - Acknowledge what they said
- **Recall details** - Reference something from their diary
- **Guide them** - Ask questions to help them think

### Example Flow

**User diary entry (current):**
```
"Had a fight with mom again today. 
I don't know why I always end up 
getting defensive about my career choices."
```

**Past entries (last 7 days):**
- Day 1: "Mom called, gave me unsolicited advice"
- Day 2: "Still thinking about that conversation"
- Day 3: "Feeling guilty but also angry"
- etc.

**Virtual profile:**
```
Personality: Introverted, highly sensitive, perfectionist
Emotional state: Conflicted
Interests: Writing, design, psychology
```

**Fumiko's response strategy:**
1. **Validate:** "Arey, family conflicts are the hardest"
2. **Recall:** "You mentioned your mom's advice on Day 1..."
3. **Guide:** "What would it feel like if you responded differently?"

---

## 🟢 Route 2: GET /api/fumiko-context

**The Context Info Endpoint - "What Data Exists?"**

### Purpose
Show the frontend what context is available WITHOUT making a chat request

### Request
```
GET /api/fumiko-context
```

### Response
```json
{
    "success": true,
    "current_entry": "Today I felt overwhelmed with work...",
    "past_entries_count": 7,
    "past_entries": [
        {
            "date": "2024-01-15",
            "preview": "Had a productive day, finished the project..."
        },
        {
            "date": "2024-01-14",
            "preview": "Feeling tired, need a break from..."
        }
    ],
    "virtual_profile": {
        "personality_traits": ["introvert", "creative", "perfectionist"],
        "emotional_state": "Reflective",
        "interests": ["reading", "art", "design"],
        "has_profile": true
    },
    "chat_history_count": 12
}
```

### Use Cases
1. **UI Display:** Show "You have 7 past entries" before opening chat
2. **Smart Prompts:** "Your profile says you're creative - want to journal creatively?"
3. **Status Check:** "No current entry today" → Suggest writing first
4. **Context Indicator:** "12 past chats" → Show "Rich conversation history available"

### What Happens Behind Scenes
```
GET /api/fumiko-context
    ↓
1. Get current diary entry (or "No entry today")
2. Get all entries from past 7 days with previews
3. Get virtual profile analysis
4. Count chat history messages
5. Format and return (NO AI call)
    ↓
INSTANT RESPONSE (<1 second)
```

---

## 🟡 Route 3: GET /api/fumiko-history

**The Chat History Endpoint - "Show Me All Our Conversations"**

### Purpose
Retrieve complete chat history with Fumiko

### Request
```
GET /api/fumiko-history?limit=50
```

### Response
```json
{
    "success": true,
    "messages": [
        {
            "timestamp": "2024-01-15T10:30:00Z",
            "sender": "user",
            "message": "I'm feeling overwhelmed",
            "response": "Arey, what happened? Tell me...",
            "response_timestamp": "2024-01-15T10:30:05Z"
        },
        {
            "timestamp": "2024-01-14T18:45:00Z",
            "sender": "user",
            "message": "Had a good day today",
            "response": "Mujhe tell kar! What made it good?",
            "response_timestamp": "2024-01-14T18:45:03Z"
        }
    ]
}
```

### Parameters
- `limit` (optional, default=50): How many messages to return

### Use Cases
1. **Conversation Thread:** Show all chats in chronological order
2. **Relationship Building:** "You've been talking to Fumiko for 30 days"
3. **Pattern Analysis:** "Fumiko noticed you've asked about career 5 times"
4. **Re-engagement:** Show past conversations to remind users

### What Happens Behind Scenes
```
GET /api/fumiko-history?limit=50
    ↓
1. Query Firestore: /artifacts/{app_id}/users/{uid}/chat_history
2. Sort by timestamp (newest first)
3. Limit to 50 (or requested limit)
4. Return with sender info and timestamps
    ↓
INSTANT RESPONSE (<1 second)
```

---

## 🔄 How the Three Routes Work Together

### Typical User Journey

**Step 1: Check Context**
```
GET /api/fumiko-context
← "You have 7 entries and previous chats available"
```

**Step 2: Read Past Chats**
```
GET /api/fumiko-history?limit=5
← Shows last 5 conversations
```

**Step 3: Start Chat**
```
POST /api/fumiko-chat
{message: "I want to talk about something"}
→ Fumiko responds using all context
← Response saved automatically
```

**Step 4: Repeat**
Each new message in `/api/fumiko-chat` adds to history and next time will include it as context.

---

## 🏗️ Architecture

### Data Flow
```
Frontend
  ↓
Flask Routes (app.py)
  ├── /api/fumiko-chat → chat_system.chat_fumiko()
  ├── /api/fumiko-context → Helper functions
  └── /api/fumiko-history → Helper functions
  ↓
function.py
  ├── chat_system class
  └── send_gemini_prompt()
  ↓
Firestore (Database)
  ├── Diary entries
  ├── Virtual profile
  ├── Chat history
  └── User data
  ↓
Gemini API
  └── Generates responses
```

### Key Files
| File | Role |
|------|------|
| `app.py` | Flask routes, authentication, data fetching |
| `function.py` | chat_system class, Gemini API wrapper |
| `fumiko.txt` | 3000+ word persona definition |
| `firestore` | Stores entries, profile, history |

---

## 🎨 Fumiko's Behavior in Responses

### Voice & Tone
- **Slang:** Uses Hindi/Hinglish words ("Arey", "haan", "mujhe tell kar")
- **Empathy:** Always validates emotions first
- **Curiosity:** Asks specific questions, not generic ones
- **Character:** Stays as a supportive, artistic friend—NOT a therapist

### Strategy: "Mirror & Lamp"
1. **Mirror** - Reflect back what you said
2. **Recall** - Remember details from your past entries
3. **Lamp** - Ask questions that illuminate the path forward

### Example
```
User: "I failed my exam"

Fumiko's thought process:
- Mirror: Acknowledge the failure
- Recall: "You mentioned this in your entry 3 days ago"
- Lamp: "But what matters more - the exam or what you learned?"
```

---

## ⚡ Performance Notes

### Timing
- **`/api/fumiko-chat`:** 2-5 seconds (Gemini API call included)
- **`/api/fumiko-context`:** <100ms (database queries only)
- **`/api/fumiko-history`:** <100ms (single database query)

### Optimization Tips
1. Call `/api/fumiko-context` on page load (instant)
2. Show "Fumiko is thinking..." for 2-3 seconds while `/api/fumiko-chat` loads
3. Call `/api/fumiko-history` with `?limit=10` on first load, then lazy-load more

---

## 🔐 Security

All routes use `@auth_required` decorator:
- Only authenticated users can access
- User ID from session prevents accessing others' data
- Firestore rules enforce user isolation

---

## ✅ Ready to Use!

Your three routes are now:
- ✅ Properly integrated with `chat_system` class
- ✅ Free of code duplication
- ✅ Fully functional and tested
- ✅ Documented and ready for frontend integration

**Next step:** Hook these routes to your frontend UI!
