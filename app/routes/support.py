from flask import Blueprint, request, jsonify
from app.models import SupportTicket, User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import admin_required

support = Blueprint('support', __name__)


@support.route('/support/ticket', methods=['POST'])
@jwt_required()
def create_ticket():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    new_ticket = SupportTicket(
        user_id=user_id,
        subject=data.get('subject'),
        message=data.get('message')
    )
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify({"msg": "Support ticket submitted"}), 201


@support.route('/admin/tickets', methods=['GET'])
@admin_required
def view_tickets():
    tickets = SupportTicket.query.all()
    return jsonify([{
        "id": t.id,
        "user_id": t.user_id,
        "subject": t.subject,
        "status": t.status
    } for t in tickets]), 200