from flask import Blueprint, request, jsonify
from app.models import User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import admin_required 

admin_mgmt = Blueprint('admin_mgmt', __name__)


@admin_mgmt.route('/admin/users', methods=['GET'])
@admin_required 
def list_users():
    users = User.query.all()

    return jsonify([
        {
            "id": u.user_id, 
            "username": u.username, 
            "email": u.email, 
            "role": u.role
        } for u in users
    ]), 200


@admin_mgmt.route('/admin/users/<int:id>', methods=['DELETE'])
@admin_required
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    

    current_admin_id = get_jwt_identity()
    if int(id) == int(current_admin_id):
        return jsonify({"msg": "You cannot delete your own admin account!"}), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "User deleted successfully"}), 200


@admin_mgmt.route('/admin/promote/<int:id>', methods=['PATCH'])
@admin_required
def promote_to_admin(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    user.role = 'admin'
    db.session.commit()
    return jsonify({"msg": f"User {user.username} has been promoted to Admin"}), 200

@admin_mgmt.route('/admin/users/add', methods=['POST'])
@admin_required
def admin_add_user():
    data = request.get_json()
    
    if not data.get('email') or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "Email, username and password are required"}), 400
  
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"msg": "Email already exists"}), 400

    new_user = User(
        username=data.get('username'),
        email=data.get('email'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        role=data.get('role', 'user')
    )
    new_user.set_password(data.get('password'))
    
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User created successfully by admin"}), 201

@admin_mgmt.route('/admin/users/update/<int:id>', methods=['PUT'])
@admin_required
def admin_update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    data = request.get_json()
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.username = data.get('username', user.username)
    
    if data.get('password'):
        user.set_password(data.get('password'))
        
    db.session.commit()
    return jsonify({"msg": "User data updated by admin"}), 200