# API Reference - Virtual Profile Analysis Endpoints

## Manual Analysis Trigger

### Endpoint
```
POST /api/analyze-now
```

### Description
Manually trigger analysis of the current logged-in user's most recent diary entry. This is useful for testing without waiting for the 12:00 AM UTC scheduled job.

### Authentication
Required. User must be logged in (session must be valid).

### Request
```bash
POST http://localhost:5000/api/analyze-now
Header: Cookie: session=<user-session-cookie>
```

### Response (Success - 200)
```json
{
    "success": true,
    "message": "Entry analyzed and profile updated",
    "analysis": {
        "timestamp": "2024-01-15T12:00:00.123456",
        "uid": "user-123",
        "personality_traits": ["introspective", "creative", "thoughtful"],
        "emotional_state": "Reflective and contemplative",
        "interests_hobbies": ["reading", "writing", "hiking"],
        "habits_patterns": ["daily journaling", "morning walks"],
        "values_priorities": ["personal growth", "creativity", "relationships"],
        "challenges_concerns": ["perfectionism", "work-life balance"],
        "behavioral_insights": "Shows strong introspective tendencies...",
        "mental_health_indicators": "Positive: Good self-reflection. Note: Some anxiety patterns.",
        "relationship_insights": "Values close relationships, mentions family frequently",
        "summary": "Introspective and creative individual with strong values around personal growth."
    }
}
```

### Response (Error - 500 - API Not Configured)
```json
{
    "error": "Gemini API not configured"
}
```

### Response (Error - 404 - No Entry Found)
```json
{
    "error": "No entry found to analyze"
}
```

### Response (Error - 500 - Other Error)
```json
{
    "error": "Error description from exception"
}
```

### Example Usage

**Python:**
```python
import requests
import json

# Assuming you have a valid session cookie
cookies = {'session': 'your-session-cookie-value'}

response = requests.post(
    'http://localhost:5000/api/analyze-now',
    cookies=cookies
)

if response.status_code == 200:
    data = response.json()
    analysis = data['analysis']
    print(f"Personality Traits: {analysis['personality_traits']}")
    print(f"Emotional State: {analysis['emotional_state']}")
    print(f"Summary: {analysis['summary']}")
else:
    print(f"Error: {response.json()}")
```

**JavaScript/Fetch:**
```javascript
async function analyzeEntry() {
    const response = await fetch('/api/analyze-now', {
        method: 'POST',
        credentials: 'include'  // Include cookies
    });
    
    if (response.ok) {
        const data = await response.json();
        console.log('Analysis:', data.analysis);
    } else {
        const error = await response.json();
        console.error('Error:', error);
    }
}
```

**cURL:**
```bash
# Get session cookie first (after login)
curl -c cookies.txt -X POST http://localhost:5000/login \
  -d "email=user@example.com&password=password"

# Use cookie to call analyze endpoint
curl -b cookies.txt -X POST http://localhost:5000/api/analyze-now
```

## Scheduled Daily Analysis

### Schedule
- **Time**: 12:00 AM UTC (midnight UTC)
- **Frequency**: Every day
- **Trigger**: APScheduler background job

### What It Does
1. Fetches all users from Firestore
2. For each user, gets their most recent diary entry
3. Sends the entry to Gemini API for analysis
4. Parses the JSON response with insights
5. Stores the analysis in Firestore under `virtual_profile` collection
6. Logs progress to console

### Example Console Output
```
🔄 Running daily virtual profile analysis job at 2024-01-15 12:00:00.123456
✅ Analyzed entry for user user-123
✅ Analyzed entry for user user-456
✅ Daily analysis job completed. Analyzed 2 users.
```

### Error Handling
- Missing entries: Skipped silently
- API errors: Logged, job continues with next user
- Network issues: Logged, job continues
- Overall job failure: Logged to console

## Response Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | String (ISO 8601) | When the analysis was performed |
| `uid` | String | User ID (for reference) |
| `personality_traits` | Array of Strings | Core personality characteristics |
| `emotional_state` | String | Current emotional state and intensity |
| `interests_hobbies` | Array of Strings | Activities and interests the user enjoys |
| `habits_patterns` | Array of Strings | Behavioral patterns and recurring habits |
| `values_priorities` | Array of Strings | What matters most to the user |
| `challenges_concerns` | Array of Strings | Identified challenges or areas of concern |
| `behavioral_insights` | String | Detailed behavioral observations and patterns |
| `mental_health_indicators` | String | Mental health observations (positive and concerning) |
| `relationship_insights` | String | Insights about relationships mentioned in entry |
| `summary` | String | 2-3 sentence summary of the user |

## Storage Details

### Firestore Path
```
/artifacts/{app_id}/users/{uid}/virtual_profile/{timestamp}
```

### Database Collection
- **Collection Name**: `virtual_profile`
- **Parent**: User document
- **Document ID**: ISO 8601 timestamp (unique per analysis)
- **Retention**: Indefinite (consider implementing cleanup policy for large-scale apps)

### Example Firestore Document
```
Document ID: 2024-01-15T12:00:00.123456
{
    "timestamp": "2024-01-15T12:00:00.123456",
    "uid": "user-123",
    "personality_traits": [...],
    "emotional_state": "...",
    ...
}
```

## Rate Limiting

Currently, there are no rate limits on `/api/analyze-now`. Consider implementing:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/analyze-now', methods=['POST'])
@limiter.limit("5 per hour")  # Max 5 analyses per hour per user
@auth_required
def manual_analysis():
    ...
```

## Testing Scenarios

### Scenario 1: Happy Path
1. User is logged in
2. User has created a diary entry with text
3. Call `/api/analyze-now`
4. Receive analysis with all fields populated
5. Analysis stored in Firestore

### Scenario 2: No Existing Entry
1. User is logged in
2. User has NO diary entries
3. Call `/api/analyze-now`
4. Receive 404 error: "No entry found to analyze"
5. No database write occurs

### Scenario 3: API Not Configured
1. `GEMINI_API_KEY` not set in .env
2. Call `/api/analyze-now`
3. Receive 500 error: "Gemini API not configured"

### Scenario 4: User Not Authenticated
1. No valid session cookie
2. Call `/api/analyze-now`
3. Receive 401 error (from @auth_required decorator)

## Performance Considerations

### Response Time
- **Single Analysis**: 2-5 seconds (API call to Gemini)
- **Manual Endpoint**: ~3-6 seconds (includes Firestore write)
- **Daily Job**: ~30-150 minutes for 1000 users

### Concurrent Requests
- Manual endpoint: Sequential processing
- Daily job: Sequential per user (no concurrency)
- Database: Firestore handles concurrent writes

### Optimization Tips
1. Implement request queuing for high volume
2. Use Firestore batch writes for large-scale jobs
3. Cache analysis results if needed
4. Implement exponential backoff for API errors

## Monitoring & Logging

### Console Logs
```
✅ Scheduler started - Daily analysis scheduled for 12:00 AM UTC
🔄 Running daily virtual profile analysis job at 2024-01-15 12:00:00
✅ Analyzed entry for user user-123
⚠️ Error processing user user-456: <error details>
✅ Daily analysis job completed. Analyzed 1 users.
```

### How to Monitor
1. **Check console**: Watch for daily job at 12:00 AM UTC
2. **Verify Firestore**: Query `virtual_profile` collection for new documents
3. **Manual test**: Call `/api/analyze-now` and verify response

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| 500 "Gemini API not configured" | Missing API key | Add GEMINI_API_KEY to .env |
| 404 "No entry found" | No diary entries created | Create an entry first |
| Slow response | Gemini API delay | Normal, takes 2-5 seconds |
| Analysis not in Firestore | Write error | Check Firestore rules and permissions |
| Scheduler not running | Not started | Check console for startup message |

---

**Last Updated**: 2024-01-15
**Status**: Fully Implemented
**API Version**: 1.0
