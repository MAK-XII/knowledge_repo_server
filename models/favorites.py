"""
Favorites model for Knowledge Repository
"""

from db import query


class Favorites:
    @staticmethod
    def get_user_favorites(user_id):
        result = query("""
            SELECT 
                uf.article_id,
                uf.created_at,
                a.title,
                a.summary,
                c.name as category,
                d.name as department
            FROM user_favorites uf
            JOIN articles a ON uf.article_id = a.id
            LEFT JOIN categories c ON a.category_id = c.id
            LEFT JOIN departments d ON a.department_id = d.id
            WHERE uf.user_id = %s
            ORDER BY uf.created_at DESC
        """, (user_id,))
        return result['rows']
    
    @staticmethod
    def add_favorite(user_id, article_id):
        query(
            'INSERT INTO user_favorites (user_id, article_id) VALUES (%s, %s) ON CONFLICT DO NOTHING',
            (user_id, article_id)
        )
        return {'success': True}
    
    @staticmethod
    def remove_favorite(user_id, article_id):
        query(
            'DELETE FROM user_favorites WHERE user_id = %s AND article_id = %s',
            (user_id, article_id)
        )
        return {'success': True}
    
    @staticmethod
    def is_favorited(user_id, article_id):
        result = query(
            'SELECT 1 FROM user_favorites WHERE user_id = %s AND article_id = %s',
            (user_id, article_id)
        )
        return len(result['rows']) > 0
