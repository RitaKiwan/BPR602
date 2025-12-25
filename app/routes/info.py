from flask import Blueprint, jsonify

info = Blueprint('info', __name__)

@info.route('/about', methods=['GET'])
def get_about_app():
    return jsonify({
        "app_name": "Dream Scene AI",
        "version": "1.0.0",
        "description": "An innovative app that turns your dream descriptions into visual AI-generated scenes.",
        "features": [
            "AI Scene Generation",
            "Dream Journaling",
            "Community Sharing",
            "Dream Evaluations"
        ],
        "developer": "rand❤️😍",
        "contact_email": "support@dreamapp.com"
    }), 200