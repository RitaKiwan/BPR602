from flask import Blueprint, request, jsonify
from app.models import Favorite, Dream
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

favorites = Blueprint('favorites', __name__)


@favorites.route('/favorites', methods=['POST'])
@jwt_required()
def add_to_favorites():
    user_id = get_jwt_identity()
    data = request.get_json()
    dream_id = data.get('dream_id')

    if not Dream.query.get(dream_id):
        return jsonify({"msg": "Dream not found"}), 404
    if Favorite.query.filter_by(user_id=user_id, dream_id=dream_id).first():
        return jsonify({"msg": "Already in favorites"}), 400

    new_fav = Favorite(user_id=user_id, dream_id=dream_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Added to favorites"}), 201

@favorites.route('/favorites/<int:dream_id>', methods=['DELETE'])
@jwt_required()
def remove_from_favorites(dream_id):
    user_id = get_jwt_identity()
    fav = Favorite.query.filter_by(user_id=user_id, dream_id=dream_id).first()
    if not fav:
        return jsonify({"msg": "Not found in favorites"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Removed from favorites"}), 200

@favorites.route('/favorites', methods=['GET'])
@jwt_required()
def get_my_favorites():
    user_id = get_jwt_identity()
    my_favs = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([f.to_dict() for f in my_favs])