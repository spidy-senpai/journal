import os
import sys
from flask import session
from unittest.mock import MagicMock

# Add the application directory to the python path
sys.path.append(r'c:\Users\HP\Desktop\journal_prototype1\journal')

from app import app, db

def verify_chat_separation():
    print("Starting verification of chat history separation...")
    
    # Mock authentication
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user'] = {'uid': 'test_user_verification'}
            
        # 1. Send message to Fumiko
        print("\n1. Sending message to Fumiko...")
        response = client.post('/api/fumiko', json={
            'message': 'Hello Fumiko, this is a test.',
            'context': 'Test context'
        })
        if response.status_code == 200:
            print("   -> Success")
        else:
            print(f"   -> Failed: {response.status_code} - {response.data}")

        # 2. Send message to Krishna
        print("\n2. Sending message to Krishna...")
        response = client.post('/api/krishna', json={
            'message': 'Hello Krishna, this is a test.',
            'context': 'Test context'
        })
        if response.status_code == 200:
            print("   -> Success")
        else:
            print(f"   -> Failed: {response.status_code} - {response.data}")

        # 3. Fetch Fumiko History
        print("\n3. Fetching Fumiko History...")
        response = client.get('/api/chat-history?model=fumiko')
        data = response.get_json()
        messages = data.get('messages', [])
        print(f"   -> Found {len(messages)} messages")
        
        fumiko_messages = [m for m in messages if 'Fumiko' in str(m) or 'Hello Fumiko' in str(m)]
        krishna_messages_in_fumiko = [m for m in messages if 'Krishna' in str(m) or 'Hello Krishna' in str(m)]
        
        if len(fumiko_messages) > 0 and len(krishna_messages_in_fumiko) == 0:
             print("   -> VERIFIED: Only Fumiko messages found in Fumiko history.")
        else:
             print("   -> FAILED: Fumiko history contains unexpected messages.")
             print(messages)

        # 4. Fetch Krishna History
        print("\n4. Fetching Krishna History...")
        response = client.get('/api/chat-history?model=krishna')
        data = response.get_json()
        messages = data.get('messages', [])
        print(f"   -> Found {len(messages)} messages")
        
        krishna_messages = [m for m in messages if 'Krishna' in str(m) or 'Hello Krishna' in str(m)]
        fumiko_messages_in_krishna = [m for m in messages if 'Fumiko' in str(m) or 'Hello Fumiko' in str(m)]
        
        if len(krishna_messages) > 0 and len(fumiko_messages_in_krishna) == 0:
             print("   -> VERIFIED: Only Krishna messages found in Krishna history.")
        else:
             print("   -> FAILED: Krishna history contains unexpected messages.")
             print(messages)

        # Cleanup (Optional, but good practice)
        # db.collection('artifacts').document('default-journal-app-id').collection('users').document('test_user_verification').delete()

if __name__ == "__main__":
    verify_chat_separation()
