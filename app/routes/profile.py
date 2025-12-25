from flask import Blueprint, request, jsonify
from app.models import User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

profile = Blueprint('profile', __name__)

@profile.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def manage_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id) 
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    if user.account_status != 'active':
        return jsonify({"msg": "Account is disabled"}), 403

    if request.method == 'GET':
        return jsonify(user.to_dict())

    data = request.get_json()

    if 'username' in data:
        if User.query.filter(User.user_id != user_id, User.username == data['username']).first():
            return jsonify({"msg": "Username already taken"}), 409
        user.username = data['username']
    

    if 'email' in data:
        if User.query.filter(User.user_id != user_id, User.email == data['email']).first():
            return jsonify({"msg": "Email already registered"}), 409
        user.email = data['email']

    if 'first_name' in data: user.first_name = data['first_name']
    if 'last_name' in data: user.last_name = data['last_name']

    if 'password' in data:
        if len(data['password']) < 6:
            return jsonify({"msg": "Password too short"}), 400
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify({
        "msg": "Profile updated successfully",
        "user": user.to_dict()
    })