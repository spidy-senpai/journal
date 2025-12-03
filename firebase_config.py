import firebase_admin
from firebase_admin import credentials, firestore, auth

# Firebase Admin SDK setup
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase-auth.json")
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")

db = firestore.client()

# Frontend config (kept for reference if needed, though usually used in JS)
firebaseConfig = {
  "apiKey": "AIzaSyDXZ_Q3UJKepiwSao4IIo5vBNVx80UJNMo",
  "authDomain": "moon-69bef.firebaseapp.com",
  "projectId": "moon-69bef",
  "storageBucket": "moon-69bef.firebasestorage.app",
  "messagingSenderId": "489523094617",
  "appId": "1:489523094617:web:f641df150b037c7f49bd48",
  "measurementId": "G-3BXWF2S80J"
}