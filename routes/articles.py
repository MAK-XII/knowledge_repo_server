"""
Articles routes for Knowledge Repository
"""

from flask import Blueprint, request, jsonify
from auth import auth_required, get_current_user
from models.articles import Articles

articles_bp = Blueprint('articles', __name__)


@articles_bp.route('', methods=['GET'])
def get_all():
    """Get all articles with optional filters."""
    try:
        filters = {
            'category_id': request.args.get('category_id'),
            'department_id': request.args.get('department_id'),
            'priority_id': request.args.get('priority_id')
        }
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        articles = Articles.get_all(filters)
        return jsonify(articles)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@articles_bp.route('/search', methods=['GET'])
def search():
    """Search articles."""
    try:
        q = request.args.get('q', '')
        if not q:
            return jsonify([])
        
        articles = Articles.search(q)
        return jsonify(articles)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@articles_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get article statistics."""
    try:
        stats = Articles.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@articles_bp.route('/<int:id>', methods=['GET'])
def get_by_id(id):
    """Get a single article by ID."""
    try:
        article = Articles.get_by_id(id)
        if not article:
            return jsonify({'error': 'Article not found'}), 404
        
        # Increment view count
        Articles.increment_views(id)
        return jsonify(article)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@articles_bp.route('', methods=['POST'])
@auth_required
def create():
    """Create a new article."""
    try:
        data = request.get_json()
        
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        current_user = get_current_user()
        
        article_data = {
            'title': data.get('title'),
            'summary': data.get('summary'),
            'content': data.get('content'),
            'category_id': data.get('category_id'),
            'department_id': data.get('department_id'),
            'priority_id': data.get('priority_id'),
            'author': current_user['email'],
            'author_id': current_user['id'],
            'tags': data.get('tags', []),
            'attachmentIds': data.get('attachmentIds', [])
        }
        
        article = Articles.create(article_data)
        return jsonify(article), 201
        
    except Exception as e:
        print(f'Error creating article: {e}')
        return jsonify({'error': str(e)}), 500


@articles_bp.route('/<int:id>', methods=['PUT'])
@auth_required
def update(id):
    """Update an article."""
    try:
        data = request.get_json()
        
        # Permission check: Admin or Author
        existing = Articles.get_by_id(id)
        if not existing:
            return jsonify({'error': 'Article not found'}), 404
        
        current_user = get_current_user()
        is_author = str(existing.get('author_id')) == str(current_user['id'])
        is_admin = current_user.get('role') == 'admin'
        
        if not is_author and not is_admin:
            return jsonify({'error': 'You do not have permission to edit this article'}), 403
        
        article_data = {
            'title': data.get('title'),
            'summary': data.get('summary'),
            'content': data.get('content'),
            'category_id': data.get('category_id'),
            'department_id': data.get('department_id'),
            'priority_id': data.get('priority_id'),
            'author': data.get('author') or existing.get('author'),
            'author_id': existing.get('author_id'),
            'tags': data.get('tags', []),
            'attachmentIds': data.get('attachmentIds', [])
        }
        
        article = Articles.update(id, article_data)
        return jsonify(article)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@articles_bp.route('/<int:id>', methods=['DELETE'])
@auth_required
def delete(id):
    """Delete an article."""
    try:
        existing = Articles.get_by_id(id)
        if not existing:
            return jsonify({'error': 'Article not found'}), 404
        
        current_user = get_current_user()
        is_author = str(existing.get('author_id')) == str(current_user['id'])
        is_admin = current_user.get('role') == 'admin'
        
        if not is_author and not is_admin:
            return jsonify({'error': 'You do not have permission to delete this article'}), 403
        
        Articles.delete(id)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
