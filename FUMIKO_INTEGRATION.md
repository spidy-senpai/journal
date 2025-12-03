# 🤖 Fumiko AI Integration - Complete Guide

## Overview

Fumiko is a deeply personalized AI companion that uses your diary entries, virtual profile, and conversation history to provide meaningful, character-accurate responses. She reads between the lines and helps you find clarity while maintaining her unique personality.

## How It Works

### Architecture

```
User sends message
        ↓
/api/fumiko-chat endpoint
        ↓
Fetch context:
├── Current diary entry
├── Past 7 days entries
├── Virtual profile (personality insights)
├── Recent chat history (last 5 conversations)
└── Fumiko's persona data
        ↓
Build comprehensive prompt with all context
        ↓
Send to Gemini API with system instructions
        ↓
Get response from Fumiko
        ↓
Save to Firestore chat_history collection
        ↓
Return response to user
```

## API Endpoints

### 1. Chat with Fumiko - POST /api/fumiko-chat

**Purpose:** Send a message to Fumiko and get a personalized response

**Authentication:** Required (user must be logged in)

**Request:**
```json
{
    "message": "I've been feeling really anxious lately",
    "chat_id": "default"
}
```

**Response (Success - 200):**
```json
{
    "success": true,
    "response": "Haan haan, I can see that in your recent entries... Kya hua? Talk to me abt it.",
    "context_provided": {
        "has_current_entry": true,
        "past_entries_count": 5,
        "has_virtual_profile": true,
        "chat_history_messages": 3
    }
}
```

**Response (Error - 400/500):**
```json
{
    "error": "Error message here"
}
```

**How It Works:**
1. Receives your message
2. Fetches all context (entries, profile, history)
3. Sends to Gemini with Fumiko's persona
4. Returns personalized response
5. Saves to chat history automatically

### 2. Get Context Data - GET /api/fumiko-context

**Purpose:** Get summary of available context for display

**Authentication:** Required

**Response:**
```json
{
    "success": true,
    "current_entry": "Today was really tough, I felt...",
    "past_entries_count": 7,
    "past_entries": [
        {
            "date": "2024-01-15",
            "preview": "Had a great day with friends..."
        }
    ],
    "virtual_profile": {
        "personality_traits": ["introspective", "creative"],
        "emotional_state": "Reflective",
        "interests": ["reading", "art"],
        "has_profile": true
    },
    "chat_history_count": 5
}
```

### 3. Get Chat History - GET /api/fumiko-history

**Purpose:** Retrieve all past conversations with Fumiko

**Authentication:** Required

**Query Parameters:**
- `limit` (optional, default=50): Number of messages to return

**Response:**
```json
{
    "success": true,
    "messages": [
        {
            "timestamp": "2024-01-15T10:30:00",
            "sender": "user",
            "message": "I'm feeling overwhelmed",
            "response": "Kya hua? Let's talk abt it...",
            "response_timestamp": "2024-01-15T10:30:05"
        }
    ]
}
```

## Data Fumiko Uses

### 1. Current Entry
Your latest diary entry is used as the immediate context for Fumiko's response.

### 2. Past 7 Days Entries
The last 7 days of entries are analyzed to detect patterns:
- Recurring emotions or situations
- Progress or regression in certain areas
- Topics that appear multiple times

### 3. Virtual Profile
Your personality insights help Fumiko tailor advice:
- **Personality Traits**: How she understands you fundamentally
- **Emotional State**: Current psychological state
- **Interests & Hobbies**: What brings you joy
- **Habits & Patterns**: Your behavioral routines
- **Values & Priorities**: What matters most to you
- **Challenges & Concerns**: Areas you struggle with

### 4. Chat History
Recent conversations show:
- Patterns in what you discuss
- Previous advice and how you responded
- Ongoing concerns or celebrations

### 5. Fumiko's Persona
Loaded from `fumiko.txt` - contains:
- Her unique vocabulary and slang
- Emotional tendencies
- Humor style
- Relationship dynamic with you
- Values and beliefs

## Fumiko's Personality Traits

### Communication Style
- **Casual & Colloquial**: Uses Hindi/English mix with slang ("Haan haan," "Accha," "Kya hua")
- **Quick & Responsive**: Short replies for casual chat, deeper for serious topics
- **Playful**: Teasing but never hurtful
- **Emoji-heavy**: Uses emojis to convey tone

### Emotional Tendencies
- **Deeply Empathetic**: Offers genuine comfort
- **Supportive**: Provides motivation and practical advice
- **Optimistic**: Believes things will get better
- **Direct**: Can set boundaries politely

### Interaction Strategy: "The Mirror & The Lamp"
1. **Validate** - Acknowledge your emotion
2. **Recall** - Reference details you shared before
3. **Guide** - Ask questions to help you figure it out

## Database Schema

### Chat History Collection
```
/artifacts/
  └── default-journal-app-id/
      └── users/
          └── {uid}/
              └── chat_history/
                  ├── doc1: {
                  │   "timestamp": "2024-01-15T10:30:00",
                  │   "sender": "user",
                  │   "message": "...",
                  │   "chat_id": "default",
                  │   "response": "...",
                  │   "response_timestamp": "2024-01-15T10:30:05"
                  │ }
                  └── doc2: { ... }
```

## Frontend Integration Example

### HTML
```html
<div id="fumiko-chat">
    <div id="chat-messages"></div>
    <input type="text" id="user-message" placeholder="Talk to Fumiko...">
    <button id="send-btn">Send</button>
</div>
```

### JavaScript
```javascript
async function sendMessageToFumiko() {
    const message = document.getElementById('user-message').value;
    
    const response = await fetch('/api/fumiko-chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            chat_id: 'default'
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        // Display Fumiko's response
        displayMessage('fumiko', data.response);
        console.log('Context provided:', data.context_provided);
    } else {
        console.error('Error:', data.error);
    }
}

async function getContext() {
    const response = await fetch('/api/fumiko-context');
    const context = await response.json();
    
    console.log('Past entries:', context.past_entries_count);
    console.log('Your profile:', context.virtual_profile);
    console.log('Chat history:', context.chat_history_count);
}
```

## Configuration

### Models Used
- **Fumiko Chat**: `gemini-2.5-flash` (faster, more casual)
- **Profile Analysis**: `gemini-pro` (more thorough)

### Context Limits
- **Past Entries**: 7 days
- **Chat History**: Last 5 conversations (configurable)
- **Message Limit**: 50 characters minimum

## Important Features

### 1. Pattern Recognition
Fumiko analyzes your past entries to spot patterns:
- "I notice you mention sleep issues in 3 of your past entries..."
- "Seems like when you feel anxious, you tend to isolate..."
- "Every time you mention work, your mood shifts..."

### 2. Character Consistency
Fumiko maintains her personality across all conversations:
- Uses her unique vocabulary
- Follows her emotional patterns
- Maintains relationship dynamic with you
- Never breaks character

### 3. Privacy & Safety
- All conversations saved privately in your Firestore
- No data shared with external services (except Gemini API)
- Authentication required for all endpoints
- Emotional safety: Non-judgmental, supportive approach

### 4. Context Awareness
Fumiko understands:
- Your personality type
- Current emotional state
- Long-term patterns
- Recent conversations
- What you value

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Message empty | No text provided | Type a message and send |
| No context | First time chatting | Create a diary entry first |
| API not configured | GEMINI_API_KEY missing | Add key to .env |
| Empty response | Gemini timeout | Try again in a moment |

## Best Practices

### For Users
1. **Be Honest** - Fumiko works best with authentic feelings
2. **Write Diary Entries** - More context = better responses
3. **Revisit Patterns** - Let Fumiko point out what you might have missed
4. **Ask Questions** - Fumiko loves deep conversations
5. **Trust the Process** - She learns about you over time

### For Developers
1. **Check Rate Limits** - Gemini API has usage limits
2. **Handle Timeouts** - API calls may take 2-5 seconds
3. **Log Errors** - Monitor console for issues
4. **Test Without API** - Mock responses for testing
5. **Cache Context** - Consider caching if many requests

## Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Single chat | 2-5s | Includes Gemini API call |
| Fetch context | <1s | Local Firestore query |
| Chat history | <1s | Database retrieval |
| Save message | <1s | Firestore write |

## Future Enhancements

1. **Voice Input** - Speak to Fumiko instead of typing
2. **Image Sharing** - Upload photos with diary entries
3. **Weekly Summaries** - Fumiko generates weekly insights
4. **Mood Tracking** - Visual representation of emotional trends
5. **Recommendation Engine** - Suggestions based on patterns
6. **Multiple Personas** - Chat with Krishna too
7. **Offline Mode** - Basic responses without API
8. **Export Conversations** - Download chat history

## Troubleshooting

### "No Response from Fumiko"
- Check API key is set
- Verify internet connection
- Check Gemini API status
- Try again in a few seconds

### "Fumiko Breaking Character"
- She might be responding to an unusual input
- Try rephrasing your message
- Ensure diary entries provide context
- Report if persistent

### "Missing Chat History"
- Ensure you're logged in with correct account
- Check Firestore permissions
- Messages may not have saved if offline

### "Empty Virtual Profile"
- Run daily analysis at 12:00 AM UTC
- Or call POST /api/analyze-now manually
- Need at least one complete entry

## Database Maintenance

### Cleaning Old Chat History
```python
# Optional: Delete chats older than 90 days
def clean_old_chat_history(uid, days=90):
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    chat_ref = db.collection('artifacts').document('default-journal-app-id')\
        .collection('users').document(uid).collection('chat_history')
    
    old_messages = chat_ref.where('timestamp', '<', cutoff_date).stream()
    for msg in old_messages:
        msg.reference.delete()
```

## API Rate Limits

- Gemini: Check Google's current limits
- Firestore: 1M reads/day free tier
- Messages: No hard limit (respects Firestore limits)

## Security Considerations

✅ **API Key Protection**
- GEMINI_API_KEY in .env only
- Never exposed in responses

✅ **User Data Privacy**
- Each user's data isolated by UID
- No cross-user data access
- Encrypted in transit

✅ **Authentication**
- All endpoints require login
- Session-based access control
- Logged requests for audit

## Testing the Integration

### Quick Test
```bash
# 1. Start the app
python app.py

# 2. Create a diary entry
# (Use dashboard or API)

# 3. Send test message
curl -X POST http://localhost:5000/api/fumiko-chat \
  -H "Content-Type: application/json" \
  -b "session=your-session" \
  -d '{"message": "I am feeling great today"}'

# 4. Check response
# (Should get Fumiko's personalized response)
```

### Verify Context Loading
```bash
# Check what context is available
curl http://localhost:5000/api/fumiko-context \
  -b "session=your-session"

# Should show entries, profile, and history
```

---

## Summary

Fumiko is now fully integrated into your webapp with:
- ✅ 7-day entry context
- ✅ Virtual profile integration
- ✅ Chat history tracking
- ✅ Character consistency
- ✅ Pattern recognition
- ✅ Full error handling
- ✅ Privacy protection

**Start chatting with Fumiko!** She's ready to listen and help you find clarity.
