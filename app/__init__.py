import os
import sys
from flask import Flask
from flask_migrate import Migrate

# Añadir el directorio raíz del proyecto a la ruta de Python para que
# encuentre el módulo 'config' sin importar cómo se ejecute la app.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import DevConfig
from app.db import db

# Importar modelos para que SQLAlchemy los reconozca al crear tablas
from app.models.roles_models import Rol
from app.models.protocolos_models import Protocolo
from app.models.jerarquias_models import Jerarquia
from app.models.juegos_models import Juego
from app.models.torneos_models import Torneo
from app.models.equipos_models import Equipo
from app.models.usuarios_models import Usuario
from app.models.registros_models import Registro
from app.models.resultados_models import Resultado


def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # registro de Blueprints
    from app.routes.index_routes import inicio_bp
    from app.routes.roles_routes import rol_bp
    from app.routes.protocolos_routes import protocolo_bp
    from app.routes.jerarquias_routes import jerarquia_bp
    from app.routes.juegos_routes import juegos_bp
    from app.routes.torneos_routes import torneos_bp
    from app.routes.equipos_routes import equipos_bp
    from app.routes.usuarios_routes import usuarios_bp
    
    app.register_blueprint(inicio_bp)
    app.register_blueprint(rol_bp)
    app.register_blueprint(protocolo_bp)
    app.register_blueprint(jerarquia_bp)
    app.register_blueprint(juegos_bp)
    app.register_blueprint(torneos_bp)
    app.register_blueprint(equipos_bp)
    app.register_blueprint(usuarios_bp)
    
    return app
    