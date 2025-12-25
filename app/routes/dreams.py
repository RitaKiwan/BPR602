from flask import Blueprint, request, jsonify
from app.models import Dream
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

dreams = Blueprint('dreams', __name__)

@dreams.route('/dreams', methods=['POST'])
@jwt_required()
def add_dream():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get('title') or not data.get('description'): 
        return jsonify({"msg": "Title and description required"}), 400

    dream = Dream(
        title=data['title'],
        dream_description=data['description'], 
        mood=data.get('mood'),
        user_id=user_id
    )
    db.session.add(dream)
    db.session.commit()
    return jsonify(dream.to_dict()), 201

@dreams.route('/dreams', methods=['GET'])
@jwt_required()
def get_dreams():
    user_id = get_jwt_identity()

    dreams = Dream.query.filter_by(user_id=user_id).order_by(Dream.created_at.desc()).all()
    return jsonify([d.to_dict() for d in dreams])

@dreams.route('/dreams/<int:dream_id>', methods=['GET'])
@jwt_required()
def get_dream(dream_id):
    user_id = get_jwt_identity()

    dream = Dream.query.filter_by(dream_id=dream_id, user_id=user_id).first()
    if not dream:
        return jsonify({"msg": "Dream not found"}), 404
    return jsonify(dream.to_dict())


@dreams.route('/dreams/<int:dream_id>', methods=['DELETE'])
@jwt_required()
def delete_dream(dream_id):
    user_id = get_jwt_identity()
    dream = Dream.query.filter_by(dream_id=dream_id, user_id=user_id).first()
    if not dream:
        return jsonify({"msg": "Dream not found or unauthorized"}), 404
    db.session.delete(dream)
    db.session.commit()
    return jsonify({"msg": "Dream deleted successfully"}), 200