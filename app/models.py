from datetime import datetime, timezone
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False) 
    role = db.Column(db.String(20), default='User')
    account_status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)


    def set_password(self, password_plain_text):
        self.password = generate_password_hash(password_plain_text)

    def check_password(self, password_plain_text):
        return check_password_hash(self.password, password_plain_text)


    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "full_name": f"{self.first_name} {self.last_name}",
            "email": self.email,
            "role": self.role
        }
class Dream(db.Model):
    __tablename__ = 'dreams' 
    
    dream_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(100), nullable=True) 
    mood = db.Column(db.String(20), nullable=True) 
    dream_description = db.Column(db.Text, nullable=False)
    scene_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending') 
    is_public = db.Column(db.Boolean, default=False) 
    share_token = db.Column(db.String(100), unique=True, nullable=True) 
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user = db.relationship('User', backref='user_dreams')

    def to_dict(self):
        return {
            "dream_id": self.dream_id,
            "user_id": self.user_id,
            "title": self.title,     
            "mood": self.mood,      
            "description": self.dream_description,
            "scene_url": self.scene_url,
            "status": self.status,
            "is_public": self.is_public,
            "share_link": f"/shared/{self.share_token}" if self.share_token else None,
            "date": self.created_at.isoformat()
        }


class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    evaluation_id = db.Column(db.Integer, primary_key=True)
    dream_id = db.Column(db.Integer, db.ForeignKey('dreams.dream_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    
    rating = db.Column(db.Integer, nullable=False) 
    feedback = db.Column(db.Text, nullable=True) 
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "evaluation_id": self.evaluation_id,
            "dream_id": self.dream_id,
            "rating": self.rating,
            "feedback": self.feedback,
            "date": self.created_at.isoformat()
        }

class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Favorite(db.Model):
    __tablename__ = 'favorites'
    favorite_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    dream_id = db.Column(db.Integer, db.ForeignKey('dreams.dream_id'), nullable=False)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    dream = db.relationship('Dream', backref='favorited_by')
    def to_dict(self):
        return {
            "favorite_id": self.favorite_id,
            "dream": self.dream.to_dict(),
            "added_at": self.added_at.isoformat()
        }
    
class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    subject = db.Column(db.String(100))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='open') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)