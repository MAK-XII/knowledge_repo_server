"""
Authentication utilities for Knowledge Repository
JWT token handling and password hashing compatible with the Node.js version
"""

import hashlib
import secrets
import time
import base64
import hmac
import json
from functools import wraps
from flask import request, jsonify, g
from config import config


def base64url_encode(data: bytes) -> str:
    """Encode bytes to base64url string (no padding)."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def base64url_decode(data: str) -> bytes:
    """Decode base64url string to bytes."""
    # Add back padding
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)


def create_token(payload: dict, expires_in_hours: int = None) -> str:
    """
    Create a JWT token compatible with the Node.js implementation.
    Uses HS256 algorithm with base64url encoding.
    """
    if expires_in_hours is None:
        expires_in_hours = config.JWT_EXPIRY_HOURS
    
    # Header
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64url_encode(json.dumps(header, separators=(',', ':')).encode())
    
    # Payload with expiration
    exp = int(time.time() * 1000) + (expires_in_hours * 60 * 60 * 1000)
    payload_with_exp = {**payload, "exp": exp}
    body_b64 = base64url_encode(json.dumps(payload_with_exp, separators=(',', ':')).encode())
    
    # Signature
    message = f"{header_b64}.{body_b64}"
    signature = hmac.new(
        config.JWT_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = base64url_encode(signature)
    
    return f"{header_b64}.{body_b64}.{signature_b64}"


def verify_token(token: str) -> dict | None:
    """
    Verify a JWT token and return the payload if valid.
    Returns None if invalid or expired.
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_b64, body_b64, signature_b64 = parts
        
        # Verify signature
        message = f"{header_b64}.{body_b64}"
        expected_sig = hmac.new(
            config.JWT_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        expected_sig_b64 = base64url_encode(expected_sig)
        
        if signature_b64 != expected_sig_b64:
            return None
        
        # Decode payload
        payload = json.loads(base64url_decode(body_b64))
        
        # Check expiration
        if 'exp' in payload:
            if time.time() * 1000 > payload['exp']:
                return None
        
        return payload
    except Exception:
        return None


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2 compatible with the Node.js implementation.
    Returns format: salt:hash
    """
    salt = secrets.token_hex(16)
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha512',
        password.encode(),
        salt.encode(),
        10000,
        dklen=64
    )
    return f"{salt}:{hash_bytes.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """
    Verify a password against a stored hash.
    Compatible with the Node.js implementation.
    """
    try:
        salt, stored_hash = stored.split(':')
        hash_bytes = hashlib.pbkdf2_hmac(
            'sha512',
            password.encode(),
            salt.encode(),
            10000,
            dklen=64
        )
        return hash_bytes.hex() == stored_hash
    except Exception:
        return False


def get_current_user():
    """Get the current authenticated user from the request."""
    return getattr(g, 'current_user', None)


def auth_required(f):
    """Decorator to require authentication for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Access denied'}), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 403
        
        # Attach user info to flask g object
        g.current_user = {
            'id': payload.get('id'),
            'email': payload.get('email'),
            'role': payload.get('role', 'user')
        }
        
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator to require admin role for a route."""
    @wraps(f)
    @auth_required
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated
