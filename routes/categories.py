"""
Categories routes for Knowledge Repository
"""

from flask import Blueprint, request, jsonify
from auth import auth_required, get_current_user
from models.categories import Categories

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('', methods=['GET'])
def get_all():
    """Get all categories."""
    try:
        categories = Categories.get_all()
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@categories_bp.route('', methods=['POST'])
@auth_required
def create():
    """Create a new category."""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        current_user = get_current_user()
        category = Categories.create(name, description, current_user.get('id'))
        return jsonify(category), 201
        
    except Exception as e:
        error_msg = str(e)
        if 'unique constraint' in error_msg.lower() or 'duplicate key' in error_msg.lower():
            return jsonify({'error': 'Category already exists'}), 400
        return jsonify({'error': error_msg}), 500


@categories_bp.route('/<int:id>', methods=['PUT'])
def update(id):
    """Update a category."""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        
        category = Categories.update(id, name, description)
        return jsonify(category)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@categories_bp.route('/<int:id>', methods=['DELETE'])
@auth_required
def delete(id):
    """Delete a category."""
    try:
        if Categories.is_in_use(id):
            return jsonify({'error': 'Cannot delete category in use'}), 400
        
        category = Categories.get_by_id(id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        current_user = get_current_user()
        is_admin = current_user and current_user.get('role') == 'admin'
        is_creator = current_user and category.get('created_by') and str(current_user['id']) == str(category['created_by'])
        
        if not is_admin and not is_creator:
            return jsonify({'error': 'You do not have permission to delete this category'}), 403
        
        Categories.delete(id)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
