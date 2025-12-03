# 🔧 Troubleshooting Guide

## Common Issues & Solutions

### 1. "Gemini API not configured" Error

**Symptoms:**
- POST /api/analyze-now returns 500 error
- Error message: "Gemini API not configured"
- Console shows: "⚠️ Warning: GEMINI_API_KEY not found in environment variables"

**Causes:**
- GEMINI_API_KEY not set in .env
- .env file not in correct location
- App not restarted after adding key
- Empty or invalid API key

**Solutions:**

**Step 1: Verify .env File Exists**
```bash
# Check if .env file exists in project root
ls -la .env           # macOS/Linux
dir .env              # Windows PowerShell
```

**Step 2: Verify API Key Format**
```
GEMINI_API_KEY=AIzaSy...  # Should start with AIzaSy
```

**Step 3: Restart Flask App**
```bash
# Stop the app (Ctrl+C)
# Then restart:
python app.py
```

**Step 4: Check Console Output**
```
Look for: ✅ "Scheduler started - Daily analysis scheduled"
If missing, restart app
```

**Step 5: Get Fresh API Key**
- Visit: https://makersuite.google.com/app/apikey
- Delete old key if expired
- Create new key
- Copy and paste into .env

---

### 2. "No entry found to analyze" Error

**Symptoms:**
- POST /api/analyze-now returns 404 error
- Error message: "No entry found to analyze"

**Causes:**
- User has not created any diary entries
- All entries are empty (no text)
- Firestore entries collection is empty

**Solutions:**

**Step 1: Create a Diary Entry**
1. Log into the application
2. Go to the diary/journal page
3. Write some text in the editor
4. Click "Save Entry" button
5. Verify entry appears in "Past Entries"

**Step 2: Verify Entry Has Text**
- Entry must have actual text content
- Empty entries are skipped
- Minimum: Few sentences recommended

**Step 3: Check Entry in Firestore**
```python
from firebase_config import db
uid = "your-user-id"
entries = db.collection('artifacts').document('default-journal-app-id')\
    .collection('users').document(uid)\
    .collection('entries').stream()

for doc in entries:
    data = doc.to_dict()
    print(f"Entry {doc.id}:")
    print(f"  Has text: {bool(data.get('text'))}")
    print(f"  Text length: {len(data.get('text', ''))}")
```

**Step 4: Try Again**
- Create entry
- Wait 5 seconds
- Call /api/analyze-now again

---

### 3. Scheduler Not Running

**Symptoms:**
- Analysis not running at 12:00 AM UTC
- No logs appearing at scheduled time
- Console doesn't show scheduler startup message

**Causes:**
- `start_scheduler()` not being called
- Flask app not running
- Running in wrong environment

**Solutions:**

**Step 1: Verify Startup Message**
```bash
# When you start app, should see:
# ✅ Scheduler started - Daily analysis scheduled for 12:00 AM UTC

# If not appearing:
# - App may be crashing on startup
# - Check for errors above the startup message
```

**Step 2: Check if App is Running**
```bash
# Verify Flask app is running
# Should see messages like:
# * Running on http://127.0.0.1:5000
# * WARNING: This is a development server...
```

**Step 3: Verify Scheduler Code**
```python
# app.py, last 5 lines should be:
if __name__ == '__main__':
    start_scheduler()
    app.run(debug=True)
```

**Step 4: Check for Errors**
- Look for red error messages in console
- Search for "Error" or "Exception" in output
- Check that imports succeeded

**Step 5: Manual Test**
```bash
# Test if scheduler works at all:
POST /api/analyze-now

# If this returns 200 and analysis appears:
# - Scheduler code is working
# - Just wait for 12:00 AM UTC
```

---

### 4. "Unable to connect to Firestore" Error

**Symptoms:**
- POST /api/analyze-now returns 500 error
- Error mentions Firestore or database connection
- Cannot retrieve entries

**Causes:**
- firebase-auth.json not found
- Firestore rules blocking access
- Network connectivity issue
- Firebase project not initialized

**Solutions:**

**Step 1: Verify Firebase Credentials File**
```bash
# Check if firebase-auth.json exists
ls -la firebase-auth.json     # macOS/Linux
dir firebase-auth.json        # Windows

# Should be in project root
```

**Step 2: Check Firestore Rules**
1. Go to Firebase Console
2. Firestore Database → Rules
3. Rules should allow authenticated users:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /artifacts/{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

**Step 3: Test Firestore Connection**
```python
from firebase_config import db

try:
    db.collection('artifacts').document('test').set({'test': True})
    print("✅ Firestore connection works!")
except Exception as e:
    print(f"❌ Firestore error: {e}")
```

**Step 4: Check Network**
- Verify internet connection
- Try opening firebase.google.com
- Check if any firewall blocking

---

### 5. Slow Analysis Response

**Symptoms:**
- POST /api/analyze-now takes 30+ seconds
- Timeout errors
- Response very slow

**Causes:**
- Gemini API slow response
- Network latency
- Server overload
- Firestore slow writes

**Solutions:**

**Step 1: Check Network Speed**
```bash
# Test internet speed
ping google.com

# Should see response times <100ms
```

**Step 2: Expected Response Times**
- Gemini API call: 2-5 seconds (normal)
- Firestore write: <1 second (normal)
- Total: 3-6 seconds (normal)

**Step 3: Optimize Gemini Prompt**
If consistently slow:
```python
# In app.py, line ~360, try shorter prompt:
prompt = f"""Analyze this diary entry briefly:
{entry_text[:1000]}  # Limit to 1000 chars

Provide JSON with: personality_traits, emotional_state, interests_hobbies, summary"""
```

**Step 4: Check System Resources**
```bash
# Check CPU and memory usage
# If system is slow, Gemini API will be too
```

---

### 6. Analysis Results Empty or Incomplete

**Symptoms:**
- Analysis saved but missing fields
- Some fields have empty arrays
- Only partial data returned

**Causes:**
- Gemini API couldn't parse entry properly
- Prompt didn't extract all fields
- Entry text too short or unclear

**Solutions:**

**Step 1: Verify Entry Content**
- Entry should have multiple sentences
- Minimum 2-3 paragraphs recommended
- Should contain personal thoughts/feelings

**Step 2: Check Stored Analysis**
```python
from firebase_config import db

uid = "your-user-id"
analyses = db.collection('artifacts').document('default-journal-app-id')\
    .collection('users').document(uid)\
    .collection('virtual_profile').stream()

for doc in analyses:
    data = doc.to_dict()
    print(f"\nAnalysis from {doc.id}:")
    for key, value in data.items():
        print(f"  {key}: {value}")
```

**Step 3: Test with Longer Entry**
- Create detailed diary entry (500+ words)
- Include thoughts, feelings, observations
- Try analysis again with /api/analyze-now

**Step 4: Check Gemini Response**
Add temporary debug code in app.py:
```python
def analyze_entry_with_gemini(entry_text, uid):
    # ... existing code ...
    response = model.generate_content(prompt)
    print(f"Raw Gemini response:\n{response.text}")
    # Continue with parsing
```

---

### 7. Duplicate Analyses

**Symptoms:**
- Multiple analyses created at same time
- Duplicate entries in virtual_profile collection

**Causes:**
- `/api/analyze-now` called multiple times
- Scheduler and manual trigger ran together
- Flask debug mode reloading

**Solutions:**

**Step 1: Check Request Frequency**
- Only call /api/analyze-now once
- Don't refresh page multiple times
- Wait for response before calling again

**Step 2: Disable Debug Mode for Testing**
```python
# In app.py, change:
if __name__ == '__main__':
    start_scheduler()
    app.run(debug=False)  # Change to False
```

**Step 3: Check Firestore**
If duplicates exist:
```python
# Delete duplicates from Firestore Console:
# 1. Go to virtual_profile collection
# 2. Check document timestamps
# 3. Delete duplicate entries with same timestamp
```

---

### 8. Firebase Double Initialization Error

**Symptoms:**
- Error: "Firebase app already exists"
- Multiple Firebase instances

**Causes:**
- Multiple Firebase initialization calls
- Circular imports in code

**Solutions:**

**Step 1: Check firebase_config.py**
Should have:
```python
if not firebase_admin._apps:
    firebase_admin.initialize_app(...)
db = firestore.client()
```

**Step 2: Check app.py Imports**
Should be:
```python
from firebase_config import db  # Import only db, not initialize
```

Should NOT have:
```python
import firebase_admin  # Don't do this
firebase_admin.initialize_app(...)  # Don't do this
```

**Step 3: Restart App**
```bash
python app.py
```

---

### 9. Scheduler Still Runs Even After App Stops

**Symptoms:**
- Processes still running after Ctrl+C
- Python process doesn't fully terminate
- Port still in use

**Causes:**
- Background scheduler thread not cleaning up
- Daemon threads not properly configured

**Solutions:**

**Step 1: Force Kill Process**
```bash
# Find process ID
lsof -i :5000          # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process
kill -9 <PID>          # macOS/Linux
taskkill /PID <PID> /F # Windows
```

**Step 2: Verify Port Clear**
```bash
# Test if port 5000 is free
curl http://localhost:5000

# Should get "Connection refused"
```

**Step 3: Restart App**
```bash
python app.py
```

---

### 10. Analysis Never Runs at 12:00 AM UTC

**Symptoms:**
- No analyses created at scheduled time
- Console doesn't show job running
- Scheduler started but job doesn't execute

**Causes:**
- System time not in UTC
- Scheduler job not properly configured
- App crashes at midnight

**Solutions:**

**Step 1: Check System Time**
```bash
# View current UTC time
date -u              # macOS/Linux
powershell (Get-Date).ToUniversalTime()  # Windows
```

**Step 2: Manual Test Before Midnight**
```bash
# Call function manually to verify it works:
POST /api/analyze-now

# If this works, job will work at midnight
```

**Step 3: Check Scheduler Configuration**
```python
# In app.py around line 519:
scheduler.add_job(
    func=daily_analysis_job,
    trigger="cron",
    hour=0,        # ← Should be 0 for midnight UTC
    minute=0,
    ...
)
```

**Step 4: Enable Scheduler Logging**
```python
import logging
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
```

**Step 5: Monitor Logs**
- Leave app running before midnight
- Watch console output
- Should see analysis job start at 12:00 AM UTC

---

## Diagnostic Checklist

Run through these to diagnose issues:

### Basic Setup
- [ ] GEMINI_API_KEY in .env
- [ ] firebase-auth.json in project root
- [ ] requirements.txt installed
- [ ] Flask app starts without errors

### Firestore
- [ ] Can connect to Firestore
- [ ] Entries saved successfully
- [ ] Current user logged in

### Scheduler
- [ ] Console shows "✅ Scheduler started"
- [ ] /api/analyze-now endpoint works
- [ ] Manual analysis returns result

### Analysis
- [ ] Analysis contains data
- [ ] Analysis saved in virtual_profile
- [ ] Timestamps correct

---

## Getting Help

### Check These Files First
1. **QUICK_START.md** - Basic setup
2. **GEMINI_INTEGRATION.md** - Detailed docs
3. **API_REFERENCE.md** - Endpoint specs

### Debug Output to Check
```bash
# Look for these in console:
✅ Scheduler started              # If missing, scheduler not running
⚠️ GEMINI_API_KEY not found       # If appearing, add API key
✅ Analyzed entry for user        # Shows successful analyses
❌ Error                          # Shows what went wrong
```

### Test Commands
```bash
# Test API key setup
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"

# Test Gemini import
python -c "import google.generativeai; print('OK')"

# Test Firestore connection
python -c "from firebase_config import db; print(db)"
```

---

## Production Troubleshooting

### Issue: Scheduler Doesn't Survive App Restart
**Solution**: Use proper WSGI server with separate scheduler process

### Issue: High Latency on Scheduled Job
**Solution**: Implement queue system (Celery/RQ)

### Issue: Rate Limiting from Gemini API
**Solution**: Implement exponential backoff in retry logic

### Issue: Memory Leak from Scheduler
**Solution**: Ensure jobs complete properly, implement cleanup

---

## Still Need Help?

Check the comprehensive documentation:
- QUICK_START.md (5-min setup)
- GEMINI_INTEGRATION.md (full details)
- API_REFERENCE.md (endpoints)
- ARCHITECTURE_OVERVIEW.md (how it works)

Or review the code comments in app.py for inline documentation.

---

**Last Updated**: 2024-01-15
**Status**: Complete
