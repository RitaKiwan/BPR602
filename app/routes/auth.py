from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
from app.models import User, TokenBlocklist
from app.extensions import db, jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
import os
import random


# At the top of auth.py, after imports
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY') or 'dreamweaver-secret')
    return serializer.dumps(email, salt='email-verify')

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY') or 'dreamweaver-secret')
    try:
        email = serializer.loads(token, salt='email-verify', max_age=expiration)
    except:
        return False
    return email

auth = Blueprint('auth', __name__)

# Home
@auth.route('/')
def home():
    return jsonify({"message": "Dreamweaver API"})

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('first_name') or not data.get('last_name'):
        return jsonify({"msg": "Missing fields"}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "Username taken"}), 409
    user = User(
        username=data['username'], 
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "User created"}), 201


@auth.route('/login', methods=['POST'])
def login():
  
    data = request.get_json()
    if not data:
        return jsonify({"msg": "No JSON data provided"}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')
 
    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid credentials"}), 401
    token = create_access_token(identity=str(user.user_id)) 
    return jsonify({
        "access_token": token, 
        "user": user.to_dict()
    }), 200

# Logout
@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()
    return jsonify({"msg": "Logged out"}), 200



@auth.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"msg": "Email not found"}), 404
    otp = str(random.randint(100000, 999999))
    user.otp_code = otp
    user.otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    db.session.commit()
    return jsonify({
        "msg": "Password reset instructions sent",
        "debug_otp": otp 
    }), 200
@auth.route('/verify-email/send', methods=['POST'])
@jwt_required()
def send_verification_email():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.email_verified:
        return jsonify({"msg": "Email already verified"}), 400

    token = generate_confirmation_token(user.email)
    confirm_url = f"http://localhost:3000/verify-email/{token}" 

    # Send email
    msg = Message(
        subject="Dreamweaver – Please Verify Your Email",
        recipients=[user.email],
        html=f"<p>Please click the link to verify: <a href='{confirm_url}'>Verify Email</a></p>"
    )
    from app import mail  
    mail.send(msg)

    return jsonify({"msg": "Verification email sent"}), 200

@auth.route('/verify-email/confirm/<token>', methods=['GET'])
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        return jsonify({"msg": "Invalid or expired token"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.email_verified:
        return jsonify({"msg": "Email already verified"}), 200

    user.email_verified = True
    db.session.commit()
    return jsonify({"msg": "Email verified successfully!"}), 200

@auth.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp_provided = data.get('otp')
    new_password = data.get('new_password')

    user = User.query.filter_by(email=email).first()


    if not user or user.otp_code != otp_provided:
        return jsonify({"msg": "Invalid OTP or Email"}), 400

    if datetime.now(timezone.utc) > user.otp_expiry.replace(tzinfo=timezone.utc):
        return jsonify({"msg": "OTP expired"}), 400

    user.set_password(new_password)
    user.otp_code = None  
    user.otp_expiry = None
    
    db.session.commit()
    return jsonify({"msg": "Password updated successfully"}), 200
