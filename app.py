from flask import Flask, redirect, render_template, request, make_response, session, abort, jsonify, url_for
import secrets
from functools import wraps
from firebase_admin import firestore, auth
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv
from crud import upload_file_to_cloudinary
from firebase_config import db
import base64
from io import BytesIO
import google.generativeai as genai
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import time

load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    print("⚠️ Warning: GEMINI_API_KEY not found in environment variables")
    model = None

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Increase file upload limits to handle large media files
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['MAX_FORM_MEMORY_SIZE'] = 100 * 1024 * 1024  # 100MB max form data

# CORS support for web tunnels
from flask_cors import CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = False # Ensure cookies are sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)  # Adjust session expiration as needed
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Can be 'Strict', 'Lax', or 'None'

# Firebase is already initialized in firebase_config.py
# Just import db from there (done above)

########################################
""" Authentication and Authorization """

# Decorator for routes that require authentication
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if 'user' not in session:
            return redirect(url_for('login'))
        else:
            return f(*args, **kwargs)
    return decorated_function

@app.route('/auth', methods=['POST'])
def authorize():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return "Unauthorized", 401

    token = token[7:]  # Strip off 'Bearer ' to get the actual token

    try:
        decoded_token = auth.verify_id_token(token, check_revoked=True, clock_skew_seconds=60)
        session['user'] = decoded_token
        return redirect(url_for('dashboard'))
    except:
        return "Unauthorized", 401
    else:
        return render_template('login.html')


#####################
""" Public Routes """

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')

@app.route('/signup')
def signup():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('signup.html')

@app.route('/reset-password')
def reset_password():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('forgot_password.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session', '', expires=0)
    return response

##############################################
""" Private Routes (Require authorization) """

@app.route('/dashboard')
@auth_required
def dashboard():
    print(session)
    return render_template('dashboard.html')

#########################################################
""" Chat History Management """

def save_chat_history(uid, chat_id, message, sender, response=None, model_name='fumiko'):
    """Save chat message to Firestore for a specific model"""
    try:
        # Save to model-specific messages subcollection
        chat_ref = db.collection('artifacts').document('default-journal-app-id').collection('users').document(uid).collection('models').document(model_name).collection('messages')
        
        doc_data = {
            'timestamp': datetime.utcnow(),
            'sender': sender,
            'message': message,
            'chat_id': chat_id
        }
        
        if response:
            doc_data['response'] = response
            doc_data['response_timestamp'] = datetime.utcnow()
        
        chat_ref.add(doc_data)
        return True
    except Exception as e:
        print(f"Error saving chat history: {e}")
        return False


def get_chat_history(uid, limit=10, model_name='fumiko'):
    """Retrieve chat history for a specific model"""
    try:
        # Query from model-specific messages subcollection
        chat_ref = db.collection('artifacts').document('default-journal-app-id').collection('users').document(uid).collection('models').document(model_name).collection('messages')
        
        # Get recent messages
        messages = chat_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
        
        chat_history = []
        for msg_doc in messages:
            chat_history.append(msg_doc.to_dict())
        
        # Reverse to get chronological order
        return list(reversed(chat_history))
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return []


@app.route('/api/chat-history', methods=['GET'])
@auth_required
def get_model_chat_history():
    """Fetch chat history for a specific model"""
    try:
        uid = session['user']['uid']
        model_name = request.args.get('model', 'fumiko')
        limit = request.args.get('limit', 50, type=int)
        
        chat_history = get_chat_history(uid, limit=limit, model_name=model_name)
        
        return jsonify({
            'success': True,
            'messages': chat_history,
            'model': model_name
        }), 200
    except Exception as e:
        print(f"Error in get_model_chat_history: {e}")
        return jsonify({'error': str(e)}), 500


#########################################################
""" AI Chat Endpoints """

from function import chat_system

@app.route('/api/krishna', methods=['POST'])
@auth_required
def chat_krishna():
    """Handle chat messages for Krishna model"""
    try:
        uid = session['user']['uid']
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', '')
        chat_id = data.get('chat_id', 'default')
        
        print(f"Krishna - Message: {message}")
        print(f"Krishna - Context: {context}")
        
        # TODO: Implement Krishna model logic here
        # For now, just a placeholder response
        krishna_response = f'Krishna received: {message}'
        
        # Save the chat to history with Krishna model name
        save_chat_history(uid, chat_id, message, 'user', krishna_response, model_name='krishna')
        
        return jsonify({
            'response': krishna_response,
            'model': 'krishna'
        })
    except Exception as e:
        print(f"Error in chat_krishna: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/fumiko', methods=['POST', 'OPTIONS'])
@auth_required
def fumiko_chat():
    """Handle chat messages for Fumiko model"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        uid = session['user']['uid']
        print(f"\n🤖 Fumiko Chat Request")
        print(f"  User ID: {uid}")
        
        data = request.get_json()
        user_message = data.get('message', '').strip()
        provided_context = data.get('context', '')
        chat_id = data.get('chat_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        print(f"  Message: {user_message[:50]}...")
        print(f"  Chat ID: {chat_id}")
        
        # Fetch context data
        print(f"  📚 Fetching context data...")
        try:
            past_entries_list = get_past_7_days_entries(uid)
            print(f"    ✓ Past entries: {len(past_entries_list)}")
        except Exception as e:
            print(f"    ⚠️ Error fetching past entries: {e}")
            past_entries_list = []
        
        try:
            virtual_profile = get_user_virtual_profile(uid)
            print(f"    ✓ Virtual profile: {'Found' if virtual_profile else 'Not found'}")
        except Exception as e:
            print(f"    ⚠️ Error fetching virtual profile: {e}")
            virtual_profile = None
        
        try:
            chat_history = get_chat_history(uid, limit=5, model_name='fumiko')
            print(f"    ✓ Chat history: {len(chat_history)} messages")
        except Exception as e:
            print(f"    ⚠️ Error fetching chat history: {e}")
            chat_history = []
        
        # Call Fumiko AI
        print(f"  🤖 Calling Fumiko AI...")
        try:
            a = chat_system(provided_context, past_entries_list, chat_history, virtual_profile)
            fumiko_response = a.chat_fumiko(user_message)
            print(f"    ✓ Response generated: {len(fumiko_response)} chars")
        except Exception as ai_error:
            print(f"    ❌ AI Error: {ai_error}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'AI service error: {str(ai_error)}'}), 503
        
        # Add delay for better UX
        if len(user_message) <= 10:
            time.sleep(2)
        else:
            time.sleep(1)
        
        # Save chat history
        print(f"  💾 Saving to database...")
        try:
            save_success = save_chat_history(uid, chat_id, user_message, 'user', fumiko_response, model_name='fumiko')
            if save_success:
                print(f"    ✓ Chat saved successfully")
            else:
                print(f"    ⚠️ Chat save returned False")
        except Exception as save_error:
            print(f"    ⚠️ Error saving chat: {save_error}")
            # Don't fail the response, still send the AI response
        
        print(f"  ✅ Request completed successfully\n")
        
        return jsonify({
            'response': fumiko_response,
            'model': 'fumiko',
            'success': True
        }), 200
        
    except Exception as e:
        print(f"  ❌ Error in fumiko_chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'details': 'Check server logs for more information'
        }), 500


#########################################################
""" Journal Entry Management """

@app.route('/api/test-upload', methods=['POST'])
@auth_required
def test_upload():
    """Test endpoint to diagnose upload issues"""
    try:
        print("\n" + "="*60)
        print("🧪 TEST UPLOAD ENDPOINT")
        print("="*60)
        print(f"Content-Type: {request.content_type}")
        print(f"Content-Length: {request.content_length}")
        print(f"Request Method: {request.method}")
        print(f"\nRequest Files: {list(request.files.keys())}")
        print(f"Request Form: {list(request.form.keys())}")
        
        for key in request.files:
            file = request.files[key]
            print(f"\n  File '{key}':")
            print(f"    Filename: {file.filename}")
            print(f"    Content-Type: {file.content_type}")
            print(f"    Size: {len(file.read())} bytes")
            file.seek(0)
        
        for key in request.form:
            value = request.form[key]
            if len(str(value)) > 100:
                print(f"\n  Form '{key}': {str(value)[:100]}... ({len(str(value))} chars)")
            else:
                print(f"\n  Form '{key}': {value}")
        
        print("\n" + "="*60)
        return jsonify({'success': True, 'message': 'Test upload received'}), 200
    except Exception as e:
        print(f"\n❌ Error in test upload: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/entries', methods=['POST'])
@auth_required
def save_entry():
    """Save a new journal entry or update existing one with media uploads"""
    try:
        uid = session['user']['uid']
        print(f"📝 Saving entry for user: {uid}")
        print(f"📊 Request content-type: {request.content_type}")
        print(f"📊 Request content-length: {request.content_length}")
        
        # Check if we're receiving JSON or FormData
        try:
            if request.is_json:
                print("  ✓ Parsing as JSON")
                data = request.get_json()
            else:
                print("  ✓ Parsing as FormData")
                data = request.form.to_dict()
        except Exception as parse_error:
            print(f"❌ Error parsing request: {parse_error}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Failed to parse request: {str(parse_error)}'}), 400
        
        date_id = data.get('date_id')  # Format: YYYY-MM-DD
        title = data.get('title', 'Untitled Entry')
        blocks = data.get('blocks')
        theme = data.get('theme', 'light')
        font = data.get('font', 'Inter')
        
        print(f"📋 Date ID: {date_id}")
        print(f"📚 Files in request: {list(request.files.keys())}")
        print(f"🎬 Block count: {len(blocks) if blocks else 0}")
        
        if not date_id:
            return jsonify({'error': 'Date ID is required'}), 400
        
        # Parse blocks if it's a string
        import json
        if isinstance(blocks, str):
            blocks = json.loads(blocks)
        elif not blocks:
            blocks = []
        
        # Process each block and upload media files
        processed_blocks = []
        for idx, block in enumerate(blocks):
            processed_block = {
                'id': block.get('id'),
                'type': block.get('type'),
                'text': block.get('text', ''),
                'caption': block.get('caption', '')
            }
            
            print(f"\n🔄 Processing block {idx}: type={block.get('type')}")
            
            # Handle different block types
            if block.get('type') == 'image':
                # Check if we have a file upload or base64 data
                file_key = f'file_{idx}'
                print(f"  Looking for file_key: {file_key}")
                print(f"  Available files: {list(request.files.keys())}")
                
                if file_key in request.files:
                    file = request.files[file_key]
                    print(f"  ✅ Found file: {file.filename}")
                    url = upload_file_to_cloudinary(file, uid, date_id)
                    processed_block['url'] = url if url else block.get('url', '')
                    print(f"  📤 Uploaded to: {processed_block['url'][:50]}...")
                else:
                    # Use existing base64 or URL
                    print(f"  ⚠️ No file found, using base64 data")
                    processed_block['url'] = block.get('url', '')
                    
            elif block.get('type') == 'video':
                file_key = f'file_{idx}'
                if file_key in request.files:
                    file = request.files[file_key]
                    print(f"  ✅ Found video file: {file.filename}")
                    url = upload_file_to_cloudinary(file, uid, date_id)
                    processed_block['url'] = url if url else block.get('url', '')
                else:
                    print(f"  ⚠️ No video file found, using base64 data")
                    processed_block['url'] = block.get('url', '')
                    
            elif block.get('type') == 'document':
                file_key = f'file_{idx}'
                if file_key in request.files:
                    file = request.files[file_key]
                    print(f"  ✅ Found document: {file.filename}")
                    url = upload_file_to_cloudinary(file, uid, date_id)
                    processed_block['url'] = url if url else ''
                    processed_block['fileName'] = block.get('fileName', file.filename)
                    processed_block['fileSize'] = block.get('fileSize', '')
                else:
                    print(f"  ⚠️ No document file found")
                    processed_block['fileName'] = block.get('fileName', '')
                    processed_block['fileSize'] = block.get('fileSize', '')
            
            elif block.get('type') == 'voice':
                file_key = f'file_{idx}'
                if file_key in request.files:
                    file = request.files[file_key]
                    print(f"  ✅ Found voice file: {file.filename}")
                    url = upload_file_to_cloudinary(file, uid, date_id)
                    processed_block['url'] = url if url else block.get('url', '')
                else:
                    print(f"  ⚠️ No voice file found, using base64 data")
                    processed_block['url'] = block.get('url', '')
            
            processed_blocks.append(processed_block)
        
        entry_data = {
            'title': title,
            'blocks': processed_blocks,
            'theme': theme,
            'font': font,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        # Reference to the entry document
        entry_ref = db.collection('artifacts').document('default-journal-app-id').collection('users').document(uid).collection('entries').document(date_id)
        
        # Check if entry exists
        existing_entry = entry_ref.get()
        if not existing_entry.exists:
            entry_data['created_at'] = firestore.SERVER_TIMESTAMP
        
        entry_ref.set(entry_data, merge=True)
        print(f"✅ Entry saved successfully to Firestore!")
        
        return jsonify({
            'success': True,
            'message': 'Entry saved successfully',
            'date_id': date_id,
            'blocks_saved': len(processed_blocks)
        }), 201
    except Exception as e:
        print(f"❌ Error saving entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/entries', methods=['GET'])
@auth_required
def get_past_entries():
    """Retrieve list of all past entries for the user"""
    try:
        uid = session['user']['uid']
        
        entries_ref = db.collection('artifacts').document('default-journal-app-id').collection('users').document(uid).collection('entries')
        docs = entries_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        
        entries = []
        for doc in docs:
            entry_data = doc.to_dict()
            entries.append({
                'date_id': doc.id,
                'title': entry_data.get('title', 'Untitled Entry'),
                'created_at': entry_data.get('created_at'),
                'updated_at': entry_data.get('updated_at'),
                'preview': entry_data.get('blocks', [])[:1]  # Get first block as preview
            })
        
        return jsonify(entries), 200
    except Exception as e:
        print(f"Error retrieving past entries: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/entries/<date_id>', methods=['GET'])
@auth_required
def get_entry(date_id):
    """Retrieve a specific entry by date ID"""
    try:
        uid = session['user']['uid']
        
        entry_ref = db.collection('artifacts').document('default-journal-app-id').collection('users').document(uid).collection('entries').document(date_id)
        entry_doc = entry_ref.get()
        
        if not entry_doc.exists:
            return jsonify({'error': 'Entry not found'}), 404
        
        entry_data = entry_doc.to_dict()
        entry_data['date_id'] = date_id
        
        return jsonify(entry_data), 200
    except Exception as e:
        print(f"Error retrieving entry: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/entries/<date_id>', methods=['DELETE'])
@auth_required
def delete_entry(date_id):
    """Delete a journal entry"""
    try:
        uid = session['user']['uid']
        
        entry_ref = db.collection('artifacts').document('default-journal-app-id').collection('users').document(uid).collection('entries').document(date_id)
        entry_ref.delete()
        
        return jsonify({'success': True, 'message': 'Entry deleted successfully'}), 200
    except Exception as e:
        print(f"Error deleting entry: {e}")
        return jsonify({'error': str(e)}), 500


    # ==================== GEMINI API - Virtual Profile Analysis ====================

def analyze_entry_with_gemini(entry_text, uid):
    """
    Analyze a diary entry using Gemini API to create/update user virtual profile.
    Extracts personality traits, emotional patterns, interests, habits, and behavioral insights.
    """
    if not model or not GEMINI_API_KEY:
        print("⚠️ Gemini API not configured. Skipping analysis.")
        return None
    
    try:
        # Create detailed prompt for user profiling
        prompt = f"""You are a professional psychologist and behavioral analyst. Analyze the following diary entry carefully and provide a comprehensive user profile based on this single entry.

DIARY ENTRY:
{entry_text}

Please provide analysis in the following JSON format:
{{
    "personality_traits": ["list of identified personality traits"],
    "emotional_state": "current emotional state and intensity",
    "interests_hobbies": ["identified interests and hobbies"],
    "habits_patterns": ["behavioral patterns and habits"],
    "values_priorities": ["values and what matters to the user"],
    "challenges_concerns": ["identified challenges or concerns"],
    "behavioral_insights": "key behavioral observations",
    "mental_health_indicators": "positive and any concerning mental health indicators",
    "relationship_insights": "insights about relationships mentioned",
    "summary": "2-3 sentence summary of the user based on this entry"
}}

Be specific, insightful, and nuanced. Look for both explicit and implicit information."""

        response = model.generate_content(prompt)
        
        # Parse the response
        import json
        response_text = response.text
        
        # Try to extract JSON from the response
        try:
            # Find JSON block in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                analysis_data = json.loads(json_str)
            else:
                analysis_data = {"raw_analysis": response_text}
        except json.JSONDecodeError:
            analysis_data = {"raw_analysis": response_text}
        
        # Add metadata
        analysis_data['timestamp'] = datetime.utcnow()
        analysis_data['uid'] = uid
        
        return analysis_data
        
    except Exception as e:
        print(f"❌ Error analyzing entry with Gemini: {e}")
        return None


def daily_analysis_job():
    """
    Scheduled job that runs daily at 12 AM (UTC).
    Fetches all users' latest entries and runs Gemini analysis.
    """
    print(f"\n🔄 Running daily virtual profile analysis job at {datetime.utcnow()}")
    
    try:
        # Get all users
        users_ref = db.collection('artifacts').document('default-journal-app-id').collection('users')
        users = users_ref.stream()
        
        analysis_count = 0
        
        for user_doc in users:
            uid = user_doc.id
            
            try:
                # Get the most recent entry (check last 24 hours)
                entries_ref = users_ref.document(uid).collection('entries')
                
                # Get today's entry (most recent)
                entries_query = entries_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1)
                recent_entries = entries_query.stream()
                
                entry_to_analyze = None
                for entry_doc in recent_entries:
                    entry_data = entry_doc.to_dict()
                    entry_to_analyze = entry_data
                    break
                
                if not entry_to_analyze or not entry_to_analyze.get('text'):
                    continue
                
                # Analyze the entry
                analysis = analyze_entry_with_gemini(entry_to_analyze.get('text', ''), uid)
                
                if analysis:
                    # Save to virtual_profile collection
                    profile_ref = users_ref.document(uid).collection('virtual_profile')
                    
                    # Save analysis with timestamp as document ID
                    timestamp_str = datetime.utcnow().isoformat()
                    profile_ref.document(timestamp_str).set(analysis)
                    
                    analysis_count += 1
                    print(f"✅ Analyzed entry for user {uid}")
                    
            except Exception as e:
                print(f"⚠️ Error processing user {uid}: {e}")
                continue
        
        print(f"✅ Daily analysis job completed. Analyzed {analysis_count} users.")
        
    except Exception as e:
        print(f"❌ Error in daily_analysis_job: {e}")


@app.route('/api/analyze-now', methods=['POST'])
@auth_required
def manual_analysis():
    """Manually trigger analysis for current user's latest entry (for testing)"""
    if not model or not GEMINI_API_KEY:
        return jsonify({'error': 'Gemini API not configured'}), 500
    
    try:
        uid = session['user']['uid']
        
        # Get the most recent entry
        entries_ref = db.collection('artifacts').document('default-journal-app-id').collection('users').document(uid).collection('entries')
        entries_query = entries_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1)
        recent_entries = entries_query.stream()
        
        entry_to_analyze = None
        for entry_doc in recent_entries:
            entry_to_analyze = entry_doc.to_dict()
            break
        
        if not entry_to_analyze or not entry_to_analyze.get('text'):
            return jsonify({'error': 'No entry found to analyze'}), 404
        
        # Analyze the entry
        analysis = analyze_entry_with_gemini(entry_to_analyze.get('text', ''), uid)
        
        if not analysis:
            return jsonify({'error': 'Failed to analyze entry'}), 500
        
        # Save to virtual_profile collection
        profile_ref = db.collection('artifacts').document('default-journal-app-id').collection('users').document(uid).collection('virtual_profile')
        timestamp_str = datetime.utcnow().isoformat()
        profile_ref.document(timestamp_str).set(analysis)
        
        return jsonify({
            'success': True,
            'message': 'Entry analyzed and profile updated',
            'analysis': analysis
        }), 200
        
    except Exception as e:
        print(f"Error in manual analysis: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== FUMIKO AI INTEGRATION ====================


def get_past_7_days_entries(uid):
    """Fetch the past 7 days of diary entries for a user"""
    try:
        entries_ref = db.collection('artifacts').document('default-journal-app-id').collection('users').document(uid).collection('entries')
        
        # Get entries from the last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        entries_query = entries_ref.where('timestamp', '>=', seven_days_ago).order_by('timestamp', direction=firestore.Query.DESCENDING)
        entries = entries_query.stream()
        
        past_entries = []
        for entry_doc in entries:
            entry_data = entry_doc.to_dict()
            entry_data['date_id'] = entry_doc.id
            past_entries.append(entry_data)
        
        return past_entries
        
    except Exception as e:
        print(f"Error fetching past entries: {e}")
        return []


def get_user_virtual_profile(uid):
    """Fetch the most recent virtual profile for a user"""
    try:
        profile_ref = db.collection('artifacts').document('default-journal-app-id').collection('users').document(uid).collection('virtual_profile')
        
        # Get the most recent profile
        profiles = profile_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
        
        for profile_doc in profiles:
            return profile_doc.to_dict()
        
        return None
        
    except Exception as e:
        print(f"Error fetching virtual profile: {e}")
        return None


def get_current_entry(uid):
    """Fetch the current/latest diary entry for a user"""
    try:
        entries_ref = db.collection('artifacts').document('default-journal-app-id').collection('users').document(uid).collection('entries')
        virtual_profile = get_user_virtual_profile(uid)
        chat_history = get_chat_history(uid, limit=10)
        
        return jsonify({
            'success': True,
            'current_entry': current_entry[:200] if current_entry else 'No current entry',
            'past_entries_count': len(past_entries),
            'past_entries': [
                {
                    'date': entry.get('date_id', 'Unknown'),
                    'preview': entry.get('text', 'No text')[:150]
                }
                for entry in past_entries
            ],
            'virtual_profile': {
                'personality_traits': virtual_profile.get('personality_traits', []) if virtual_profile else [],
                'emotional_state': virtual_profile.get('emotional_state', 'Not available') if virtual_profile else 'Not available',
                'interests': virtual_profile.get('interests_hobbies', []) if virtual_profile else [],
                'has_profile': bool(virtual_profile)
            },
            'chat_history_count': len(chat_history)
        }), 200
        
    except Exception as e:
        print(f"Error in fumiko_context: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/fumiko-history', methods=['GET'])
@auth_required
def get_fumiko_history():
    """Get all chat history with Fumiko"""
    try:
        uid = session['user']['uid']
        limit = request.args.get('limit', 50, type=int)
        
        chat_history = get_chat_history(uid, limit=limit)
        
        return jsonify({
            'success': True,
            'messages': chat_history
        }), 200
        
    except Exception as e:
        print(f"Error in get_fumiko_history: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== SCHEDULER SETUP ====================

scheduler = BackgroundScheduler()

# Schedule the analysis job to run every day at 12:00 AM UTC
scheduler.add_job(
    func=daily_analysis_job,
    trigger="cron",
    hour=0,
    minute=0,
    id='daily_analysis_job',
    name='Daily Virtual Profile Analysis',
    replace_existing=True
)

def start_scheduler():
    """Start the background scheduler"""
    if not scheduler.running:
        scheduler.start()
        print("✅ Scheduler started - Daily analysis scheduled for 12:00 AM UTC")

def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("✅ Scheduler stopped")

# Register shutdown handler
atexit.register(stop_scheduler)


if __name__ == '__main__':
    start_scheduler()
    # Run on all network interfaces to allow external access
    app.run( debug=True)