"""
Priorities model for Knowledge Repository
"""

from db import query


class Priorities:
    @staticmethod
    def get_all():
        result = query('SELECT * FROM priorities ORDER BY level DESC')
        return result['rows']
    
    @staticmethod
    def get_by_id(id):
        result = query('SELECT * FROM priorities WHERE id = %s', (id,))
        return result['rows'][0] if result['rows'] else None
    
    @staticmethod
    def create(name, level=0, color=None, creator_id=None):
        result = query(
            'INSERT INTO priorities (name, level, color, created_by) VALUES (%s, %s, %s, %s) RETURNING id',
            (name, level, color, creator_id)
        )
        return {
            'id': result['rows'][0]['id'],
            'name': name,
            'level': level,
            'color': color,
            'created_by': creator_id
        }
    
    @staticmethod
    def update(id, name, level=0, color=None):
        query(
            'UPDATE priorities SET name = %s, level = %s, color = %s WHERE id = %s',
            (name, level, color, id)
        )
        return Priorities.get_by_id(id)
    
    @staticmethod
    def delete(id):
        query('DELETE FROM priorities WHERE id = %s', (id,))
        return True
    
    @staticmethod
    def is_in_use(id):
        result = query('SELECT COUNT(*) as count FROM articles WHERE priority_id = %s', (id,))
        return int(result['rows'][0]['count']) > 0
