"""
Recently Viewed routes for Knowledge Repository
"""

from flask import Blueprint, jsonify
from auth import auth_required, get_current_user
from models.recently_viewed import RecentlyViewed
from models.articles import Articles

recently_viewed_bp = Blueprint('recently_viewed', __name__)


@recently_viewed_bp.route('', methods=['GET'])
@auth_required
def get_recently_viewed():
    """Get user's recently viewed articles."""
    try:
        current_user = get_current_user()
        recently_viewed = RecentlyViewed.get_user_recently_viewed(current_user['id'])
        return jsonify(recently_viewed)
    except Exception as e:
        print(f'Error getting recently viewed: {e}')
        return jsonify({'error': str(e)}), 500


@recently_viewed_bp.route('/<int:article_id>', methods=['POST'])
@auth_required
def add_recently_viewed(article_id):
    """Add article to recently viewed."""
    try:
        # Check if article exists
        article = Articles.get_by_id(article_id)
        if not article:
            return jsonify({'error': 'Article not found'}), 404
        
        current_user = get_current_user()
        RecentlyViewed.add_view(current_user['id'], article_id)
        return jsonify({'success': True, 'articleId': article_id})
        
    except Exception as e:
        print(f'Error adding recently viewed: {e}')
        return jsonify({'error': str(e)}), 500


@recently_viewed_bp.route('', methods=['DELETE'])
@auth_required
def clear_recently_viewed():
    """Clear user's recently viewed history."""
    try:
        current_user = get_current_user()
        RecentlyViewed.clear_user_history(current_user['id'])
        return jsonify({'success': True})
    except Exception as e:
        print(f'Error clearing recently viewed: {e}')
        return jsonify({'error': str(e)}), 500
