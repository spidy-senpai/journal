# Virtual Profile Analysis - Gemini API Integration

## Overview
This implementation adds automated daily analysis of diary entries using Google's Gemini API. Every day at 12:00 AM UTC, the system analyzes each user's latest diary entry and builds a comprehensive virtual profile stored in Firestore.

## Features

### 1. **Automated Daily Analysis**
- **Schedule**: Every day at 12:00 AM UTC (configurable)
- **Trigger**: Background scheduler (APScheduler)
- **Scope**: Analyzes the most recent entry for each user
- **Storage**: Results saved in `virtual_profile` collection

### 2. **Deep User Profiling**
The Gemini API extracts:
- **Personality Traits**: Core personality characteristics
- **Emotional State**: Current emotions and their intensity
- **Interests & Hobbies**: What the user enjoys
- **Habits & Patterns**: Behavioral patterns and habits
- **Values & Priorities**: What matters to the user
- **Challenges & Concerns**: Identified challenges
- **Behavioral Insights**: Key behavioral observations
- **Mental Health Indicators**: Both positive and concerning indicators
- **Relationship Insights**: Information about relationships
- **Summary**: 2-3 sentence summary of the user

### 3. **Data Storage Structure**
```
/artifacts/{app_id}/users/{uid}/virtual_profile/{timestamp}
{
    "timestamp": "2024-01-15T12:00:00.123456",
    "uid": "user-id",
    "personality_traits": ["trait1", "trait2", ...],
    "emotional_state": "description of emotional state",
    "interests_hobbies": ["interest1", "interest2", ...],
    "habits_patterns": ["habit1", "habit2", ...],
    "values_priorities": ["value1", "value2", ...],
    "challenges_concerns": ["challenge1", "challenge2", ...],
    "behavioral_insights": "detailed insights about behavior",
    "mental_health_indicators": "mental health observations",
    "relationship_insights": "relationship observations",
    "summary": "concise summary of the user"
}
```

## Setup Instructions

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

Required packages:
- `google-generativeai` - Gemini API client
- `APScheduler` - Background job scheduling
- `firebase-admin` - Firestore access
- `flask` - Web framework

### 2. **Configure Gemini API**

1. Get your API key from: https://makersuite.google.com/app/apikey
2. Create a `.env` file in the project root (or copy `.env.example`):
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

### 3. **Verify Requirements**
Ensure these are in your `requirements.txt`:
```
google-generativeai
APScheduler
```

## API Endpoints

### Manual Analysis Trigger (for testing)
```
POST /api/analyze-now
```

**Authentication**: Required (user must be logged in)

**Response**:
```json
{
    "success": true,
    "message": "Entry analyzed and profile updated",
    "analysis": {
        "personality_traits": [...],
        "emotional_state": "...",
        ...
    }
}
```

**Use Case**: Test the analysis functionality manually without waiting for 12 AM.

## How It Works

### Automated Daily Job
1. **Trigger**: 12:00 AM UTC every day
2. **Process**:
   - Fetches all users from Firestore
   - For each user, retrieves their most recent diary entry
   - Sends entry text to Gemini API with analysis prompt
   - Parses JSON response with user insights
   - Stores analysis in `virtual_profile` collection with timestamp
3. **Logging**: Console output shows which users were analyzed

### Manual Trigger (Testing)
1. Call POST `/api/analyze-now` while logged in
2. System analyzes your most recent entry
3. Returns analysis immediately
4. Stores result in your virtual_profile collection

## Error Handling

The system handles various error scenarios:

1. **Missing Gemini API Key**
   - Warning printed to console
   - `model` variable set to `None`
   - Endpoints return 500 error with "Gemini API not configured"

2. **No Entry to Analyze**
   - Skipped during automated job
   - `/api/analyze-now` returns 404 "No entry found"

3. **API Failures**
   - Logged to console with detailed error
   - Job continues processing other users
   - Manual endpoint returns 500 error

4. **Network Issues**
   - Automatically retried on next scheduled run
   - No blocking of other operations

## Scheduler Details

### APScheduler Configuration
```python
scheduler.add_job(
    func=daily_analysis_job,
    trigger="cron",
    hour=0,           # Midnight (UTC)
    minute=0,
    id='daily_analysis_job',
    name='Daily Virtual Profile Analysis',
    replace_existing=True
)
```

### Lifecycle
- **Start**: `start_scheduler()` called in `if __name__ == '__main__':`
- **Stop**: `stop_scheduler()` registered via `atexit.register()`
- **Check Status**: See console output for scheduler status

## Customization Options

### Change Analysis Time
In `app.py`, modify the scheduler job:
```python
scheduler.add_job(
    func=daily_analysis_job,
    trigger="cron",
    hour=14,           # 2:00 PM UTC
    minute=30,
    ...
)
```

### Modify Analysis Prompt
Edit the prompt in `analyze_entry_with_gemini()` function to customize what insights are extracted.

### Change Model
Current model: `gemini-pro`
You can change to other models:
```python
model = genai.GenerativeModel('gemini-1.5-pro')  # or other available models
```

## Testing

### Test 1: Manual Analysis
1. Log in to the application
2. Create or view a diary entry
3. Call: `POST /api/analyze-now`
4. Check Firestore for new entry in `virtual_profile` collection

### Test 2: Verify Entry Structure
1. Navigate to Firestore Console
2. Go to: `artifacts/default-journal-app-id/users/{your-uid}/virtual_profile`
3. Verify document contains all expected fields

### Test 3: Check Scheduler Status
1. Start the Flask app
2. Check console for: "✅ Scheduler started - Daily analysis scheduled for 12:00 AM UTC"
3. App logs will show analysis runs at scheduled time

## Monitoring & Debugging

### Check Scheduler Status
```bash
# In app.py, scheduler is stored as global variable
# Can be checked via Python console or added to admin endpoint
```

### View Analysis Results
1. **Firestore Console**: Navigate to `artifacts/default-journal-app-id/users/{uid}/virtual_profile`
2. **Sample Query**: Get all analyses for a user (sorted by timestamp)
3. **Analysis History**: Each timestamp represents a separate analysis run

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Gemini API not configured" | Missing GEMINI_API_KEY in .env | Add API key to .env and restart app |
| No analysis saved | Entry has no text field | Ensure entries have `text` field populated |
| Scheduler not running | `start_scheduler()` not called | Check if running in `if __name__ == '__main__':` |
| Analysis takes long time | API rate limits or slow entry | Increase timeout or implement queue system |

## Database Schema

### Virtual Profile Collection
```
collection('virtual_profile')
├── document(timestamp_1)
│   ├── timestamp: string (ISO 8601)
│   ├── uid: string
│   ├── personality_traits: array
│   ├── emotional_state: string
│   ├── interests_hobbies: array
│   ├── habits_patterns: array
│   ├── values_priorities: array
│   ├── challenges_concerns: array
│   ├── behavioral_insights: string
│   ├── mental_health_indicators: string
│   ├── relationship_insights: string
│   └── summary: string
├── document(timestamp_2)
│   └── ... (older analysis)
```

## Performance Considerations

1. **Number of Users**: Scheduler scales linearly with user count
2. **API Rate Limits**: Gemini API has rate limits (check documentation)
3. **Database Queries**: Uses efficient Firestore queries
4. **Memory**: Background scheduler uses minimal memory

## Security & Privacy

1. **API Key**: Stored in .env, not committed to git
2. **Data**: Analyses stored in Firestore with user-specific paths
3. **Authentication**: `/api/analyze-now` requires login via `@auth_required`
4. **No Logging**: Sensitive data not logged to files

## Future Enhancements

1. **Aggregate Profiles**: Combine multiple analyses for long-term trends
2. **Insights Dashboard**: Display user profiles in UI
3. **Notifications**: Alert user when analysis is available
4. **Multi-language Support**: Analyze entries in different languages
5. **Export Functionality**: Download analyses as PDF/JSON
6. **Analysis History**: Track how profile changes over time

## References

- [Google Gemini API Documentation](https://ai.google.dev/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Firebase Firestore Documentation](https://firebase.google.com/docs/firestore)
