from flask import Blueprint, request, jsonify
from app.models import Evaluation, Dream
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

evaluations = Blueprint('evaluations', __name__)

@evaluations.route('/dreams/<int:dream_id>/evaluate', methods=['POST'])
@jwt_required()
def user_evaluate_dream(dream_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    

    dream = Dream.query.filter_by(dream_id=dream_id, user_id=user_id).first()
    if not dream:
        return jsonify({"msg": "Dream not found"}), 404


    new_eval = Evaluation(
        dream_id=dream_id,
        user_id=user_id,
        rating=data.get('rating'), 
        feedback=data.get('feedback') 
    )
    
    db.session.add(new_eval)
    db.session.commit()
    
    return jsonify({"msg": "Thank you for your feedback!", "evaluation": new_eval.to_dict()}), 201