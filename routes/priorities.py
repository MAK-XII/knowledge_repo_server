"""
Priorities routes for Knowledge Repository
"""

from flask import Blueprint, request, jsonify
from auth import auth_required, get_current_user
from models.priorities import Priorities

priorities_bp = Blueprint('priorities', __name__)


@priorities_bp.route('', methods=['GET'])
def get_all():
    """Get all priorities."""
    try:
        priorities = Priorities.get_all()
        return jsonify(priorities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@priorities_bp.route('', methods=['POST'])
@auth_required
def create():
    """Create a new priority."""
    try:
        data = request.get_json()
        name = data.get('name')
        level = data.get('level', 0)
        color = data.get('color')
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        current_user = get_current_user()
        priority = Priorities.create(name, level, color, current_user.get('id'))
        return jsonify(priority), 201
        
    except Exception as e:
        error_msg = str(e)
        if 'unique constraint' in error_msg.lower() or 'duplicate key' in error_msg.lower():
            return jsonify({'error': 'Priority already exists'}), 400
        return jsonify({'error': error_msg}), 500


@priorities_bp.route('/<int:id>', methods=['PUT'])
def update(id):
    """Update a priority."""
    try:
        data = request.get_json()
        name = data.get('name')
        level = data.get('level', 0)
        color = data.get('color')
        
        priority = Priorities.update(id, name, level, color)
        return jsonify(priority)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@priorities_bp.route('/<int:id>', methods=['DELETE'])
@auth_required
def delete(id):
    """Delete a priority."""
    try:
        if Priorities.is_in_use(id):
            return jsonify({'error': 'Cannot delete priority in use'}), 400
        
        priority = Priorities.get_by_id(id)
        if not priority:
            return jsonify({'error': 'Priority not found'}), 404
        
        current_user = get_current_user()
        is_admin = current_user and current_user.get('role') == 'admin'
        is_creator = current_user and priority.get('created_by') and str(current_user['id']) == str(priority['created_by'])
        
        if not is_admin and not is_creator:
            return jsonify({'error': 'You do not have permission to delete this priority'}), 403
        
        Priorities.delete(id)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
