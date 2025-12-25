import uuid
from flask import Blueprint, request, jsonify
from app.models import Dream
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

sharing = Blueprint('sharing', __name__)

@sharing.route('/dreams/<int:dream_id>/share', methods=['POST'])
@jwt_required()
def toggle_dream_share(dream_id):
    user_id = get_jwt_identity()
    dream = Dream.query.filter_by(dream_id=dream_id, user_id=user_id).first()

    if not dream:
        return jsonify({"msg": "Dream not found"}), 404


    dream.is_public = True
    if not dream.share_token:
        dream.share_token = str(uuid.uuid4())
    
    db.session.commit()
    
    share_url = f"http://127.0.0.1:5000/shared/{dream.share_token}"
    return jsonify({
        "msg": "Dream is now public",
        "share_url": share_url
    }), 200

@sharing.route('/shared/<string:token>', methods=['GET'])
def get_shared_dream(token):
    dream = Dream.query.filter_by(share_token=token, is_public=True).first()
    
    if not dream:
        return jsonify({"msg": "Shared dream not found or private"}), 404
        
    return jsonify({
        "owner": dream.user.username,
        "content": dream.to_dict()
    }), 200