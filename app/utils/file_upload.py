import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def ensure_directory_exists(directory):
    """Ensure that a directory exists, creating it if necessary"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_file(file, folder, allowed_extensions=None):
    """
    Save an uploaded file with proper validation and security
    
    Args:
        file: FileStorage object from Flask request
        folder: Subfolder within UPLOAD_FOLDER to store the file
        allowed_extensions: Set of allowed extensions (e.g., {'pdf', 'doc'})
    
    Returns:
        Tuple of (success, file_path or error_message)
    """
    if not file:
        return False, "No file provided"
    
    # Validate file extension if specified
    if allowed_extensions:
        extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if extension not in allowed_extensions:
            return False, f"File extension not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    # Ensure upload directory exists
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    ensure_directory_exists(upload_dir)
    
    # Create a secure filename with UUID to prevent collisions
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save the file
    try:
        file.save(file_path)
        return True, file_path
    except Exception as e:
        return False, f"Error saving file: {str(e)}"

def delete_file(file_path):
    """Safely delete a file if it exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False