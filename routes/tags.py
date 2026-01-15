"""
Tags routes for Knowledge Repository
"""

from flask import Blueprint, request, jsonify
from auth import auth_required, get_current_user
from models.tags import Tags

tags_bp = Blueprint('tags', __name__)


@tags_bp.route('', methods=['GET'])
def get_all():
    """Get all tags."""
    try:
        tags = Tags.get_all()
        return jsonify(tags)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tags_bp.route('', methods=['POST'])
@auth_required
def create():
    """Create a new tag."""
    try:
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        current_user = get_current_user()
        tag = Tags.create(name, current_user.get('id'))
        return jsonify(tag), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tags_bp.route('/<int:id>', methods=['DELETE'])
@auth_required
def delete(id):
    """Delete a tag."""
    try:
        tag = Tags.get_by_id(id)
        if not tag:
            return jsonify({'error': 'Tag not found'}), 404
        
        current_user = get_current_user()
        is_admin = current_user and current_user.get('role') == 'admin'
        is_creator = current_user and tag.get('created_by') and str(current_user['id']) == str(tag['created_by'])
        
        if not is_admin and not is_creator:
            return jsonify({'error': 'You do not have permission to delete this tag'}), 403
        
        Tags.delete(id)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
