# 📔 Fumiko Journal App

A beautiful, feature-rich journal application with AI-powered diary companions and intelligent entry analysis.

## ✨ Features

### Core Features
- 📝 **Rich Text Editor** - Write and format diary entries with ease
- 🎨 **Multiple Themes** - Dark, Light, Sepia, Blue, Green themes
- 📸 **Media Support** - Add images, videos, documents, and voice notes
- 🗂️ **Organized Storage** - All entries securely stored in Firestore
- 🔐 **Secure Authentication** - Google Sign-in & Email/Password auth

### AI Companions
- **Fumiko** - Supportive companion trained on your diary patterns
- **Krishna** - Philosophical guide for reflection
- 💬 **Smart Chat** - Talk to AI models trained on your entries
- 📊 **Chat History** - All conversations saved and retrievable

### Smart Analysis
- 🤖 **AI Profile Analysis** - Automatic daily personality analysis using Gemini
- 📈 **Behavioral Insights** - Track emotional patterns and interests
- 🎯 **Personalized Responses** - AI companions understand your writing style
- 📅 **Daily Scheduling** - Automatic analysis runs at 12:00 AM UTC

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Firebase account
- Cloudinary account (for media uploads)
- Google Gemini API key

### Installation

1. **Clone and setup**
   ```bash
   git clone https://github.com/malasheohar55-hub/journal.git
   cd journal
   pip install -r requirements.txt
   ```

2. **Configure environment** (create `.env` file)
   ```
   SECRET_KEY=your-secret-key
   GEMINI_API_KEY=your-gemini-api-key
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```

3. **Setup Firebase**
   - Add `firebase-auth.json` to project root
   - Configure Firestore security rules

4. **Run the app**
   ```bash
   python app.py
   ```

5. **Access**
   - Open `http://localhost:5000`
   - Sign up or login
   - Start journaling!

## 📁 Project Structure

```
journal/
├── app.py                          # Main Flask application
├── crud.py                         # Database operations
├── firebase_config.py              # Firebase setup
├── function.py                     # AI companion logic
├── requirements.txt                # Python dependencies
│
├── static/
│   ├── styles.css                  # Main styles
│   ├── dashboard_styles.css        # Dashboard styling
│   ├── firebase-config.js          # Firebase client config
│   ├── login-auth.js               # Authentication logic
│   └── *.js                        # Other scripts
│
├── templates/
│   ├── dashboard.html              # Main editor
│   ├── login.html                  # Login page
│   ├── signup.html                 # Registration page
│   ├── home.html                   # Landing page
│   └── *.html                      # Other templates
│
├── uploads/                        # Uploaded files storage
├── firebase-auth.json              # Firebase credentials
└── .env                            # Environment variables
```

## 🔌 Key API Endpoints

### Authentication
- `POST /auth` - Verify Firebase token
- `GET /logout` - Logout user

### Journal Entries
- `POST /api/entries` - Save new entry with media
- `GET /api/entries` - Get all past entries
- `GET /api/entries/<date_id>` - Get specific entry
- `DELETE /api/entries/<date_id>` - Delete entry

### AI Chat
- `POST /api/fumiko` - Chat with Fumiko AI
- `POST /api/krishna` - Chat with Krishna AI
- `GET /api/chat-history` - Get conversation history

### Analysis
- `POST /api/analyze-now` - Manually trigger analysis
- `GET /api/fumiko-history` - Get all Fumiko conversations

## 🤖 AI Companions

### Fumiko
Supportive companion that learns from your diary entries:
- Understands your writing style
- Responds with empathy
- References your past entries
- Helps you reflect on patterns

### Krishna
Philosophical guide for deeper reflection:
- Asks thought-provoking questions
- Offers wisdom-based perspectives
- Encourages introspection
- Placeholder for custom logic

## 💾 Data Storage

### Firestore Structure
```
artifacts/
└── default-journal-app-id/
    └── users/
        └── {user-id}/
            ├── entries/
            │   └── {YYYY-MM-DD}/
            │       ├── title
            │       ├── blocks[]
            │       └── created_at
            ├── models/
            │   ├── fumiko/
            │   │   └── messages/
            │   │       ├── message
            │   │       ├── response
            │   │       └── timestamp
            │   └── krishna/
            │       └── messages/
            └── virtual_profile/
                └── {timestamp}/
                    ├── personality_traits
                    ├── emotional_state
                    ├── interests_hobbies
                    └── ...
```

## 🔒 Security

- **Authentication**: Firebase Auth (Google + Email)
- **Session Management**: Secure session cookies
- **HTTPS**: Enforced for production
- **Data Privacy**: User data isolated by UID
- **API Keys**: Stored in environment variables
- **Media Upload**: Cloudinary with folder organization

## ⚙️ Configuration

### Change AI Analysis Time
Edit `app.py`, find scheduler configuration:
```python
scheduler.add_job(
    func=daily_analysis_job,
    trigger="cron",
    hour=0,    # Change to desired hour (UTC)
    minute=0,
    ...
)
```

### Customize Gemini Model
Edit `app.py`:
```python
model = genai.GenerativeModel('gemini-pro')  # Change model name
```

### Adjust Upload Limits
Edit `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

## 🧪 Testing

### Test Image Upload
1. Add image via "Attach" button
2. Check browser console for logs
3. Save entry
4. Verify in Firestore

### Test AI Chat
1. Write diary entry
2. Click AI Chat button (💬)
3. Select companion
4. Type message
5. Check chat history saved

### Test Daily Analysis
Before 12:00 AM UTC, test manually:
```bash
curl -X POST http://localhost:5000/api/analyze-now \
  -H "Authorization: Bearer {your-token}"
```

## 📚 File Specifications

### Entry Blocks Support
- **Text**: Plain text with formatting
- **Image**: JPEG, PNG, WebP (uploaded to Cloudinary)
- **Video**: MP4, WebM (uploaded to Cloudinary)
- **Document**: PDF, DOCX, TXT (uploaded to Cloudinary)
- **Voice**: WebM audio (uploaded to Cloudinary)

### Media Upload Limits
- **Max file size**: 100MB per file
- **Total form data**: 100MB max
- **Storage**: Cloudinary (secure URLs returned)

## 🐛 Troubleshooting

### Images not saving?
1. Check Cloudinary credentials in `.env`
2. Verify file size < 100MB
3. Check browser console for upload logs
4. Restart Flask server

### Chat not working?
1. Verify GEMINI_API_KEY is set
2. Check Firestore write permissions
3. Ensure user is authenticated
4. Check chat history collection exists

### Auth failing?
1. Verify Firebase config in `firebase-config.js`
2. Check `firebase-auth.json` exists
3. Ensure domain is in Firebase authorized domains
4. Try incognito/private mode

## 🌐 Deployment

### Production Checklist
- [ ] Set `debug=False` in app.py
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Set secure session cookies
- [ ] Configure Firebase security rules
- [ ] Add domain to Firebase authorized domains
- [ ] Test all API endpoints
- [ ] Monitor Firestore usage

### Deploy to Heroku
```bash
heroku create your-app-name
heroku config:set GEMINI_API_KEY=your-key
git push heroku main
```

## 📊 Database Queries

### Get user's latest entries (JavaScript)
```javascript
const entriesRef = db.collection('artifacts')
  .document('default-journal-app-id')
  .collection('users')
  .document(uid)
  .collection('entries')
  .orderBy('created_at', 'desc')
  .limit(10);
```

### Analyze usage (Python)
```python
# Get entries count by date
entries_ref = db.collection('artifacts').document('default-journal-app-id')\
    .collection('users').document(uid).collection('entries')
entries = entries_ref.stream()
print(f"Total entries: {sum(1 for _ in entries)}")
```

## 🤝 Contributing

Contributions welcome! Areas to improve:
- [ ] Mobile app
- [ ] Export to PDF
- [ ] Entry reminders
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Offline support

## 📝 License

MIT License - feel free to use for personal projects

## 👤 Author

**malasheohar55-hub** - [GitHub Profile](https://github.com/malasheohar55-hub)

## 🎯 Future Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Entry reminders & notifications
- [ ] Export to PDF/Word
- [ ] Multi-language AI support
- [ ] Team collaboration features
- [ ] Backup & sync
- [ ] Offline mode

---

**Happy journaling! 📔✨**
