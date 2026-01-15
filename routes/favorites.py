"""
Favorites routes for Knowledge Repository
"""

from flask import Blueprint, jsonify
from auth import auth_required, get_current_user
from models.favorites import Favorites
from models.articles import Articles

favorites_bp = Blueprint('favorites', __name__)


@favorites_bp.route('', methods=['GET'])
@auth_required
def get_favorites():
    """Get user's favorite article IDs."""
    try:
        current_user = get_current_user()
        favorite_ids = Favorites.get_user_favorites(current_user['id'])
        return jsonify(favorite_ids)
    except Exception as e:
        print(f'Error getting favorites: {e}')
        return jsonify({'error': str(e)}), 500


@favorites_bp.route('/<int:article_id>', methods=['POST'])
@auth_required
def add_favorite(article_id):
    """Add article to favorites."""
    try:
        # Check if article exists
        article = Articles.get_by_id(article_id)
        if not article:
            return jsonify({'error': 'Article not found'}), 404
        
        current_user = get_current_user()
        Favorites.add_favorite(current_user['id'], article_id)
        return jsonify({'success': True, 'articleId': article_id})
        
    except Exception as e:
        print(f'Error adding favorite: {e}')
        return jsonify({'error': str(e)}), 500


@favorites_bp.route('/<int:article_id>', methods=['DELETE'])
@auth_required
def remove_favorite(article_id):
    """Remove article from favorites."""
    try:
        current_user = get_current_user()
        Favorites.remove_favorite(current_user['id'], article_id)
        return jsonify({'success': True, 'articleId': article_id})
        
    except Exception as e:
        print(f'Error removing favorite: {e}')
        return jsonify({'error': str(e)}), 500
