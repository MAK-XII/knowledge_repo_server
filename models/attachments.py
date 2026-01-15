"""
Attachments model for Knowledge Repository
"""

from db import query


class Attachments:
    @staticmethod
    def create(article_id=None, file_name=None, mime_type=None, size=None, url=None):
        result = query("""
            INSERT INTO attachments (article_id, file_name, mime_type, size, url)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (article_id, file_name, mime_type, size, url))
        return Attachments.get_by_id(result['rows'][0]['id'])
    
    @staticmethod
    def get_by_id(id):
        result = query('SELECT * FROM attachments WHERE id = %s', (id,))
        return result['rows'][0] if result['rows'] else None
    
    @staticmethod
    def get_by_article_id(article_id):
        result = query(
            'SELECT * FROM attachments WHERE article_id = %s ORDER BY created_at DESC',
            (article_id,)
        )
        return result['rows']
    
    @staticmethod
    def detach_from_article(article_id):
        query('UPDATE attachments SET article_id = NULL WHERE article_id = %s', (article_id,))
    
    @staticmethod
    def assign_to_article(article_id, attachment_ids):
        if not attachment_ids:
            return
        
        # Clear current links
        Attachments.detach_from_article(article_id)
        
        # Assign new attachments
        for att_id in attachment_ids:
            query('UPDATE attachments SET article_id = %s WHERE id = %s', (article_id, att_id))
