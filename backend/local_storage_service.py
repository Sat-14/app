import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import send_file, current_app
import shutil

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads/receipts'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def init_storage():
    """Initialize local storage directories"""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_receipt_to_local(file, user_id):
    """Upload receipt image to local storage"""
    try:
        # Initialize storage
        init_storage()
        
        # Check if file is allowed
        if not allowed_file(file.filename):
            return {
                "success": False, 
                "error": "File type not allowed. Allowed types: " + ", ".join(ALLOWED_EXTENSIONS)
            }
        
        # Create user directory if it doesn't exist
        user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
        os.makedirs(user_folder, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = secure_filename(file.filename).rsplit('.', 1)[1].lower()
        filename = f"{timestamp}_{uuid.uuid4()}.{file_extension}"
        
        # Full path for the file
        file_path = os.path.join(user_folder, filename)
        
        # Save file
        file.save(file_path)
        
        # Generate URL path (relative path that will be used to retrieve the file)
        url_path = f"/api/receipts/view/{user_id}/{filename}"
        
        return {
            "success": True,
            "filename": f"{user_id}/{filename}",
            "url": url_path,
            "full_path": file_path
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_receipt_from_local(filename):
    """Delete receipt from local storage"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"success": True}
        else:
            return {"success": False, "error": "File not found"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_receipt_path(filename):
    """Get full path for a receipt file"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if os.path.exists(file_path):
            return {"success": True, "path": file_path}
        else:
            return {"success": False, "error": "File not found"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_receipt_url(filename):
    """Get URL for receipt (for local storage, returns the view endpoint)"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if os.path.exists(file_path):
            # Extract user_id and filename from the path
            parts = filename.split('/')
            if len(parts) == 2:
                user_id, file_name = parts
                url = f"/api/receipts/view/{user_id}/{file_name}"
            else:
                url = f"/api/receipts/view/{filename}"
                
            return {"success": True, "url": url}
        else:
            return {"success": False, "error": "File not found"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def cleanup_user_receipts(user_id):
    """Clean up all receipts for a user (useful when deleting user account)"""
    try:
        user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}