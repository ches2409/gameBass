import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_migrate import Migrate
from config import DevConfig
from app.db import db

# Importar modelos para que SQLAlchemy los reconozca al crear tablas
from app.models.roles_models import Rol

def create_app(config_class=DevConfig):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # registro de Blueprints
    from app.routes.roles_routes import rol_bp
    from app.routes.index_routes import inicio_bp
    
    app.register_blueprint(rol_bp)
    app.register_blueprint(inicio_bp)
    
    
    return app