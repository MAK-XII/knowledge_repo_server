"""
Configuration management for Knowledge Repository Flask Backend
"""

import os
import secrets
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/knowledge_repo')
    
    # JWT Secret - use env variable or generate a secure random one
    JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_hex(64))
    JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', '24'))
    
    # Server
    PORT = int(os.getenv('PORT', '3000'))
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # File uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB max file size
    
    # S3 (optional)
    S3_BUCKET = os.getenv('S3_BUCKET')
    S3_REGION = os.getenv('S3_REGION', 'us-east-1')
    S3_ENDPOINT = os.getenv('S3_ENDPOINT')
    S3_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
    S3_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_ACCESS_KEY')


config = Config()
