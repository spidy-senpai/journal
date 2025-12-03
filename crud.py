from firebase_admin import firestore
from typing import Dict, Any, List, Optional
import os 
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import traceback
from firebase_config import db

load_dotenv()

# Note: In the 45etdfg environment, this variable must be set to the global __app_id 
# in the actual execution environment. We use a placeholder here for testing.
APP_ID = "default-journal-app-id" 
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

# File Upload Utility Function (Now uses Cloudinary)
def upload_file_to_cloudinary(file, uid, date_id):
    """
    Uploads a file object to Cloudinary and returns its secure URL.
    """
    if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
        print(f"❌ Cloudinary credentials missing!")
        print(f"   Cloud Name: {'✓' if CLOUDINARY_CLOUD_NAME else '✗'}")
        print(f"   API Key: {'✓' if CLOUDINARY_API_KEY else '✗'}")
        print(f"   API Secret: {'✓' if CLOUDINARY_API_SECRET else '✗'}")
        return None # Upload is disabled without credentials
        
    try:
        # Use the user ID and date ID for folder structure on Cloudinary
        folder_path = f"journal_app/{uid}/{date_id}"
        
        # CRITICAL FIX: Reset file pointer before upload.
        file.seek(0)
        print(f"📤 Uploading file: {file.filename}")
        print(f"   Folder: {folder_path}")
        print(f"   File size: {file.content_length or 'unknown'} bytes")
        
        # Upload the file using Cloudinary's upload method
        upload_result = cloudinary.uploader.upload(
            file,
            folder=folder_path,
            resource_type="auto" # Auto-detects image, video, or raw
        )
        
        # Return the secure URL from the result
        url = upload_result.get("secure_url")
        print(f"✅ File uploaded successfully!")
        print(f"   URL: {url}")
        return url

    except Exception as e:
        print(f"❌ Error during file upload to Cloudinary: {e}")
        traceback.print_exc()
        return None






