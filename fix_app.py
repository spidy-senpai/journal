"""
Script to fix the corrupted app.py file by inserting missing routes
"""

# Read the corrupted file
with open('app.py.backup', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with @app.route('/signup')
insert_pos = None
for i, line in enumerate(lines):
    if line.strip() == "@app.route('/signup')":
        insert_pos = i
        break

if insert_pos is None:
    print("Could not find @app.route('/signup')")
    exit(1)

# The missing routes that should come BEFORE the corrupted section
missing_routes = '''
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


@app.route('/api/fumiko', methods=['POST'])
@auth_required
def fumiko_chat():
    """Handle chat messages for Fumiko model"""
    try:
        uid = session['user']['uid']
        data = request.get_json()
        user_message = data.get('message', '')
        provided_context = data.get('context', '')
        chat_id = data.get('chat_id', 'default')
        
        # Fetch context data
        past_entries_list = get_past_7_days_entries(uid)
        virtual_profile = get_user_virtual_profile(uid)
        chat_history = get_chat_history(uid, limit=5, model_name='fumiko')
        
        # Build prompt for Fumiko
        prompt = f"""You are Fumiko, a warm and empathetic AI companion who helps users with their journaling.
        
User's message: {user_message}

Context from past entries: {past_entries_list[:200] if past_entries_list else 'No past entries'}

Please respond to the user in a friendly and supportive manner."""
        
        # Get response from Gemini
        fumiko_response = send_gemini_prompt(prompt)
        
        # Save the chat to history with Fumiko model name
        save_chat_history(uid, chat_id, user_message, 'user', fumiko_response, model_name='fumiko')
        
        return jsonify({
            'response': fumiko_response,
            'model': 'fumiko'
        })
    except Exception as e:
        print(f"Error in fumiko_chat: {e}")
        return jsonify({'error': str(e)}), 500


#########################################################
""" Journal Entry Management """

@app.route('/api/entries', methods=['POST'])
@auth_required
def save_entry():
    """Save a new journal entry or update existing one with media uploads"""
    try:
        uid = session['user']['uid']
        
        # Check if we're receiving JSON or FormData
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        date_id = data.get('date_id')  # Format: YYYY-MM-DD
        title = data.get('title', 'Untitled Entry')
        blocks = data.get('blocks')
        theme = data.get('theme', 'light')
        font = data.get('font', 'Inter')
        
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
            
            # Handle different block types
            if block.get('type') == 'image':
                # Check if we have a file upload or base64 data
                file_key = f'file_{idx}'
                if file_key in request.files:
                    file = request.files[file_key]
                    url = upload_file_to_cloudinary(file, uid, date_id)
                    processed_block['url'] = url if url else block.get('url', '')
                else:
                    # Use existing base64 or URL
                    processed_block['url'] = block.get('url', '')
                    
            elif block.get('type') == 'video':
                file_key = f'file_{idx}'
                if file_key in request.files:
                    file = request.files[file_key]
                    url = upload_file_to_cloudinary(file, uid, date_id)
                    processed_block['url'] = url if url else block.get('url', '')
                else:
                    processed_block['url'] = block.get('url', '')
                    
            elif block.get('type') == 'document':
                file_key = f'file_{idx}'
                if file_key in request.files:
                    file = request.files[file_key]
                    url = upload_file_to_cloudinary(file, uid, date_id)
                    processed_block['url'] = url if url else ''
                    processed_block['fileName'] = block.get('fileName', file.filename)
                    processed_block['fileSize'] = block.get('fileSize', '')
                else:
                    processed_block['fileName'] = block.get('fileName', '')
                    processed_block['fileSize'] = block.get('fileSize', '')
            
            elif block.get('type') == 'voice':
                file_key = f'file_{idx}'
                if file_key in request.files:
                    file = request.files[file_key]
                    url = upload_file_to_cloudinary(file, uid, date_id)
                    processed_block['url'] = url if url else block.get('url', '')
                else:
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
        
        return jsonify({
            'success': True,
            'message': 'Entry saved successfully',
            'date_id': date_id
        }), 201
    except Exception as e:
        print(f"Error saving entry: {e}")
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

'''

# Remove the corrupt @app.route('/signup') and everything up to @app.route('/api/entries/<date_id>', methods=['GET'])
# which is at line 72 in the current file

end_of_corrupt_section = None
for i in range(insert_pos, min(insert_pos + 10, len(lines))):
    if "@app.route('/api/entries/<date_id>', methods=['GET'])" in lines[i]:
        end_of_corrupt_section = i
        break

if end_of_corrupt_section is None:
    print("Could not find end of corrupt section")
    exit(1)

# Build new file
new_lines = []
new_lines.extend(lines[:insert_pos])  # Everything before @app.route('/signup')
new_lines.append(missing_routes)  # Insert all missing routes
new_lines.extend(lines[end_of_corrupt_section:])  # Everything from @app.route('/api/entries/<date_id>') onwards

# Write the fixed file
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("[SUCCESS] app.py has been fixed!")
print(f"   - Removed lines {insert_pos} to {end_of_corrupt_section}")
print(f"   - Inserted {len(missing_routes.split(chr(10)))} lines of missing code")
