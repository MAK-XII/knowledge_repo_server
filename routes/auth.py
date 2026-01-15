"""
Authentication routes for Knowledge Repository
"""

from flask import Blueprint, request, jsonify
from auth import hash_password, verify_password, create_token, auth_required, get_current_user
from models.users import Users

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Check if user exists
        existing = Users.get_by_email(email)
        if existing:
            return jsonify({'error': 'User already exists'}), 400
        
        # Hash password and create user
        password_hash = hash_password(password)
        user = Users.create(email, password_hash, 'user', False)
        
        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'role': user['role'],
                'approved': user['approved']
            },
            'session': None  # Require approval before login
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = Users.get_by_email(email)
        if not user or not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check approval status
        if not user.get('approved') and not user.get('is_root'):
            return jsonify({'error': 'Account is pending admin approval'}), 403
        
        # Update last login
        Users.update_last_login(user['id'])
        
        # Create JWT token
        token = create_token({
            'id': user['id'],
            'email': user['email'],
            'role': user['role']
        })
        
        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'role': user['role'],
                'approved': user.get('approved')
            },
            'session': {
                'access_token': token,
                'token_type': 'bearer'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@auth_required
def get_me():
    """Get current user info."""
    current_user = get_current_user()
    user = Users.get_by_id(current_user['id'])
    return jsonify({'user': user})


@auth_bp.route('/config', methods=['GET'])
def get_config():
    """Get auth configuration."""
    return jsonify({'hCaptchaSiteKey': None})  # No captcha for local auth
