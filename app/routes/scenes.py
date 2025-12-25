from flask import Blueprint, request, jsonify
from app.models import Dream
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

scenes = Blueprint('scenes', __name__)

@scenes.route('/dreams/<int:dream_id>/scene', methods=['POST'])
@jwt_required()
def save_dream_scene(dream_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    dream = Dream.query.filter_by(dream_id=dream_id, user_id=user_id).first()
    
    if not dream:
        return jsonify({"msg": "Dream not found"}), 404

    scene_url = data.get('scene_url')
    if not scene_url:
        return jsonify({"msg": "Scene URL is required"}), 400

    dream.scene_url = scene_url
    db.session.commit()
    
    return jsonify({
        "msg": "Dream scene saved successfully",
        "dream_id": dream_id,
        "scene_url": dream.scene_url
    }), 200