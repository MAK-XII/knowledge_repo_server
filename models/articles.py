"""
Articles model for Knowledge Repository
"""

import re
from db import query
from models.tags import Tags
from models.attachments import Attachments


class Articles:
    @staticmethod
    def get_all(filters=None):
        if filters is None:
            filters = {}
        
        sql = """
            SELECT 
                a.*,
                c.name as category_name,
                d.name as department_name,
                p.name as priority_name,
                p.color as priority_color,
                p.level as priority_level
            FROM articles a
            LEFT JOIN categories c ON a.category_id = c.id
            LEFT JOIN departments d ON a.department_id = d.id
            LEFT JOIN priorities p ON a.priority_id = p.id
            WHERE 1=1
        """
        params = []
        
        if filters.get('category_id'):
            sql += " AND a.category_id = %s"
            params.append(filters['category_id'])
        
        if filters.get('department_id'):
            sql += " AND a.department_id = %s"
            params.append(filters['department_id'])
        
        if filters.get('priority_id'):
            sql += " AND a.priority_id = %s"
            params.append(filters['priority_id'])
        
        sql += " ORDER BY a.updated_at DESC"
        
        result = query(sql, params if params else None)
        articles = result['rows']
        
        # Get tags and attachments for each article
        for article in articles:
            article['tags'] = Tags.get_by_article_id(article['id'])
            article['attachments'] = Attachments.get_by_article_id(article['id'])
        
        return articles
    
    @staticmethod
    def get_by_id(id):
        result = query("""
            SELECT 
                a.*,
                c.name as category_name,
                d.name as department_name,
                p.name as priority_name,
                p.color as priority_color,
                p.level as priority_level
            FROM articles a
            LEFT JOIN categories c ON a.category_id = c.id
            LEFT JOIN departments d ON a.department_id = d.id
            LEFT JOIN priorities p ON a.priority_id = p.id
            WHERE a.id = %s
        """, (id,))
        
        if not result['rows']:
            return None
        
        article = result['rows'][0]
        article['tags'] = Tags.get_by_article_id(id)
        article['attachments'] = Attachments.get_by_article_id(id)
        
        return article
    
    @staticmethod
    def create(data):
        result = query("""
            INSERT INTO articles (title, summary, content, category_id, department_id, priority_id, author, author_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get('title'),
            data.get('summary'),
            data.get('content'),
            data.get('category_id'),
            data.get('department_id'),
            data.get('priority_id'),
            data.get('author'),
            data.get('author_id')
        ))
        
        article_id = result['rows'][0]['id']
        
        # Add tags
        tags = data.get('tags', [])
        if tags:
            Articles.set_tags(article_id, tags, data.get('author_id'))
        
        # Link attachments
        attachment_ids = data.get('attachmentIds', [])
        if attachment_ids:
            Attachments.assign_to_article(article_id, attachment_ids)
        
        return Articles.get_by_id(article_id)
    
    @staticmethod
    def update(id, data):
        query("""
            UPDATE articles SET
                title = %s,
                summary = %s,
                content = %s,
                category_id = %s,
                department_id = %s,
                priority_id = %s,
                author = %s,
                author_id = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            data.get('title'),
            data.get('summary'),
            data.get('content'),
            data.get('category_id'),
            data.get('department_id'),
            data.get('priority_id'),
            data.get('author'),
            data.get('author_id'),
            id
        ))
        
        # Update tags
        tags = data.get('tags', [])
        if tags is not None:
            Articles.set_tags(id, tags, data.get('author_id'))
        
        # Update attachments
        attachment_ids = data.get('attachmentIds', [])
        if attachment_ids is not None:
            Attachments.assign_to_article(id, attachment_ids)
        
        return Articles.get_by_id(id)
    
    @staticmethod
    def delete(id):
        query('DELETE FROM articles WHERE id = %s', (id,))
        return True
    
    @staticmethod
    def set_tags(article_id, tag_names, author_id=None):
        # Remove existing tags
        query('DELETE FROM article_tags WHERE article_id = %s', (article_id,))
        
        # Add new tags
        for tag_name in tag_names:
            tag = Tags.create(tag_name, author_id)
            query(
                'INSERT INTO article_tags (article_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                (article_id, tag['id'])
            )
    
    @staticmethod
    def increment_views(id):
        query('UPDATE articles SET views = views + 1 WHERE id = %s', (id,))
    
    @staticmethod
    def search(search_term):
        result = query("""
            SELECT 
                a.*,
                c.name as category_name,
                d.name as department_name,
                p.name as priority_name,
                p.color as priority_color,
                p.level as priority_level
            FROM articles a
            LEFT JOIN categories c ON a.category_id = c.id
            LEFT JOIN departments d ON a.department_id = d.id
            LEFT JOIN priorities p ON a.priority_id = p.id
            WHERE 
                a.title ILIKE %s OR 
                a.summary ILIKE %s OR 
                a.content ILIKE %s
            ORDER BY a.updated_at DESC
        """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        articles = result['rows']
        
        # Enrich with tags and snippets
        for article in articles:
            article['tags'] = Tags.get_by_article_id(article['id'])
            article['snippet'] = Articles._generate_snippet(article, search_term)
            article['matchField'] = Articles._get_match_field(article, search_term)
        
        return articles
    
    @staticmethod
    def _generate_snippet(article, search_term):
        """Generate a snippet showing content around the search match."""
        snippet_length = 150
        term = search_term.lower()
        
        # Check title first
        if article.get('title') and term in article['title'].lower():
            return article['title']
        
        # Then summary
        if article.get('summary') and term in article['summary'].lower():
            return Articles._extract_snippet(article['summary'], search_term, snippet_length)
        
        # Finally content (strip HTML first)
        if article.get('content'):
            text_content = re.sub(r'<[^>]*>', ' ', article['content'])
            text_content = re.sub(r'\s+', ' ', text_content)
            if term in text_content.lower():
                return Articles._extract_snippet(text_content, search_term, snippet_length)
        
        return article.get('summary', '')
    
    @staticmethod
    def _extract_snippet(text, search_term, length):
        """Extract a snippet around the match."""
        lower_text = text.lower()
        lower_term = search_term.lower()
        index = lower_text.find(lower_term)
        
        if index == -1:
            return text[:length * 2]
        
        start = max(0, index - length)
        end = min(len(text), index + len(search_term) + length)
        
        snippet = text[start:end]
        if start > 0:
            snippet = '...' + snippet
        if end < len(text):
            snippet = snippet + '...'
        
        return snippet
    
    @staticmethod
    def _get_match_field(article, search_term):
        """Determine which field matched."""
        term = search_term.lower()
        if article.get('title') and term in article['title'].lower():
            return 'title'
        if article.get('summary') and term in article['summary'].lower():
            return 'summary'
        if article.get('content') and term in article['content'].lower():
            return 'content'
        return 'unknown'
    
    @staticmethod
    def get_stats():
        count_result = query('SELECT COUNT(*) as count FROM articles')
        views_result = query('SELECT COALESCE(SUM(views), 0) as total FROM articles')
        
        cat_result = query("""
            SELECT c.name, COUNT(a.id) as count 
            FROM categories c 
            LEFT JOIN articles a ON c.id = a.category_id 
            GROUP BY c.id, c.name
        """)
        
        dep_result = query("""
            SELECT d.name, COUNT(a.id) as count 
            FROM departments d 
            LEFT JOIN articles a ON d.id = a.department_id 
            GROUP BY d.id, d.name
        """)
        
        recent_result = query("""
            SELECT id, title, updated_at 
            FROM articles 
            ORDER BY updated_at DESC 
            LIMIT 5
        """)
        
        return {
            'totalArticles': count_result['rows'][0]['count'],
            'totalViews': views_result['rows'][0]['total'] or 0,
            'byCategory': cat_result['rows'],
            'byDepartment': dep_result['rows'],
            'recentArticles': recent_result['rows']
        }
