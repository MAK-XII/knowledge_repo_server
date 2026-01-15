"""
Seed Root User for Knowledge Repository
Creates or updates the root admin user
"""

import os
import sys

# Add server directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from db import query, init_database, seed_default_data
from auth import hash_password

ROOT_EMAIL = 'rondayan42@gmail.com'
ROOT_PASSWORD = os.getenv('ROOT_INITIAL_PASSWORD', 'BsmartRoot2025!')


def seed_root_user():
    print(f'Checking for root user: {ROOT_EMAIL}...')
    
    try:
        # Initialize database first
        init_database()
        seed_default_data()
        
        # Check if root user exists
        result = query('SELECT * FROM users WHERE email = %s', (ROOT_EMAIL,))
        
        if result['rows']:
            print('Root user already exists.')
            # Ensure admin privileges
            query(
                'UPDATE users SET role = %s, approved = %s, is_root = %s WHERE email = %s',
                ('admin', True, True, ROOT_EMAIL)
            )
            print('Root user privileges confirmed.')
        else:
            print('Root user not found. Creating...')
            password_hash = hash_password(ROOT_PASSWORD)
            
            query(
                'INSERT INTO users (email, password_hash, role, approved, is_root) VALUES (%s, %s, %s, %s, %s)',
                (ROOT_EMAIL, password_hash, 'admin', True, True)
            )
            
            print(f'Root user created successfully.')
            print(f'Email: {ROOT_EMAIL}')
            print(f'Password: {ROOT_PASSWORD}')
            print('IMPORTANT: Change the default password after first login.')
        
    except Exception as e:
        print(f'Error seeding root user: {e}')
        sys.exit(1)


if __name__ == '__main__':
    seed_root_user()
