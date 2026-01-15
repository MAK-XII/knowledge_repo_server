"""
Recently Viewed model for Knowledge Repository
"""

from db import query


class RecentlyViewed:
    @staticmethod
    def get_user_recently_viewed(user_id, limit=20):
        result = query("""
            SELECT 
                rv.article_id,
                rv.viewed_at,
                a.title,
                a.summary,
                c.name as category,
                d.name as department
            FROM recently_viewed rv
            JOIN articles a ON rv.article_id = a.id
            LEFT JOIN categories c ON a.category_id = c.id
            LEFT JOIN departments d ON a.department_id = d.id
            WHERE rv.user_id = %s
            AND rv.viewed_at > NOW() - INTERVAL '3 days'
            ORDER BY rv.viewed_at DESC
            LIMIT %s
        """, (user_id, limit))
        return result['rows']
    
    @staticmethod
    def add_view(user_id, article_id):
        # Use ON CONFLICT to update viewed_at if already exists
        query("""
            INSERT INTO recently_viewed (user_id, article_id, viewed_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id, article_id)
            DO UPDATE SET viewed_at = CURRENT_TIMESTAMP
        """, (user_id, article_id))
        
        # Keep only last 20 for this user
        query("""
            DELETE FROM recently_viewed
            WHERE user_id = %s
            AND id NOT IN (
                SELECT id FROM recently_viewed
                WHERE user_id = %s
                ORDER BY viewed_at DESC
                LIMIT 20
            )
        """, (user_id, user_id))
        
        # Delete entries older than 3 days
        query("""
            DELETE FROM recently_viewed
            WHERE user_id = %s
            AND viewed_at < NOW() - INTERVAL '3 days'
        """, (user_id,))
        
        return {'success': True}
    
    @staticmethod
    def clear_user_history(user_id):
        query('DELETE FROM recently_viewed WHERE user_id = %s', (user_id,))
        return {'success': True}
    
    @staticmethod
    def cleanup_old_entries():
        result = query("DELETE FROM recently_viewed WHERE viewed_at < NOW() - INTERVAL '3 days'")
        return {'deleted': result['rowcount']}
