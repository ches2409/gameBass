import os
import sys
from flask import Flask, request, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from datetime import datetime
import pytz  # Librería para manejo de zonas horarias
from app.utils.permissions import Permissions, Profiles

# Añadir el directorio raíz del proyecto a la ruta de Python para que
# encuentre el módulo 'config' sin importar cómo se ejecute la app.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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

    # --- CONFIGURACIÓN DE FLASK-LOGIN ---
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = (
        "ACCESO DENEGADO: Credenciales requeridas para este sector."
    )
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        # Recarga el objeto usuario desde el ID almacenado en la sesión
        return db.session.get(Usuario, int(user_id))

    # --- FILTROS DE PLANTILLA (CONVERTIDORES) ---
    @app.template_filter("formato_hora_local")
    def formato_hora_local(dt, format="%H:%M:%S"):
        if dt is None:
            return ""

        # 1. Define zona horaria (Ej: 'Europe/Madrid', 'America/Bogota', 'America/Mexico_City')
        # https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        zona_usuario = pytz.timezone("Europe/Madrid")

        # 2. Si la fecha viene sin zona (naive), asumimos que es UTC (estándar en BD)
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)

        # 3. Convertir a la zona del usuario
        dt_local = dt.astimezone(zona_usuario)
        return dt_local.strftime(format)

    # --- CONTEXT PROCESSORS ---
    @app.context_processor
    def inject_permissions():
        return dict(Permissions=Permissions, Profiles=Profiles)

    # --- SEGURIDAD GLOBAL ---
    @app.before_request
    def require_login():
        if not current_user.is_authenticated:
            if (
                request.endpoint
                and not request.endpoint.startswith("auth.")
                and not request.endpoint.startswith("static")
            ):
                # 'next' guarda la url a la que quería ir, para enviarlo allí después de loguearse
                return redirect(url_for("auth.login", next=request.url))

    # registro de Blueprints
    from app.routes.index_routes import inicio_bp
    from app.routes.roles_routes import rol_bp
    from app.routes.protocolos_routes import protocolo_bp
    from app.routes.jerarquias_routes import jerarquia_bp
    from app.routes.juegos_routes import juegos_bp
    from app.routes.torneos_routes import torneos_bp
    from app.routes.equipos_routes import equipos_bp
    from app.routes.usuarios_routes import usuarios_bp
    from app.routes.registros_routes import registros_bp
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(inicio_bp)
    app.register_blueprint(rol_bp)
    app.register_blueprint(protocolo_bp)
    app.register_blueprint(jerarquia_bp)
    app.register_blueprint(juegos_bp)
    app.register_blueprint(torneos_bp)
    app.register_blueprint(equipos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(registros_bp)
    app.register_blueprint(auth_bp)

    return app
