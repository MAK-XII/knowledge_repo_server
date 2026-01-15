"""
Tags model for Knowledge Repository
"""

from db import query


class Tags:
    @staticmethod
    def get_all():
        result = query('SELECT * FROM tags ORDER BY name')
        return result['rows']
    
    @staticmethod
    def get_by_id(id):
        result = query('SELECT * FROM tags WHERE id = %s', (id,))
        return result['rows'][0] if result['rows'] else None
    
    @staticmethod
    def get_by_name(name):
        result = query('SELECT * FROM tags WHERE name = %s', (name,))
        return result['rows'][0] if result['rows'] else None
    
    @staticmethod
    def create(name, creator_id=None):
        # Check if tag already exists
        existing = Tags.get_by_name(name)
        if existing:
            return existing
        
        result = query(
            'INSERT INTO tags (name, created_by) VALUES (%s, %s) RETURNING id',
            (name, creator_id)
        )
        return {
            'id': result['rows'][0]['id'],
            'name': name,
            'created_by': creator_id
        }
    
    @staticmethod
    def delete(id):
        query('DELETE FROM tags WHERE id = %s', (id,))
        return True
    
    @staticmethod
    def get_by_article_id(article_id):
        result = query("""
            SELECT t.* FROM tags t
            JOIN article_tags at ON t.id = at.tag_id
            WHERE at.article_id = %s
            ORDER BY t.name
        """, (article_id,))
        return result['rows']
