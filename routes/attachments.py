"""
Attachments and Images upload routes for Knowledge Repository
"""

import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from auth import auth_required
from config import config
from models.attachments import Attachments

attachments_bp = Blueprint('attachments', __name__)

# Ensure uploads directory exists
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)


def generate_unique_filename(original_filename):
    """Generate a unique filename preserving extension."""
    ext = os.path.splitext(original_filename)[1]
    return f"{int(__import__('time').time() * 1000)}-{uuid.uuid4()}{ext}"


@attachments_bp.route('/attachments', methods=['POST'])
@auth_required
def upload_attachment():
    """Upload a file attachment."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'File is required'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'File is required'}), 400
        
        # Generate unique filename
        filename = generate_unique_filename(secure_filename(file.filename))
        filepath = os.path.join(config.UPLOAD_FOLDER, filename)
        
        # Save file
        file.save(filepath)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Generate URL
        file_url = f'/uploads/{filename}'
        
        # Get article_id if provided
        article_id = request.form.get('articleId')
        
        # Create attachment record
        attachment = Attachments.create(
            article_id=article_id if article_id else None,
            file_name=file.filename,
            mime_type=file.content_type,
            size=file_size,
            url=file_url
        )
        
        return jsonify(attachment), 201
        
    except Exception as e:
        print(f'Attachment upload error: {e}')
        return jsonify({'error': str(e)}), 500


@attachments_bp.route('/images', methods=['POST'])
@auth_required
def upload_image():
    """Upload an inline image for article content."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Image file is required'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Image file is required'}), 400
        
        # Check if it's an image
        if not file.content_type or not file.content_type.startswith('image/'):
            return jsonify({'error': 'Only image files are allowed'}), 400
        
        # Generate unique filename
        filename = generate_unique_filename(secure_filename(file.filename))
        filepath = os.path.join(config.UPLOAD_FOLDER, filename)
        
        # Save file
        file.save(filepath)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Generate URL
        file_url = f'/uploads/{filename}'
        
        return jsonify({
            'url': file_url,
            'fileName': file.filename,
            'mimeType': file.content_type,
            'size': file_size
        }), 201
        
    except Exception as e:
        print(f'Image upload error: {e}')
        return jsonify({'error': str(e)}), 500
