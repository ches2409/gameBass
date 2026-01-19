import os.path
import sys

from app.db import db
from config import DevConfig

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask

def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    
    # registro de Blueprints
    
    # Ruta raíz de prueba
    @app.route("/")
    def index():
        return "Bienvenido a la API de E-sports By ChesDev - TokioSchool"
    
    return app