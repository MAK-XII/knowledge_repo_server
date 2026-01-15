"""
Users model for Knowledge Repository
"""

from db import query


class Users:
    @staticmethod
    def get_by_email(email):
        result = query('SELECT * FROM users WHERE email = %s', (email,))
        return result['rows'][0] if result['rows'] else None
    
    @staticmethod
    def get_by_id(id):
        result = query(
            'SELECT id, email, role, approved, is_root, created_at, last_login_at FROM users WHERE id = %s',
            (id,)
        )
        return result['rows'][0] if result['rows'] else None
    
    @staticmethod
    def create(email, password_hash, role='user', approved=False):
        result = query(
            'INSERT INTO users (email, password_hash, role, approved) VALUES (%s, %s, %s, %s) RETURNING id, email, role, approved',
            (email, password_hash, role, approved)
        )
        return result['rows'][0]
    
    @staticmethod
    def update_last_login(id):
        query('UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = %s', (id,))
    
    @staticmethod
    def update_role(id, role):
        result = query(
            'UPDATE users SET role = %s WHERE id = %s RETURNING id, email, role, approved',
            (role, id)
        )
        return result['rows'][0] if result['rows'] else None
    
    @staticmethod
    def update_approved(id, approved):
        result = query(
            'UPDATE users SET approved = %s WHERE id = %s RETURNING id, email, role, approved',
            (approved, id)
        )
        return result['rows'][0] if result['rows'] else None
    
    @staticmethod
    def get_all():
        result = query(
            'SELECT id, email, role, approved, is_root, created_at, last_login_at FROM users ORDER BY created_at DESC'
        )
        return result['rows']
    
    @staticmethod
    def delete(id):
        # Check if user is root
        user = Users.get_by_id(id)
        if user and user.get('is_root'):
            raise Exception('Cannot delete root user')
        
        query('DELETE FROM users WHERE id = %s', (id,))
        return True
