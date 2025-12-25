from flask import Blueprint, jsonify
from app.models import User, Dream
from flask_jwt_extended import jwt_required, get_jwt_identity

monitoring = Blueprint('monitoring', __name__)

@monitoring.route('/admin/stats', methods=['GET'])
@jwt_required()
def get_app_stats():

    
    total_users = User.query.count()
    total_dreams = Dream.query.count()
    public_dreams = Dream.query.filter_by(is_public=True).count()
    
    return jsonify({
        "status": "Running",
        "database": "Connected",
        "statistics": {
            "total_users": total_users,
            "total_dreams": total_dreams,
            "published_scenes": public_dreams
        }
    }), 200