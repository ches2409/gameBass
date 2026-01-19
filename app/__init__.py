import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_migrate import Migrate
from config import DevConfig
from app.db import db



def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # registro de Blueprints
    from app.routes.roles_routes import rol_bp
    app.register_blueprint(rol_bp)
    
    # Ruta raíz de prueba
    @app.route("/")
    def index():
        return "Bienvenido a la API de E-sports By ChesDev - TokioSchool"
    
    return app