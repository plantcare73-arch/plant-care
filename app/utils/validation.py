"""
Shared validation utilities.

Centralized input validation to avoid duplication across routes.
"""

import os
import re
import uuid
import mimetypes
from PIL import Image
from flask import current_app


def validate_email(email):
    """Validate email format. Returns normalized email or raises ValueError."""
    if not email or not isinstance(email, str):
        raise ValueError('Email is required.')
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError('Invalid email format.')
    if len(email) > 254:
        raise ValueError('Email is too long.')
    return email


def validate_password(password):
    """Validate password strength. Returns password or raises ValueError."""
    if not password or not isinstance(password, str):
        raise ValueError('Password is required.')
    if len(password) < 6:
        raise ValueError('Password must be at least 6 characters.')
    if len(password) > 128:
        raise ValueError('Password is too long.')
    return password


def validate_name(name):
    """Validate user name. Returns stripped name or raises ValueError."""
    if not name or not isinstance(name, str):
        raise ValueError('Name is required.')
    name = name.strip()
    if len(name) < 2:
        raise ValueError('Name must be at least 2 characters.')
    if len(name) > 100:
        raise ValueError('Name is too long.')
    return name


def validate_rating(rating):
    """Validate review rating. Returns int or raises ValueError."""
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        raise ValueError('Rating must be a number between 1 and 5.')
    if rating < 1 or rating > 5:
        raise ValueError('Rating must be between 1 and 5.')
    return rating


def validate_image_upload(file_storage):
    """
    Validate an uploaded image file.

    Checks:
    1. File exists and has a filename
    2. Extension is allowed
    3. MIME type matches
    4. File is actually a valid image (PIL verify)
    5. File size is within limits

    Returns (saved_filepath, filename) or raises ValueError.
    """
    if file_storage is None or file_storage.filename == '':
        raise ValueError('No image file selected.')

    filename = file_storage.filename
    allowed_ext = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg'})

    # Check extension
    if '.' not in filename:
        raise ValueError('Invalid file type. Please upload a PNG or JPG image.')
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_ext:
        raise ValueError(f'Invalid file type .{ext}. Allowed: {", ".join(allowed_ext)}')

    # Check MIME type
    allowed_mimes = current_app.config.get(
        'ALLOWED_MIME_TYPES', {'image/png', 'image/jpeg'}
    )
    content_type = file_storage.content_type or ''
    guessed_type = mimetypes.guess_type(filename)[0] or ''
    if content_type not in allowed_mimes and guessed_type not in allowed_mimes:
        raise ValueError('Invalid image type. Only PNG and JPEG images are accepted.')

    # Save with secure unique filename
    safe_filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = current_app.config['UPLOAD_DIR']
    filepath = os.path.join(upload_dir, safe_filename)
    file_storage.save(filepath)

    # Validate actual image content
    try:
        img = Image.open(filepath)
        img.verify()
    except Exception:
        # Clean up invalid file
        if os.path.exists(filepath):
            os.remove(filepath)
        raise ValueError('The uploaded file is not a valid image.')

    return filepath, safe_filename


def sanitize_string(value, max_length=500):
    """Sanitize a string input."""
    if not isinstance(value, str):
        return ''
    value = value.strip()
    if len(value) > max_length:
        value = value[:max_length]
    return value
