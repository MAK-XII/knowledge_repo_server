"""
Categories model for Knowledge Repository
"""

from db import query


class Categories:
    @staticmethod
    def get_all():
        result = query('SELECT * FROM categories ORDER BY name')
        return result['rows']
    
    @staticmethod
    def get_by_id(id):
        result = query('SELECT * FROM categories WHERE id = %s', (id,))
        return result['rows'][0] if result['rows'] else None
    
    @staticmethod
    def create(name, description=None, creator_id=None):
        result = query(
            'INSERT INTO categories (name, description, created_by) VALUES (%s, %s, %s) RETURNING id',
            (name, description, creator_id)
        )
        return {
            'id': result['rows'][0]['id'],
            'name': name,
            'description': description,
            'created_by': creator_id
        }
    
    @staticmethod
    def update(id, name, description=None):
        query(
            'UPDATE categories SET name = %s, description = %s WHERE id = %s',
            (name, description, id)
        )
        return Categories.get_by_id(id)
    
    @staticmethod
    def delete(id):
        query('DELETE FROM categories WHERE id = %s', (id,))
        return True
    
    @staticmethod
    def is_in_use(id):
        result = query('SELECT COUNT(*) as count FROM articles WHERE category_id = %s', (id,))
        return int(result['rows'][0]['count']) > 0
