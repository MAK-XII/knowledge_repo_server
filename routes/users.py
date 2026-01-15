"""
Users management routes for Knowledge Repository (Admin Only)
"""

from flask import Blueprint, request, jsonify
from auth import admin_required, get_current_user
from models.users import Users

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@admin_required
def get_all():
    """Get all users (admin only)."""
    try:
        users = Users.get_all()
        return jsonify(users)
    except Exception as e:
        print(f'Error listing users: {e}')
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:id>/role', methods=['PUT'])
@admin_required
def update_role(id):
    """Update user role (admin only)."""
    try:
        data = request.get_json()
        role = data.get('role')
        
        if not role or role not in ['user', 'admin']:
            return jsonify({'error': 'Invalid role. Must be "user" or "admin"'}), 400
        
        current_user = get_current_user()
        
        # Prevent admin from demoting themselves
        if id == current_user['id'] and role != 'admin':
            return jsonify({'error': 'You cannot remove your own admin privileges'}), 400
        
        # Check if target is root user
        target_user = Users.get_by_id(id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        if target_user.get('is_root'):
            return jsonify({'error': 'Cannot modify the root user role'}), 403
        
        updated = Users.update_role(id, role)
        return jsonify(updated)
        
    except Exception as e:
        print(f'Error updating user role: {e}')
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:id>/approve', methods=['PUT'])
@admin_required
def approve_user(id):
    """Approve or reject a user (admin only)."""
    try:
        data = request.get_json()
        approved = data.get('approved')
        
        if not isinstance(approved, bool):
            return jsonify({'error': 'Approved status must be a boolean'}), 400
        
        updated = Users.update_approved(id, approved)
        if not updated:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(updated)
        
    except Exception as e:
        print(f'Error approving user: {e}')
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_user(id):
    """Delete a user (admin only)."""
    try:
        current_user = get_current_user()
        
        # Prevent admin from deleting themselves
        if id == current_user['id']:
            return jsonify({'error': 'You cannot delete yourself'}), 400
        
        Users.delete(id)
        return jsonify({'success': True})
        
    except Exception as e:
        if 'Cannot delete root user' in str(e):
            return jsonify({'error': str(e)}), 403
        print(f'Error deleting user: {e}')
        return jsonify({'error': str(e)}), 500
