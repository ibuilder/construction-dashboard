import uuid
import random
import string
from datetime import datetime

def generate_request_id(prefix='REQ', length=8):
    """
    Generate a unique request ID with an optional prefix.
    
    Args:
        prefix (str): Prefix for the request ID (default: 'REQ')
        length (int): Length of the random part of the ID (default: 8)
        
    Returns:
        str: A unique request ID
    """
    # Generate random alphanumeric string
    random_part = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    
    # Include timestamp for better uniqueness
    timestamp = datetime.now().strftime('%Y%m%d')
    
    # Combine prefix, timestamp, and random part
    request_id = f"{prefix}-{timestamp}-{random_part}"
    
    return request_id

def generate_unique_filename(original_filename):
    """
    Generate a unique filename while preserving the original extension.
    
    Args:
        original_filename (str): The original filename
        
    Returns:
        str: A unique filename with the original extension
    """
    # Extract file extension
    if '.' in original_filename:
        extension = original_filename.rsplit('.', 1)[1].lower()
    else:
        extension = ''
    
    # Generate UUID
    unique_id = str(uuid.uuid4())
    
    # Create new filename
    if extension:
        return f"{unique_id}.{extension}"
    else:
        return unique_id

def format_currency(amount, currency='$', decimals=2):
    """
    Format a number as currency
    
    Args:
        amount (float or decimal): The amount to format
        currency (str): Currency symbol
        decimals (int): Number of decimal places
        
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return f"{currency}0.00"
    
    return f"{currency}{float(amount):,.{decimals}f}"

def format_percentage(value, decimals=1):
    """
    Format a number as percentage
    
    Args:
        value (float): The value to format (0.1 for 10%)
        decimals (int): Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    if value is None:
        return "0%"
    
    return f"{float(value) * 100:.{decimals}f}%"

def truncate_text(text, max_length=100, suffix='...'):
    """
    Truncate text to a specified length and add suffix if needed
    
    Args:
        text (str): The text to truncate
        max_length (int): Maximum length
        suffix (str): Suffix to add when truncated
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length] + suffix