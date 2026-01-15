"""
Departments routes for Knowledge Repository
"""

from flask import Blueprint, request, jsonify
from auth import auth_required, get_current_user
from models.departments import Departments

departments_bp = Blueprint('departments', __name__)


@departments_bp.route('', methods=['GET'])
def get_all():
    """Get all departments."""
    try:
        departments = Departments.get_all()
        return jsonify(departments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('', methods=['POST'])
@auth_required
def create():
    """Create a new department."""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        current_user = get_current_user()
        department = Departments.create(name, description, current_user.get('id'))
        return jsonify(department), 201
        
    except Exception as e:
        error_msg = str(e)
        if 'unique constraint' in error_msg.lower() or 'duplicate key' in error_msg.lower():
            return jsonify({'error': 'Department already exists'}), 400
        return jsonify({'error': error_msg}), 500


@departments_bp.route('/<int:id>', methods=['PUT'])
def update(id):
    """Update a department."""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        
        department = Departments.update(id, name, description)
        return jsonify(department)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/<int:id>', methods=['DELETE'])
@auth_required
def delete(id):
    """Delete a department."""
    try:
        if Departments.is_in_use(id):
            return jsonify({'error': 'Cannot delete department in use'}), 400
        
        department = Departments.get_by_id(id)
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        current_user = get_current_user()
        is_admin = current_user and current_user.get('role') == 'admin'
        is_creator = current_user and department.get('created_by') and str(current_user['id']) == str(department['created_by'])
        
        if not is_admin and not is_creator:
            return jsonify({'error': 'You do not have permission to delete this department'}), 403
        
        Departments.delete(id)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
