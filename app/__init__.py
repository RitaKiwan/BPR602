from flask import Flask, jsonify
from flask_migrate import Migrate
from app.extensions import db, jwt, mail
from app.config import Config
from app.models import User, Dream, TokenBlocklist
from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_cors import CORS
migrate = Migrate()


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
       
        if not user or user.role != 'admin':
            return jsonify({"msg": "Admins only!"}), 403
        return fn(*args, **kwargs)
    return wrapper

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db) 

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None

  
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(role='admin').first():
            admin = User(
                username="admin",
                email="admin@dreamapp.com",
                first_name="System",  
                last_name="Admin",  
                role="admin"
            )
            admin.set_password("Admin@123")
            db.session.add(admin)
            db.session.commit()
            print(">>> Admin account created: admin@dreamapp.com / Admin@123")


    from app.routes.auth import auth
    app.register_blueprint(auth)
    
    from app.routes.profile import profile
    app.register_blueprint(profile)
    
    from app.routes.dreams import dreams 
    app.register_blueprint(dreams)
    
    from app.routes.evaluations import evaluations
    app.register_blueprint(evaluations)

    from app.routes.scenes import scenes
    app.register_blueprint(scenes)
   
    from app.routes.favorites import favorites
    app.register_blueprint(favorites)

    from app.routes.sharing import sharing
    app.register_blueprint(sharing)

    from app.routes.info import info
    app.register_blueprint(info)

    from app.routes.admin_management import admin_mgmt
    app.register_blueprint(admin_mgmt)

    from app.routes.monitoring import monitoring
    app.register_blueprint(monitoring)
    
    from app.routes.support import support
    app.register_blueprint(support)
    
    return app